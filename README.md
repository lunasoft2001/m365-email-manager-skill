# Gestión de correos M365

Automatiza tu correo de Outlook/Microsoft 365 con Microsoft Graph.

## Requisitos

- Python 3.9+
- macOS (usa keychain para almacenar tokens de forma segura)

## Instalación y Setup (una sola vez)

### 1. Crear app en Microsoft Entra ID

1. Ve a https://portal.azure.com
2. Busca **"App registrations"** → **New registration**
   - Nombre: `M365 Email Manager`
   - Tipo: _Accounts in this organizational directory only_
   - Click **Register**
3. En **Authentication**:
   - Habilita **"Allow public client flows"** → YES
   - Guarda
4. En **API permissions** → **Add a permission**:
   - Microsoft Graph → Delegated permissions
   - Busca y agrega:
     - `Mail.Read`
     - `Mail.ReadWrite`
     - `Mail.Send`
   - Click **Grant admin consent** (si tienes permisos)
5. En **Overview**, copia:
   - **Application (client) ID**
   - **Directory (tenant) ID**

### 2. Ejecutar setup

```bash
python3 scripts/setup.py
```

Sigue las instrucciones:
- Pega el **Client ID**
- Pega el **Tenant ID**
- (Opcional) Ingresa tu email por defecto
- Abre el navegador en el enlace que te da y completa el login

**Eso es todo.** Se guardan automáticamente en el keychain de forma segura.

## Uso

Ahora puedes usar los comandos directamente sin autenticación adicional:

### Listar correos

```bash
# Listar 10 últimos correos
python3 scripts/m365_mail.py list --top 10

# Listar solo los no leídos
python3 scripts/m365_mail.py list --unread --top 25

# Usar un usuario diferente al configurado
python3 scripts/m365_mail.py list --user otro@empresa.com --top 15
```

### Buscar correos

```bash
python3 scripts/m365_mail.py search --query "palabra clave"
python3 scripts/m365_mail.py search --query "facturas marzo" --top 50
```

### Marcar como leído

```bash
python3 scripts/m365_mail.py mark-read --message-id "ID_DEL_MENSAJE"
```

### Enviar correo

```bash
# Texto corto (opción --body)
python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "Hello" \
  --body "Message body here"

# Texto desde archivo (recomendado para textos largos)
python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "Update" \
  --body-file plantilla.txt

# Texto desde stdin/pipe
echo "Contenido del correo" | python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "From pipe"

# Con CC
python3 scripts/m365_mail.py send \
  --to "person1@company.com" \
  --cc "person2@company.com, person3@company.com" \
  --subject "Update" \
  --body "Content"
```

**Opciones de body:**
- `--body` - Para textos cortos (línea de comandos)
- `--body-file <ruta>` - Para textos largos (desde archivo)
- stdin - Para integración con pipes/scripts

Ver [BODY_OPTIONS.md](BODY_OPTIONS.md) para ejemplos detallados.

### Mover correo

```bash
python3 scripts/m365_mail.py move \
  --message-id "ID_DEL_MENSAJE" \
  --folder "trash"

# Carpetas disponibles: inbox, drafts, sent, trash, spam, archive
```

### Responder a un correo

```bash
# Texto corto
python3 scripts/m365_mail.py reply \
  --message-id "ID_DEL_MENSAJE" \
  --body "Reply text"

# Texto desde archivo
python3 scripts/m365_mail.py reply \
  --message-id "ID_DEL_MENSAJE" \
  --body-file respuesta.txt

# Texto desde stdin
echo "Mi respuesta" | python3 scripts/m365_mail.py reply \
  --message-id "ID_DEL_MENSAJE"

# Con CC en la respuesta
python3 scripts/m365_mail.py reply \
  --message-id "ID" \
  --body "Reply" \
  --cc "person@company.com"
```

**Opciones de body:** `--body`, `--body-file`, o stdin (igual que send)

## Configuración

La configuración se guarda en `~/.m365_email_config/config.json`:

- **Client ID y Tenant ID**: Guardados en el archivo
- **Refresh Token**: Guardado de forma segura en keychain de macOS
- **Usuario por defecto**: Opcional, si no lo especificas debes pasar `--user`

### Reconfigura el setup

```bash
python3 scripts/setup.py
# Te pedirá confirmación si ya existe configuración
```

## Autenticación alternativa

Si prefieres usar `GRAPH_ACCESS_TOKEN` manualmente:

```bash
export GRAPH_ACCESS_TOKEN="tu_token_aqui"
python3 scripts/m365_mail.py list
```

Con token ya emitido:

```bash
export GRAPH_ACCESS_TOKEN="<token>"
```

## Uso rápido

```bash
python3 scripts/m365_mail.py list --top 15
python3 scripts/m365_mail.py list --user "juanjo@luna-soft.es" --top 5
python3 scripts/m365_mail.py list --unread --top 25
python3 scripts/m365_mail.py search --query "factura marzo"
python3 scripts/m365_mail.py mark-read --message-id "<MESSAGE_ID>"
python3 scripts/m365_mail.py move --message-id "<MESSAGE_ID>" --folder "archive"
python3 scripts/m365_mail.py reply --message-id "<MESSAGE_ID>" --body "Gracias, revisado"
python3 scripts/m365_mail.py send --to "persona@empresa.com" --subject "Seguimiento" --body "Hola, te comparto avance"
```

## Nota sobre AADSTS65002

Si ves `AADSTS65002`, significa que Azure CLI no puede pedir esos scopes de Mail en tu tenant para la app first-party de Microsoft.
Solución: usa `M365_CLIENT_ID` + `M365_TENANT_ID` con tu propia app registrada (sección de autenticación recomendada).

## Carpetas válidas para `move`

- `inbox`
- `drafts`
- `sent`
- `trash`
- `spam`
- `archive`
