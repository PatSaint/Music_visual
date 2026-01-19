from moviepy import VideoClip, AudioFileClip
from proglog import ProgressBarLogger
import numpy as np
import visualizer
import os

class CancellableProgressBarLogger(ProgressBarLogger):
    def __init__(self, progress_callback, cancel_check_func):
        super().__init__()
        self.progress_notifier = progress_callback # Renamed to avoid using 'self.callback' which proglog uses for everything
        self.cancel_check_func = cancel_check_func

    def bars_callback(self, bar, attr, value, old_value=None):
        # Cada vez que moviepy actualiza la barra
        if self.cancel_check_func():
            raise Exception("Export cancelled by user")
            
        if self.progress_notifier and 'total' in self.bars[bar]:
            percentage = (value / self.bars[bar]['total']) * 100
            self.progress_notifier(percentage)

def render_video(audio_engine, output_filepath, width, height, fps, viz_mode, progress_callback=None, cancel_check_func=None, draw_func=None, use_random=False, random_pool=None):
    """
    Renderiza el video usando moviepy.
    Si use_random=True, cambia automáticamente de visualizador cada 5-10 segundos.
    """
    if not audio_engine.is_loaded or not audio_engine.current_file:
        print("Error: No audio loaded to export.")
        return

    # Usar function de dibujo personalizada o la por defecto
    current_draw_func = draw_func or visualizer.draw_frame

    print(f"Iniciando render: {width}x{height} @ {fps}FPS. Mode: {viz_mode}")
    if use_random:
        print(f"[EXPORT] AUTO RANDOM activado con pool de {len(random_pool) if random_pool else 0} visualizadores")
    
    duration = audio_engine.duration
    
    # Logger especial
    my_logger = CancellableProgressBarLogger(progress_callback, cancel_check_func or (lambda: False))
    
    # Variables para AUTO RANDOM
    if use_random:
        import random as rnd
        viz_pool = random_pool if random_pool else []
        if not viz_pool:
            print("[EXPORT WARNING] Pool vacío, usando visualizador fijo")
            use_random = False
        else:
            current_viz = rnd.choice(viz_pool)
            next_change_time = rnd.uniform(5.0, 10.0)
            print(f"[EXPORT RANDOM] Iniciando con: {current_viz}, próximo cambio en {next_change_time:.1f}s")
    else:
        current_viz = viz_mode
    
    # Función que genera el frame para el tiempo t
    def make_frame(t):
        nonlocal current_viz, next_change_time
        
        if cancel_check_func and cancel_check_func():
             raise Exception("Export cancelled by user")
        
        # AUTO RANDOM: verificar si es momento de cambiar
        if use_random and t >= next_change_time:
            available = [v for v in viz_pool if v != current_viz] if len(viz_pool) > 1 else viz_pool
            current_viz = rnd.choice(available)
            next_change_time = t + rnd.uniform(5.0, 10.0)
            print(f"[EXPORT RANDOM] t={t:.1f}s - Cambiando a: {current_viz}")
             
        # 1. Obtener datos de audio para el tiempo t
        data = audio_engine.get_audio_data(t=t)
        
        # 2. Dibujar frame con el visualizador actual
        pil_img = current_draw_func(data, width, height, mode=current_viz, t=t)
        
        # 3. Convertir a numpy array
        return np.array(pil_img)

    audio_clip = None
    video = None
    # Definir nombre de audio temporal para poder monitorearlo/limpiarlo
    # Usamos .m4a porque el codec es 'aac'
    temp_audio_path = output_filepath + ".temp_audio.m4a"

    try:
        audio_clip = AudioFileClip(audio_engine.current_file)
        video = VideoClip(make_frame, duration=duration)
        
        # Compatibilidad de versiones de moviepy (v1 vs v2)
        if hasattr(video, 'with_audio'):
            video = video.with_audio(audio_clip)
        else:
            video = video.set_audio(audio_clip)

        # Usamos nuestro logger custom
        video.write_videofile(
            output_filepath, 
            fps=fps, 
            codec='libx264', 
            audio_codec='aac', 
            logger=my_logger,
            temp_audiofile=temp_audio_path,
            remove_temp=True
        )
        
        print("Exportación finalizada exitosamente.")
        if progress_callback:
            progress_callback(100)
            
    except Exception as e:
        print(f"Render detenido/error: {e}")
        # Si falló/canceló, intentamos borrar el archivo de salida parcial si existe
        if os.path.exists(output_filepath) and os.path.getsize(output_filepath) < 1000:
             try: os.remove(output_filepath)
             except: pass
        raise e 
    finally:
        # CERRAR CLIPS para liberar archivos (Crucial en Windows)
        print("[DEBUG] Closing clips and cleaning temp files...")
        if video: 
            try: video.close()
            except: pass
        if audio_clip: 
            try: audio_clip.close()
            except: pass
            
        # Limpieza manual de refuerzo
        # Buscamos tanto mp3 como m4a para limpiar residuos de fallos anteriores
        for f in [temp_audio_path, output_filepath + ".temp_audio.mp3", output_filepath + ".temp"]:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    print(f"[DEBUG] Removed temp file: {f}")
                except Exception as ex: 
                    print(f"[DEBUG] Could not remove {f}: {ex}")


