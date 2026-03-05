# ⚡ INICIO RÁPIDO

## Paso 1: Setup (una sola vez)

```bash
python3 scripts/setup.py
```

Te pedirá:
- **Application (client) ID** (de portal.azure.com)
- **Directory (tenant) ID** (de portal.azure.com)
- **Email opcional** (tu cuenta M365, por defecto)

El token se guarda automáticamente en almacenamiento seguro local (keyring si está disponible).

---

## Paso 2: Usa los comandos

Sin autenticación adicional, directamente:

```bash
# Listar correos
python3 scripts/m365_mail.py list

# Listar no leídos
python3 scripts/m365_mail.py list --unread

# Buscar
python3 scripts/m365_mail.py search --query "palabra clave"

# Enviar
python3 scripts/m365_mail.py send \
  --to persona@empresa.com \
  --subject "Asunto" \
  --body "Mensaje"

# Marcar como leído
python3 scripts/m365_mail.py mark-read --message-id "ID_AQUI"

# Mover a carpeta
python3 scripts/m365_mail.py move --message-id "ID" --folder trash
```

---

## ¿Dónde obtengo Client ID y Tenant ID?

1. Ve a https://portal.azure.com
2. Busca **"App registrations"**
3. Abre tu app (o crea una nueva si no existe)
4. En **Overview** verás:
   - **Application (client) ID** ← Cópialo
   - **Directory (tenant) ID** ← Cópialo
5. En **Authentication**, asegúrate que **"Allow public client flows"** esté habilitado

---

## Problemas?

Revisa `api_reference.md` y `PERMISSIONS.md` para más detalles y troubleshooting.
