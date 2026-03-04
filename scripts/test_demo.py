#!/usr/bin/env python3
"""
Demo script que simula respuestas de Microsoft Graph API
para probar el skill sin necesidad de estar autenticado.
"""

import json
import sys

# Respuestas simuladas
MOCK_MESSAGES = {
    "value": [
        {
            "id": "AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGAAAAAAB",
            "subject": "Propuesta de presupuesto Q1 2026",
            "from": {
                "emailAddress": {
                    "address": "cliente@empresa.com",
                    "name": "Cliente Empresa"
                }
            },
            "receivedDateTime": "2026-03-04T14:30:00Z",
            "isRead": False
        },
        {
            "id": "AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGBBBBBB",
            "subject": "RE: Reunión de seguimiento",
            "from": {
                "emailAddress": {
                    "address": "manager@empresa.com",
                    "name": "Manager"
                }
            },
            "receivedDateTime": "2026-03-03T10:15:00Z",
            "isRead": True
        },
        {
            "id": "AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGCCCCC",
            "subject": "Factura #2026-0342",
            "from": {
                "emailAddress": {
                    "address": "billing@proveedor.com",
                    "name": "Facturación"
                }
            },
            "receivedDateTime": "2026-03-01T09:00:00Z",
            "isRead": False
        },
    ]
}

def print_messages(title, messages):
    print(f"\n{'='*70}")
    print(f"📧 {title}")
    print(f"{'='*70}")
    for item in messages:
        sender = item.get("from", {}).get("emailAddress", {}).get("address", "desconocido")
        received = item.get("receivedDateTime", "")
        status = "✅ LEÍDO" if item.get("isRead") else "🔵 NO LEÍDO"
        subject = (item.get("subject") or "(sin asunto)").replace("\n", " ").strip()
        msg_id = item.get("id", "")[:20] + "..."
        print(f"{status} | {received[:10]} | {sender:30} | {subject}")
        print(f"        ID: {msg_id}")
    print(f"{'='*70}\n")

def demo_list():
    print("\n🧪 DEMO: List (listar correos no leídos)")
    print("Comando: python3 scripts/m365_mail.py list --unread --top 3")
    unread = [m for m in MOCK_MESSAGES["value"] if not m["isRead"]]
    print_messages(f"Correos no leídos ({len(unread)})", unread)

def demo_search():
    print("\n🧪 DEMO: Search (buscar por texto)")
    print("Comando: python3 scripts/m365_mail.py search --query 'Factura'")
    results = [m for m in MOCK_MESSAGES["value"] if "factura" in m["subject"].lower()]
    print_messages(f"Resultados de búsqueda ({len(results)})", results)

def demo_mark_read():
    print("\n🧪 DEMO: Mark-read (marcar como leído)")
    print("Comando: python3 scripts/m365_mail.py mark-read \\")
    print("  --message-id 'AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGAAAAAAB'")
    print("\n✅ Mensaje actualizado a leído.")

def demo_move():
    print("\n🧪 DEMO: Move (mover a carpeta)")
    print("Comando: python3 scripts/m365_mail.py move \\")
    print("  --message-id 'AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGCCCCC' \\")
    print("  --folder trash")
    print("\n✅ Correo movido a trash.")

def demo_reply():
    print("\n🧪 DEMO: Reply (responder correo)")
    print("Comando: python3 scripts/m365_mail.py reply \\")
    print("  --message-id 'AAMkADc4ZDAwNTAwLTM3YjctNDUzZi1iMTRlLTY2MTMxOTQ4ZDI5MwBGAAAAAAB' \\")
    print("  --body 'Gracias por tu mensaje, lo revisaré mañana.' \\")
    print("  --cc 'supervisor@empresa.com'")
    print("\n✅ Respuesta enviada correctamente.")

def demo_send():
    print("\n🧪 DEMO: Send (enviar correo nuevo)")
    print("Comando: python3 scripts/m365_mail.py send \\")
    print("  --to 'cliente@empresa.com' \\")
    print("  --subject 'Propuesta actualizada' \\")
    print("  --body 'Adjunto encontrarás la propuesta revisada del Q1 2026.'")
    print("\n✅ Correo enviado correctamente.")

def main():
    print("\n" + "="*70)
    print("🎯 DEMOSTRACIÓN DEL SKILL M365-EMAIL-MANAGER")
    print("="*70)
    print("\nEste script simula las operaciones disponibles sin autenticación real.")
    print("Para usar con tu cuenta, ejecuta: az login")
    
    demo_list()
    demo_search()
    demo_mark_read()
    demo_move()
    demo_reply()
    demo_send()
    
    print("\n" + "="*70)
    print("✅ Todas las operaciones están disponibles y funcionan correctamente")
    print("="*70)
    print("\n📚 Para más detalles, lee:")
    print("   - SKILL.md (instrucciones)")
    print("   - references/api_reference.md (referencia técnica)")
    print("\n")

if __name__ == "__main__":
    main()
