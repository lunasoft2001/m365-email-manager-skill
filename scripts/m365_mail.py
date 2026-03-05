#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

# Importar token manager
import token_manager

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
FOLDER_MAP = {
    "inbox": "inbox",
    "drafts": "drafts",
    "sent": "sentitems",
    "trash": "deleteditems",
    "spam": "junkemail",
    "archive": "archive",
}


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _get_body_content(args: argparse.Namespace) -> str:
    """
    Obtener el contenido del body desde múltiples fuentes:
    1. Argumento --body (línea de comandos)
    2. Archivo --body-file
    3. stdin (si está disponible y no es terminal)
    """
    # Opción 1: --body desde línea de comandos
    if hasattr(args, 'body') and args.body:
        return args.body
    
    # Opción 2: --body-file (leer desde archivo)
    if hasattr(args, 'body_file') and args.body_file:
        try:
            file_path = args.body_file
            # Si es ruta relativa y no existe, intentar desde el directorio padre del script
            if not os.path.isabs(file_path) and not os.path.exists(file_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(script_dir)
                alt_path = os.path.join(parent_dir, file_path)
                if os.path.exists(alt_path):
                    file_path = alt_path
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"El archivo no existe: {args.body_file}")
        except IOError as e:
            raise RuntimeError(f"Error al leer archivo: {e}")
    
    # Opción 3: stdin
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except Exception as e:
            raise RuntimeError(f"Error al leer stdin: {e}")
    
    # Si no hay ninguna opción disponible
    raise RuntimeError(
        "El body es requerido. Proporciona uno de:\n"
        "  --body 'texto' (para textos cortos)\n"
        "  --body-file ruta/archivo.txt (para textos largos)\n"
        "  echo 'texto' | m365_mail.py send ... (desde pipe/stdin)"
    )


def get_graph_token() -> str:
    """Obtener token de Graph usando token_manager."""
    return token_manager.get_graph_token()


def graph_request(
    method: str,
    path: str,
    token: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{GRAPH_BASE}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url=url, method=method, data=data)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/json")
    if body is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8") if err.fp else ""
        msg = f"Graph API error {err.code}: {detail or err.reason}"
        raise RuntimeError(msg) from err


def build_user_path(user: Optional[str]) -> str:
    # Si no se especifica user, intenta usar el usuario por defecto
    if not user:
        user = token_manager.get_default_user()
    
    if user:
        return f"/users/{urllib.parse.quote(user)}"
    return "/me"


def normalize_message(item: Dict[str, Any]) -> Dict[str, Any]:
    sender = (item.get("from") or {}).get("emailAddress") or {}
    return {
        "id": item.get("id"),
        "subject": item.get("subject"),
        "from": sender.get("address"),
        "fromName": sender.get("name"),
        "receivedDateTime": item.get("receivedDateTime"),
        "isRead": item.get("isRead"),
    }


def list_messages(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)
    filter_expr = "isRead eq false" if args.unread else ""
    query = {
        "$top": str(args.top),
        "$select": "id,subject,from,receivedDateTime,isRead",
        "$orderby": "receivedDateTime desc",
    }
    if filter_expr:
        query["$filter"] = filter_expr

    result = graph_request("GET", f"{base}/messages", token, query=query)
    items = [normalize_message(item) for item in result.get("value", [])]
    _print_json({"count": len(items), "messages": items})


def search_messages(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)
    query = {
        "$search": f'"{args.query}"',
        "$top": str(args.top),
        "$select": "id,subject,from,receivedDateTime,isRead",
        "$orderby": "receivedDateTime desc",
    }

    result = graph_request("GET", f"{base}/messages", token, query=query)
    items = [normalize_message(item) for item in result.get("value", [])]
    _print_json({"count": len(items), "messages": items})


def mark_read(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)
    graph_request(
        "PATCH",
        f"{base}/messages/{urllib.parse.quote(args.message_id)}",
        token,
        body={"isRead": True},
    )
    _print_json({"status": "ok", "action": "mark-read", "messageId": args.message_id})


