from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytube
from pytube.cli import on_progress
import os
import re
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data['url']
        format_type = data.get('format', 'mp4')
        
        yt = pytube.YouTube(url, on_progress_callback=on_progress)
        filename = f"{sanitize_filename(yt.title)}_{str(uuid.uuid4())[:8]}"
        
        if format_type == 'mp3':
            stream = yt.streams.get_audio_only()
            ext = 'mp3'
        else:
            stream = yt.streams.filter(
                file_extension='mp4',
                resolution='1080p' if format_type == 'mp4' else '720p'
            ).first()
            ext = 'mp4'

        if not stream:
            return jsonify({"error": "No suitable stream found"}), 400

        # Download file
        stream.download(
            output_path=DOWNLOAD_FOLDER,
            filename=f"{filename}.{ext}"
        )

        return jsonify({
            "message": "Download successful",
            "download_url": f"/downloads/{filename}.{ext}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)