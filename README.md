# 🛡️ Local-Data-Ingestor : Downloads ETL & Smart Backup Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Status](https://img.shields.io/badge/Status-Production-green?style=for-the-badge)

Este proyecto automatiza la gestión del almacenamiento local, solucionando el problema del "Disco C: lleno" común en entornos de Data Science. Actúa como un pipeline ETL que **Extrae** archivos de la carpeta Descargas, los **Transforma** (clasifica y renombra) y los **Carga** en dos unidades de almacenamiento físico independientes (Redundancia).

Finalmente, realiza una limpieza del origen y envía un reporte de auditoría vía Email.

## 🚀 Funcionalidades Clave

- **📂 Clasificación Inteligente:** Organiza archivos automáticamente en carpetas según su tipo (`Datasets`, `Modelos_IA`, `Notebooks`, `Imágenes`, etc.).
- **💿 Doble Redundancia (Software RAID-1):** Copia los datos simultáneamente a dos discos físicos distintos (`D:` y `A:`) para tolerancia a fallos.
- **📅 Versionado Temporal:** Crea carpetas con fecha `YYYY-MM-DD` para mantener un histórico limpio y ordenado.
- **🧹 Auto-Limpieza (Garbage Collection):** Elimina los archivos del origen (`C:\Downloads`) **solo** si la copia a los discos de respaldo fue exitosa.
- **🤖 Automatización Total:** Diseñado para ejecutarse en segundo plano mediante el Programador de Tareas de Windows.
- **📧 Reportes SMTP:** Envía un correo electrónico con el resumen de la operación y el espacio liberado (MB).
- **📝 Logging:** Registro detallado de cada ejecución en `backup_log.txt`.

## 🛠️ Requisitos

* Python 3.x
* Entorno Windows (Rutas configuradas para sistema de archivos Windows)
* Librerías estándar de Python (`os`, `shutil`, `sys`, `datetime`, `smtplib`).

## ⚙️ Configuración

Edita las variables constantes al inicio del script `limpieza.py` para adaptarlo a tu entorno:

```python
# Rutas de Almacenamiento
DEFAULT_SOURCE = r"C:\Users\TuUsuario\Downloads"
ROOT_PRIMARY   = r"D:\Backups\Descargas"      # Disco Principal
ROOT_SECONDARY = r"A:\Descargas"              # Disco de Respaldo (Redundancia)

# Configuración SMTP (Para reportes)
SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 587
EMAIL_SENDER   = "tu_email@gmail.com"
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx" # Usar Contraseña de Aplicación
EMAIL_RECEIVER = "tu_email@gmail.com"
````

### Categorías de Archivos

El script incluye una configuración predefinida para **Data Scientists**:

| Categoría | Extensiones |
| :--- | :--- |
| **Datasets\_Data** | `.csv`, `.json`, `.parquet`, `.sql`, `.db`... |
| **Modelos\_IA** | `.gguf`, `.pt`, `.safetensors`, `.onnx`, `.pkl`... |
| **Notebooks** | `.ipynb`, `.py`, `.r`, `.sh`... |

*(Puedes modificar el diccionario `FOLDERS_BY_TYPE` en el script para añadir más).*

## 🖥️ Uso

### 1\. Ejecución Manual (Modo Interactivo)

Ejecuta el script sin argumentos. Te pedirá confirmación antes de proceder.

```bash
python limpieza.py
```

### 2\. Ejecución Automática (Modo Silencioso)

Para tareas programadas, añade el argumento `auto`. Esto omite las preguntas de seguridad y asume "Sí" a todo.

```bash
python limpieza.py auto
```

## ⏰ Automatización (Windows Task Scheduler)

Para que el script se ejecute solo (ej. cada viernes a las 21:00):

1.  Abrir **Programador de Tareas**.
2.  Crear nueva tarea básica.
3.  **Desencadenador:** Semanal (Viernes).
4.  **Acción:** Iniciar un programa.
      * **Programa/Script:** Ruta a tu Python (ej: `E:\anaconda3\python.exe`).
      * **Argumentos:** `"C:\Ruta\Al\Script\limpieza.py" auto`
5.  **Configuración extra:** Marcar *"Ejecutar tarea lo antes posible si no hubo un inicio programado"* (para redundancia si el PC está apagado).

## 📥 Gestión de Correos (Filtros)

Para mantener tu bandeja de entrada limpia, crea una regla en Gmail/Outlook:

  * **Condición:** El asunto contiene "Backup Descargas".
  * **Acción:** Mover a etiqueta/carpeta `Logs Backup`.

## Ejemplo Correo :
<img width="1207" height="372" alt="image" src="https://github.com/user-attachments/assets/4a4a30e7-2f52-4e10-a0ef-99298e3d0e40" />


## 📄 Licencia

Este proyecto es de uso personal y libre modificación. ¡Úsalo bajo tu propia responsabilidad\!
