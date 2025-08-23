# PT: Importa as bibliotecas necessárias
# EN: Imports the necessary libraries
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
import threading
import json
import socket
import atexit
from zeroconf import ServiceInfo, Zeroconf
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

# --- Funções de Descoberta de Rede (mDNS) / Network Discovery (mDNS) Functions ---

def get_local_ip():
    """
    PT: Tenta descobrir o endereço IP local da máquina na rede.
    EN: Tries to discover the local IP address of the machine on the network.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        print(f"Não foi possível obter o IP local automaticamente: {e} / Could not get local IP automatically: {e}")
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def register_mdns_service():
    """
    PT: Registra o serviço da Jukebox na rede local usando mDNS (Bonjour/Avahi).
    EN: Registers the Jukebox service on the local network using mDNS (Bonjour/Avahi).
    """
    service_name = "rfidbox"
    service_type = "_http._tcp.local."
    port = 5000
    server_name = f"{service_name}.local."

    try:
        ip_address = get_local_ip()
        info = ServiceInfo(
            service_type,
            f"{service_name}.{service_type}",
            addresses=[socket.inet_aton(ip_address)],
            port=port,
            properties={'path': '/'},
            server=server_name,
        )
        zeroconf = Zeroconf()
        print(f"Registrando serviço mDNS: {service_name} em {ip_address}:{port} / Registering mDNS service: {service_name} at {ip_address}:{port}")
        zeroconf.register_service(info)
        atexit.register(zeroconf.close)
    except Exception as e:
        print(f"Erro ao registrar o serviço mDNS: {e} / Error registering mDNS service: {e}")


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

@app.route('/api/play/<string:filename>', methods=['POST'])
def play_song(filename):
    """
    PT: Toca uma música específica pelo nome do arquivo.
    EN: Plays a specific song by its filename.
    """
    # Segurança: Garante que o nome do arquivo não contém caracteres de path.
    if '/' in filename or '\\' in filename:
        return jsonify({"status": "error", "message": "Nome de arquivo inválido."}), 400

    song_path = os.path.join(MUSIC_FOLDER, filename)

    if os.path.exists(song_path):
        player.play(song_path)
        return jsonify({"status": "success", "message": f"Tocando {filename}"})
    else:
        return jsonify({"status": "error", "message": "Arquivo não encontrado."}), 404

@app.route('/api/initiate_association', methods=['POST'])
def initiate_association():
    """
    PT: Inicia o modo de associação para um arquivo de música específico.
    EN: Initiates assignment mode for a specific music file.
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"status": "error", "message": "Nome do arquivo não fornecido."}), 400

    filename = data['filename']
    # Segurança
    if '/' in filename or '\\' in filename:
        return jsonify({"status": "error", "message": "Nome de arquivo inválido."}), 400

    song_path = os.path.join(MUSIC_FOLDER, filename)
    if not os.path.exists(song_path):
        return jsonify({"status": "error", "message": "Arquivo não encontrado."}), 404

    with assignment_state["lock"]:
        assignment_state["pending_file"] = filename

    return jsonify({"status": "success", "message": f"Aproxime um cartão para associar à música: {filename}"})

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

        return jsonify({"status": "success", "message": f"Arquivo '{filename}' salvo com sucesso."})

    return jsonify({"status": "error", "message": "Arquivo inválido. Apenas MP3 são permitidos. (Invalid file. Only MP3s are allowed.)"}), 400

@app.route('/api/association/<string:tag_id>', methods=['DELETE'])
def delete_association(tag_id):
    """
    PT: Deleta a associação de uma tag específica.
    EN: Deletes the association for a specific tag.
    """
    if not tag_id:
        return jsonify({"status": "error", "message": "ID da tag não fornecido."}), 400

    with cache_lock:
        if tag_id not in tag_cache:
            return jsonify({"status": "error", "message": "Tag não encontrada."}), 404

        # Remove do cache
        del tag_cache[tag_id]

        # Reescreve o arquivo tags.txt sem a linha deletada
        try:
            with open(TAGS_FILE, "w") as f:
                for tid, song in tag_cache.items():
                    f.write(f"{tid}:{song}\n")
            return jsonify({"status": "success", "message": f"Associação para a tag {tag_id} deletada."})
        except Exception as e:
            # Se a reescrita falhar, idealmente deveríamos ter um rollback,
            # mas por simplicidade vamos apenas logar o erro.
            print(f"Erro ao reescrever o arquivo de tags: {e}")
            # Recarregar o cache do arquivo para garantir consistência
            load_tags_to_cache()
            return jsonify({"status": "error", "message": "Erro ao salvar as alterações."}), 500

@app.route('/api/library', methods=['GET'])
def get_library():
    """
    PT: Retorna a lista de músicas e as associações de tags.
    EN: Returns the list of songs and tag associations.
    """
    try:
        # Lista de músicas na pasta
        songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
        songs.sort()

        # As associações já estão no cache em 'tag_cache'
        with cache_lock:
            associations = dict(tag_cache)

        response = jsonify({
            "songs": songs,
            "associations": associations
        })
        # PT: Evita que o navegador guarde a lista em cache.
        # EN: Prevents the browser from caching the list.
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

    # PT: Inicia o serviço de descoberta mDNS. Isso não precisa de uma thread separada
    #     pois o atexit.register cuida do fechamento. A biblioteca roda em seus próprios daemons.
    # EN: Starts the mDNS discovery service. This doesn't need a separate thread
    #     as atexit.register handles the cleanup. The library runs in its own daemons.
    register_mdns_service()

    # PT: Inicia a thread do leitor RFID em modo daemon
    # EN: Starts the RFID reader thread in daemon mode
    listener_thread = threading.Thread(target=rfid_listener, daemon=True)
    listener_thread.start()

    # PT: Executa o servidor com suporte a WebSockets
    # EN: Runs the server with WebSocket support
    print("Iniciando servidor Web... / Starting web server...")
    print("Acesse a Jukebox em http://rfidbox.local:5000 ou http://<seu_ip>:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)