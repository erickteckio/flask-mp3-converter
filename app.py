from flask import Flask, jsonify, request
import yt_dlp  # yt-dlp é a biblioteca para baixar o áudio do YouTube
import subprocess  # Para chamar o FFmpeg diretamente

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_audio():
    video_url = request.args.get('url')  # URL do vídeo do YouTube
    if not video_url:
        return jsonify({'error': 'Missing URL'}), 400

    # Configuração para download de áudio
    ydl_opts = {
        'format': 'bestaudio/best',  # Extrai o melhor áudio disponível
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Salvar o arquivo na pasta downloads
        'noplaylist': True,  # Não tentar baixar playlists
        'quiet': False,  # Para mostrar mais detalhes no terminal
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            # Caminho para o arquivo WebM baixado
            audio_file_webm = f"downloads/{info_dict['id']}.webm"
            audio_file_mp3 = f"downloads/{info_dict['id']}.mp3"  # Caminho para o arquivo MP3

            # Convertendo WebM para MP3 com FFmpeg
            # Substitua 'C:\\ffmpeg\\bin\\ffmpeg.exe' pelo caminho correto do FFmpeg no seu sistema
            subprocess.run(['C:\\ffmpeg\\bin\\ffmpeg.exe', '-i', audio_file_webm, audio_file_mp3])


            # Após a conversão, podemos deletar o arquivo WebM (opcional)
            subprocess.run(['rm', audio_file_webm])  # No Windows, use 'del' ao invés de 'rm'

            return jsonify({'audio_file': audio_file_mp3}), 200
    except Exception as e:
        # Aqui estamos logando o erro completo para depuração
        app.logger.error(f"Erro ao baixar o áudio: {str(e)}")
        return jsonify({'error': 'Failed to download audio', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
