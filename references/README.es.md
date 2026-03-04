# M365 Email Manager Skill

> GitHub Copilot Skill para gestionar correo de Microsoft 365 (Outlook/Exchange Online) usando Microsoft Graph API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Descripción

Este skill permite a GitHub Copilot automatizar operaciones de correo en Microsoft 365 de forma reproducible y segura, sin guardar credenciales en archivos del repositorio.

### Operaciones soportadas

- ✉️ **Listar correos** recientes o no leídos
- 🔍 **Buscar mensajes** por texto
- ✅ **Marcar como leído**
- 📤 **Enviar correos**
- 📁 **Mover mensajes** entre carpetas
- 💬 **Responder** a correos (con ReplyAll)

## 🚀 Instalación rápida

### Requisitos previos

- **Microsoft 365** con buzón de correo activo
- **Azure CLI** para autenticación
- **Python 3.7+** (sin dependencias externas)

### Instalación de Azure CLI

```bash
# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
winget install Microsoft.AzureCLI
```

### Configuración

1. **Autenticarse con Azure CLI**:
   ```bash
   az login
   ```

2. **Configurar la cuenta de correo**:
   ```bash
   export M365_USER="tu-usuario@empresa.onmicrosoft.com"
   ```

3. **Probar el skill**:
   ```bash
   python3 scripts/m365_mail.py list --top 5
   ```

## 📖 Uso

### Listar correos

```bash
# Últimos 10 correos
python3 scripts/m365_mail.py list

# Solo no leídos
python3 scripts/m365_mail.py list --unread --top 25

# De una carpeta específica
python3 scripts/m365_mail.py list --folder sent
```

### Buscar mensajes

```bash
python3 scripts/m365_mail.py search --query "proyecto presupuesto"
```

### Marcar como leído

```bash
python3 scripts/m365_mail.py mark-read --message-id "<ID_DEL_MENSAJE>"
```

### Enviar correo

```bash
python3 scripts/m365_mail.py send \
  --to "destinatario@empresa.com" \
  --subject "Reporte mensual" \
  --body "Adjunto el reporte del mes."
```

### Mover a carpeta

```bash
python3 scripts/m365_mail.py move \
  --message-id "<ID>" \
  --folder archive
```

Carpetas disponibles: `inbox`, `drafts`, `sent`, `trash`, `spam`, `archive`

### Responder a correo

```bash
python3 scripts/m365_mail.py reply \
  --message-id "<ID>" \
  --body "Gracias por tu mensaje..." \
  --cc "supervisor@empresa.com"
```

## 🔐 Autenticación y seguridad

El skill soporta dos métodos de autenticación:

### Opción A: Azure CLI (recomendado)

```bash
az login
# El token se obtiene automáticamente
```

### Opción B: Variable de entorno

```bash
export GRAPH_ACCESS_TOKEN="tu_token_aqui"
```

### Permisos necesarios

- `Mail.Read` - Leer correos
- `Mail.ReadWrite` - Modificar correos (marcar como leído, mover)
- `Mail.Send` - Enviar correos

**Importante**: Los tokens duran 1 hora. Nunca los guardes en archivos del repositorio.

## 📁 Estructura del proyecto

```
m365-email-manager/
├── SKILL.md                    # Instrucciones para GitHub Copilot
├── scripts/
│   ├── m365_mail.py           # Script principal (CLI)
│   └── test_demo.py           # Demostración sin autenticación
└── references/
    ├── api_reference.md       # Documentación de Graph API
    └── PERMISSIONS.md         # Guía completa de permisos
```

## 🧪 Demostración sin autenticación

Para ver el skill en acción sin configurar permisos:

```bash
python3 scripts/test_demo.py
```

Este script simula todas las operaciones con datos de ejemplo.

## 🛠️ Troubleshooting

### Error: "Debes especificar --user o definir M365_USER"

```bash
export M365_USER="tu-usuario@empresa.onmicrosoft.com"
```

### Error 403: Forbidden

Tu cuenta no tiene permisos para acceder a Graph API. Consulta [references/PERMISSIONS.md](references/PERMISSIONS.md) para configurar permisos con tu administrador.

### Error: AADSTS65002

El tenant bloquea el acceso de Azure CLI a Graph Mail. Opciones:
1. Pedir al admin que autorice Azure CLI
2. Crear un App Registration dedicado

Ver [PERMISSIONS.md](PERMISSIONS.md) para instrucciones completas.

## 📚 Documentación completa

- [SKILL.md](../SKILL.md) - Instrucciones completas del skill
- [api_reference.md](api_reference.md) - Detalles de Microsoft Graph API
- [PERMISSIONS.md](PERMISSIONS.md) - Configuración de permisos y licencias

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres agregar nuevas operaciones o mejorar la documentación:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-operacion`)
3. Commit tus cambios (`git commit -m 'Agrega operación X'`)
4. Push a la rama (`git push origin feature/nueva-operacion`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE.txt) para más detalles.

## 🔗 Enlaces útiles

- [Microsoft Graph REST API v1.0](https://learn.microsoft.com/en-us/graph/api/overview)
- [Mail resource type](https://learn.microsoft.com/en-us/graph/api/resources/message)
- [Azure CLI documentation](https://learn.microsoft.com/en-us/cli/azure/)
- [GitHub Copilot Skills](https://github.com/features/copilot)

## ✨ Autor

Creado como ejemplo de GitHub Copilot Skill para automatización de Microsoft 365.

---

**Nota**: Este skill NO almacena credenciales ni tokens en el repositorio. Toda la autenticación se realiza mediante Azure CLI o variables de entorno temporales.
