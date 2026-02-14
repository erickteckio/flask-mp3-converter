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
    # Vamos forçar o nome final do arquivo aqui
    final_filename = f"{file_id}.mp3"
    final_path = os.path.join(DOWNLOAD_DIR, final_filename)

    ydl_opts = {
        # 'bestaudio' busca a melhor qualidade sem frescura de formato inicial
        'format': 'bestaudio/best',
        # 'outtmpl' sem a extensão no final para o postprocessor gerenciar
        'outtmpl': os.path.join(DOWNLOAD_DIR, file_id), 
        'noplaylist': True,
        # Argumentos vitais para evitar bloqueios de bot/formato
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash']
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Verifica se o arquivo .mp3 realmente existe
        if not os.path.exists(final_path):
            # Se falhou, vamos ver o que o yt-dlp realmente criou no log
            files = os.listdir(DOWNLOAD_DIR)
            return jsonify({'error': 'File not found', 'debug_files': files}), 500

        return send_file(final_path, mimetype='audio/mpeg', as_attachment=True, download_name="audio.mp3")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
