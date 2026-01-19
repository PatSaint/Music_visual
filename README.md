# 🎵 Music Visualizer - GPU Edition

A powerful, GPU-accelerated music visualizer with 20 psychedelic effects and advanced export capabilities. Built with Python, OpenGL, and love for visual music experiences.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ Features

### 🎨 20 Stunning Visualizers
- **Classic Modes**: Bars Spectrum, Waveform, Circle Pulse
- **Neon Effects**: Neon Tunnel, Kaleidoscope, Plasma Fluid
- **GPU-Accelerated Shaders**:
  - 🌀 Hyperwarp Tunnel - Extreme psychedelic warp
  - 🧬 DNA Helix - 3D double helix with luminous bases
  - ⚡ Electric Storm - Procedural lightning with FBM clouds
  - 🔮 Mandelbrot Trip - Smooth fractal zoom
  - 🎲 Geometric Chaos - Morphing 3D shapes with dynamic camera
  - 🌈 Rainbow Flow - Hyper-vibrant fluid streams
  - 🔥 Fire & Ice - Elemental clash with FBM textures
  - 🪞 Infinity Mirrors - Kaleidoscopic geometry
  - 💎 Quantum Bloom, Neural Liquid, Organic Cells, Audio Matrix

### 🎲 AUTO RANDOM Mode
- **Live Rotation**: Automatically switches visualizers every 5-10 seconds
- **Custom Pool**: Select your favorite visualizers for rotation
- **Export Support**: Generate videos with automatic visualizer changes
- **Persistent Config**: Your selections are saved between sessions

### 🎬 Professional Video Export
- **Multiple Resolutions**: HD (1920x1080), Vertical (1080x1920), Square (1080x1080)
- **High Frame Rates**: 24-120 FPS support
- **AUTO RANDOM Export**: Create dynamic videos with visualizer rotation
- **GPU Optimization**: Efficient rendering with OpenGL delegation
- **Progress Tracking**: Real-time export progress with cancellation support

### 📂 Music Library Browser
- **Folder-Based**: Select a music folder and browse all tracks
- **Scrollable List**: Easy navigation through your music collection
- **Quick Switching**: Click any song to instantly load and visualize
- **Auto-Load**: Remembers your last folder on startup

### 💾 Configuration Persistence
- Last music folder
- Random pool selection
- Export settings (resolution, FPS, output folder)
- All preferences saved in `app_config.json`

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- OpenGL-compatible GPU

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/PatSaint/Music_visual.git
cd Music_visual
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

## 🎮 Usage

### Basic Workflow
1. **Load Music**: Click "SELECT FOLDER 📂" and choose your music directory
2. **Select Track**: Click any song from the track list
3. **Choose Visualizer**: Select from the dropdown menu (20 options)
4. **Play**: Hit the green ▶ button
5. **Export** (optional): Click "EXPORT VIDEO" to render your visualization

### AUTO RANDOM Setup
1. Click **⚙️ CONFIGURE RANDOM**
2. Select your favorite visualizers
3. Click **✓ ACCEPT & SAVE**
4. Toggle **🎲 AUTO RANDOM** to enable live rotation

### Video Export with AUTO RANDOM
1. Configure your random pool (see above)
2. Click **EXPORT VIDEO**
3. Check **🎲 Use AUTO RANDOM rotation**
4. Set resolution, FPS, and output folder
5. Click **START RENDER**

## 🎨 Visualizer Gallery

| Mode | Description | Type |
|------|-------------|------|
| Hyperwarp Tunnel | Extreme psychedelic warp with chromatic aberration | GPU |
| DNA Helix | 3D double helix with depth-based glow | GPU |
| Electric Storm | Realistic lightning with procedural clouds | GPU |
| Mandelbrot Trip | Smooth fractal zoom with psychedelic colors | GPU |
| Geometric Chaos | Morphing 3D shapes (spheres, tori, cubes) | GPU |
| Rainbow Flow | Hyper-vibrant multi-layer fluid streams | GPU |
| Fire & Ice | Elemental clash with FBM textures | GPU |
| Infinity Mirrors | Kaleidoscopic geometry with tone mapping | GPU |
| Quantum Bloom | Particle-based bloom effects | GPU |
| Neural Liquid | Organic liquid simulation | GPU |
| Audio Matrix | Digital rain (Matrix-style) | GPU |
| Organic Cells | Cellular automata visualization | GPU |
| GPU Fractal | Classic fractal patterns | GPU |
| Neon Tunnel | 3D tunnel with neon lights | CPU |
| Kaleidoscope | Symmetrical pattern generation | CPU |
| Plasma Fluid | Smooth plasma waves | CPU |
| Cosmic Particles | Particle system visualization | CPU |
| Bars Spectrum | Classic frequency bars | CPU |
| Waveform | Audio waveform display | CPU |
| Circle Pulse | Circular audio-reactive pulse | CPU |

## 🛠️ Technical Details

### Architecture
- **UI Framework**: CustomTkinter (modern dark theme)
- **Audio Engine**: Librosa (spectral analysis)
- **Graphics**: OpenGL 3.3+ (GPU shaders)
- **Video Export**: MoviePy (H.264 encoding)
- **Threading**: Multi-threaded export with GL delegation

### Key Components
- `main.py` - Application entry point and UI logic
- `audio_engine.py` - Audio loading and spectral analysis
- `visualizer.py` - Visualization dispatcher
- `opengl_engine.py` - GPU shader definitions (13 shaders)
- `exporter.py` - Video rendering pipeline
- `ui_components.py` - UI widgets and dialogs
- `config_manager.py` - Configuration persistence

### Performance
- **Real-time**: 60+ FPS on modern GPUs
- **Export**: Depends on resolution and visualizer complexity
- **Memory**: ~500MB typical usage

## 📋 Requirements

See `requirements.txt` for full list. Key dependencies:
- `pygame-ce` - Audio playback and OpenGL context
- `librosa` - Audio analysis
- `PyOpenGL` - GPU shader support
- `customtkinter` - Modern UI
- `moviepy` - Video export

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new visualizers
- Improve performance
- Add features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by classic Winamp visualizers
- Built with modern GPU shader techniques
- Community feedback and testing

## 📧 Contact

**Author**: PatSaint  
**GitHub**: [@PatSaint](https://github.com/PatSaint)

---

⭐ If you like this project, please give it a star on GitHub!
