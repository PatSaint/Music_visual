import customtkinter as ctk

class RandomConfigDialog(ctk.CTkToplevel):
    """Dialog para configurar qué visualizadores incluir en la rotación automática."""
    def __init__(self, parent, all_visualizers, current_selection, on_save):
        super().__init__(parent)
        self.title("Auto-Random Configuration")
        self.geometry("450x620")
        self.resizable(False, False)
        self.on_save = on_save
        self.attributes("-topmost", True)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="🎲 Auto-Random Configuration", 
                     font=("Roboto", 18, "bold"),
                     text_color="#00E5FF").pack(pady=15)
        
        # Descripción
        desc_frame = ctk.CTkFrame(self, fg_color="transparent")
        desc_frame.pack(padx=20, pady=(0, 10))
        
        ctk.CTkLabel(desc_frame, 
                     text="Select which visualizers to include in the rotation pool:",
                     font=("Roboto", 11), 
                     text_color="#AAAAAA").pack()
        
        # Separador
        ctk.CTkFrame(self, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=10)
        
        # Scrollable frame para los checkboxes
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            width=380, 
            height=280,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333"
        )
        self.scroll_frame.pack(pady=10, padx=20)
        
        self.checkboxes = {}
        for viz in all_visualizers:
            var = ctk.BooleanVar(value=(viz in current_selection))
            cb = ctk.CTkCheckBox(
                self.scroll_frame, 
                text=viz, 
                variable=var,
                font=("Roboto", 12),
                fg_color="#6200EA",
                hover_color="#651FFF",
                border_color="#555555"
            )
            cb.pack(anchor="w", pady=4, padx=15)
            self.checkboxes[viz] = var
        
        # Separador
        ctk.CTkFrame(self, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=15)
        
        # Botones de selección rápida
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(pady=(0, 15))
        
        ctk.CTkLabel(quick_frame, text="Quick Select:", 
                     font=("Roboto", 10, "bold"),
                     text_color="#888888").grid(row=0, column=0, padx=10)
        
        btn_all = ctk.CTkButton(
            quick_frame, 
            text="✓ All", 
            width=90,
            height=28,
            fg_color="#444444",
            hover_color="#555555",
            font=("Roboto", 11),
            command=self.select_all
        )
        btn_all.grid(row=0, column=1, padx=5)
        
        btn_none = ctk.CTkButton(
            quick_frame, 
            text="✗ None", 
            width=90,
            height=28,
            fg_color="#444444",
            hover_color="#555555",
            font=("Roboto", 11),
            command=self.clear_all
        )
        btn_none.grid(row=0, column=2, padx=5)
        
        # Botones de acción principal
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=(5, 20))
        
        btn_cancel = ctk.CTkButton(
            action_frame, 
            text="CANCEL",
            width=140,
            height=45,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            border_width=1,
            border_color="#555555",
            font=("Roboto", 13),
            command=self.destroy
        )
        btn_cancel.grid(row=0, column=0, padx=10)
        
        btn_save = ctk.CTkButton(
            action_frame, 
            text="✓ ACCEPT & SAVE",
            width=200,
            height=45,
            fg_color="#00C853",
            hover_color="#00E676",
            font=("Roboto", 14, "bold"),
            command=self.save_config
        )
        btn_save.grid(row=0, column=1, padx=10)
    
    def select_all(self):
        for var in self.checkboxes.values():
            var.set(True)
    
    def clear_all(self):
        for var in self.checkboxes.values():
            var.set(False)
    
    def save_config(self):
        selected = [viz for viz, var in self.checkboxes.items() if var.get()]
        self.destroy()
        self.on_save(selected)
