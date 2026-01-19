import json
import os

class ConfigManager:
    """Gestiona la persistencia de configuración de la aplicación."""
    
    def __init__(self, config_file="app_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Carga la configuración desde el archivo JSON."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[CONFIG] Error al cargar configuración: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def save_config(self):
        """Guarda la configuración actual al archivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"[CONFIG] Configuración guardada en {self.config_file}")
        except Exception as e:
            print(f"[CONFIG] Error al guardar configuración: {e}")
    
    def get_default_config(self):
        """Retorna la configuración por defecto."""
        return {
            "random_pool": [],
            "last_music_folder": "",
            "export_settings": {
                "resolution": "1920x1080 (HD)",
                "fps": 60,
                "folder": os.getcwd()
            }
        }
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Establece un valor de configuración y guarda automáticamente."""
        self.config[key] = value
        self.save_config()
    
    def update_export_settings(self, settings):
        """Actualiza la configuración de exportación."""
        self.config["export_settings"] = settings
        self.save_config()
