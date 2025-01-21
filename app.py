import os
import requests
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageSequence
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/convert": {"origins": "http://localhost:8060"}})

# Folder to store temporary spritesheets
TEMP_FOLDER = "temp_spritesheets"
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_gif_to_spritesheet():
    try:
        # Get the GIF URL from the request
        data = request.json
        gif_url = data.get('gif_url')

        if not gif_url:
            return jsonify({'error': 'No GIF URL provided'}), 400

        # Download the GIF
        response = requests.get(gif_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch GIF'}), 400

        # Load the GIF into PIL
        gif_bytes = BytesIO(response.content)
        gif = Image.open(gif_bytes)

        # Create a spritesheet
        frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
        width, height = gif.size
        spritesheet_width = width * len(frames)
        spritesheet = Image.new("RGBA", (spritesheet_width, height))

        for i, frame in enumerate(frames):
            spritesheet.paste(frame, (i * width, 0))

        # Save the spritesheet to a temporary file
        output_path = os.path.join(TEMP_FOLDER, "spritesheet.png")
        spritesheet.save(output_path, format="PNG")

        # Send the spritesheet back to the client
        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