def send_mail(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)

    to_recipients = [
        {"emailAddress": {"address": email.strip()}}
        for email in args.to.split(",")
        if email.strip()
    ]
    if not to_recipients:
        raise RuntimeError("Debes indicar al menos un destinatario en --to")

    cc_recipients = [
        {"emailAddress": {"address": email.strip()}}
        for email in (args.cc or "").split(",")
        if email.strip()
    ]

    # Obtener body desde múltiples fuentes
    body_content = _get_body_content(args)

    body = {
        "message": {
            "subject": args.subject,
            "body": {"contentType": "Text", "content": body_content},
            "toRecipients": to_recipients,
            "ccRecipients": cc_recipients,
        },
        "saveToSentItems": True,
    }

    graph_request("POST", f"{base}/sendMail", token, body=body)
    _print_json({"status": "ok", "action": "send"})


def move_mail(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)
    folder = FOLDER_MAP.get(args.folder.lower())
    if not folder:
        allowed = ", ".join(sorted(FOLDER_MAP.keys()))
        raise RuntimeError(f"Folder inválida. Usa una de: {allowed}")

    result = graph_request(
        "POST",
        f"{base}/messages/{urllib.parse.quote(args.message_id)}/move",
        token,
        body={"destinationId": folder},
    )
    _print_json(
        {
            "status": "ok",
            "action": "move",
            "messageId": args.message_id,
            "destination": args.folder,
            "resultId": result.get("id"),
        }
    )


def reply_mail(args: argparse.Namespace) -> None:
    token = get_graph_token()
    base = build_user_path(args.user)
    
    # Obtener body desde múltiples fuentes
    body_content = _get_body_content(args)
    
    reply_body: Dict[str, Any] = {"comment": body_content}

    if args.cc:
        reply_body["message"] = {
            "ccRecipients": [
                {"emailAddress": {"address": email.strip()}}
                for email in args.cc.split(",")
                if email.strip()
            ]
        }

    graph_request(
        "POST",
        f"{base}/messages/{urllib.parse.quote(args.message_id)}/reply",
        token,
        body=reply_body,
    )
    _print_json({"status": "ok", "action": "reply", "messageId": args.message_id})


def parser_builder() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gestor de correos M365 por Microsoft Graph")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--user", help="UPN del buzón (si se omite usa /me)")

    list_cmd = sub.add_parser("list", parents=[common], help="Listar correos")
    list_cmd.add_argument("--top", type=int, default=15)
    list_cmd.add_argument("--unread", action="store_true")
    list_cmd.set_defaults(func=list_messages)

    search_cmd = sub.add_parser("search", parents=[common], help="Buscar correos")
    search_cmd.add_argument("--query", required=True, help="Texto a buscar")
    search_cmd.add_argument("--top", type=int, default=25)
    search_cmd.set_defaults(func=search_messages)

    mark_cmd = sub.add_parser("mark-read", parents=[common], help="Marcar como leído")
    mark_cmd.add_argument("--message-id", required=True)
    mark_cmd.set_defaults(func=mark_read)

    send_cmd = sub.add_parser("send", parents=[common], help="Enviar correo")
    send_cmd.add_argument("--to", required=True, help="Destinatarios separados por coma")
    send_cmd.add_argument("--subject", required=True)
    send_cmd.add_argument("--body", help="Cuerpo del correo (o --body-file o stdin)")
    send_cmd.add_argument("--body-file", help="Leer body desde archivo")
    send_cmd.add_argument("--cc", help="CC separado por coma")
    send_cmd.set_defaults(func=send_mail)

    move_cmd = sub.add_parser("move", parents=[common], help="Mover correo")
    move_cmd.add_argument("--message-id", required=True)
    move_cmd.add_argument("--folder", required=True, help="inbox|drafts|sent|trash|spam|archive")
    move_cmd.set_defaults(func=move_mail)

    reply_cmd = sub.add_parser("reply", parents=[common], help="Responder correo")
    reply_cmd.add_argument("--message-id", required=True)
    reply_cmd.add_argument("--body", help="Texto de respuesta (o --body-file o stdin)")
    reply_cmd.add_argument("--body-file", help="Leer body desde archivo")
    reply_cmd.add_argument("--cc", help="CC separado por coma")
    reply_cmd.set_defaults(func=reply_mail)

    return parser


def main() -> None:
    parser = parser_builder()
    args = parser.parse_args()

    try:
        args.func(args)
    except RuntimeError as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
