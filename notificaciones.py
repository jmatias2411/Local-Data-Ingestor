import smtplib
import shutil
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# --- CARGAR VARIABLES DE ENTORNO (Modo Seguro) ---
# Esto asegura que encuentre el .env aunque lo ejecute el Programador de Tareas
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# --- CONFIGURACIÓN ---
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com") # Valor por defecto si falla el env
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Validación simple de seguridad
if not EMAIL_PASSWORD:
    print("⚠️ ADVERTENCIA: No se encontró la contraseña en el archivo .env")

# ... (El resto de funciones obtener_estado_disco, generar_html, enviar_reporte sigue IGUAL) ...
def obtener_estado_disco(ruta="C:\\"):
    """
    Devuelve métricas del disco formateadas y porcentaje para la gráfica.
    """
    try:
        total, used, free = shutil.disk_usage(ruta)
        
        # Convertir a GB
        gb_total = total / (1024**3)
        gb_used = used / (1024**3)
        gb_free = free / (1024**3)
        percent = (used / total) * 100
        
        return {
            "total": f"{gb_total:.2f}",
            "used": f"{gb_used:.2f}",
            "free": f"{gb_free:.2f}",
            "percent": round(percent, 1)
        }
    except Exception:
        return None

def generar_html(asunto, mb_liberados, log_lines, disco_info):
    """Genera un reporte visual en HTML con CSS estilo 'Clean'."""
    
    # Determinar color de la barra según uso
    color_barra = "#28a745" # Verde (ok)
    if disco_info['percent'] > 75: color_barra = "#ffc107" # Naranja (aviso)
    if disco_info['percent'] > 90: color_barra = "#dc3545" # Rojo (crítico)

    # Convertir lista de logs a HTML. 
    # Añadimos un pequeño estilo a cada línea para que se lea mejor.
    log_html = ""
    for line in log_lines:
        # Colorear ligeramente los errores o advertencias
        if "❌" in line or "Error" in line:
            estilo_linea = "color: #dc3545; font-weight: bold;"
        elif "⚠️" in line:
            estilo_linea = "color: #d39e00;"
        else:
            estilo_linea = "color: #333;"
        
        log_html += f'<div style="{estilo_linea} margin-bottom: 2px;">{line}</div>'

    html = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 20px auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            
            <div style="background-color: #0d6efd; color: white; padding: 25px; text-align: center;">
                <h2 style="margin: 0; font-weight: 600; font-size: 22px;">🚀 Reporte de Limpieza</h2>
                <p style="margin: 5px 0 0; opacity: 0.9; font-size: 14px;">{datetime.now().strftime('%d/%m/%Y - %H:%M')}</p>
            </div>

            <div style="padding: 20px; background-color: #ffffff; border-bottom: 1px solid #f0f0f0; text-align: center;">
                <p style="margin: 0; color: #6c757d; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Espacio Recuperado</p>
                <h3 style="margin: 5px 0 0; color: #198754; font-size: 32px; font-weight: 700;">+{mb_liberados} MB</h3>
            </div>

            <div style="padding: 25px; background-color: #ffffff;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; color: #495057;">
                    <span>💾 <strong>Disco Local (C:)</strong></span>
                    <span>{disco_info['free']} GB Libres</span>
                </div>
                
                <div style="background-color: #e9ecef; border-radius: 10px; height: 12px; width: 100%; overflow: hidden;">
                    <div style="width: {disco_info['percent']}%; background-color: {color_barra}; height: 100%; border-radius: 10px;"></div>
                </div>
                <div style="text-align: right; font-size: 11px; color: #adb5bd; margin-top: 5px;">
                    {disco_info['percent']}% Ocupado
                </div>
            </div>

            <div style="padding: 25px; border-top: 1px solid #f0f0f0; background-color: #f8f9fa;">
                <h4 style="margin-top: 0; margin-bottom: 15px; color: #495057; font-size: 16px;">📜 Registro de actividad</h4>
                
                <div style="background-color: #ffffff; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; font-family: Consolas, 'Courier New', monospace; font-size: 12px; max-height: 300px; overflow-y: auto; color: #212529;">
                    {log_html}
                </div>
            </div>

            <div style="padding: 15px; text-align: center; background-color: #ffffff; font-size: 11px; color: #adb5bd; border-top: 1px solid #f0f0f0;">
                Automatización Python v2.0 🐍 | Matías Palomino
            </div>
        </div>
    </body>
    </html>
    """
    return html

def enviar_reporte(asunto_prefix, lineas_cuerpo, logger_func=print, mb_freed=0):
    """
    Envía el reporte visual.
    Args:
        mb_freed: Float o Int con la cantidad de MB liberados para destacar en el header.
    """
    try:
        msg = MIMEMultipart('alternative') # Importante: 'alternative' para soportar HTML y Texto
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"{asunto_prefix} - Backup {datetime.now().strftime('%Y-%m-%d')}"

        # 1. Obtener datos del disco
        disco_info = obtener_estado_disco("C:\\") 
        if not disco_info:
            disco_info = {"total": "?", "used": "?", "free": "?", "percent": 0}

        # 2. Generar versiones Texto y HTML
        text_body = "\n".join(lineas_cuerpo) + f"\n\nEspacio Libre C: {disco_info['free']} GB"
        html_body = generar_html(asunto_prefix, mb_freed, lineas_cuerpo, disco_info)

        # 3. Adjuntar ambas partes (El cliente de correo elegirá la mejor, usualmente HTML)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger_func("📧 Correo HTML enviado correctamente.")
        return True
    except Exception as e:
        logger_func(f"❌ Error enviando correo: {e}")
        return False