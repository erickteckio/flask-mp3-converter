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
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

    ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'extractor_args': {'youtube': {'player_client': ['mweb']}},
    'outtmpl': os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s"),
    'noplaylist': True,
    'cookiefile': '/app/cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'quiet': False,   # ← temporariamente, para ver logs
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not os.path.exists(output_path):
            return jsonify({'error': 'Conversion failed'}), 500

        response = send_file(output_path, mimetype='audio/mpeg')

        @response.call_on_close
        def cleanup():
            try:
                os.remove(output_path)
            except:
                pass

        return response
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
