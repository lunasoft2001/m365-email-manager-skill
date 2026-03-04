#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
DEFAULT_USER = os.environ.get("M365_USER", "")


def _get_access_token():
    token_from_env = os.environ.get("GRAPH_ACCESS_TOKEN", "").strip()
    if token_from_env:
        return token_from_env

    try:
        result = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource-type",
                "ms-graph",
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "No se encontró Azure CLI. Instala az o define GRAPH_ACCESS_TOKEN."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise RuntimeError(
            "No fue posible obtener token con Azure CLI. Ejecuta 'az login' o define GRAPH_ACCESS_TOKEN."
            + (f" Detalle: {stderr}" if stderr else "")
        ) from exc

    token = result.stdout.strip()
    if not token:
        raise RuntimeError(
            "Azure CLI no devolvió access token. Ejecuta 'az login' o define GRAPH_ACCESS_TOKEN."
        )

    return token


def _graph_request(method, path, token, data=None, extra_headers=None):
    url = f"{GRAPH_BASE_URL}{path}"
    payload = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if extra_headers:
        headers.update(extra_headers)

    request = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Graph API devolvió HTTP {exc.code}: {details}") from exc


def _encode_user(user):
    return urllib.parse.quote(user, safe="@.-_")


def _print_messages(messages):
    if not messages:
        print("No se encontraron mensajes.")
        return

    for item in messages:
        sender = (
            (item.get("from") or {})
            .get("emailAddress", {})
            .get("address", "desconocido")
        )
        received = item.get("receivedDateTime", "")
        status = "LEÍDO" if item.get("isRead") else "NO LEÍDO"
        subject = (item.get("subject") or "(sin asunto)").replace("\n", " ").strip()
        print(f"- [{status}] {received} | {sender} | {subject} | id={item.get('id','')}")


def command_list(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)

    query_params = [
        ("$select", "id,subject,from,receivedDateTime,isRead"),
        ("$orderby", "receivedDateTime desc"),
        ("$top", str(args.top)),
    ]

    if args.unread:
        query_params.append(("$filter", "isRead eq false"))

    query = urllib.parse.urlencode(query_params)
    path = f"/users/{user}/mailFolders/{urllib.parse.quote(args.folder)}/messages?{query}"
    response = _graph_request("GET", path, token)
    _print_messages(response.get("value", []))


def command_search(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)

    query_params = [
        ("$search", f'"{args.query}"'),
        ("$select", "id,subject,from,receivedDateTime,isRead"),
        ("$top", str(args.top)),
    ]

    query = urllib.parse.urlencode(query_params)
    path = f"/users/{user}/messages?{query}"
    response = _graph_request(
        "GET",
        path,
        token,
        extra_headers={"ConsistencyLevel": "eventual"},
    )
    _print_messages(response.get("value", []))


def command_mark_read(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)
    message_id = urllib.parse.quote(args.message_id, safe="")

    path = f"/users/{user}/messages/{message_id}"
    _graph_request("PATCH", path, token, data={"isRead": True})
    print("Mensaje actualizado a leído.")


def command_send(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)

    recipients = []
    for address in args.to.split(","):
        email = address.strip()
        if email:
            recipients.append({"emailAddress": {"address": email}})

    if not recipients:
        raise RuntimeError("Debes indicar al menos un destinatario en --to.")

    body_type = "HTML" if args.body_is_html else "Text"
    payload = {
        "message": {
            "subject": args.subject,
            "body": {
                "contentType": body_type,
                "content": args.body,
            },
            "toRecipients": recipients,
        },
        "saveToSentItems": True,
    }

    path = f"/users/{user}/sendMail"
    _graph_request("POST", path, token, data=payload)
    print("Correo enviado correctamente.")


def command_move(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)
    message_id = urllib.parse.quote(args.message_id, safe="")

    folder_id = _get_folder_id(token, user, args.folder)
    if not folder_id:
        raise RuntimeError(f"No se encontró la carpeta: {args.folder}")

    path = f"/users/{user}/messages/{message_id}/move"
    payload = {"destinationId": folder_id}
    _graph_request("POST", path, token, data=payload)
    print(f"Correo movido a {args.folder}.")


