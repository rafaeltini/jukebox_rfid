import pygame
import os

class Player:
    """
    Uma classe singleton para controlar a reprodução de música usando pygame.
    Gerencia o estado do player (faixa atual, volume, status de reprodução).
    """
    _instance = None

    # Padrão Singleton para garantir que apenas uma instância do player exista
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Player, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Evita a re-inicialização
        if hasattr(self, '_initialized'):
            return

        print("Inicializando o Player de áudio (pygame)...")
        pygame.mixer.init()
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5  # Volume padrão de 50%
        pygame.mixer.music.set_volume(self.volume)
        self._initialized = True

    def play(self, song_path):
        """
        Carrega e toca uma nova música. Se uma música já estiver tocando, ela é parada.
        """
        if not os.path.exists(song_path):
            print(f"Erro: Arquivo de áudio não encontrado em '{song_path}'")
            return

        print(f"Tocando: {song_path}")
        self.current_song = song_path
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False

    def toggle_play_pause(self):
        """
        Alterna entre tocar e pausar a música atual.
        """
        if not self.is_playing:
            return

        if self.is_paused:
            print("Continuando a música.")
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            print("Pausando a música.")
            pygame.mixer.music.pause()
            self.is_paused = True

    def set_volume(self, level):
        """
        Define o volume.

        Args:
            level (float): Um valor entre 0.0 e 1.0.
        """
        self.volume = max(0.0, min(1.0, level))
        print(f"Ajustando volume para: {self.volume:.2f}")
        pygame.mixer.music.set_volume(self.volume)

    def get_status(self):
        """
        Retorna o estado atual do player.
        """
        # pygame.mixer.music.get_busy() retorna True se algo estiver tocando (mesmo que pausado)
        self.is_playing = pygame.mixer.music.get_busy()

        return {
            "current_song": os.path.basename(self.current_song) if self.current_song else None,
            "is_playing": self.is_playing and not self.is_paused,
            "is_paused": self.is_paused,
            "volume": self.volume
        }
