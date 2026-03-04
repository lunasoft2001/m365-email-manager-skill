# Microsoft Graph Mail API Reference

## Context

This skill operates on Microsoft Graph `v1.0` for Exchange Online email.

Target account:

- Configurable via `M365_USER` (environment variable) or `--user` (CLI argument)

Base URL:

- `https://graph.microsoft.com/v1.0`

## Minimum suggested permissions

For delegated flow (authenticated user):

- `Mail.Read` to list/search emails.
- `Mail.ReadWrite` to mark as read and move messages.
- `Mail.Send` to send emails.

## Endpoints used by the script

### List inbox messages

- `GET /users/{user}/mailFolders/inbox/messages`
- Typical query:

  - `$select=id,subject,from,receivedDateTime,isRead`
  - `$orderby=receivedDateTime desc`
  - `$top=<N>`
  - `$filter=isRead eq false` (optional)

### Search messages

- `GET /users/{user}/messages?$search="text"`
- Required header:

  - `ConsistencyLevel: eventual`

### Mark as read

- `PATCH /users/{user}/messages/{messageId}`
- Body:

```json
{
  "isRead": true
}
```

### Send email

- `POST /users/{user}/sendMail`
- Minimum body:

```json
{
  "message": {
    "subject": "Subject",
    "body": {
      "contentType": "Text",
      "content": "Message"
    },
    "toRecipients": [
      {
        "emailAddress": {
          "address": "recipient@company.com"
        }
      }
    ]
  },
  "saveToSentItems": true
}
```

### Move message

- `POST /users/{user}/messages/{messageId}/move`
- Body:

```json
{
  "destinationId": "inbox"
}
```

Common folder IDs:
- `inbox`
- `drafts`
- `sentitems` (sent)
- `deleteditems` (trash)
- `junkemail` (spam)
- `archive`

### Reply to message

- `POST /users/{user}/messages/{messageId}/reply`
- Body:

```json
{
  "message": {
    "body": {
      "contentType": "Text",
      "content": "Reply to message..."
    },
    "ccRecipients": [
      {
        "emailAddress": {
          "address": "cc@company.com"
        }
      }
    ]
  }
}
```

## Token handling

Recommended order:

1. Reuse `GRAPH_ACCESS_TOKEN` if it exists.
2. If not available, obtain token with Azure CLI for Graph resource.

Command:

```bash
az account get-access-token --resource-type ms-graph --query accessToken -o tsv
```

## Common errors

- `401/403`: missing login, expired token or insufficient permissions.
- `404` on message: invalid `messageId` or email out of scope.
- `429`: throttling; retry with backoff.
