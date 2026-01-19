# 🚀 Comandos para subir a GitHub

## Paso 1: Configurar Git (solo la primera vez)
```bash
git config --global user.name "PatSaint"
git config --global user.email "tu-email@ejemplo.com"
```

## Paso 2: Añadir archivos y hacer commit
```bash
cd "C:\Users\TEL\OneDrive - Hexagon\Documents\VIRTUALBOX\GitHub\Music_visual"

git add .
git commit -m "Initial commit: Music Visualizer with 20 GPU effects and AUTO RANDOM export"
```

## Paso 3: Crear repositorio en GitHub
1. Ve a: https://github.com/new
2. Repository name: `Music_visual`
3. Description: `GPU-accelerated music visualizer with 20 psychedelic effects`
4. Elige Public o Private
5. **NO marques** "Add README" (ya lo tienes)
6. Click "Create repository"

## Paso 4: Conectar y subir
```bash
git branch -M main
git remote add origin https://github.com/PatSaint/Music_visual.git
git push -u origin main
```

## ✅ ¡Listo!
Tu proyecto estará en: https://github.com/PatSaint/Music_visual

---

## 📝 Para futuras actualizaciones:
```bash
git add .
git commit -m "Descripción de los cambios"
git push
```