def _get_folder_id(token, user, folder_name):
    common_folders = {
        "inbox": "inbox",
        "drafts": "drafts",
        "sent": "sentitems",
        "trash": "deleteditems",
        "spam": "junkemail",
        "archive": "archive",
    }

    if folder_name.lower() in common_folders:
        return common_folders[folder_name.lower()]
    
    return folder_name


def command_reply(args):
    if not args.user:
        raise RuntimeError(
            "Debes especificar --user o definir M365_USER en el entorno.\n"
            "Ejemplo: export M365_USER='tu-usuario@empresa.onmicrosoft.com'"
        )
    token = _get_access_token()
    user = _encode_user(args.user)
    message_id = urllib.parse.quote(args.message_id, safe="")

    body_type = "HTML" if args.body_is_html else "Text"
    payload = {
        "message": {
            "body": {
                "contentType": body_type,
                "content": args.body,
            }
        }
    }

    if args.cc:
        recipients = []
        for address in args.cc.split(","):
            email = address.strip()
            if email:
                recipients.append({"emailAddress": {"address": email}})
        if recipients:
            payload["message"]["ccRecipients"] = recipients

    path = f"/users/{user}/messages/{message_id}/reply"
    _graph_request("POST", path, token, data=payload)
    print("Respuesta enviada correctamente.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Gestión básica de correo Microsoft 365 via Microsoft Graph"
    )
    parser.add_argument(
        "--user",
        default=DEFAULT_USER,
        help="UPN/correo de la cuenta de Microsoft 365 (o define M365_USER)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_list = subparsers.add_parser("list", help="Listar correos de una carpeta")
    parser_list.add_argument("--folder", default="inbox", help="Carpeta (default: inbox)")
    parser_list.add_argument("--top", type=int, default=10, help="Cantidad máxima")
    parser_list.add_argument(
        "--unread", action="store_true", help="Filtrar solo correos no leídos"
    )
    parser_list.set_defaults(handler=command_list)

    parser_search = subparsers.add_parser("search", help="Buscar correos por texto")
    parser_search.add_argument("--query", required=True, help="Texto a buscar")
    parser_search.add_argument("--top", type=int, default=10, help="Cantidad máxima")
    parser_search.set_defaults(handler=command_search)

    parser_mark = subparsers.add_parser("mark-read", help="Marcar correo como leído")
    parser_mark.add_argument("--message-id", required=True, help="ID del mensaje")
    parser_mark.set_defaults(handler=command_mark_read)

    parser_send = subparsers.add_parser("send", help="Enviar correo")
    parser_send.add_argument("--to", required=True, help="Destinatario(s), separado por coma")
    parser_send.add_argument("--subject", required=True, help="Asunto")
    parser_send.add_argument("--body", required=True, help="Contenido")
    parser_send.add_argument(
        "--body-is-html",
        action="store_true",
        help="Indicar que --body está en HTML",
    )
    parser_send.set_defaults(handler=command_send)

    parser_move = subparsers.add_parser("move", help="Mover correo a una carpeta")
    parser_move.add_argument("--message-id", required=True, help="ID del mensaje")
    parser_move.add_argument(
        "--folder",
        required=True,
        help="Carpeta destino (inbox, drafts, sent, trash, spam, archive)",
    )
    parser_move.set_defaults(handler=command_move)

    parser_reply = subparsers.add_parser("reply", help="Responder a un correo")
    parser_reply.add_argument("--message-id", required=True, help="ID del mensaje a responder")
    parser_reply.add_argument("--body", required=True, help="Contenido de la respuesta")
    parser_reply.add_argument(
        "--cc",
        default="",
        help="Direcciones en CC (opcional), separado por coma",
    )
    parser_reply.add_argument(
        "--body-is-html",
        action="store_true",
        help="Indicar que --body está en HTML",
    )
    parser_reply.set_defaults(handler=command_reply)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.handler(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
