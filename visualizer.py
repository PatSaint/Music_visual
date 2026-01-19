from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import math
import random

# Global state for engines
_gl_engine = None
_particles_state = None
_particles_colors = None

def draw_frame(audio_data, width, height, mode="Bars Spectrum", t=0.0):
    """
    Genera un frame visual basado en los datos de audio.
    Retorna un objeto PIL.Image
    """
    global _gl_engine
    
    # print(f"[DEBUG] Drawing {mode} at {width}x{height}") # Desmentado si detectamos fallos persistentes
    
    # Manejar modos GPU especiales primero
    gpu_modes = [
        "GPU Fractal", "Quantum Bloom", "Hyperwarp", "Neural Liquid",
        "Mandelbrot Trip", "Electric Storm", "DNA Helix", "Organic Cells",
        "Audio Matrix", "Infinity Mirrors", "Fire & Ice", 
        "Rainbow Flow", "Geometric Chaos"
    ]
    if mode in gpu_modes:
        if _gl_engine is None:
            try:
                from opengl_engine import (
                    OpenGLEngine, FRACTAL_FRAGMENT, BLOOM_FRAGMENT, 
                    HYPERWARP_FRAGMENT, LIQUID_FRAGMENT, MANDELBROT_FRAGMENT,
                    STORM_FRAGMENT, DNA_FRAGMENT, CELLS_FRAGMENT, 
                    MATRIX_FRAGMENT, MIRROR_FRAGMENT, 
                    FIREICE_FRAGMENT, RAINBOW_FRAGMENT,
                    CHAOS_FRAGMENT, VERTEX_DEFAULT
                )
                _gl_engine = OpenGLEngine(width, height)
                # Map names to fragments
                shaders = {
                    "GPU Fractal": FRACTAL_FRAGMENT, "Quantum Bloom": BLOOM_FRAGMENT,
                    "Hyperwarp": HYPERWARP_FRAGMENT, "Neural Liquid": LIQUID_FRAGMENT,
                    "Mandelbrot Trip": MANDELBROT_FRAGMENT, "Electric Storm": STORM_FRAGMENT,
                    "DNA Helix": DNA_FRAGMENT, "Organic Cells": CELLS_FRAGMENT,
                    "Audio Matrix": MATRIX_FRAGMENT, "Infinity Mirrors": MIRROR_FRAGMENT, 
                    "Fire & Ice": FIREICE_FRAGMENT, "Rainbow Flow": RAINBOW_FRAGMENT, 
                    "Geometric Chaos": CHAOS_FRAGMENT
                }
                _gl_engine.load_shader(VERTEX_DEFAULT, shaders.get(mode, FRACTAL_FRAGMENT))
            except Exception as e:
                print(f"Failed to load OpenGL Engine: {e}")
                return Image.new('RGB', (width, height), (20, 0, 0))
        
        # Detectar si el modo ha cambiado para recargar el shader
        current_shader_mode = getattr(_gl_engine, '_current_mode', None)
        if current_shader_mode != mode:
            from opengl_engine import (
                FRACTAL_FRAGMENT, BLOOM_FRAGMENT, HYPERWARP_FRAGMENT, 
                LIQUID_FRAGMENT, MANDELBROT_FRAGMENT, STORM_FRAGMENT, 
                DNA_FRAGMENT, CELLS_FRAGMENT, MATRIX_FRAGMENT, 
                MIRROR_FRAGMENT, FIREICE_FRAGMENT, RAINBOW_FRAGMENT, 
                CHAOS_FRAGMENT, VERTEX_DEFAULT
            )
            shaders = {
                "GPU Fractal": FRACTAL_FRAGMENT, "Quantum Bloom": BLOOM_FRAGMENT,
                "Hyperwarp": HYPERWARP_FRAGMENT, "Neural Liquid": LIQUID_FRAGMENT,
                "Mandelbrot Trip": MANDELBROT_FRAGMENT, "Electric Storm": STORM_FRAGMENT,
                "DNA Helix": DNA_FRAGMENT, "Organic Cells": CELLS_FRAGMENT,
                "Audio Matrix": MATRIX_FRAGMENT, "Infinity Mirrors": MIRROR_FRAGMENT, 
                "Fire & Ice": FIREICE_FRAGMENT, "Rainbow Flow": RAINBOW_FRAGMENT, 
                "Geometric Chaos": CHAOS_FRAGMENT
            }
            _gl_engine.load_shader(VERTEX_DEFAULT, shaders.get(mode, FRACTAL_FRAGMENT))
            _gl_engine._current_mode = mode

        # Update size if changed
        if _gl_engine.width != width or _gl_engine.height != height:
            _gl_engine.width = width
            _gl_engine.height = height
            
        return _gl_engine.render_frame(t, audio_data)

    # Crear fondo negro para modos CPU
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Manejar datos vacíos o ruido inicial
    if audio_data is None or len(audio_data) == 0:
        return img

    if mode == "Bars Spectrum":
        _draw_bars(draw, audio_data, width, height)
    elif mode == "Neon Tunnel":
        _draw_tunnel(draw, img, audio_data, width, height)
    elif mode == "Waveform":
        _draw_waveform(draw, audio_data, width, height)
    elif mode == "Circle Pulse":
        _draw_circle_pulse(draw, audio_data, width, height)
    elif mode == "Kaleidoscope":
        return _draw_kaleidoscope(audio_data, width, height, t)
    elif mode == "Plasma Fluid":
        return _draw_plasma(audio_data, width, height, t)
    elif mode == "Cosmic Particles":
        _draw_particles(draw, audio_data, width, height)
    else:
        _draw_bars(draw, audio_data, width, height)

    return img

