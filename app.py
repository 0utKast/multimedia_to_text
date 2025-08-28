from flask import Flask, request, render_template, jsonify
import os
import subprocess
import uuid
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        # Pre-flight checks for required CLIs
        if shutil.which('ffmpeg') is None:
            return "ffmpeg no está instalado o no está en el PATH", 500
        if shutil.which('whisper') is None:
            return "whisper (openai-whisper) no está instalado o no está en el PATH", 500

        unique_filename = str(uuid.uuid4())
        original_filename, file_extension = os.path.splitext(file.filename)
        input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename + file_extension)
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename + '.txt')
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename + '.wav') # Path for extracted WAV if needed

        file.save(input_file_path)
        print(f"DEBUG: File saved to {input_file_path}")

        audio_input_path = input_file_path # Assume input is audio by default

        # Check if the input file is a video (e.g., .mp4) and needs audio extraction
        if file_extension.lower() == '.mp4':
            print("DEBUG: Input is MP4, extracting audio with ffmpeg...")

        
import os
import subprocess
import uuid
import shutil
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

task_statuses = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status/<task_id>')
def get_status(task_id):
    status = task_statuses.get(task_id, {'status': 'unknown', 'transcription': None, 'error': None})
    print(f"DEBUG: Sending status: {status['status']}")
    return jsonify(status)

