# Convertidor de Multimedia a Texto

Esta es una aplicación web simple construida con Flask que permite a los usuarios subir archivos de video (MP4) y audio para transcribirlos a texto. La aplicación utiliza **FFmpeg** para la extracción de audio y **OpenAI's Whisper** para la transcripción.

## Características

- **Interfaz Web Simple:** Sube archivos directamente desde el navegador.
- **Soporte para Múltiples Formatos:** Acepta videos `.mp4` y formatos de audio comunes como `.mp3`, `.wav`, `.m4a`.
- **Procesamiento Asíncrono:** La transcripción se ejecuta en segundo plano, permitiendo al usuario seguir el estado del proceso sin bloquear la interfaz.
- **Notificaciones de Estado:** El frontend muestra el estado actual del proceso (subiendo, extrayendo audio, transcribiendo, completado).
- **Manejo de Errores:** Informa al usuario si ocurren problemas durante el proceso.
- **Configuración Flexible:** Permite especificar el modelo de Whisper a utilizar a través de variables de entorno.

## Stack Tecnológico

- **Backend:** Python, Flask
- **Transcripción:** [OpenAI Whisper](https://github.com/openai/whisper) (a través de su CLI)
- **Procesamiento de Audio/Video:** [FFmpeg](https://ffmpeg.org/)
- **Frontend:** HTML, CSS, JavaScript (con `fetch` para comunicación asíncrona)

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu sistema y disponible en el PATH:

1.  **Python 3.7+**
2.  **FFmpeg:** Esencial para la extracción de audio de archivos de video. Puedes descargarlo desde [su sitio web oficial](https://ffmpeg.org/download.html).
    - Para verificar la instalación, ejecuta: `ffmpeg -version`
3.  **Git** (para clonar el repositorio).

## Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local:

1.  **Clona el repositorio:**
    ```bash
    git clone <URL-del-repositorio-de-github>
    cd mp4Text
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # En Windows
    python -m venv venv
    venv\Scripts\activate

    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará Flask y `openai-whisper`. La primera vez que se use `whisper`, descargará un modelo, lo que puede tardar un tiempo.

## Uso

1.  **Inicia la aplicación Flask:**
    ```bash
    flask run
    ```
    Opcionalmente, puedes ejecutar `python app.py`. El servidor se iniciará en `http://127.0.0.1:5000` por defecto.

2.  **Abre tu navegador:**
    Navega a `http://127.0.0.1:5000`.

3.  **Sube un archivo:**
    - Haz clic en "Seleccionar archivo" para elegir un archivo `.mp4` o de audio.
    - Haz clic en "Transcribir".
    - La aplicación mostrará el progreso. Una vez completado, la transcripción aparecerá en la página.

## Configuración Avanzada

### Modelo de Whisper

Por defecto, `whisper` utiliza el modelo `small`. Puedes especificar un modelo diferente (ej. `tiny`, `base`, `medium`, `large`) estableciendo la variable de entorno `WHISPER_MODEL`.

```bash
# Ejemplo en Windows (cmd)
set WHISPER_MODEL=base
flask run

# Ejemplo en macOS/Linux
export WHISPER_MODEL=base
flask run
```

Modelos más grandes ofrecen mayor precisión pero requieren más recursos y tiempo de procesamiento.

## Estructura del Proyecto

```
.
├── app.py              # Lógica principal de la aplicación Flask y endpoints.
├── requirements.txt    # Dependencias de Python.
├── static/
│   └── style.css       # Estilos para el frontend.
├── templates/
│   └── index.html      # Estructura HTML y JavaScript del frontend.
├── uploads/            # Directorio temporal para archivos subidos y transcripciones.
└── README.md           # Este archivo.
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar la aplicación, por favor, abre un *issue* para discutir los cambios o envía un *pull request*.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
