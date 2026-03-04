# Permissions and Licenses - M365-Email-Manager

## 📋 License Requirements

### Microsoft 365 (Required)
- **Microsoft 365 Business Basic** or higher
- Or **Exchange Online** (Plan 1 or higher)
- Any valid Microsoft 365 account with an email mailbox

Note: Most corporate plans include access to these APIs.

### Azure AD / Entra ID (Required)
- Access to **Azure Portal** (to register the application)
- Role: Azure AD Application Administrator or higher

---

## 🔐 Microsoft Graph API Permissions

The script uses the following delegated permissions (on behalf of the user):

| Operation | Required Permissions | Description |
|-----------|-------------------|-------------|
| **list** | `Mail.Read` | Read mailbox emails |
| **search** | `Mail.Read` | Search emails |
| **mark-read** | `Mail.ReadWrite` | Modify email properties |
| **send** | `Mail.Send` | Send emails from user's mailbox |
| **move** | `Mail.ReadWrite` | Move emails between folders |
| **reply** | `Mail.Send` | Send replies |

### Minimum Recommended Permissions
```
Mail.Read
Mail.Send
Mail.ReadWrite
```

---

## ⚙️ Azure AD Configuration (One-time)

### Option A: Delegated flow (Recommended - What you're using now)

The script uses `az login` which triggers the delegated flow automatically:

1. **Login with Azure CLI**
   ```bash
   az login
   ```
   - Opens browser
   - You sign in with your Microsoft 365 account
   - Token is obtained automatically

2. **Requested permissions**
   - First time you run a command, it may ask for confirmation
   - You consent to access "on your behalf"
   - Short-lived tokens are generated

**Advantage:** No prior configuration, works immediately.

### Option B: Application flow (For automation/CI-CD)

If you want to use this in an automated job without interaction:

1. Register an **Azure AD application**
2. Assign application permissions (not delegated)
3. Generate a **client secret**
4. Use credentials in environment variables

**Example required credentials:**
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-app-id"
export AZURE_CLIENT_SECRET="your-secret"
```

---

## 🔍 Verify Your Permissions

### 1. Verify Microsoft 365 access
```bash
az account show --query "{name: name, id: id}"
```

### 2. Verify Exchange Online subscription
```bash
az graph query --query "Me.mail"
```

### 3. List your granted permissions
https://myapps.microsoft.com/ → View granted permissions

---

## ⚠️ Security Considerations

### Access Tokens
- **Duration:** 1 hour (automatic renewal)
- **Storage:** Azure CLI local cache (`~/.azure/`)
- **Security:** Not persisted in skill files

### Best Practices
1. ✅ Use `az login` (authenticate in your local session)
2. ✅ Don't share tokens or secrets in repositories
3. ✅ Revoke permissions at https://myaccount.microsoft.com/permissions if you change devices
4. ✅ Use `az logout` when ending session

### DON'T
- ❌ Export `GRAPH_ACCESS_TOKEN` in global variables
- ❌ Save credentials in `.env` or project files
- ❌ Share tokens among users
- ❌ Use in unsupervised scripts that write to critical mailboxes

---

## 📞 Troubleshooting

### Error: "Permission denied"
**Cause:** Your account doesn't have necessary permissions.

**Solution:**
1. Verify you have Exchange Online license
2. Try: `az account clear && az login`
3. Contact your Microsoft 365 administrator

### Error: "Resource not found"
**Cause:** Folder doesn't exist or you have limited access.

**Solution:**
- Use standard folders: `inbox`, `drafts`, `sent`, `trash`, `spam`
- Verify permissions with: `az graph query --query "Me/mailFolders"`

### Error: "Invalid credentials"
**Cause:** Expired token or lost session.

**Solution:**
```bash
az logout
az login
```

---

## 📱 Requirements Summary

| Item | Required | Notes |
|------|----------|-------|
| Microsoft 365 account | **YES** | With active email mailbox |
| Exchange Online license | **YES** | Verify with admin |
| Azure CLI installed | **YES** | For authentication |
| Azure Portal access | Optional | Only if switching to app flow |
| Internet | **YES** | Always |

---

## 🎯 Next Steps

1. ✅ **Install Azure CLI** (already done)
2. ⏳ **Run `az login`** (when ready)
3. 🚀 **Use the skill** without additional configuration

All set! Just need to login and permissions are handled automatically.