def _draw_bars(draw, data, w, h):
    """Dibuja barras verticales clásicas"""
    num_bars = len(data)
    bar_width = w / num_bars
    
    for i, amp in enumerate(data):
        # amp está entre 0 y 1
        bar_height = int(amp * h * 0.8) # 80% de la altura máxima
        
        # Coordenadas
        x1 = i * bar_width
        y1 = h - bar_height
        x2 = x1 + bar_width - 2 # Separación de 2px
        y2 = h
        
        # Color degradado basado en altura (Verde -> Amarillo -> Rojo)
        color = (0, 255, 0)
        if amp > 0.5: color = (255, 255, 0)
        if amp > 0.8: color = (255, 0, 0)
        
        draw.rectangle([x1, y1, x2, y2], fill=color)

def _draw_tunnel(draw, img, data, w, h):
    """Simula un tunel neón usando rectángulos concéntricos"""
    center_x, center_y = w // 2, h // 2
    
    # Usar el promedio de bajos para el "golpe" del tunel
    bass_energy = np.mean(data[:10]) if len(data) > 10 else 0
    
    # Dibujar varios cuadros concéntricos
    num_squares = 10
    max_size = min(w, h)
    
    for i in range(num_squares):
        factor = (i + 1) / num_squares
        # El bass_energy afecta la separación o tamaño
        current_size = max_size * factor * (0.8 + bass_energy * 0.4)
        
        half = current_size / 2
        x1 = center_x - half
        y1 = center_y - half
        x2 = center_x + half
        y2 = center_y + half
        
        # Color neón cian/rosa alternado
        color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
        
        # Grosor varía con la energía
        width_line = int(2 + bass_energy * 5)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width_line)

def _draw_waveform(draw, data, w, h):
    """Dibuja una línea conectando puntos"""
    points = []
    num_points = len(data)
    step_x = w / num_points
    
    center_y = h / 2
    
    for i, amp in enumerate(data):
        x = i * step_x
        # La amplitud mueve el punto arriba y abajo desde el centro
        offset = amp * (h / 3) 
        # Alternar signo para simular onda si los datos son solo magnitud FFT (siempre positivos)
        # Esto es un truco visual
        direction = 1 if i % 2 == 0 else -1 
        y = center_y + (offset * direction)
        points.append((x, y))
        
    draw.line(points, fill=(0, 150, 255), width=3)

def _draw_circle_pulse(draw, data, w, h):
    """Un círculo central que late"""
    bass = np.mean(data[:5]) # Solo sub-bajos
    center_x, center_y = w // 2, h // 2
    
    radius = 50 + (bass * 150) # Radio base 50 + hasta 150px extra
    
    # Dibujar circulo relleno semitransparente (simulado con color oscuro)
    color_fill = (int(bass*50), 0, int(bass*100)) # Púrpura oscuro
    
    x1 = center_x - radius
    y1 = center_y - radius
    x2 = center_x + radius
    y2 = center_y + radius
    
    draw.ellipse([x1, y1, x2, y2], fill=color_fill, outline=(255, 255, 255), width=2)

# --- ADVANCED NUMPY VISUALIZERS ---

