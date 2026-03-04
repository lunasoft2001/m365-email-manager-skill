# Microsoft Graph Mail API Reference

## Contexto

Este skill opera sobre Microsoft Graph `v1.0` para correo Exchange Online.

Cuenta objetivo:

- Configurable vía `M365_USER` (variable de entorno) o `--user` (argumento CLI)

Base URL:

- `https://graph.microsoft.com/v1.0`

## Permisos mínimos sugeridos

Para flujo delegado (usuario autenticado):

- `Mail.Read` para listar/buscar correos.
- `Mail.ReadWrite` para marcar como leído.
- `Mail.Send` para enviar correos.

## Endpoints usados por el script

### Listar mensajes de Inbox

- `GET /users/{user}/mailFolders/inbox/messages`
- Query típica:

  - `$select=id,subject,from,receivedDateTime,isRead`
  - `$orderby=receivedDateTime desc`
  - `$top=<N>`
  - `$filter=isRead eq false` (opcional)

### Buscar mensajes

- `GET /users/{user}/messages?$search="texto"`
- Header requerido:

  - `ConsistencyLevel: eventual`

### Marcar como leído

- `PATCH /users/{user}/messages/{messageId}`
- Body:

```json
{
  "isRead": true
}
```

### Enviar correo

- `POST /users/{user}/sendMail`
- Body mínimo:

```json
{
  "message": {
    "subject": "Asunto",
    "body": {
      "contentType": "Text",
      "content": "Mensaje"
    },
    "toRecipients": [
      {
        "emailAddress": {
          "address": "destino@empresa.com"
        }
      }
    ]
  },
  "saveToSentItems": true
}
```

### Mover mensaje

- `POST /users/{user}/messages/{messageId}/move`
- Body:

```json
{
  "destinationId": "inbox"
}
```

IDs de carpetas comunes:
- `inbox`
- `drafts`
- `sentitems` (enviados)
- `deleteditems` (papelera)
- `junkemail` (spam)
- `archive`

### Responder a mensaje

- `POST /users/{user}/messages/{messageId}/reply`
- Body:

```json
{
  "message": {
    "body": {
      "contentType": "Text",
      "content": "Respuesta al mensaje..."
    },
    "ccRecipients": [
      {
        "emailAddress": {
          "address": "cc@empresa.com"
        }
      }
    ]
  }
}
```

## Manejo de token

Orden recomendado:

1. Reutilizar `GRAPH_ACCESS_TOKEN` si existe.
2. Si no existe, obtener token con Azure CLI para recurso Graph.

Comando:

```bash
az account get-access-token --resource-type ms-graph --query accessToken -o tsv
```

## Errores comunes

- `401/403`: falta login, token expirado o permisos insuficientes.
- `404` en mensaje: `messageId` inválido o correo fuera de alcance.
- `429`: throttling; reintentar con backoff.
