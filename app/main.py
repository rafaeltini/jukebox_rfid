# Importa as bibliotecas necessárias
from flask import Flask, render_template, request, jsonify
import os
import threading
from app.player import Player  # Importa a nova classe de player
from app.rfid import read_uid   # Importa a função de leitura de RFID

# Configurações
MUSIC_FOLDER = "music"
TAGS_FILE = "tags.txt"

# Inicializa a aplicação Flask
app = Flask(__name__, template_folder='template', static_folder='static')
app.config['UPLOAD_FOLDER'] = MUSIC_FOLDER

# Cria uma instância única (singleton) do nosso Player
player = Player()

# Estado global para comunicação entre a thread da web e a thread RFID
assignment_state = {
    "pending_file": None,
    "lock": threading.Lock()
}

# --- Funções de Lógica da Jukebox ---

def get_song_for_tag(uid):
    """Busca no arquivo de tags a música associada a um UID de cartão."""
    if not os.path.exists(TAGS_FILE):
        return None
    with open(TAGS_FILE, "r") as f:
        for line in f:
            if ":" in line:
                tag_id, song_filename = line.strip().split(":", 1)
                if tag_id == uid:
                    return os.path.join(MUSIC_FOLDER, song_filename)
    return None

def assign_song_to_tag(uid, song_filename):
    """Salva a associação de um UID com um nome de arquivo de música."""
    with open(TAGS_FILE, "a") as f:
        f.write(f"{uid}:{song_filename}\n")
    print(f"Associação salva: {uid} -> {song_filename}")

# --- Lógica do Leitor RFID em Background ---

def rfid_listener():
    """Função que roda em uma thread para escutar por cartões RFID."""
    print("RFID Listener: Thread iniciada.")
    while True:
        uid = read_uid()
        if not uid:
            continue

        print(f"RFID Listener: Cartão '{uid}' escaneado.")

        with assignment_state["lock"]:
            pending_file = assignment_state["pending_file"]
            if pending_file:
                print(f"RFID Listener: Associando cartão '{uid}' com o arquivo '{pending_file}'.")
                assign_song_to_tag(uid, pending_file)
                player.play(os.path.join(MUSIC_FOLDER, pending_file))
                assignment_state["pending_file"] = None
                continue

        song_path = get_song_for_tag(uid)
        if song_path:
            player.play(song_path)
        else:
            print(f"RFID Listener: Nenhuma música encontrada para o cartão '{uid}'.")

# --- Rotas da API ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(player.get_status())

@app.route('/api/play_pause', methods=['POST'])
def play_pause():
    player.toggle_play_pause()
    return jsonify(player.get_status())

@app.route('/api/volume', methods=['POST'])
def volume():
    level = int(request.json.get('level', 50))
    volume_float = max(0, min(100, level)) / 100.0
    player.set_volume(volume_float)
    return jsonify(player.get_status())

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivos MP3."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"}), 400

    if file and file.filename.endswith('.mp3'):
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Inicia o modo de associação
        with assignment_state["lock"]:
            assignment_state["pending_file"] = filename

        return jsonify({"status": "success", "message": f"Arquivo '{filename}' salvo. Aproxime um cartão para associar."})

    return jsonify({"status": "error", "message": "Arquivo inválido. Apenas MP3 são permitidos."}), 400

# --- Ponto de Entrada da Aplicação ---

if __name__ == '__main__':
    # Garante que a pasta de música exista
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)

    # Inicia a thread do leitor RFID em modo daemon
    listener_thread = threading.Thread(target=rfid_listener, daemon=True)
    listener_thread.start()

    # Executa o servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=False)