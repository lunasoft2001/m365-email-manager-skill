# 📝 Múltiples formas de pasar el body

El script mejorado ahora soporta **3 formas diferentes** de pasar el contenido del correo (body):

## 1️⃣ Opción 1: Argumento `--body` (textos cortos)

Para textos cortos sin saltos de línea:

```bash
python3 scripts/m365_mail.py send \
  --to recipient@company.com \
  --subject "Subject" \
  --body "Simple text"
```

✅ Ideal para: Mensajes breves
❌ Problemático para: Textos multilínea complejos

---

## 2️⃣ Opción 2: Archivo `--body-file` (textos largos)

Para textos largos o plantillas:

```bash
# Crear archivo con el contenido
cat > email_body.txt << 'EOF'
Hola,

Este es un correo con múltiples líneas.
Puede contener:
- Listas
- Saltos de línea
- Caracteres especiales

Saludos,
JL
EOF

# Usar el archivo
python3 scripts/m365_mail.py send \
  --to person@company.com \
  --subject "Asunto" \
  --body-file email_body.txt
```

✅ Ideal para: Textos extensos, plantillas
✅ Fácil de auditar y mantener
✅ Sin problemas de escape

---

## 3️⃣ Opción 3: stdin (desde pipes)

Para integración con otros comandos:

```bash
# Desde echo
echo "Contenido del correo" | python3 scripts/m365_mail.py send \
  --to person@company.com \
  --subject "Asunto"

# Desde cat
cat mensajito.txt | python3 scripts/m365_mail.py send \
  --to person@company.com \
  --subject "Asunto"

# Desde heredoc
python3 scripts/m365_mail.py send \
  --to person@company.com \
  --subject "Asunto" \
  << 'BODY'
Contenido multilinea
Con saltos de línea
Sin problemas de escape
BODY

# Desde comandos complejos
ls -la | python3 scripts/m365_mail.py send \
  --to person@company.com \
  --subject "Listado de archivos"
```

✅ Ideal para: Automatización, scripts
✅ Integración perfecta con pipes
✅ Sin archivos temporales

---

## 📊 Comparativa

| Método | Líneas cortas | Multilínea | Archivos | Pipes | Caracteres especiales |
|--------|--------------|-----------|---------|-------|----------------------|
| `--body` | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| `--body-file` | ✅ | ✅ | ✅ | ❌ | ✅ |
| stdin | ✅ | ✅ | ❌ | ✅ | ✅ |

---

## 🎯 Recomendaciones

- **Textos cortos**: Usa `--body`
- **Textos largos o plantillas**: Usa `--body-file`
- **Automatización/scripts**: Usa stdin
- **Máxima claridad**: Siempre usa `--body-file` o stdin

---

## 🔧 Ejemplos prácticos

### Enviar listado de errores

```bash
python3 scripts/m365_mail.py send \
  --to admin@company.com \
  --subject "Errores del día $(date +%Y-%m-%d)" \
  --body-file /var/log/errors.log
```

### Enviar desde script automático

```bash
# script.sh
RESULTADO=$(comando_importante 2>&1)
echo "$RESULTADO" | python3 scripts/m365_mail.py send \
  --to admin@company.com \
  --subject "Resultado de tarea automática"
```

### Responder a correo con archivo

```bash
python3 scripts/m365_mail.py reply \
  --message-id "ID_AQUI" \
  --body-file respuesta_plantilla.txt
```

---

## ✨ Beneficios de esta mejora

✅ **Flexibilidad**: 3 formas de usar según el caso
✅ **Robustez**: Sin problemas de escape de caracteres
✅ **Automatización**: Perfecto para scripts
✅ **Claridad**: El código es más legible
✅ **Mantenibilidad**: Fácil actualizar plantillas sin cambiar código
