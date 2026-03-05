---
name: m365-email-manager-skill
description: Manage Microsoft 365 (Outlook/Exchange Online) email using Microsoft Graph. Use when you need to list recent or unread emails, search messages by text, mark messages as read, move emails between folders, reply to or send emails in an automated and repeatable way. Setup once, use forever with tokens stored securely using cross-platform local storage.
---

# M365 Email Manager

## Overview

Automate Microsoft 365 email operations with secure, transparent authentication. **Setup once, then execute email operations without repetitive authentication prompts.**

**Key Features:**
- ✅ Setup once,use forever (tokens stored securely in cross-platform storage)
- ✅ Auto-detection of credentials from PowerShell Graph
- ✅ 3 flexible body input methods (CLI, file, stdin)
- ✅ Transparent token refresh
- ✅ Production-ready with comprehensive error handling

## Quick Start (First Time)

### 1. Run setup (one time only)
```bash
python3 scripts/setup.py
```
This will:
- Auto-detect Client ID and Tenant ID from PowerShell (if available)
- Store configuration in `~/.m365_email_config/config.json`
- Save refresh token securely (keyring when available, local protected file fallback)
- Optionally set default user email

### 2. Use without further authentication
```bash
python3 scripts/m365_mail.py list --top 10
python3 scripts/m365_mail.py send --to user@company.com --subject "Test" --body "Hi"
```

**That's it!** No more device codes or manual token management.

## Authentication System

The skill uses a three-tier authentication approach:

1. **setup.py** - One-time configuration (~1 minute)
   - Auto-detects credentials from PowerShell Graph context
   - Falls back to manual input if needed
  - Stores refresh token in cross-platform secure storage
   
2. **token_manager.py** - Transparent token refresh
   - Automatically refreshes access tokens when expired
   - No user interaction required
   - Uses OS-level encryption
   
3. **m365_mail.py** - Focuses on email operations
   - Calls token_manager to get valid tokens
   - Simple CLI interface for all operations

## Common Operations

### List recent emails
```bash
python3 scripts/m365_mail.py list --top 15
python3 scripts/m365_mail.py list --unread --top 25
python3 scripts/m365_mail.py list --user another@company.com --top 10
```

### Search emails
```bash
python3 scripts/m365_mail.py search --query "invoice march"
python3 scripts/m365_mail.py search --query "project update" --top 50
```

### Send emails (3 body input options)

**Option 1: Short text (CLI argument)**
```bash
python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "Quick update" \
  --body "Hi, just a quick note..."
```

**Option 2: Long text from file (recommended for multiline)**
```bash
python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "Detailed proposal" \
  --body-file email_content.txt
```

**Option 3: From stdin/pipe**
```bash
echo "Email content here" | python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "From pipe"
```

**With CC:**
```bash
python3 scripts/m365_mail.py send \
  --to "person1@company.com" \
  --cc "person2@company.com, person3@company.com" \
  --subject "Team update" \
  --body "Sharing latest progress..."
```

### Reply to emails
```bash
# Short reply
python3 scripts/m365_mail.py reply \
  --message-id "<MESSAGE_ID>" \
  --body "Thanks, reviewed and approved"

# Long reply from file
python3 scripts/m365_mail.py reply \
  --message-id "<MESSAGE_ID>" \
  --body-file response.txt

# Reply with CC
python3 scripts/m365_mail.py reply \
  --message-id "<MESSAGE_ID>" \
  --body "Confirmed" \
  --cc "manager@company.com"
```

### Mark as read
```bash
python3 scripts/m365_mail.py mark-read --message-id "<MESSAGE_ID>"
```

### Move emails
```bash
python3 scripts/m365_mail.py move \
  --message-id "<MESSAGE_ID>" \
  --folder "archive"
```

Available folders: `inbox`, `drafts`, `sent`, `trash`, `spam`, `archive`

## Configuration

Configuration is stored in `~/.m365_email_config/config.json`:
- `client_id` - Azure AD application (client) ID
- `tenant_id` - Azure AD directory (tenant) ID  
- `default_user` - Optional default user email
- `configured` - Setup completion flag
- `version` - Config version

Refresh token is stored securely using keyring when available, with protected local-file fallback.

### Reconfigure
```bash
python3 scripts/setup.py
# Prompts to confirm if config already exists
```

## Prerequisites

- Python 3.9+
- Windows, Linux or macOS
- Microsoft Entra ID app registration with Mail permissions:
  - `Mail.Read`
  - `Mail.ReadWrite`
  - `Mail.Send`

## Security Best Practices

- ✅ Tokens stored in keyring when available (or protected local fallback)
- ✅ Config file has 0o600 permissions (owner-only read/write)
- ✅ Credentials never in bash history or environment variables
- ✅ Automatic token refresh (no manual copy/paste)
- ✅ Device code flow happens only once during setup

## Resources

- **Main script**: `scripts/m365_mail.py` - CLI interface
- **Setup script**: `scripts/setup.py` - One-time configuration
- **Token manager**: `scripts/token_manager.py` - Transparent auth
- **Quick start**: `references/QUICKSTART.md` - 3-step guide
- **Body options**: `references/BODY_OPTIONS.md` - Detailed body input guide
- **API reference**: `references/api_reference.md` - Graph API details
- **Permissions**: `references/PERMISSIONS.md` - Azure setup guide

## Troubleshooting

### "Module not found: token_manager"
Run from scripts directory:
```bash
cd scripts/
python3 m365_mail.py list
```

### "El archivo no existe" (file not found)
For `--body-file`, use relative path from scripts directory:
```bash
cd scripts/
python3 m365_mail.py send --to user@co.com --subject "Test" --body-file ../email.txt
```

### Token expired
Token manager automatically refreshes. If issues persist:
```bash
python3 scripts/setup.py  # Reconfigure
```

## Example Workflow

After initial setup:

```bash
# Check emails
python3 scripts/m365_mail.py list --top 20

# Search
python3 scripts/m365_mail.py search --query "contract review"

# Send from file
python3 scripts/m365_mail.py send \
  --to client@company.com \
  --subject "Proposal" \
  --body-file proposal.txt

# Reply
python3 scripts/m365_mail.py reply \
  --message-id "AAMkAD..." \
  --body "Confirmed"

# Archive
python3 scripts/m365_mail.py move \
  --message-id "AAMkAD..." \
  --folder "archive"
```