def _draw_kaleidoscope(data, w, h, t):
    """
    Uses numpy to generate a radial spectrum effect.
    Optimized: Calculates at lower resolution and downscales to improve FPS.
    """
    # Optimization: Render at lower resolution
    scale = 2 # Improved from 4 to 2 for better quality
    sw, sh = max(50, w // scale), max(50, h // scale)
    
    # Create coordinate grid
    x = np.linspace(-1, 1, sw)
    y = np.linspace(-1, 1, sh)
    X, Y = np.meshgrid(x, y)
    
    # Polar coordinates
    R = np.sqrt(X**2 + Y**2)
    Angle = np.arctan2(Y, X)
    
    # Bass influence
    bass = np.mean(data[:5]) * 2.0
    
    # Pattern generation
    # Create a rotating pattern based on angle, time, and radius
    # Speed up: t * 3 instead of t
    pattern = np.sin(Angle * 6 + t * 2) + np.cos(R * 10 - t * 4)
    
    # Modulate with audio
    # Map audio data to rings
    # We resize data to match R resolution roughly or just pick values based on R
    idx = (R * len(data)).astype(int) % len(data)
    audio_val = data[idx] # This broadcasts
    
    # Combine
    # Boost contrast and sensitivity
    intensity = (pattern * 0.5 + 0.5) * audio_val * 255 * (1 + bass * 3)
    
    # Color mapping (Psychedelic)
    # More vivid colors, faster cycling
    red = (np.sin(R * 5 + t * 2) * 127 + 128) * audio_val
    green = (np.cos(Angle * 3 - t * 3) * 127 + 128) * audio_val
    blue = intensity
    
    # Stack and convert
    rgb = np.dstack((red, green, blue)).astype(np.uint8)
    img = Image.fromarray(rgb)
    
    return img.resize((w, h), Image.Resampling.LANCZOS)

def _draw_plasma(data, w, h, t):
    """
    Vectorized plasma fluid effect.
    """
    # Downscale for performance, then upscale
    scale = 4
    sw, sh = w // scale, h // scale
    
    x = np.linspace(0, 4 * np.pi, sw)
    y = np.linspace(0, 4 * np.pi, sh)
    X, Y = np.meshgrid(x, y)
    
    bass = np.mean(data[:10])
    mid = np.mean(data[10:30])
    
    # Fluid math: sum of sines interacting
    # Speed up: t * 3
    t_fast = t * 3
    v1 = np.sin(X + t_fast)
    v2 = np.sin(Y + t_fast)
    v3 = np.sin((X + Y) + t_fast)
    v4 = np.sin(np.sqrt(X**2 + Y**2) + t_fast * 2)
    
    val = (v1 + v2 + v3 + v4)
    
    # Map execution to color
    # shift color based on audio
    c_shift = bass * 10 # More shift
    
    r = np.sin(val * np.pi + c_shift) * 127 + 128
    g = np.cos(val * np.pi + t_fast) * 127 + 128
    b = np.sin(val * np.pi - c_shift) * 127 + 128
    
    rgb = np.dstack((r, g, b)).astype(np.uint8) 
    
    img = Image.fromarray(rgb)
    
    # Upscale nicely
    return img.resize((w, h), Image.Resampling.BILINEAR)

def _draw_particles(draw, data, w, h):
    """
    Starfield like effect.
    """
    global _particles_state, _particles_colors
    
    num_particles = 200
    
    # Initialize if needed
    if _particles_state is None or len(_particles_state) != num_particles:
        # x, y, speed, size
        _particles_state = np.random.rand(num_particles, 4)
        _particles_state[:, 0] *= w # x
        _particles_state[:, 1] *= h # y
        _particles_state[:, 2] = np.random.rand(num_particles) * 5 + 2 # speed (faster base)
        _particles_state[:, 3] = np.random.rand(num_particles) * 3 + 1 # size
        
        # Colors (R, G, B) normalized 0-1
        _particles_colors = np.random.rand(num_particles, 3)

    bass = np.mean(data[:5])
    # MUCH faster on bass
    speed_factor = 1 + (bass * 50) 
    
    # Update positions
    # Move X
    _particles_state[:, 0] -= _particles_state[:, 2] * speed_factor
    
    # Reset if out of bounds (left side)
    reset_mask = _particles_state[:, 0] < 0
    _particles_state[reset_mask, 0] = w
    _particles_state[reset_mask, 1] = np.random.rand(np.sum(reset_mask)) * h
    
    # Draw
    # We iterate here because PIL draw primitive is faster for sparse dots than constructing huge array
    for i, p in enumerate(_particles_state):
        x, y, _, size = p
        # Size reacts to audio too
        s = size * (1 + bass * 5)
        
        # Color processing
        # Base color + brightness boost from bass
        c_r, c_g, c_b = _particles_colors[i]
        
        # Brightness boost
        boost = 1 + bass * 2
        final_color = (
            min(255, int(c_r * 255 * boost)),
            min(255, int(c_g * 255 * boost)),
            min(255, int(c_b * 255 * boost))
        )
        
        draw.ellipse([x, y, x+s, y+s], fill=final_color)


def _draw_manim_placeholder(w, h):
    """Draws a placeholder text for Manim mode."""
    img = Image.new('RGB', (w, h), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    text = "MANIM RENDERER SELECTED"
    subtext = "Live Preview Unavailable -- Click 'EXPORT VIDEO' to Render"
    
    cx, cy = w // 2, h // 2
    
    # Draw simple crosshair
    draw.line([0, cy, w, cy], fill=(50, 50, 50))
    draw.line([cx, 0, cx, h], fill=(50, 50, 50))
    
    # Simple default font
    draw.text((cx - 75, cy - 20), text, fill=(255, 255, 255))
    draw.text((cx - 120, cy + 10), subtext, fill=(150, 150, 150))
    
    return img
