
@echo off
echo ========================================
echo   KRONOS - Instalacion y ejecucion
echo ========================================
 
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Descargalo desde https://www.python.org/downloads/
    pause
    exit /b
)
 
echo Instalando dependencias...
pip install requests --quiet
 
echo.
echo Iniciando KRONOS...
echo.
cd /d "%~dp0proyecto_kronos"
python main.py
pause
 