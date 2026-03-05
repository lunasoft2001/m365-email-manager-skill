#!/usr/bin/env python3
"""
Token manager para m365-email-manager.
Maneja obtención y refresh de tokens de forma transparente.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


CONFIG_DIR = os.path.expanduser("~/.m365_email_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> Dict[str, Any]:
    """Cargar configuración guardada."""
    if not os.path.exists(CONFIG_FILE):
        raise RuntimeError(
            "❌ No hay configuración. Ejecuta primero:\n"
            "   python3 scripts/setup.py"
        )
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_from_keychain(account: str) -> Optional[str]:
    """Recuperar valor del keychain de macOS."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "m365-email-manager", "-a", account, "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _post_form(url: str, payload: Dict[str, str]) -> Dict[str, Any]:
    """Hacer POST con form-urlencoded."""
    body = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url=url, method="POST", data=body)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(request) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw)


def refresh_access_token(client_id: str, tenant_id: str, refresh_token: str) -> str:
    """Refrescar el access token usando refresh token."""
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    try:
        token_data = _post_form(token_url, {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
            "scope": (
                "https://graph.microsoft.com/Mail.Read "
                "https://graph.microsoft.com/Mail.ReadWrite "
                "https://graph.microsoft.com/Mail.Send "
                "offline_access"
            )
        })
        
        new_access_token = token_data.get("access_token")
        if not new_access_token:
            raise RuntimeError("No se obtuvo access token en refresh")
        
        # Opcionalmente guardar nuevo refresh token si vino en la respuesta
        new_refresh_token = token_data.get("refresh_token")
        if new_refresh_token:
            subprocess.run(
                [
                    "security",
                    "add-generic-password",
                    "-s", "m365-email-manager",
                    "-a", "refresh_token",
                    "-w", new_refresh_token,
                    "-U"
                ],
                check=True,
                capture_output=True
            )
        
        return new_access_token
        
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8") if err.fp else err.reason
        raise RuntimeError(f"Error al refrescar token: {detail}") from err


def get_graph_token() -> str:
    """
    Obtener token de acceso para Graph API.
    Intenta en este orden:
    1. Variable de entorno GRAPH_ACCESS_TOKEN
    2. Token guardado en configuración (desde keychain)
    3. Si no está disponible, indicar setup
    """
    
    # Opción 1: Variable de entorno
    env_token = os.getenv("GRAPH_ACCESS_TOKEN")
    if env_token:
        return env_token.strip()
    
    # Opción 2: Keychain + refresh si es necesario
    try:
        config = load_config()
        refresh_token = get_from_keychain("refresh_token")
        
        if not refresh_token:
            raise RuntimeError(
                "❌ No hay refresh token en keychain. Ejecuta:\n"
                "   python3 scripts/setup.py"
            )
        
        # Refrescar token
        new_token = refresh_access_token(
            config["client_id"],
            config["tenant_id"],
            refresh_token
        )
        return new_token
        
    except RuntimeError as e:
        if "No hay configuración" in str(e):
            print(str(e), file=sys.stderr)
            sys.exit(1)
        raise


def get_default_user() -> Optional[str]:
    """Obtener usuario por defecto desde configuración."""
    try:
        config = load_config()
        return config.get("default_user")
    except RuntimeError:
        return None
