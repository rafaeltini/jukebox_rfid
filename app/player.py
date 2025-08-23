import pygame
import os

class Player:
    """
    PT: Uma classe singleton para controlar a reprodução de música usando pygame.
        Gerencia o estado do player (faixa atual, volume, status de reprodução).
    EN: A singleton class to control music playback using pygame.
        Manages the player's state (current track, volume, playback status).
    """
    _instance = None

    # PT: Padrão Singleton para garantir que apenas uma instância do player exista.
    # EN: Singleton pattern to ensure that only one instance of the player exists.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Player, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # PT: Evita a re-inicialização da instância já existente.
        # EN: Prevents re-initialization of the existing instance.
        if hasattr(self, '_initialized'):
            return

        print("Inicializando o Player de áudio (pygame)... / Initializing audio player (pygame)...")
        pygame.mixer.init()
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5  # PT: Volume padrão de 50% | EN: Default volume of 50%
        pygame.mixer.music.set_volume(self.volume)
        self._initialized = True

    def play(self, song_path):
        """
        PT: Carrega e toca uma nova música. Se uma música já estiver tocando, ela é parada.
        EN: Loads and plays a new song. If a song is already playing, it is stopped.
        """
        if not os.path.exists(song_path):
            print(f"Erro: Arquivo de áudio não encontrado em (Error: Audio file not found at) '{song_path}'")
            return

        print(f"Tocando (Now Playing): {song_path}")
        self.current_song = song_path
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False

    def toggle_play_pause(self):
        """
        PT: Alterna entre tocar e pausar a música atual.
        EN: Toggles between playing and pausing the current song.
        """
        if not self.is_playing:
            return

        if self.is_paused:
            print("Continuando a música (Resuming music).")
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            print("Pausando a música (Pausing music).")
            pygame.mixer.music.pause()
            self.is_paused = True

    def set_volume(self, level):
        """
        PT: Define o volume.
        EN: Sets the volume.

        Args:
            level (float): PT: Um valor entre 0.0 e 1.0. | EN: A value between 0.0 and 1.0.
        """
        self.volume = max(0.0, min(1.0, level))
        print(f"Ajustando volume para (Adjusting volume to): {self.volume:.2f}")
        pygame.mixer.music.set_volume(self.volume)

    def get_status(self):
        """
        PT: Retorna o estado atual do player.
        EN: Returns the current state of the player.
        """
        # PT: pygame.mixer.music.get_busy() retorna True se algo estiver tocando (mesmo que pausado).
        # EN: pygame.mixer.music.get_busy() returns True if something is playing (even if paused).
        self.is_playing = pygame.mixer.music.get_busy()

        return {
            "current_song": os.path.basename(self.current_song) if self.current_song else None,
            "is_playing": self.is_playing and not self.is_paused,
            "is_paused": self.is_paused,
            "volume": self.volume
        }
