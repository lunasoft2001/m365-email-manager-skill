---
name: m365-email-manager
description: Manage Microsoft 365 (Outlook/Exchange Online) email using Microsoft Graph. Use when you need to list recent or unread emails, search messages by text, mark messages as read, move emails between folders, reply to or send emails in an automated and repeatable way. Compatible with personal and business accounts.
---

# M365 Email Manager

## Overview

Use this skill to operate Microsoft 365 email with reproducible commands without storing credentials in repository files.
The main automation lives in `scripts/m365_mail.py`.

## Quick workflow

1. Get Graph token:
	 - Prefer `GRAPH_ACCESS_TOKEN` if it already exists.
	 - If not available, use Azure CLI (`az login` then automatic token acquisition in script).
2. Execute required operation (`list`, `search`, `mark-read`, `send`, `move`, `reply`).
3. Validate result in console before additional actions.

## Authentication

- Option A: export `GRAPH_ACCESS_TOKEN`.
- Option B: login with Azure CLI (`az login`), and let the script obtain token with:
	- `az account get-access-token --resource-type ms-graph --query accessToken -o tsv`

## Common tasks

### List recent emails

```bash
python3 scripts/m365_mail.py list --top 15
```

### List only unread

```bash
python3 scripts/m365_mail.py list --unread --top 25
```

### Search by text

```bash
python3 scripts/m365_mail.py search --query "invoice march"
```

### Mark email as read

```bash
python3 scripts/m365_mail.py mark-read --message-id "<MESSAGE_ID>"
```

### Send email

```bash
python3 scripts/m365_mail.py send \
	--to "recipient@company.com" \
	--subject "Follow-up" \
	--body "Hi, sharing an update..."
```

### Move email to folder

```bash
python3 scripts/m365_mail.py move \
	--message-id "<MESSAGE_ID>" \
	--folder "trash"
```

Available folders: `inbox`, `drafts`, `sent`, `trash`, `spam`, `archive`.

### Reply to email

```bash
python3 scripts/m365_mail.py reply \
	--message-id "<MESSAGE_ID>" \
	--body "Thanks for your message..."
```

Optional: add CC with `--cc "email1@company.com, email2@company.com"`

## Account configuration

- Set your account with environment variable: `export M365_USER="your-user@company.onmicrosoft.com"`
- Or specify user in each command with `--user your-user@company.onmicrosoft.com`

## Security and limits

- Don't persist tokens in skill files.
- Review recipients before `send`.
- Use minimum Graph permissions for the use case.

## Resources

- Main script: `scripts/m365_mail.py`
- No-auth demonstration: `scripts/test_demo.py`
- API reference: `references/api_reference.md`
- Permissions and licenses: `references/PERMISSIONS.md` ← Read first if you have configuration questions

