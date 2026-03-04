---
name: m365-email-manager
description: Gestiona correo de Microsoft 365 (Outlook/Exchange Online) usando Microsoft Graph. Use cuando necesites listar correos recientes o no leídos, buscar mensajes por texto, marcar mensajes como leídos, mover correos entre carpetas, responder o enviar correos de forma automatizada y repetible. Compatible con cuentas personales y empresariales.
---

# M365 Email Manager

## Overview

Usa este skill para operar correo de Microsoft 365 con comandos reproducibles y sin guardar credenciales en archivos del repositorio.
La automatización principal vive en `scripts/m365_mail.py`.

## Flujo rápido

1. Obtener token de Graph:
	 - Preferir `GRAPH_ACCESS_TOKEN` si ya existe.
	 - Si no existe, usar Azure CLI (`az login` y luego token automático en script).
2. Ejecutar operación requerida (`list`, `search`, `mark-read`, `send`).
3. Validar resultado en consola antes de acciones adicionales.

## Autenticación

- Opción A: exportar `GRAPH_ACCESS_TOKEN`.
- Opción B: iniciar sesión con Azure CLI (`az login`), y dejar que el script obtenga token con:
	- `az account get-access-token --resource-type ms-graph --query accessToken -o tsv`

## Tareas comunes

### Listar últimos correos

```bash
python3 scripts/m365_mail.py list --top 15
```

### Listar solo no leídos

```bash
python3 scripts/m365_mail.py list --unread --top 25
```

### Buscar por texto

```bash
python3 scripts/m365_mail.py search --query "factura marzo"
```

### Marcar correo como leído

```bash
python3 scripts/m365_mail.py mark-read --message-id "<ID_DEL_MENSAJE>"
```

### Enviar correo

```bash
python3 scripts/m365_mail.py send \
	--to "destino@empresa.com" \
	--subject "Seguimiento" \
	--body "Hola, comparto actualización..."
```

### Mover correo a carpeta

```bash
python3 scripts/m365_mail.py move \
	--message-id "<ID_DEL_MENSAJE>" \
	--folder "trash"
```

Carpetas disponibles: `inbox`, `drafts`, `sent`, `trash`, `spam`, `archive`.

### Responder a un correo

```bash
python3 scripts/m365_mail.py reply \
	--message-id "<ID_DEL_MENSAJE>" \
	--body "Gracias por tu mensaje..."
```

Opcional: agregar CC con `--cc "email1@empresa.com, email2@empresa.com"`

## Configuración de cuenta

- Define tu cuenta con variable de entorno: `export M365_USER="tu-usuario@empresa.onmicrosoft.com"`
- O especifica el usuario en cada comando con `--user tu-usuario@empresa.onmicrosoft.com`

## Seguridad y límites

- No persistir tokens en archivos del skill.
- Revisar destinatarios antes de `send`.
- Usar permisos mínimos de Graph para el caso de uso.

## Recursos

- Script principal: `scripts/m365_mail.py`
- Demostración sin autenticación: `scripts/test_demo.py`
- Referencia de API: `references/api_reference.md`
- Permisos y licencias: `references/PERMISSIONS.md` ← Lee primero si tienes dudas de configuración

