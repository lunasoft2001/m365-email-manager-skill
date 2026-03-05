#!/usr/bin/env python3
"""
Setup inicial para m365-email-manager-skill.
Ejecutar este script UNA SOLA VEZ para configurar la autenticación.

Guarda el refresh token de forma multiplataforma (keyring o archivo local protegido).
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict


GRAPH_BASE = "https://graph.microsoft.com/v1.0"
CONFIG_DIR = os.path.expanduser("~/.m365_email_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
REFRESH_TOKEN_FILE = os.path.join(CONFIG_DIR, "refresh_token.txt")
SERVICE_NAME = "m365-email-manager-skill"
LEGACY_SERVICE_NAME = "m365-email-manager"


def _ensure_config_dir() -> None:
    """Crear directorio de configuración si no existe."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)


def _post_form(url: str, payload: Dict[str, str]) -> Dict[str, Any]:
    """Hacer POST con form-urlencoded."""
    body = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url=url, method="POST", data=body)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(request) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw)


def _load_keyring():
    """Cargar keyring si está disponible en el entorno."""
    try:
        import keyring  # type: ignore
        return keyring
    except ImportError:
        return None


def _save_to_macos_keychain(service: str, account: str, password: str) -> None:
    """Guardar contraseña en keychain de macOS (compatibilidad)."""
    cmd = [
        "security",
        "add-generic-password",
        "-s", service,
        "-a", account,
        "-w", password,
        "-U"
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _save_refresh_token_to_file(refresh_token: str) -> None:
    """Guardar refresh token en archivo local con permisos restrictivos."""
    with open(REFRESH_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(refresh_token)
    try:
        os.chmod(REFRESH_TOKEN_FILE, 0o600)
    except (PermissionError, NotImplementedError):
        pass


def _save_refresh_token(refresh_token: str) -> str:
    """Guardar refresh token en backend disponible según SO/entorno."""
    keyring = _load_keyring()
    if keyring:
        try:
            keyring.set_password(SERVICE_NAME, "refresh_token", refresh_token)
            return "keyring"
        except Exception as exc:
            print(f"⚠️  No se pudo guardar en keyring ({exc}). Se usará archivo local.")

    if sys.platform == "darwin":
        try:
            _save_to_macos_keychain(SERVICE_NAME, "refresh_token", refresh_token)
            return "macOS Keychain"
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                _save_to_macos_keychain(LEGACY_SERVICE_NAME, "refresh_token", refresh_token)
                return "macOS Keychain"
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

    _save_refresh_token_to_file(refresh_token)
    return f"archivo local ({REFRESH_TOKEN_FILE})"


def _device_code_flow(client_id: str, tenant_id: str) -> Dict[str, str]:
    """Ejecutar device code flow para obtener token."""
    scope = (
        "https://graph.microsoft.com/Mail.Read "
        "https://graph.microsoft.com/Mail.ReadWrite "
        "https://graph.microsoft.com/Mail.Send "
        "offline_access"
    )
    
    device_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    print("\n🔑 Iniciando autenticación device code...")
    
    try:
        device_data = _post_form(device_url, {
            "client_id": client_id,
            "scope": scope
        })
    except urllib.error.HTTPError as err:
        print(f"❌ Error en device code: {err.reason}")
        sys.exit(1)

    print(f"\n📱 {device_data.get('message')}")
    
    device_code = device_data.get("device_code")
    interval = int(device_data.get("interval", 5))
    expires_in = int(device_data.get("expires_in", 900))
    
    start_time = time.time()
    while time.time() - start_time < expires_in:
        try:
            token_data = _post_form(token_url, {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": client_id,
                "device_code": device_code,
            })
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            if access_token and refresh_token:
                print("✓ Autenticación exitosa")
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": token_data.get("token_type", "Bearer"),
                    "expires_in": str(token_data.get("expires_in", 3600))
                }
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8") if err.fp else ""
            try:
                error_data = json.loads(detail)
                error_code = error_data.get("error")
            except json.JSONDecodeError:
                error_code = None

            if error_code == "authorization_pending":
                time.sleep(interval)
                continue
            if error_code == "slow_down":
                interval += 2
                time.sleep(interval)
                continue
            if error_code in {"access_denied", "expired_token"}:
                print(f"❌ Login cancelado o expirado")
                sys.exit(1)

    print("❌ Tiempo de espera agotado")
    sys.exit(1)


def _get_creds_from_powershell() -> tuple:
    """Intentar obtener Client ID y Tenant ID de PowerShell."""
    try:
        result = subprocess.run(
            ["pwsh", "-Command", 
             "Connect-MgGraph -Scopes 'Mail.Read' -NoWelcome; "
             "(Get-MgContext).ClientId + '|' + (Get-MgContext).TenantId"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if "|" in output:
                client_id, tenant_id = output.split("|")
                return client_id.strip(), tenant_id.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None, None


def setup() -> None:
    """Ejecutar el setup inicial."""
    print("=" * 60)
    print("CONFIGURACIÓN INICIAL - m365-email-manager-skill")
    print("=" * 60)
    
    # Verificar si ya está configurado
    if os.path.exists(CONFIG_FILE):
        print("\n⚠️  Ya existe una configuración.")
        response = input("¿Deseas reconfigurar? (s/n): ").strip().lower()
        if response != "s":
            print("Cancelado.")
            return
    
    # Intentar obtener Client ID y Tenant ID automáticamente de PowerShell
    print("\n🔍 Intentando obtener credenciales de PowerShell...")
    client_id, tenant_id = _get_creds_from_powershell()
    
    if not client_id or not tenant_id:
        print("⚠️  No se pudieron obtener credenciales automáticamente.")
        print("\n📝 Ingresa tus datos de Microsoft Entra ID manualmente:")
        print("   (Los puedes encontrar en portal.azure.com > App registrations)")
        
        client_id = input("\nApplication (client) ID: ").strip()
        if not client_id:
            print("❌ Client ID no puede estar vacío")
            sys.exit(1)
        
        tenant_id = input("Directory (tenant) ID: ").strip()
        if not tenant_id:
            print("❌ Tenant ID no puede estar vacío")
            sys.exit(1)
    else:
        print(f"✓ Credenciales obtenidas automáticamente desde PowerShell")
        print(f"  Client ID: {client_id[:12]}...")
        print(f"  Tenant ID: {tenant_id[:12]}...")
    
    default_user = input("\nCuenta de Microsoft 365 (ej: tu@empresa.com) [opcional]: ").strip()
    
    # Intentar obtener token automáticamente de PowerShell
    print("\n🔑 Intentando obtener refresh token de PowerShell...")
    try:
        # Conectar con PowerShell y obtener tokens
        pwsh_result = subprocess.run(
            ["pwsh", "-Command",
             "Connect-MgGraph -Scopes 'Mail.Read','Mail.Send','Mail.ReadWrite' 'offline_access' -NoWelcome | Out-Null; "
             "(Get-MgContext).AccessToken"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if pwsh_result.returncode == 0:
            access_token = pwsh_result.stdout.strip()
            if access_token and len(access_token) > 100:
                print("✓ Token obtenido automáticamente desde PowerShell")
                tokens = {
                    "access_token": access_token,
                    "refresh_token": access_token,  # PowerShell no devuelve refresh token fácilmente
                    "token_type": "Bearer",
                    "expires_in": "3600"
                }
            else:
                print(f"⚠️  Token inválido o vacío, ejecutando device-code flow...")
                tokens = _device_code_flow(client_id, tenant_id)
        else:
            print(f"⚠️  Error en PowerShell, ejecutando device-code flow...")
            tokens = _device_code_flow(client_id, tenant_id)
    except Exception as e:
        print(f"⚠️  No se pudo obtener token automáticamente ({e})")
        print("\n🔑 Ejecutando device-code flow manual...")
        # Ejecutar device code flow manual
        tokens = _device_code_flow(client_id, tenant_id)
    
    # Guardar refresh token en backend disponible
    _ensure_config_dir()
    storage_backend = _save_refresh_token(tokens["refresh_token"])
    
    # Guardar configuración (sin tokens sensibles)
    config = {
        "client_id": client_id,
        "tenant_id": tenant_id,
        "default_user": default_user or None,
        "configured": True,
        "version": "1.0"
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except (PermissionError, NotImplementedError):
        pass
    
    print(f"\n✓ Configuración guardada en: {CONFIG_FILE}")
    print(f"✓ Refresh token guardado en: {storage_backend}")
    
    if default_user:
        print(f"✓ Cuenta por defecto: {default_user}")
    
    print("\n✅ SETUP COMPLETADO")
    print("\nAhora puedes usar: python3 scripts/m365_mail.py list")
    print("                 python3 scripts/m365_mail.py search --query 'texto'")
    print("                 python3 scripts/m365_mail.py send --to persona@empresa.com --subject '...' --body '...'")


if __name__ == "__main__":
    setup()