@app.route('/upload', methods=['POST'])
def upload_file():
    task_id = str(uuid.uuid4())
    task_statuses[task_id] = {'status': 'received', 'transcription': None, 'error': None}

    if 'file' not in request.files:
        task_statuses[task_id]['status'] = 'error'
        task_statuses[task_id]['error'] = "No file part"
        return jsonify({'task_id': task_id, 'status': 'error', 'message': "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        task_statuses[task_id]['status'] = 'error'
        task_statuses[task_id]['error'] = "No selected file"
        return jsonify({'task_id': task_id, 'status': 'error', 'message': "No selected file"}), 400
    if file:
        # Pre-flight checks for required CLIs
        if shutil.which('ffmpeg') is None:
            task_statuses[task_id]['status'] = 'error'
            task_statuses[task_id]['error'] = "ffmpeg no está instalado o no está en el PATH"
            return jsonify({'task_id': task_id, 'status': 'error', 'message': "ffmpeg no está instalado o no está en el PATH"}), 500
        if shutil.which('whisper') is None:
            task_statuses[task_id]['status'] = 'error'
            task_statuses[task_id]['error'] = "whisper (openai-whisper) no está instalado o no está en el PATH"
            return jsonify({'task_id': task_id, 'status': 'error', 'message': "whisper (openai-whisper) no está instalado o no está en el PATH"}), 500

        # Save the file to a temporary location before starting the thread
        unique_filename = str(uuid.uuid4())
        original_filename, file_extension = os.path.splitext(file.filename)
        temp_input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename + file_extension)
        file.save(temp_input_file_path)
        print(f"DEBUG: File saved temporarily to {temp_input_file_path}")

        # Run the transcription in a separate thread to avoid blocking the main Flask thread
        threading.Thread(target=process_file_for_transcription, args=(temp_input_file_path, file_extension, task_id, original_filename)).start()

        return jsonify({'task_id': task_id, 'status': 'processing_started'}), 202

def process_file_for_transcription(input_file_path, file_extension, task_id, original_filename):
    # This function will contain the original logic of upload_file, but will update task_statuses
    # and handle file operations. It will not return HTTP responses directly.
    # txt_path and wav_path need to be derived from the input_file_path
    # Sanitize original_filename for safe use in file paths
    sanitized_original_filename = "".join([c for c in original_filename if c.isalnum() or c in (' ', '_', '-')]).rstrip()
    if not sanitized_original_filename: # Fallback if sanitization results in empty string
        sanitized_original_filename = "transcription"

    # Use sanitized original filename + a portion of UUID for TXT output to ensure uniqueness
    base_filename_for_txt = f"{sanitized_original_filename}_{str(uuid.uuid4())[:8]}"

    # Use sanitized original filename + a portion of UUID for TXT output to ensure uniqueness
    
    base_filename = os.path.splitext(os.path.basename(input_file_path))[0]
    wav_path = os.path.join(app.config['UPLOAD_FOLDER'], base_filename + '.wav') # Path for extracted WAV if needed

    # Initialize audio_input_path
    audio_input_path = input_file_path
    txt_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(os.path.basename(audio_input_path))[0] + '.txt')
    txt_path_final = os.path.join(app.config['UPLOAD_FOLDER'], base_filename_for_txt + '.txt')

    try:
        task_statuses[task_id]['status'] = 'file_saved' # Already saved in main thread

        # Check if the input file is a video (e.g., .mp4) and needs audio extraction
        if file_extension.lower() == '.mp4':
            print("DEBUG: Input is MP4, extracting audio with ffmpeg...")
            task_statuses[task_id]['status'] = 'extracting_audio'
            try:
                subprocess.run(
                    ['ffmpeg', '-y', '-loglevel', 'error', '-i', input_file_path, '-vn', wav_path],
                    check=True,
                    capture_output=True,
                    timeout=600,
                )
                print("DEBUG: ffmpeg process completed.")
                audio_input_path = wav_path # Use the extracted WAV for whisper
                task_statuses[task_id]['status'] = 'audio_extracted'
            except subprocess.TimeoutExpired:
                print("DEBUG: ffmpeg timeout.")
                task_statuses[task_id]['status'] = 'error'
                task_statuses[task_id]['error'] = "Timeout al extraer audio con ffmpeg"
                return
            except subprocess.CalledProcessError as e:
                stderr = (e.stderr or b'').decode(errors='ignore')
                print(f"DEBUG: ffmpeg error: {stderr}")
                task_statuses[task_id]['status'] = 'error'
                task_statuses[task_id]['error'] = f"Error extrayendo audio (ffmpeg): {stderr}"
                return
        else:
            print(f"DEBUG: Input is audio ({file_extension}), proceeding directly to whisper.")
            task_statuses[task_id]['status'] = 'ready_for_transcription'

        # Transcribe audio using whisper
        print("DEBUG: Starting whisper process...")
        task_statuses[task_id]['status'] = 'transcribing'
        try:
            # Whisper will create the .txt file in the specified output directory
            whisper_cmd = ['whisper', audio_input_path, '--output_dir', app.config['UPLOAD_FOLDER'], '--output_format', 'txt']
            model = os.getenv('WHISPER_MODEL')
            if model:
                whisper_cmd += ['--model', model]
            whisper_process = subprocess.run(
                whisper_cmd,
                check=True,
                capture_output=True,
                timeout=3600,
            )
            print("DEBUG: whisper process completed.")
            print(f"Whisper STDOUT: {whisper_process.stdout.decode(errors='ignore')}")
            print(f"Whisper STDERR: {whisper_process.stderr.decode(errors='ignore')}")
            task_statuses[task_id]['status'] = 'transcription_completed'
            # Rename the generated .txt file to the desired personalized name
            if os.path.exists(txt_path):
                os.rename(txt_path, txt_path_final)
                print(f"DEBUG: Renamed {txt_path} to {txt_path_final}")
        except subprocess.TimeoutExpired:
            print("DEBUG: whisper timeout.")
            task_statuses[task_id]['status'] = 'error'
            task_statuses[task_id]['error'] = "Timeout transcribiendo audio con whisper (modelo puede tardar)."
            return
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or b'').decode(errors='ignore')
            print(f"DEBUG: whisper error: {stderr}")
            task_statuses[task_id]['status'] = 'error'
            task_statuses[task_id]['error'] = f"Error transcribiendo audio (whisper): {stderr}"
            return

        # Read the transcribed text
        print(f"DEBUG: Attempting to read transcription from {txt_path_final}...")
        task_statuses[task_id]['status'] = 'reading_transcription'
        try:
            with open(txt_path_final, 'r', encoding='utf-8') as f:
                transcription = f.read()
            print("DEBUG: Transcription read successfully.")
            task_statuses[task_id]['transcription'] = transcription
            task_statuses[task_id]['status'] = 'completed'
        except Exception as e:
            print(f"DEBUG: Error reading transcription file: {e}")
            task_statuses[task_id]['status'] = 'error'
            task_statuses[task_id]['error'] = f"Error reading transcription file: {e}"
        finally:
            # Clean up temporary files
            print("DEBUG: Cleaning up temporary files...")
            files_to_remove = [input_file_path] # The original uploaded file
            if os.path.exists(wav_path) and audio_input_path == wav_path: # Only remove wav if it was created and used
                files_to_remove.append(wav_path)

            for p in files_to_remove:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                        print(f"DEBUG: Removed {p}")
                except Exception as e:
                    print(f"DEBUG: Failed to remove {p}: {e}")
                    # No bloquear la respuesta por fallos de borrado (Windows locks, etc.)
                    pass
            print("DEBUG: Temporary file cleanup completed.")

        print("DEBUG: Returning transcription.")

    except Exception as e:
        print(f"DEBUG: Unhandled exception in process_file_for_transcription: {e}")
        task_statuses[task_id]['status'] = 'error'
        task_statuses[task_id]['error'] = f"Unhandled server error: {e}"

        

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') in ('1', 'true', 'True', 'yes', 'YES')
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
