@echo off
cd /d "%~dp0"

echo ========================================
echo Instalando PyInstaller para Nomina ABCOPA
echo ========================================
echo.

REM Usar pip del entorno virtual para instalar en env
if exist env\Scripts\pip.exe (
    echo Instalando PyInstaller en el entorno virtual (env)...
    env\Scripts\pip.exe install pyinstaller
) else (
    echo No hay entorno virtual en env\. Instalando con Python del sistema...
    python -m pip install pyinstaller
)

echo.
if errorlevel 1 (
    echo.
    echo Si aparece "file is being used by another process":
    echo   1. Cierra Cursor, otras ventanas de Python o IDEs.
    echo   2. Cierra cualquier ventana que use este proyecto.
    echo   3. Vuelve a ejecutar este archivo.
    echo.
) else (
    echo PyInstaller instalado correctamente.
    echo Ahora puedes ejecutar build_executable.bat
)
echo.
pause
