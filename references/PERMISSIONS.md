# Permisos y Licencias - M365-Email-Manager

## 📋 Requisitos de Licencia

### Microsoft 365 (Obligatorio)
- **Microsoft 365 Business Basic** o superior
- O **Exchange Online** (Plan 1 o superior)
- Cualquier cuenta válida de Microsoft 365 con buzón de correo

Nota: La mayoría de planes corporativos incluyen acceso a estos APIs.

### Azure AD / Entra ID (Obligatorio)
- Acceso a **Azure Portal** (para registrar la aplicación)
- Rol: Administrador de aplicaciones Azure AD o superior

---

## 🔐 Permisos de Microsoft Graph API

El script utiliza los siguientes permisos delegados (en nombre del usuario):

| Operación | Permisos Requeridos | Descripción |
|-----------|-------------------|-------------|
| **list** | `Mail.Read` | Leer correos de buzón |
| **search** | `Mail.Read` | Buscar correos |
| **mark-read** | `Mail.ReadWrite` | Modificar propiedades del correo |
| **send** | `Mail.Send` | Enviar correos desde el buzón del usuario |
| **move** | `Mail.ReadWrite` | Mover correos entre carpetas |
| **reply** | `Mail.Send` | Enviar respuestas |

### Permisos Mínimos Recomendados
```
Mail.Read
Mail.Send
Mail.ReadWrite
```

---

## ⚙️ Configuración en Azure AD (Una sola vez)

### Opción A: Flujo delegado (Recomendado - Lo que usas ahora)

El script usa `az login` que activa el flujo delegado automáticamente:

1. **Login con Azure CLI**
   ```bash
   az login
   ```
   - Se abre navegador
   - Inicias sesión con tu cuenta de Microsoft 365
   - El token se obtiene automáticamente

2. **Permisos solicitados**
   - La primera vez que ejecutas un comando, puede pedir confirmación
   - Consientes acceso "en nombre tuyo"
   - Se generan tokens de corta duración

**Ventaja:** Sin configuración previa, funciona inmediatamente.

### Opción B: Flujo de aplicación (Para automatización/CI-CD)

Si quieres usar esto en un job automatizado sin interacción:

1. Registra una **aplicación de Azure AD**
2. Asigna permisos de aplicación (no delegados)
3. Genera un **client secret**
4. Usa las credenciales en variables de entorno

**Ejemplo de credenciales necesarias:**
```bash
export AZURE_TENANT_ID="tu-tenant-id"
export AZURE_CLIENT_ID="tu-app-id"
export AZURE_CLIENT_SECRET="tu-secret"
```

---

## 🔍 Verificar tus Permisos

### 1. Verificar acceso a Microsoft 365
```bash
az account show --query "{name: name, id: id}"
```

### 2. Verificar suscripción a Exchange Online
```bash
az graph query --query "Me.mail"
```

### 3. Listar tus permisos otorgados
https://myapps.microsoft.com/ → Ver permisos otorgados

---

## ⚠️ Consideraciones de Seguridad

### Tokens de Acceso
- **Duración:** 1 hora (renovación automática)
- **Almacenamiento:** En caché local de Azure CLI (`~/.azure/`)
- **Seguridad:** No persisten en archivos del skill

### Buenas Prácticas
1. ✅ Usa `az login` (autentica en tu sesión local)
2. ✅ No compartas tokens ni secrets en repositorios
3. ✅ Revoca permisos en https://myaccount.microsoft.com/permissions si cambias de dispositivo
4. ✅ Usa `az logout` si terminas sesión

### NO hacer
- ❌ Exportar `GRAPH_ACCESS_TOKEN` en variables globales
- ❌ Guardar credenciales en `.env` o archivos del proyecto
- ❌ Compartir tokens entre usuarios
- ❌ Usar en scripts sin supervisión que escriban en buzones críticos

---

## 📞 Troubleshooting

### Error: "Permission denied"
**Causa:** Tu cuenta no tiene los permisos necesarios.

**Solución:**
1. Verifica que tengas licencia Exchange Online
2. Intenta: `az account clear && az login`
3. Contacta a tu administrador de Microsoft 365

### Error: "Resource not found"
**Causa:** La carpeta no existe o tienes acceso limitado.

**Solución:**
- Usa carpetas estándar: `inbox`, `drafts`, `sent`, `trash`, `spam`
- Verifica permisos con: `az graph query --query "Me/mailFolders"`

### Error: "Invalid credentials"
**Causa:** Token expirado o sesión perdida.

**Solución:**
```bash
az logout
az login
```

---

## 📱 Resumen de Requisitos

| Ítem | Requerido | Notas |
|------|-----------|-------|
| Cuenta Microsoft 365 | **SÍ** | Con buzón de correo activo |
| Licencia Exchange Online | **SÍ** | Verifica con admin |
| Azure CLI instalado | **SÍ** | Para autenticación |
| Acceso a Azure Portal | Opcional | Solo si cambias a flujo de app |
| Internet | **SÍ** | Siempre |

---

## 🎯 Próximos Pasos

1. ✅ **Instalar Azure CLI** (ya hecho)
2. ⏳ **Ejecutar `az login`** (cuando estés listo)
3. 🚀 **Usar el skill** sin configuración adicional

¡Todo listo! Solo necesitas hacer login y los permisos se manejan automáticamente.
