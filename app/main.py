from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/play', methods=['POST'])
def play():
    os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Play")
    return jsonify({"status": "playing"})

@app.route('/api/pause', methods=['POST'])
def pause():
    os.system("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Pause")
    return jsonify({"status": "paused"})

@app.route('/api/volume', methods=['POST'])
def volume():
    level = request.args.get('level', default='50')
    os.system(f"amixer set PCM {level}%")
    return jsonify({"volume": level})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)