from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__, template_folder='templates', static_folder='static')

# Função auxiliar para enviar comandos D-Bus ao Spotify
def send_dbus_command(action):
    try:
        subprocess.run([
            "dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.spotify",
            "/org/mpris/MediaPlayer2", f"org.mpris.MediaPlayer2.Player.{action}"
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar D-Bus: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/play', methods=['POST'])
def play():
    success = send_dbus_command("Play")
    return jsonify({"status": "playing" if success else "error"})

@app.route('/api/pause', methods=['POST'])
def pause():
    success = send_dbus_command("Pause")
    return jsonify({"status": "paused" if success else "error"})

@app.route('/api/volume', methods=['POST'])
def volume():
    try:
        level = int(request.args.get('level', default='50'))
        if not 0 <= level <= 100:
            raise ValueError("Volume deve estar entre 0 e 100")
        subprocess.run(["amixer", "set", "PCM", f"{level}%"], check=True)
        return jsonify({"volume": level})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)