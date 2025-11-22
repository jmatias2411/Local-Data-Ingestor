import os
import shutil
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
DEFAULT_SOURCE = r"C:\Users\jmati\Downloads"
ROOT_PRIMARY = r"D:\Backups\Descargas"
ROOT_SECONDARY = r"A:\Descargas"
LOG_FILE = r"C:\Users\jmati\backup_log.txt"

# --- CONFIGURACIÓN DE CORREO (SMTP) ---
# ¡Rellena esto con tus datos!
SMTP_SERVER = "smtp.gmail.com"  # O "smtp-mail.outlook.com"
SMTP_PORT = 587
EMAIL_SENDER = "tu_correo@gmail.com"
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx" # <--- TU CONTRASEÑA DE APLICACIÓN (NO la normal)
EMAIL_RECEIVER = "tu_correo@gmail.com" # A quién le llega el aviso

# --- CLASIFICACIÓN ---
FOLDERS_BY_TYPE = {
    "Datasets_Data": [".csv", ".json", ".parquet", ".xlsx", ".xml", ".sql", ".db"],
    "Notebooks_Scripts": [".ipynb", ".py", ".r", ".sh", ".bat", ".ps1"],
    "Modelos_IA": [".gguf", ".pt", ".safetensors", ".bin", ".h5", ".onnx", ".pkl"],
    "Documentos": [".pdf", ".docx", ".txt", ".pptx", ".md"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico"],
    "Videos_Audio": [".mp4", ".avi", ".mov", ".mkv", ".mp3", ".wav"],
    "Comprimidos_Installers": [".zip", ".rar", ".7z", ".tar.gz", ".exe", ".msi", ".iso"],
}

def log_message(message, buffer_msg=None):
    """Loguea en archivo y opcionalmente guarda en una lista para el email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{full_msg}\n")
    print(message)
    
    if buffer_msg is not None:
        buffer_msg.append(message)

def send_email_report(subject_prefix, body_lines):
    """Envía el reporte por email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"{subject_prefix} - Backup Descargas {datetime.now().strftime('%Y-%m-%d')}"

        body = "\n".join(body_lines)
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        log_message("📧 Correo enviado correctamente.")
    except Exception as e:
        log_message(f"❌ Error enviando correo: {e}")

def get_dynamic_paths():
    now = datetime.now()
    year_folder = now.strftime("%Y")
    folder_name = f"{now.strftime('%Y-%m-%d')}_Backup_Descargas"
    return os.path.join(ROOT_PRIMARY, year_folder, folder_name), os.path.join(ROOT_SECONDARY, year_folder, folder_name)

def get_unique_filename(target_path):
    if not os.path.exists(target_path): return target_path
    base, ext = os.path.splitext(target_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}{ext}"

def copy_to_target(source_path, root_dest_folder, category, filename):
    try:
        final_folder = os.path.join(root_dest_folder, category)
        os.makedirs(final_folder, exist_ok=True)
        target_path = get_unique_filename(os.path.join(final_folder, filename))
        shutil.copy2(source_path, target_path)
        return True, None
    except Exception as e:
        return False, str(e)

def clean_source_folder(source_folder, email_buffer):
    """BORRA los archivos de la carpeta origen."""
    log_message("🧹 Iniciando limpieza de Descargas (C:)...", email_buffer)
    deleted_count = 0
    freed_space = 0
    
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        try:
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                os.remove(item_path)
                deleted_count += 1
                freed_space += size
            # Opcional: Descomentar para borrar carpetas también (cuidado con esto)
            # elif os.path.isdir(item_path):
            #     shutil.rmtree(item_path)
        except Exception as e:
            log_message(f"⚠️ No se pudo borrar {item}: {e}", email_buffer)

    mb_freed = round(freed_space / (1024 * 1024), 2)
    log_message(f"🗑️ Limpieza completada. Archivos borrados: {deleted_count}. Espacio liberado: {mb_freed} MB", email_buffer)
    return mb_freed

def organize_and_backup(source_folder, dest_primary, dest_secondary, email_buffer):
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    if not files:
        log_message("ℹ️ No hay archivos nuevos en Descargas.", email_buffer)
        return 0, 0, []

    success_primary, success_secondary, errors = 0, 0, []

    for filename in files:
        source_path = os.path.join(source_folder, filename)
        _, ext = os.path.splitext(filename)
        
        category_selected = "Otros"
        for category, extensions in FOLDERS_BY_TYPE.items():
            if ext.lower() in extensions:
                category_selected = category
                break
        
        ok_d, err_d = copy_to_target(source_path, dest_primary, category_selected, filename)
        if ok_d: success_primary += 1
        else: errors.append(f"D: {filename} -> {err_d}")

        ok_a, err_a = copy_to_target(source_path, dest_secondary, category_selected, filename)
        if ok_a: success_secondary += 1
        else: errors.append(f"A: {filename} -> {err_a}")

    return success_primary, success_secondary, errors

def main():
    email_buffer = [] # Aquí guardamos el resumen para el email
    is_auto = len(sys.argv) > 1 and sys.argv[1] == "auto"

    if is_auto:
        log_message("--- 🤖 INICIO AUTOMÁTICO ---", email_buffer)
    else:
        print("=== 🛡️ BACKUP + LIMPIEZA MANUAL ===")

    source_dir = DEFAULT_SOURCE
    if not os.path.exists(source_dir):
        log_message(f"❌ Error: No existe {source_dir}", email_buffer)
        if is_auto: send_email_report("❌ FALLO", email_buffer)
        return

    path_d, path_a = get_dynamic_paths()

    if not is_auto:
        print(f"⚠️ ADVERTENCIA: Al finalizar, SE BORRARÁ el contenido de: {source_dir}")
        confirm = input("¿Proceder con Backup + BORRADO? [Escribe 'si' para continuar]: ").lower()
        if confirm != 'si': return

    try: os.makedirs(path_d, exist_ok=True)
    except: pass
    try: os.makedirs(path_a, exist_ok=True)
    except: pass

    s_d, s_a, errs = organize_and_backup(source_dir, path_d, path_a, email_buffer)

    space_freed = 0
    # LÓGICA DE SEGURIDAD PARA BORRADO
    # Solo borramos si al menos UN disco recibió copias correctamente
    if s_d > 0 or s_a > 0:
        log_message(f"✅ Copia exitosa: D:({s_d}) | A:({s_a})", email_buffer)
        if errs: log_message(f"⚠️ Errores parciales: {errs}", email_buffer)
        
        # --- EJECUCIÓN DEL BORRADO ---
        space_freed = clean_source_folder(source_dir, email_buffer)
    else:
        log_message("⚠️ No se copiaron archivos (o no había). No se borra nada.", email_buffer)

    if is_auto:
        log_message("--- FIN AUTO ---\n", email_buffer)
        # Enviar email si hubo actividad
        if s_d > 0 or s_a > 0:
            send_email_report(f"✅ ÉXITO (+{space_freed}MB)", email_buffer)
    else:
        print("\n✨ Proceso terminado.")
        send_email_report(f"✅ MANUAL (+{space_freed}MB)", email_buffer)

if __name__ == "__main__":
    main()
