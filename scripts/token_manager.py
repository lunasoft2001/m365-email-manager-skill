#!/usr/bin/env python3
"""
Token manager para m365-email-manager-skill.
Maneja obtención y refresh de tokens de forma transparente.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


CONFIG_DIR = os.path.expanduser("~/.m365_email_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
REFRESH_TOKEN_FILE = os.path.join(CONFIG_DIR, "refresh_token.txt")
SERVICE_NAME = "m365-email-manager-skill"
LEGACY_SERVICE_NAME = "m365-email-manager"


def load_config() -> Dict[str, Any]:
    """Cargar configuración guardada."""
    if not os.path.exists(CONFIG_FILE):
        raise RuntimeError(
            "❌ No hay configuración. Ejecuta primero:\n"
            "   python3 scripts/setup.py"
        )
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def _load_keyring():
    """Cargar keyring si está disponible en el entorno."""
    try:
        import keyring  # type: ignore
        return keyring
    except ImportError:
        return None


def _get_from_macos_keychain(service: str, account: str) -> Optional[str]:
    """Recuperar valor desde keychain de macOS (compatibilidad)."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _save_to_macos_keychain(service: str, account: str, password: str) -> None:
    """Guardar valor en keychain de macOS (compatibilidad)."""
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-s", service,
            "-a", account,
            "-w", password,
            "-U"
        ],
        check=True,
        capture_output=True
    )


def _get_refresh_token_from_file() -> Optional[str]:
    """Leer refresh token desde archivo local protegido."""
    if not os.path.exists(REFRESH_TOKEN_FILE):
        return None
    try:
        with open(REFRESH_TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()
        return token or None
    except OSError:
        return None


def _save_refresh_token_to_file(refresh_token: str) -> None:
    """Guardar refresh token en archivo local protegido."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    with open(REFRESH_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(refresh_token)
    try:
        os.chmod(REFRESH_TOKEN_FILE, 0o600)
    except (PermissionError, NotImplementedError):
        pass


def get_refresh_token() -> Optional[str]:
    """Obtener refresh token desde keyring, keychain o archivo local."""
    keyring = _load_keyring()
    if keyring:
        try:
            token = keyring.get_password(SERVICE_NAME, "refresh_token")
            if token:
                return token
            legacy_token = keyring.get_password(LEGACY_SERVICE_NAME, "refresh_token")
            if legacy_token:
                return legacy_token
        except Exception:
            pass

    if sys.platform == "darwin":
        token = _get_from_macos_keychain(SERVICE_NAME, "refresh_token")
        if token:
            return token
        legacy_token = _get_from_macos_keychain(LEGACY_SERVICE_NAME, "refresh_token")
        if legacy_token:
            return legacy_token

    return _get_refresh_token_from_file()


def save_refresh_token(refresh_token: str) -> None:
    """Guardar refresh token en el backend disponible."""
    keyring = _load_keyring()
    if keyring:
        try:
            keyring.set_password(SERVICE_NAME, "refresh_token", refresh_token)
            return
        except Exception:
            pass

    if sys.platform == "darwin":
        try:
            _save_to_macos_keychain(SERVICE_NAME, "refresh_token", refresh_token)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                _save_to_macos_keychain(LEGACY_SERVICE_NAME, "refresh_token", refresh_token)
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

    _save_refresh_token_to_file(refresh_token)


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
            save_refresh_token(new_refresh_token)
        
        return new_access_token
        
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8") if err.fp else err.reason
        raise RuntimeError(f"Error al refrescar token: {detail}") from err


def get_graph_token() -> str:
    """
    Obtener token de acceso para Graph API.
    Intenta en este orden:
    1. Variable de entorno GRAPH_ACCESS_TOKEN
    2. Refresh token guardado en keyring/keychain/archivo local
    3. Si no está disponible, indicar setup
    """
    
    # Opción 1: Variable de entorno
    env_token = os.getenv("GRAPH_ACCESS_TOKEN")
    if env_token:
        return env_token.strip()
    
    # Opción 2: Storage local + refresh si es necesario
    try:
        config = load_config()
        refresh_token = get_refresh_token()
        
        if not refresh_token:
            raise RuntimeError(
                "❌ No hay refresh token guardado. Ejecuta:\n"
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
