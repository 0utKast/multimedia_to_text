Resumen de diagnóstico y mejoras

- Estado inicial: No había archivo GEMINI.md en el proyecto. Se ha creado este documento para resumir hallazgos y cambios.

Hallazgos clave

- Flujo backend: `app.py` recibe el MP4, lo guarda en `uploads/`, extrae WAV con `ffmpeg` y transcribe con `whisper` CLI, leyendo después el `.txt` generado.
- Potenciales causas del bloqueo:
  - `ffmpeg` esperando confirmación de overwrite (falta `-y`) si existe el archivo de salida.
  - `ffmpeg` o `whisper` no disponibles en el PATH del proceso que ejecuta Flask (levanta `FileNotFoundError` o se percibe como cuelgue si no se maneja).
  - Descarga de modelo de Whisper en primer uso (sin caché) puede tardar mucho o bloquear tras cortafuegos.
  - Procesos largos sin timeout: si `ffmpeg`/`whisper` se quedan esperando (I/O, locks), la petición HTTP queda abierta y el front queda en “Transcribiendo…”.
  - Windows: locks al borrar archivos justo tras transcribir; borrar puede fallar y antes interrumpía la respuesta.

Cambios aplicados

- `app.py`:
  - Añadido chequeo de `ffmpeg` y `whisper` en PATH con mensajes de error claros.
  - `ffmpeg` ahora usa `-y` y `-loglevel error` para evitar prompts y reducir ruido.
  - Añadidos timeouts: `ffmpeg` (10 min), `whisper` (60 min) con errores específicos en caso de timeout.
  - Manejo robusto de errores capturando `stderr` y devolviendo textos informativos al cliente.
  - Borrado de temporales protegido con `try/except` para evitar que un fallo al borrar bloquee la respuesta.
  - Soporte opcional de modelo Whisper vía env `WHISPER_MODEL` (p.ej. `base`, `small`, `medium`, etc.).
- `requirements.txt`: añadido `openai-whisper` para disponer del CLI.

Recomendaciones de uso

- Instalar dependencias: `pip install -r requirements.txt`.
- Instalar ffmpeg y asegurarlo en el PATH del usuario que ejecuta Flask.
- Pre-caché del modelo de Whisper para evitar esperas: `WHISPER_MODEL=small whisper ejemplo.wav` (o ejecutar una vez la app para que descargue).
- En Windows, ejecutar la app y ffmpeg con permisos suficientes; evitar tener abiertos los archivos en otros programas durante la transcripción.
- Si el entorno no permite descargas, descargar manualmente los modelos de Whisper y configurar `WHISPER_MODEL`.

Notas adicionales

- El archivo `errores.txt` contiene un error de consola del navegador no relacionado con el backend; no afecta al flujo.
- Si se desea evitar el CLI, se podría migrar a la API Python de Whisper para mayor control y evitar dependencias del PATH.

