# ui_components.py
# Este módulo contendrá los componentes de la interfaz de usuario (Botones, Sliders, Panel de Control).

import customtkinter as ctk
import os

def create_control_panel(parent, load_callback, play_callback, pause_callback, stop_callback, export_callback, visualization_callback):
    """
    Crea el panel de control estilo DJ en la parte inferior.
    Divide el área en 3 'Decks' o secciones.
    """
    # Frame principal del panel de control
    control_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1a1a1a") # Color de fondo oscuro para el panel
    control_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
    
    # Configurar columnas del panel (Izquierda, Centro, Derecha)
    control_frame.grid_columnconfigure(0, weight=1) # Deck Izquierdo (Carga)
    control_frame.grid_columnconfigure(1, weight=2) # Deck Central (Transporte)
    control_frame.grid_columnconfigure(2, weight=1) # Deck Derecho (Export y FX)

    # --- DECK IZQUIERDO: BIBLIOTECA ---
    left_deck = ctk.CTkFrame(control_frame, fg_color="transparent")
    left_deck.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    lbl_lib = ctk.CTkLabel(left_deck, text="LIBRARY", font=("Roboto", 12, "bold"))
    lbl_lib.pack(pady=(0, 5))
    
    btn_folder = ctk.CTkButton(left_deck, text="SELECT FOLDER 📂", command=load_callback, 
                               fg_color="#333333", hover_color="#444444", width=140)
    btn_folder.pack(pady=5)

    # Lista scrollable de canciones
    song_list_frame = ctk.CTkScrollableFrame(left_deck, width=180, height=120, 
                                             fg_color="#101010", label_text="Track List")
    song_list_frame.pack(pady=5, fill="both", expand=True)
    
    lbl_file = ctk.CTkLabel(left_deck, text="No Track Selected", text_color="gray", font=("Roboto", 10))
    lbl_file.pack(pady=(5, 0))

    # --- DECK CENTRAL: TRANSPORTE ---
    center_deck = ctk.CTkFrame(control_frame, fg_color="#2b2b2b", corner_radius=10) # Un poco más claro para resaltar
    center_deck.grid(row=0, column=1, padx=10, pady=10)
    
    # Botonera de reproducción
    btn_frame = ctk.CTkFrame(center_deck, fg_color="transparent")
    btn_frame.pack(pady=10)
    
    btn_play = ctk.CTkButton(btn_frame, text="▶", width=50, height=50, command=play_callback,
                             font=("Arial", 20), fg_color="#00C853", hover_color="#009624") # Verde neón
    btn_play.grid(row=0, column=1, padx=10)
    
    btn_pause = ctk.CTkButton(btn_frame, text="||", width=40, height=40, command=pause_callback,
                              font=("Arial", 16), fg_color="#FFD600", hover_color="#F57F17") # Amarillo
    btn_pause.grid(row=0, column=2, padx=5)

    btn_stop = ctk.CTkButton(btn_frame, text="■", width=40, height=40, command=stop_callback,
                             font=("Arial", 16), fg_color="#D50000", hover_color="#B71C1C") # Rojo
    btn_stop.grid(row=0, column=0, padx=5)

    # Label de estado/tiempo (placeholder)
    lbl_status = ctk.CTkLabel(center_deck, text="READY TO PLAY", font=("Consolas", 14), text_color="#00E5FF")
    lbl_status.pack(pady=(0, 10))

    # --- DECK DERECHO: EXPORT & FX ---
    right_deck = ctk.CTkFrame(control_frame, fg_color="transparent")
    right_deck.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    lbl_viz = ctk.CTkLabel(right_deck, text="VISUALIZATION MODE", font=("Roboto", 10, "bold"))
    lbl_viz.pack()
    
    viz_options = [
        "Bars Spectrum", "Waveform", "Neon Tunnel", "Circle Pulse", 
        "Kaleidoscope", "Plasma Fluid", "Cosmic Particles", "GPU Fractal", 
        "Quantum Bloom", "Hyperwarp", "Neural Liquid", 
        "Mandelbrot Trip", "Electric Storm", "DNA Helix", "Organic Cells",
        "Audio Matrix", "Infinity Mirrors", "Fire & Ice", 
        "Rainbow Flow", "Geometric Chaos"
    ]
    viz_menu = ctk.CTkOptionMenu(right_deck, values=viz_options, command=visualization_callback,
                                 fg_color="#555555", button_color="#444444")
    viz_menu.set(viz_options[0])
    viz_menu.pack(pady=5)
    
    # Separador visual
    ctk.CTkLabel(right_deck, text="─" * 20, text_color="#333333").pack(pady=5)
    
    # Botones de Auto-Random
    btn_config_random = ctk.CTkButton(right_deck, text="⚙️ CONFIGURE RANDOM",
                                     fg_color="#444444", hover_color="#555555",
                                     font=("Roboto", 10), height=28)
    btn_config_random.pack(pady=3)
    
    btn_auto_random = ctk.CTkButton(right_deck, text="🎲 AUTO RANDOM: OFF",
                                   fg_color="#555555", hover_color="#666666",
                                   font=("Roboto", 11, "bold"), height=32)
    btn_auto_random.pack(pady=5)
    
    btn_export = ctk.CTkButton(right_deck, text="EXPORT VIDEO",
                               command=export_callback,  # ¡Faltaba esto!
                               fg_color="#6200EA", hover_color="#651FFF",
                               font=("Roboto", 12, "bold"), height=35)
    btn_export.pack(pady=(10, 5))

    return {
        "lbl_file": lbl_file,
        "lbl_status": lbl_status,
        "viz_menu": viz_menu,
        "btn_folder": btn_folder,
        "song_list_frame": song_list_frame,
        "btn_play": btn_play,
        "btn_pause": btn_pause,
        "btn_stop": btn_stop,
        "btn_config_random": btn_config_random,
        "btn_auto_random": btn_auto_random,
        "btn_export": btn_export
    }

