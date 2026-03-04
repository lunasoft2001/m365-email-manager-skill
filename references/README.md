# M365 Email Manager Skill

> GitHub Copilot Skill for managing Microsoft 365 (Outlook/Exchange Online) email using Microsoft Graph API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**[🇪🇸 Versión en Español](README.es.md)**

## 📋 Description

This skill allows GitHub Copilot to automate email operations in Microsoft 365 in a reproducible and secure way, without storing credentials in repository files.

### Supported operations

- ✉️ **List emails** recent or unread
- 🔍 **Search messages** by text
- ✅ **Mark as read**
- 📤 **Send emails**
- 📁 **Move messages** between folders
- 💬 **Reply** to emails (with ReplyAll)

## 🚀 Quick Installation

### Prerequisites

- **Microsoft 365** with active email mailbox
- **Azure CLI** for authentication
- **Python 3.7+** (no external dependencies)

### Azure CLI Installation

```bash
# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
winget install Microsoft.AzureCLI
```

### Configuration

1. **Authenticate with Azure CLI**:
   ```bash
   az login
   ```

2. **Configure email account**:
   ```bash
   export M365_USER="your-user@company.onmicrosoft.com"
   ```

3. **Test the skill**:
   ```bash
   python3 scripts/m365_mail.py list --top 5
   ```

## 📖 Usage

### List emails

```bash
# Last 10 emails
python3 scripts/m365_mail.py list

# Only unread
python3 scripts/m365_mail.py list --unread --top 25

# From a specific folder
python3 scripts/m365_mail.py list --folder sent
```

### Search messages

```bash
python3 scripts/m365_mail.py search --query "project budget"
```

### Mark as read

```bash
python3 scripts/m365_mail.py mark-read --message-id "<MESSAGE_ID>"
```

### Send email

```bash
python3 scripts/m365_mail.py send \
  --to "recipient@company.com" \
  --subject "Monthly report" \
  --body "Please find attached the monthly report."
```

### Move to folder

```bash
python3 scripts/m365_mail.py move \
  --message-id "<ID>" \
  --folder archive
```

Available folders: `inbox`, `drafts`, `sent`, `trash`, `spam`, `archive`

### Reply to email

```bash
python3 scripts/m365_mail.py reply \
  --message-id "<ID>" \
  --body "Thanks for your message..." \
  --cc "supervisor@company.com"
```

## 🔐 Authentication and security

The skill supports two authentication methods:

### Option A: Azure CLI (recommended)

```bash
az login
# Token is obtained automatically
```

### Option B: Environment variable

```bash
export GRAPH_ACCESS_TOKEN="your_token_here"
```

### Required permissions

- `Mail.Read` - Read emails
- `Mail.ReadWrite` - Modify emails (mark as read, move)
- `Mail.Send` - Send emails

**Important**: Tokens last 1 hour. Never save them in repository files.

## 📁 Project structure

```
m365-email-manager/
├── SKILL.md                    # Instructions for GitHub Copilot
├── scripts/
│   ├── m365_mail.py           # Main script (CLI)
│   └── test_demo.py           # No-auth demonstration
└── references/
    ├── api_reference.md       # Graph API documentation
    └── PERMISSIONS.md         # Complete permissions guide
```

## 🧪 No-auth demonstration

To see the skill in action without configuring permissions:

```bash
python3 scripts/test_demo.py
```

This script simulates all operations with sample data.

## 🛠️ Troubleshooting

### Error: "You must specify --user or set M365_USER"

```bash
export M365_USER="your-user@company.onmicrosoft.com"
```

### Error 403: Forbidden

Your account doesn't have permissions to access Graph API. See [references/PERMISSIONS.md](references/PERMISSIONS.md) to configure permissions with your administrator.

### Error: AADSTS65002

The tenant blocks Azure CLI access to Graph Mail. Options:
1. Ask admin to authorize Azure CLI
2. Create a dedicated App Registration

See [PERMISSIONS.md](PERMISSIONS.md) for complete instructions.

## 📚 Complete documentation

- [SKILL.md](../SKILL.md) - Complete skill instructions
- [api_reference.md](api_reference.md) - Microsoft Graph API details
- [PERMISSIONS.md](PERMISSIONS.md) - Permissions and licenses configuration

## 🤝 Contributions

Contributions are welcome! If you want to add new operations or improve documentation:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/new-operation`)
3. Commit your changes (`git commit -m 'Add operation X'`)
4. Push to the branch (`git push origin feature/new-operation`)
5. Open a Pull Request

## 📄 License

This project is under MIT license. See [LICENSE](LICENSE.txt) for more details.

## 🔗 Useful links

- [Microsoft Graph REST API v1.0](https://learn.microsoft.com/en-us/graph/api/overview)
- [Mail resource type](https://learn.microsoft.com/en-us/graph/api/resources/message)
- [Azure CLI documentation](https://learn.microsoft.com/en-us/cli/azure/)
- [GitHub Copilot Skills](https://github.com/features/copilot)

## ✨ Author

Created as an example of GitHub Copilot Skill for Microsoft 365 automation.

---

**Note**: This skill does NOT store credentials or tokens in the repository. All authentication is done through Azure CLI or temporary environment variables.
