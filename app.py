from flask import Flask, jsonify, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/download', methods=['GET'])
def download_audio():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing URL'}), 400

    file_id = str(uuid.uuid4())
    # IMPORTANTE: Se você quer MP3, mude aqui e no postprocessor
    output_filename = f"{file_id}.mp3"
    output_path = os.path.join(DOWNLOAD_DIR, output_filename)

    ydl_opts = {
        # 'bestaudio' é mais seguro que especificar 'm4a' de cara
        'format': 'bestaudio/best',
        'extractor_args': {'youtube': {'player_client': ['mweb']}},
        # O outtmpl deve ser genérico pois o postprocessor mudará a extensão
        'outtmpl': os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s"),
        'noplaylist': True,
        'cookiefile': '/app/cookies.txt', # Certifique-se que este arquivo existe no Fly.io
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', # Mudado para mp3 para coincidir com o output_path
            'preferredquality': '192',
        }],
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not os.path.exists(output_path):
            # Log extra para debug se falhar
            files_in_dir = os.listdir(DOWNLOAD_DIR)
            return jsonify({'error': f'File not found. Found: {files_in_dir}'}), 500

        return send_file(
            output_path, 
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name="audio.mp3"
        )

        # O cleanup será executado após o envio
        @response.call_on_close
        def cleanup():
            if os.path.exists(output_path):
                os.remove(output_path)

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
