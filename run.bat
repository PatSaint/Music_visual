@echo off
echo Iniciando Music Visualizer...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error al ejecutar la aplicacion.
    echo Revisa el mensaje de arriba.
    pause
)
