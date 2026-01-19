import customtkinter as ctk
import os
import random
from ui_components import create_control_panel, ExportDialog, toggle_inputs
from random_config_dialog import RandomConfigDialog
from config_manager import ConfigManager
from audio_engine import AudioEngine
import visualizer
import exporter
import threading
import time
import queue
from PIL import Image

# ... (Configuración inicial igual) ...

class MusicVisualizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ... (Configuración ventana igual) ...
        self.title("Music Visualizer - DJ Edition")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Iniciar Motor de Audio
        self.engine = AudioEngine()
        self.current_viz_mode = "Bars Spectrum"
        self.app_start_time = time.time()
        
        # Variables de Estado de Exportación
        self.last_export_settings = {} # Persistencia
        self.is_exporting = False
        self.cancel_export_flag = False
        
        # Variables de Auto-Random Rotation
        self.auto_random_enabled = False
        self.random_pool = []  # Visualizadores seleccionados para rotación
        self.random_timer_id = None
        self.all_visualizers = [
            "Bars Spectrum", "Waveform", "Neon Tunnel", "Circle Pulse", 
            "Kaleidoscope", "Plasma Fluid", "Cosmic Particles", "GPU Fractal", 
            "Quantum Bloom", "Hyperwarp", "Neural Liquid", 
            "Mandelbrot Trip", "Electric Storm", "DNA Helix", "Organic Cells",
            "Audio Matrix", "Infinity Mirrors", "Fire & Ice", 
            "Rainbow Flow", "Geometric Chaos"
        ]
        
        # Sistema de configuración persistente
        self.config_manager = ConfigManager()
        self.current_folder = self.config_manager.get("last_music_folder", "")
        self.random_pool = self.config_manager.get("random_pool", [])
        self.last_export_settings = self.config_manager.get("export_settings", {})
        
        # Canal seguro para renderizado OpenGL desde hilos secundarios
        self.gl_render_queue = queue.Queue(maxsize=1)
        
        # Configurar Grid
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_columnconfigure(0, weight=1)

        # --- ÁREA DE VISUALIZACIÓN ---
        self.visualizer_frame = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.visualizer_frame.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_viz = ctk.CTkLabel(self.visualizer_frame, text="")
        self.lbl_viz.place(relx=0.5, rely=0.5, anchor="center")
        
        # Barra de Progreso (Oculta por defecto)
        self.progress_bar = ctk.CTkProgressBar(self.visualizer_frame, width=400, mode="determinate")
        self.progress_bar.set(0)
        # No la mostramos aun (place/pack)
        
        self.current_image = None

        # --- PANEL DE CONTROL ---
        self.ui_elements = create_control_panel(
            self,
            load_callback=self.load_music,
            play_callback=self.play_music,
            pause_callback=self.pause_music,
            stop_callback=self.stop_music,
            export_callback=self.export_video, # Ahora actúa como Exportar/Cancelar
            visualization_callback=self.change_visualization
        )
        
        # Conectar callbacks de Auto-Random
        self.ui_elements["btn_config_random"].configure(command=self.open_random_config)
        self.ui_elements["btn_auto_random"].configure(command=self.toggle_auto_random)

        # Iniciar bucles de fondo
        self.after(33, self.update_visuals)
        self.after(10, self.process_gl_queue) # Mas frecuente para evitar lag

        # Definir estado inicial de botones
        self.set_game_buttons_state("disabled")
        
        # Auto-cargar última carpeta si existe
        if self.current_folder and os.path.exists(self.current_folder):
            self.after(500, self.refresh_library)  # Pequeño delay para que la UI se renderice primero

    def set_game_buttons_state(self, state):
        self.ui_elements["btn_play"].configure(state=state)
        self.ui_elements["btn_pause"].configure(state=state)
        self.ui_elements["btn_stop"].configure(state=state)
        self.ui_elements["btn_export"].configure(state=state)

    def on_track_ready(self):
        print(f"[DEBUG] on_track_ready. State: loaded={self.engine.is_loaded}")
        self.ui_elements["lbl_status"].configure(text="READY TO PLAY")
        self.set_game_buttons_state("normal")


    def update_visuals(self):
        """Bucle de actualización de la interfaz y visualizadores."""
        if self.is_exporting:
            self.update_idletasks()
            self.after(100, self.update_visuals)
            return

        w = self.visualizer_frame.winfo_width()
        h = self.visualizer_frame.winfo_height()
        if w < 10 or h < 10: w, h = 800, 400
        
        data = self.engine.get_audio_data()
        elapsed = time.time() - self.app_start_time
        pil_image = visualizer.draw_frame(data, w, h, mode=self.current_viz_mode, t=elapsed)
        self.current_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(w, h))
        self.lbl_viz.configure(image=self.current_image)
        
        if self.engine.is_loaded and self.ui_elements["lbl_status"].cget("text") == "ANALYZING...":
             self.ui_elements["lbl_status"].configure(text="READY TO PLAY")

        self.after(33, self.update_visuals)

    def process_gl_queue(self):
        """Atiende peticiones de renderizado GPU desde el hilo de exportación."""
        try:
            while not self.gl_render_queue.empty():
                try:
                    req = self.gl_render_queue.get_nowait()
                    data, w, h, mode, t, event, container = req
                    container['img'] = visualizer.draw_frame(data, w, h, mode, t)
                    event.set()
                except queue.Empty:
                    break
        except Exception as e:
            print(f"GL Proxy Error: {e}")
        self.after(5, self.process_gl_queue)


    # Callbacks simplificados para brevedad en parche, mantener lógica original
    def load_music(self):
        """Callback para el botón SELECT FOLDER."""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(initialdir=self.current_folder if self.current_folder else None)
        if folder_path:
            self.current_folder = folder_path
            self.config_manager.set("last_music_folder", folder_path)
            self.refresh_library()

    def refresh_library(self):
        """Escanea la carpeta actual y puebla la lista de canciones."""
        # Limpiar lista actual
        for widget in self.ui_elements["song_list_frame"].winfo_children():
            widget.destroy()
        
        files = [f for f in os.listdir(self.current_folder) if f.lower().endswith(('.mp3', '.wav'))]
        
        if not files:
            lbl = ctk.CTkLabel(self.ui_elements["song_list_frame"], text="No audio files found", font=("Roboto", 10))
            lbl.pack(pady=10)
            return

        for filename in files:
            btn = ctk.CTkButton(
                self.ui_elements["song_list_frame"], 
                text=filename,
                anchor="w",
                fg_color="transparent",
                hover_color="#2b2b2b",
                text_color="#AAAAAA",
                height=25,
                font=("Roboto", 11),
                command=lambda f=filename: self.load_selected_track(f)
            )
            btn.pack(fill="x", padx=2, pady=1)

    def load_selected_track(self, filename):
        """Carga la pista seleccionada de la lista."""
        file_path = os.path.join(self.current_folder, filename)
        
        # Bloquear controles mientras carga
        self.ui_elements["lbl_status"].configure(text="LOADING & ANALYZING...")
        self.set_game_buttons_state("disabled")
        
        # UI Feedback
        self.ui_elements["lbl_file"].configure(text=f"Selected: {filename}")
        
        # Thread safe callback
        safe_callback = lambda: self.after(0, self.on_track_ready)
        self.engine.load_track(file_path, callback_ready=safe_callback)

    def play_music(self): 
        print(f"[DEBUG] Play button clicked. Engine state: loaded={self.engine.is_loaded}, playing={self.engine.is_playing}, paused={self.engine.is_paused}")
        if not self.engine.is_loaded:
            self.ui_elements["lbl_status"].configure(text="NO TRACK LOADED!")
            return
        
        try:
            self.engine.play()
            self.ui_elements["lbl_status"].configure(text="PLAYING")
            print("[DEBUG] self.engine.play() executed successfully")
        except Exception as e:
            print(f"[ERROR] Error in play_music: {e}")
            self.ui_elements["lbl_status"].configure(text="PLAY ERROR")

    def pause_music(self): 
        if not self.engine.is_loaded: return
        self.engine.pause()
        self.ui_elements["lbl_status"].configure(text="PAUSED")

    def stop_music(self): 
        if not self.engine.is_loaded: return
        self.engine.stop()
        self.ui_elements["lbl_status"].configure(text="STOPPED")

    def change_visualization(self, v): self.current_viz_mode = v

    # --- AUTO-RANDOM ROTATION METHODS ---
    def open_random_config(self):
        """Abre el diálogo de configuración de rotación aleatoria."""
        RandomConfigDialog(
            self,
            all_visualizers=self.all_visualizers,
            current_selection=self.random_pool,
            on_save=self.save_random_config
        )
    
    def save_random_config(self, selected_visualizers):
        """Guarda la configuración de visualizadores seleccionados."""
        self.random_pool = selected_visualizers
        self.config_manager.set("random_pool", selected_visualizers)
        print(f"[RANDOM] Pool configurado con {len(selected_visualizers)} visualizadores")
    
    def toggle_auto_random(self):
        """Activa/desactiva el modo de rotación automática."""
        self.auto_random_enabled = not self.auto_random_enabled
        
        if self.auto_random_enabled:
            if not self.random_pool:
                # Si no hay pool configurado, usar todos
                self.random_pool = self.all_visualizers.copy()
            
            self.ui_elements["btn_auto_random"].configure(
                text="🎲 AUTO RANDOM: ON",
                fg_color="#00C853",
                hover_color="#009624"
            )
            print("[RANDOM] Modo AUTO RANDOM activado")
            self.schedule_next_random()
        else:
            self.ui_elements["btn_auto_random"].configure(
                text="🎲 AUTO RANDOM: OFF",
                fg_color="#555555",
                hover_color="#666666"
            )
            if self.random_timer_id:
                self.after_cancel(self.random_timer_id)
                self.random_timer_id = None
            print("[RANDOM] Modo AUTO RANDOM desactivado")
    
    def schedule_next_random(self):
        """Programa el siguiente cambio aleatorio de visualizador."""
        if not self.auto_random_enabled:
            return
        
        # Intervalo aleatorio entre 5 y 10 segundos
        interval_ms = random.randint(5000, 10000)
        
        self.random_timer_id = self.after(interval_ms, self.execute_random_change)
        print(f"[RANDOM] Próximo cambio en {interval_ms/1000:.1f} segundos")
    
    def execute_random_change(self):
        """Ejecuta el cambio aleatorio de visualizador."""
        if not self.auto_random_enabled or not self.random_pool:
            return
        
        # Elegir un visualizador aleatorio del pool
        next_viz = random.choice(self.random_pool)
        
        # Evitar repetir el mismo visualizador
        if next_viz == self.current_viz_mode and len(self.random_pool) > 1:
            # Intentar otro
            available = [v for v in self.random_pool if v != self.current_viz_mode]
            next_viz = random.choice(available)
        
        print(f"[RANDOM] Cambiando a: {next_viz}")
        self.change_visualization(next_viz)
        
        # Programar el siguiente cambio
        self.schedule_next_random()

    # --- LÓGICA DE EXPORTACIÓN FINAL ---
    def export_video(self):
        # Si YA está exportando, este botón funciona como CANCELAR
        if self.is_exporting:
            self.cancel_export_flag = True
            
            self.ui_elements["lbl_status"].configure(text="CANCELLING...")
            return

        if not self.engine.is_loaded:
            self.ui_elements["lbl_status"].configure(text="NO TRACK TO EXPORT!")
            return

        print("EXPORT presionado")
        self.engine.pause() 
        self.ui_elements["lbl_status"].configure(text="CONFIGURING EXPORT...")
        
        # Abrir diálogo pasando settings previos
        print(f"[DEBUG] Abriendo ExportDialog con settings: {self.last_export_settings}")
        try:
            ExportDialog(self, initial_settings=self.last_export_settings, on_export_start=self.start_export_process)
        except Exception as e:
            print(f"[ERROR] Error al abrir ExportDialog: {e}")
            import traceback
            traceback.print_exc()

    def start_export_process(self, width, height, fps, folder, settings):
        # Guardar settings para la próxima
        self.last_export_settings = settings
        self.config_manager.update_export_settings(settings)
        
        use_random = settings.get("use_random", False)
        print(f"Iniciando exportación: {width}x{height} a {fps} FPS en {folder}")
        if use_random:
            print(f"[EXPORT] Modo AUTO RANDOM activado - Pool: {len(self.random_pool)} visualizadores")
        
        # IMPORTANTE: Desactivar AUTO RANDOM en la UI para evitar conflictos de OpenGL
        if self.auto_random_enabled:
            print("[EXPORT] Desactivando AUTO RANDOM de la UI durante exportación")
            self.toggle_auto_random()  # Apagar el modo random de la UI
        
        # Bloquear UI
        self.is_exporting = True
        self.cancel_export_flag = False
        toggle_inputs(self.ui_elements, enabled=False)
        
        # Cambiar botón Export a Cancelar
        self.ui_elements["btn_export"].configure(text="CANCEL RENDER", fg_color="#D50000", hover_color="#B71C1C")
        
        # Mostrar barra progreso
        self.progress_bar.place(relx=0.5, rely=0.8, anchor="center")
        self.progress_bar.set(0)
        self.ui_elements["lbl_status"].configure(text="RENDERING... 0%")
        
        # Tracking de tiempo
        self.export_start_time = time.time()
        
        # Ruta salida con auto-incremento
        base_name = os.path.splitext(os.path.basename(self.engine.current_file))[0]
        filename = f"{base_name}_visualizer.mp4"
        output_path = self.get_unique_path(folder, filename)
        
        # Hilo
        threading.Thread(target=self._run_export_thread, 
                        args=(output_path, width, height, fps, self.current_viz_mode, use_random)).start()

    def get_unique_path(self, folder, filename):
        """Si el archivo existe, agrega (1), (2), etc."""
        base, ext = os.path.splitext(filename)
        counter = 1
        final_path = os.path.join(folder, filename)
        while os.path.exists(final_path):
            final_path = os.path.join(folder, f"{base}_{counter}{ext}")
            counter += 1
        return final_path

    def _run_export_thread(self, output_file, width, height, fps, viz_mode, use_random=False):
        import exporter
        
        # Lista de visualizadores que usan GPU/OpenGL
        gpu_modes = [
            "GPU Fractal", "Quantum Bloom", "Hyperwarp", "Neural Liquid",
            "Mandelbrot Trip", "Electric Storm", "DNA Helix", "Organic Cells",
            "Audio Matrix", "Infinity Mirrors", "Fire & Ice", "Rainbow Flow",
            "Geometric Chaos"
        ]
        
        # Wrapper para delegar renderizado al hilo principal si es GPU
        def safe_draw(data, w, h, mode, t):
            # Si el modo usa GPU, delegar al hilo principal
            if mode in gpu_modes:
                event = threading.Event()
                container = {}
                # Postear solicitud
                self.gl_render_queue.put((data, w, h, mode, t, event, container))
                # Esperar a que el hilo principal (process_gl_queue) lo procese
                if not event.wait(timeout=10.0): # Timeout aumentado
                    print(f"GL Render Timeout for mode: {mode}")
                    return Image.new('RGB', (w, h), (0,0,0))
                return container.get('img')
            else:
                return visualizer.draw_frame(data, w, h, mode, t)

        try:
            # === STANDARD MOVIEPY PIPELINE ===
            exporter.render_video(
                self.engine, 
                output_file, 
                width, 
                height, 
                fps, 
                viz_mode=viz_mode,
                progress_callback=self._update_progress_from_thread,
                cancel_check_func=lambda: self.cancel_export_flag,
                draw_func=safe_draw,
                use_random=use_random,
                random_pool=self.random_pool if use_random else None
            )
            self.after(0, self._export_finished, True)

        except Exception as e:
            print(f"Export failed/cancelled: {e}")
            self.after(0, self._export_finished, False)

    def _update_progress_from_thread(self, percentage):
        # Actualizar UI desde hilo principal usando after o directamente si tkinter es thread-safe (a veces lo es para configure)
        # Lo seguro es usar after, pero para progreso simple a veces funciona directo.
        # Haremos un wrapper seguro
        self.after(0, lambda: self._set_progress(percentage))

    def _set_progress(self, percentage):
        self.progress_bar.set(percentage / 100)
        
        # Calculo de ETA
        elapsed = time.time() - self.export_start_time
        if percentage > 0:
            total_estimated = elapsed * (100 / percentage)
            remaining = total_estimated - elapsed
            # Formato MM:SS
            m, s = divmod(int(remaining), 60)
            eta_str = f"{m:02d}:{s:02d}"
        else:
            eta_str = "--:--"
            
        self.ui_elements["lbl_status"].configure(text=f"RENDERING... {int(percentage)}% (ETA: {eta_str})")


    def _export_finished(self, success):
        self.is_exporting = False
        
        # Restaurar UI
        toggle_inputs(self.ui_elements, enabled=True)
        self.ui_elements["btn_export"].configure(text="EXPORT VIDEO", fg_color="#6200EA", hover_color="#651FFF")
        
        # Ocultar barra
        self.progress_bar.place_forget()
        
        if success:
            self.ui_elements["lbl_status"].configure(text="EXPORT COMPLETE!")
            # Opcional: Abrir carpeta
            # os.startfile(os.path.dirname(output_file))
        else:
            if self.cancel_export_flag:
                self.ui_elements["lbl_status"].configure(text="EXPORT CANCELLED")
            else:
                self.ui_elements["lbl_status"].configure(text="EXPORT ERROR")

if __name__ == "__main__":
    app = MusicVisualizerApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.engine.stop()