class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, initial_settings, on_export_start):
        super().__init__(parent)
        self.title("Export Configuration")
        self.geometry("450x550")  # Aumentado de 450 a 550 para el nuevo checkbox
        self.resizable(False, False)
        self.on_export_start = on_export_start
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Export Video Settings", font=("Roboto", 18, "bold")).pack(pady=20)

        # Resolution
        ctk.CTkLabel(self, text="Resolution & Orientation").pack()
        self.res_var = ctk.StringVar(value=initial_settings.get("resolution", "1920x1080 (HD)"))
        res_options = ["1920x1080 (HD)", "1280x720 (HD Ready)", "1080x1920 (Vertical/TikTok)", "1080x1080 (Square)"]
        self.res_menu = ctk.CTkOptionMenu(self, values=res_options, variable=self.res_var)
        self.res_menu.pack(pady=5)

        # FPS
        ctk.CTkLabel(self, text="Frame Rate (FPS)").pack(pady=(15, 0))
        self.fps_var = ctk.IntVar(value=initial_settings.get("fps", 60)) # Default 60
        self.slider_fps = ctk.CTkSlider(self, from_=24, to=120, number_of_steps=96, variable=self.fps_var) # Max 120
        self.slider_fps.pack(pady=5)
        self.lbl_fps_val = ctk.CTkLabel(self, text=f"{self.fps_var.get()} FPS")
        self.lbl_fps_val.pack()
        
        # Output Folder
        ctk.CTkLabel(self, text="Output Folder").pack(pady=(15, 0))
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(pady=5)
        
        self.folder_var = ctk.StringVar(value=initial_settings.get("folder", os.getcwd()))
        self.entry_folder = ctk.CTkEntry(folder_frame, textvariable=self.folder_var, width=250)
        self.entry_folder.grid(row=0, column=0, padx=5)
        
        btn_browse = ctk.CTkButton(folder_frame, text="Browse", width=60, command=self.browse_folder)
        btn_browse.grid(row=0, column=1, padx=5)

        # AUTO RANDOM Mode
        ctk.CTkLabel(self, text="Visualizer Mode", font=("Roboto", 11, "bold")).pack(pady=(15, 5))
        
        self.use_random_var = ctk.BooleanVar(value=initial_settings.get("use_random", False))
        self.cb_random = ctk.CTkCheckBox(
            self, 
            text="🎲 Use AUTO RANDOM rotation (changes every 5-10 sec)",
            variable=self.use_random_var,
            font=("Roboto", 12),
            fg_color="#6200EA",
            hover_color="#651FFF"
        )
        self.cb_random.pack(pady=5)

        # Start Button
        self.btn_start = ctk.CTkButton(self, text="START RENDER", width=200, height=40,
                                       fg_color="#6200EA", hover_color="#651FFF",
                                       command=self.start_export)
        self.btn_start.pack(pady=30)
        
        # Link slider label
        self.slider_fps.configure(command=self.update_fps_label)

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def update_fps_label(self, value):
        self.lbl_fps_val.configure(text=f"{int(value)} FPS")

    def start_export(self):
        res_str = self.res_var.get()
        # Parse resolution string "1920x1080 (HD)" -> (1920, 1080)
        res_part = res_str.split(" ")[0]
        w, h = map(int, res_part.split("x"))
        
        fps = int(self.fps_var.get())
        folder = self.folder_var.get()
        use_random = self.use_random_var.get()
        
        settings = {
            "resolution": res_str,
            "fps": fps,
            "folder": folder,
            "use_random": use_random
        }
        
        self.destroy()
        self.on_export_start(w, h, fps, folder, settings)

def toggle_inputs(ui_elements, enabled=True):
    """
    Habilita o deshabilita los controles de la UI.
    """
    state = "normal" if enabled else "disabled"
    
    # Lista de botones conocidos
    buttons = ["btn_load", "btn_play", "btn_pause", "btn_stop", "viz_menu"]
    
    for key in buttons:
        if key in ui_elements:
            try:
                ui_elements[key].configure(state=state)
            except:
                pass
    
    # btn_export lo manejamos aparte desde main si es necesario cambiarle el texto



