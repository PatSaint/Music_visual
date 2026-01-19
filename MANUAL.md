# 📖 Manual de Usuario - Music Visualizer

## 🎯 Índice
1. [Instalación](#-instalación)
2. [Primer Uso](#-primer-uso)
3. [Interfaz de Usuario](#-interfaz-de-usuario)
4. [Uso Básico](#-uso-básico)
5. [Funciones Avanzadas](#-funciones-avanzadas)
6. [Exportación de Videos](#-exportación-de-videos)
7. [Solución de Problemas](#-solución-de-problemas)

---

## 🚀 Instalación

### Requisitos del Sistema
- **Python**: 3.10 o superior
- **GPU**: Compatible con OpenGL 3.3+ (para efectos GPU)
- **RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espacio**: ~500 MB para la aplicación + espacio para videos exportados

### Pasos de Instalación

#### 1. Descargar el Proyecto
```bash
git clone https://github.com/PatSaint/Music_visual.git
cd Music_visual
```

#### 2. Crear Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

Este comando instalará automáticamente:
- `pygame-ce` - Motor de audio y OpenGL
- `numpy` - Procesamiento numérico
- `Pillow` - Procesamiento de imágenes
- `librosa` - Análisis de audio
- `soundfile` - Lectura de archivos de audio
- `customtkinter` - Interfaz gráfica moderna
- `moviepy` - Exportación de videos
- `imageio-ffmpeg` - Manejo automático de FFmpeg (sin descargas manuales)
- `PyOpenGL` - Renderizado GPU
- `proglog` - Barras de progreso

#### 4. Ejecutar la Aplicación
```bash
python main.py
```

---

## 🎬 Primer Uso

### 1. Cargar Música
Al iniciar la aplicación:
1. Haz clic en **"SELECT FOLDER 📂"**
2. Navega a tu carpeta de música
3. Selecciona la carpeta y haz clic en "Seleccionar carpeta"
4. La lista de canciones aparecerá automáticamente

### 2. Seleccionar una Canción
- Haz clic en cualquier canción de la lista
- La aplicación analizará el audio automáticamente
- Verás "READY TO PLAY" cuando esté lista

### 3. Reproducir
- Haz clic en el botón verde **▶ PLAY**
- Disfruta de la visualización en tiempo real

---

## 🎨 Interfaz de Usuario

### Panel Izquierdo - Biblioteca de Música
- **SELECT FOLDER 📂**: Selecciona tu carpeta de música
- **Lista de canciones**: Scroll para ver todas tus canciones
- **Click en canción**: Carga y analiza la canción seleccionada

### Panel Central - Visualización
- Área principal donde se muestran los efectos visuales
- Se actualiza en tiempo real con la música
- 60+ FPS en GPUs modernas

### Panel Derecho - Controles

#### Información
- **Nombre del archivo**: Canción actualmente cargada
- **Estado**: READY, PLAYING, PAUSED, etc.

#### Controles de Reproducción
- **▶ PLAY**: Reproduce la música
- **⏸ PAUSE**: Pausa la reproducción
- **⏹ STOP**: Detiene completamente

#### Selector de Visualizador
- **Menú desplegable**: 20 visualizadores disponibles
- Cambia en tiempo real mientras reproduce

#### AUTO RANDOM
- **⚙️ CONFIGURE RANDOM**: Selecciona visualizadores para rotación
- **🎲 AUTO RANDOM**: Activa/desactiva rotación automática

#### Exportación
- **EXPORT VIDEO**: Abre el diálogo de exportación

---

## 🎮 Uso Básico

### Reproducir Música con Visualización

1. **Cargar carpeta de música**
   ```
   Click en "SELECT FOLDER 📂" → Selecciona carpeta
   ```

2. **Seleccionar canción**
   ```
   Click en cualquier canción de la lista
   ```

3. **Elegir visualizador**
   ```
   Menú desplegable → Selecciona uno de los 20 efectos
   ```

4. **Reproducir**
   ```
   Click en ▶ PLAY
   ```

### Cambiar Visualizador Durante Reproducción
- Simplemente selecciona otro del menú desplegable
- El cambio es instantáneo, sin interrumpir la música

### Pausar y Reanudar
- **PAUSE**: Pausa música y visualización
- **PLAY**: Reanuda desde donde pausaste
- **STOP**: Detiene y reinicia desde el inicio

---

## 🔥 Funciones Avanzadas

### AUTO RANDOM - Rotación Automática

#### Configurar Pool de Visualizadores
1. Click en **⚙️ CONFIGURE RANDOM**
2. Se abre un diálogo con todos los visualizadores
3. **Marca** los que quieres incluir en la rotación
4. Usa **"✓ All"** para seleccionar todos
5. Usa **"✗ None"** para deseleccionar todos
6. Click en **"✓ ACCEPT & SAVE"**

#### Activar Rotación Automática
1. Click en **🎲 AUTO RANDOM: OFF**
2. El botón cambia a verde: **🎲 AUTO RANDOM: ON**
3. Los visualizadores cambiarán cada 5-10 segundos (aleatorio)
4. Solo rotará entre los visualizadores que seleccionaste

#### Desactivar
- Click nuevamente en **🎲 AUTO RANDOM: ON**
- Vuelve a modo manual

### Persistencia de Configuración
La aplicación recuerda automáticamente:
- ✅ Última carpeta de música seleccionada
- ✅ Pool de visualizadores para AUTO RANDOM
- ✅ Configuración de exportación (resolución, FPS, carpeta)

Todo se guarda en `app_config.json`

---

## 🎬 Exportación de Videos

### Exportar Video Básico

1. **Preparar**
   - Carga una canción
   - Selecciona el visualizador que quieres

2. **Abrir diálogo**
   - Click en **EXPORT VIDEO**

3. **Configurar**
   - **Resolution**: Elige entre HD, Vertical (TikTok), Square
   - **FPS**: 24-120 (recomendado: 60)
   - **Output Folder**: Carpeta donde se guardará el video

4. **Exportar**
   - Click en **START RENDER**
   - Espera a que termine (puede tardar varios minutos)

### Exportar con AUTO RANDOM

1. **Configurar pool** (si no lo has hecho)
   - Click en **⚙️ CONFIGURE RANDOM**
   - Selecciona tus visualizadores favoritos
   - **ACCEPT & SAVE**

2. **Abrir exportación**
   - Click en **EXPORT VIDEO**

3. **Activar AUTO RANDOM**
   - ✅ Marca **"🎲 Use AUTO RANDOM rotation"**

4. **Configurar y exportar**
   - Selecciona resolución y FPS
   - **START RENDER**

El video resultante cambiará de visualizador cada 5-10 segundos, usando solo los que seleccionaste.

### Resoluciones Disponibles

| Resolución | Uso Recomendado |
|------------|-----------------|
| 1920x1080 (HD) | YouTube, pantalla completa |
| 1280x720 (HD Ready) | Archivos más pequeños |
| 1080x1920 (Vertical) | TikTok, Instagram Reels, Stories |
| 1080x1080 (Square) | Instagram Feed, Facebook |

### Cancelar Exportación
- Durante la exportación, el botón cambia a **"CANCEL RENDER"**
- Click para cancelar en cualquier momento

---

## 🎨 Guía de Visualizadores

### Visualizadores CPU (Rápidos)
- **Bars Spectrum**: Barras clásicas de frecuencia
- **Waveform**: Forma de onda de audio
- **Circle Pulse**: Pulso circular reactivo
- **Neon Tunnel**: Túnel 3D con luces neón
- **Kaleidoscope**: Patrones simétricos
- **Plasma Fluid**: Ondas de plasma suaves
- **Cosmic Particles**: Sistema de partículas

### Visualizadores GPU (Intensos)
- **🌀 Hyperwarp Tunnel**: Warp psicodélico extremo
- **🧬 DNA Helix**: Hélice de ADN 3D luminosa
- **⚡ Electric Storm**: Tormentas con rayos procedurales
- **🔮 Mandelbrot Trip**: Zoom fractal suave
- **🎲 Geometric Chaos**: Formas 3D morfantes
- **🌈 Rainbow Flow**: Fluidos hiper-vibrantes
- **🔥 Fire & Ice**: Choque elemental
- **🪞 Infinity Mirrors**: Geometría caleidoscópica
- **💎 Quantum Bloom**: Efectos de bloom de partículas
- **🌊 Neural Liquid**: Simulación líquida orgánica
- **📊 Audio Matrix**: Lluvia digital estilo Matrix
- **🦠 Organic Cells**: Autómatas celulares

---

## 🔧 Solución de Problemas

### La aplicación no inicia
```bash
# Verificar versión de Python
python --version  # Debe ser 3.10+

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de OpenGL
- **Problema**: GPU no compatible
- **Solución**: Actualiza drivers de tu tarjeta gráfica
- **Alternativa**: Usa solo visualizadores CPU (primeros 7)

### Audio no se reproduce
```bash
# Verificar que librosa esté instalado
pip install librosa soundfile --upgrade
```

### Exportación muy lenta
- **Reduce FPS**: Usa 30 en lugar de 60
- **Reduce resolución**: Usa 720p en lugar de 1080p
- **Evita visualizadores GPU complejos** durante exportación

### Video exportado sin audio
- Verifica que `moviepy` esté instalado correctamente
- Reinstala: `pip install moviepy --upgrade`

### Configuración corrupta
```bash
# Eliminar archivo de configuración
# Windows:
del app_config.json

# Linux/macOS:
rm app_config.json

# La app creará uno nuevo al iniciar
```

---

## 💡 Tips y Trucos

### Mejor Rendimiento
- Cierra otras aplicaciones mientras usas el visualizador
- Usa visualizadores CPU si tu GPU es antigua
- Reduce la resolución de la ventana para mejor FPS

### Mejores Videos
- Usa 60 FPS para videos suaves
- Exporta en 1080p para mejor calidad
- Configura un pool de 5-8 visualizadores para AUTO RANDOM
- Evita mezclar visualizadores muy diferentes (ej: Bars + Hyperwarp)

### Organización
- Crea carpetas por género en tu música
- Usa nombres descriptivos para tus videos exportados
- Guarda tus configuraciones favoritas de AUTO RANDOM

---

## 📞 Soporte

**GitHub**: https://github.com/PatSaint/Music_visual
**Issues**: https://github.com/PatSaint/Music_visual/issues

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.

---

**¡Disfruta creando visualizaciones increíbles!** 🎵🎨✨
