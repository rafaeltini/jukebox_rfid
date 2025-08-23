# PT: Importa as bibliotecas necessárias
# EN: Imports the necessary libraries
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import threading
import json
from app.player import Player
from app.rfid import RFIDReader

# PT: Configurações Globais
# EN: Global Settings
MUSIC_FOLDER = "music"
TAGS_FILE = "tags.txt"
TRANSLATIONS_FILE = "app/translations.json"
tag_cache = {}
cache_lock = threading.Lock()

# PT: Inicializa a aplicação Flask e o SocketIO
# EN: Initializes the Flask application and SocketIO
app = Flask(__name__, template_folder='template', static_folder='static')
app.config['UPLOAD_FOLDER'] = MUSIC_FOLDER
socketio = SocketIO(app, async_mode='threading')

# PT: Cria uma instância única (singleton) do nosso Player
# EN: Creates a single (singleton) instance of our Player
player = Player()

# PT: Estado global para comunicação entre a thread da web e a thread RFID
# EN: Global state for communication between the web thread (Flask) and the RFID thread
assignment_state = {
    "pending_file": None,
    "lock": threading.Lock()
}

# --- Funções de Cache e Lógica da Jukebox / Cache and Jukebox Logic Functions ---

def load_tags_to_cache():
    """
    PT: Carrega as associações do arquivo tags.txt para o cache em memória.
    EN: Loads the associations from the tags.txt file into the in-memory cache.
    """
    global tag_cache
    if not os.path.exists(TAGS_FILE):
        print("Arquivo de tags não encontrado. O cache iniciará vazio. / Tags file not found. Cache will start empty.")
        return

    with cache_lock:
        with open(TAGS_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    tag_id, song_filename = line.strip().split(":", 1)
                    tag_cache[tag_id] = song_filename
    print(f"Cache de tags carregado com {len(tag_cache)} associações. / Tag cache loaded with {len(tag_cache)} associations.")

def get_song_for_tag(uid):
    """
    PT: Busca no cache a música associada a um determinado UID de cartão.
    EN: Searches the cache for the song associated with a given card UID.
    """
    with cache_lock:
        song_filename = tag_cache.get(uid)

    if song_filename:
        return os.path.join(MUSIC_FOLDER, song_filename)
    return None

def assign_song_to_tag(uid, song_filename):
    """
    PT: Salva a associação de um UID com um nome de arquivo de música no arquivo e no cache.
    EN: Saves the association of a UID with a music filename to the file and the cache.
    """
    # Adiciona ao arquivo
    with open(TAGS_FILE, "a") as f:
        f.write(f"{uid}:{song_filename}\n")

    # Adiciona ao cache
    with cache_lock:
        tag_cache[uid] = song_filename

    print(f"Associação salva (Association saved): {uid} -> {song_filename}")

# --- Lógica do Leitor RFID em Background / RFID Reader Background Logic ---

# PT: Cria uma instância única do nosso leitor RFID
# EN: Creates a single instance of our RFID reader
rfid_reader = RFIDReader()

def rfid_listener():
    """
    PT: Função que roda em uma thread para escutar por cartões RFID.
        A cada leitura, emite um evento WebSocket para a interface web.
    EN: Function that runs in a thread to listen for RFID cards.
        On each scan, it emits a WebSocket event to the web interface.
    """
    print("RFID Listener: Thread iniciada (Thread started).")
    while True:
        uid = rfid_reader.read_uid()
        if not uid:
            continue

        print(f"RFID Listener: Cartão escaneado (Card scanned) '{uid}'.")

        song_path = get_song_for_tag(uid)

        # PT: Emite o status do cartão para a interface web via WebSocket
        # EN: Emits the card status to the web interface via WebSocket
        socketio.emit('rfid_scan', {'uid': uid, 'associated': bool(song_path)})

        with assignment_state["lock"]:
            pending_file = assignment_state["pending_file"]
            if pending_file:
                print(f"RFID Listener: Associando cartão (Associating card) '{uid}' com o arquivo (with file) '{pending_file}'.")
                assign_song_to_tag(uid, pending_file)
                player.play(os.path.join(MUSIC_FOLDER, pending_file))
                assignment_state["pending_file"] = None
                # PT: Emite uma atualização após a associação
                # EN: Emits an update after association
                socketio.emit('rfid_scan', {'uid': uid, 'associated': True})
                continue

        if song_path:
            player.play(song_path)
        else:
            print(f"RFID Listener: Nenhuma música encontrada para o cartão (No song found for card) '{uid}'.")

# --- Rotas da API / API Routes ---

@app.route('/')
def index():
    # PT: Rota principal que serve a interface web.
    # EN: Main route that serves the web interface.
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    # PT: Endpoint para obter o estado atual do player.
    # EN: Endpoint to get the current player state.
    return jsonify(player.get_status())

@app.route('/api/play_pause', methods=['POST'])
def play_pause():
    # PT: Endpoint para alternar entre play e pause.
    # EN: Endpoint to toggle between play and pause.
    player.toggle_play_pause()
    return jsonify(player.get_status())

@app.route('/api/volume', methods=['POST'])
def volume():
    # PT: Endpoint para ajustar o volume.
    # EN: Endpoint to adjust the volume.
    level = int(request.json.get('level', 50))
    volume_float = max(0, min(100, level)) / 100.0
    player.set_volume(volume_float)
    return jsonify(player.get_status())

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # PT: Endpoint para upload de arquivos MP3.
    # EN: Endpoint for uploading MP3 files.
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado (No file sent)"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado (No file selected)"}), 400

    if file and file.filename.endswith('.mp3'):
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # PT: Inicia o modo de associação
        # EN: Initiates assignment mode
        with assignment_state["lock"]:
            assignment_state["pending_file"] = filename

        return jsonify({"status": "success", "message": f"Arquivo '{filename}' salvo. Aproxime um cartão para associar."})

    return jsonify({"status": "error", "message": "Arquivo inválido. Apenas MP3 são permitidos. (Invalid file. Only MP3s are allowed.)"}), 400

@app.route('/api/translations', methods=['GET'])
def get_translations():
    # PT: Endpoint que serve o arquivo de traduções.
    # EN: Endpoint that serves the translations file.
    try:
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Arquivo de traduções não encontrado (Translations file not found)."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Ponto de Entrada da Aplicação / Application Entry Point ---

if __name__ == '__main__':
    # PT: Garante que a pasta de música exista
    # EN: Ensures the music folder exists
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)

    # PT: Carrega as tags existentes para o cache
    # EN: Loads existing tags into the cache
    load_tags_to_cache()

    # PT: Inicia a thread do leitor RFID em modo daemon
    # EN: Starts the RFID reader thread in daemon mode
    listener_thread = threading.Thread(target=rfid_listener, daemon=True)
    listener_thread.start()

    # PT: Executa o servidor com suporte a WebSockets
    # EN: Runs the server with WebSocket support
    print("Iniciando servidor Web... / Starting web server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)