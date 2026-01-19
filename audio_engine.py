import pygame
import librosa
import numpy as np
import threading
import os

class AudioEngine:
    def __init__(self):
        # Inicializar Pygame Mixer
        pygame.mixer.init()
        
        self.current_file = None
        self.y = None # Audio array
        self.sr = None # Sample rate
        self.duration = 0
        
        # Datos de análisis
        self.spec = None # Espectrograma
        self.spec_db = None
        self.hop_length = 512
        self.n_fft = 2048
        
        # Estado
        self.is_loaded = False
        self.is_playing = False
        self.is_paused = False # [NEW] Nuevo estado para saber si estamos pausados
        self.loading_thread = None

    def load_track(self, filepath, callback_ready=None):
        """
        Carga el audio para reproducción (Pygame) y análisis (Librosa).
        El análisis pesado se hace en un hilo separado.
        """
        if not os.path.exists(filepath):
            print(f"Error: Archivo no encontrado {filepath}")
            return

        self.current_file = filepath
        self.audio_file = filepath # Alias para compatibilidad
        self.is_loaded = False
        self.is_paused = False # Resetear estado
        print(f"[ENGINE LOG] Loading track: {filepath}")
        
        # Cargar en Mixer (Rápido, para reproducción inmediata si se requiere)
        try:
            pygame.mixer.music.load(filepath)
        except Exception as e:
            print(f"Error cargando mixer: {e}")

        # Iniciar análisis en background
        self.loading_thread = threading.Thread(target=self._analyze_audio, args=(filepath, callback_ready))
        self.loading_thread.start()

    def _analyze_audio(self, filepath, callback):
        print("Iniciando análisis de audio con Librosa...")
        try:
            # 1. Cargar audio (puede tardar unos segundos en archivos largos)
            self.y, self.sr = librosa.load(filepath, sr=22050)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            
            # 2. Calcular STFT (Short-Time Fourier Transform)
            # Esto nos da la magnitud de frecuencias a lo largo del tiempo
            self.spec = librosa.stft(self.y, n_fft=self.n_fft, hop_length=self.hop_length)
            
            # 3. Convertir a escala de decibelios (dB) para mejor visualización
            # Solo usamos la parte de magnitud (abs)
            self.spec_db = librosa.amplitude_to_db(np.abs(self.spec), ref=np.max)
            
            # Normalizar entre 0 y 1 para facilitar el dibujo
            self.spec_db = (self.spec_db + 80) / 80
            self.spec_db = np.clip(self.spec_db, 0, 1)
            
            self.is_loaded = True
            print(f"[ENGINE LOG] Analysis completed. is_loaded={self.is_loaded}")
            
            if callback:
                callback()
                
        except Exception as e:
            print(f"Error en análisis Librosa: {e}")

    def play(self):
        print(f"[ENGINE LOG] Attempting play... current_file={self.current_file}, is_paused={self.is_paused}")
        if self.current_file:
            try:
                if self.is_paused:
                    print("[ENGINE LOG] Calling unpause()...")
                    pygame.mixer.music.unpause()
                else:
                    print("[ENGINE LOG] Calling play()...")
                    pygame.mixer.music.play()
                
                self.is_playing = True
                self.is_paused = False
                print("[ENGINE LOG] Play action completed.")
            except Exception as e:
                print(f"[ENGINE ERROR] Error in play(): {e}")

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        self.is_paused = True # Marcar como pausado

    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.is_paused = False
        
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def get_audio_time(self):
        """Devuelve el tiempo actual de reproducción en segundos."""
        if self.is_playing:
            # get_pos devuelve ms, convertimos a segundos
            return pygame.mixer.music.get_pos() / 1000.0
        return 0

    def get_audio_data(self, t=None):
        """
        Devuelve el array de frecuencias correspondiente al instante actual o al tiempo t.
        Si no hay audio cargado o analizado, devuelve ruido o ceros.
        """
        if not self.is_loaded or self.spec_db is None:
            # Devolver dummy data (pequeño ruido suave) para que no se vea muerto
            return np.random.rand(50) * 0.1

        # 1. Obtener tiempo (si no se pasa t, usamos tiempo real de playback)
        if t is None:
            t = self.get_audio_time()
        
        # 2. Calcular índice del frame correspondiente en el espectrograma
        frame_index = librosa.time_to_frames(t, sr=self.sr, hop_length=self.hop_length)
        
        # 3. Extraer columna segura
        if frame_index < self.spec_db.shape[1]:
            # Obtenemos todas las frecuencias de este instante
            # Reducimos/Promediamos para tener menos barras (ej. 64 barras)
            full_spectrum = self.spec_db[:, int(frame_index)]
            
            # Remuestrear simple para obtener 64 bandas
            # Tomamos frecuencias bajas a medias principalmente (indices 0 a 100 del FFT suelen ser graves/medios)
            bands = 64
            # Usamos lógica simple de rebanado por ahora
            step = len(full_spectrum) // bands
            if step == 0: step = 1
            simplified_spectrum = full_spectrum[::step][:bands]
            
            return simplified_spectrum
            
        return np.zeros(64)

