@echo off
cd /d "%~dp0"

echo ========================================
echo Generando ejecutable de Nomina ABCOPA
echo ========================================
echo.

REM Usar siempre el Python del entorno virtual (evita que se use el de Windows Apps)
set PYTHON_VENV=%~dp0env\Scripts\python.exe
if not exist "%PYTHON_VENV%" (
    echo Error: No se encontro el entorno virtual en env\
    echo Crea el venv con: python -m venv env
    pause
    exit /b 1
)

REM Limpiar builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Compilando ejecutable...
echo.

REM Generar ejecutable usando PyInstaller (Python del venv)
"%PYTHON_VENV%" -m PyInstaller nomina_abcopa.spec --clean

echo.
echo ========================================
if exist dist\NominaABCOPA.exe (
    echo Ejecutable generado exitosamente!
    echo Ubicacion: dist\NominaABCOPA.exe
    echo.
    echo El ejecutable esta listo para distribuir.
    echo Puedes copiar el archivo .exe a cualquier computadora Windows.
) else (
    echo Error al generar el ejecutable.
    echo Revisa los mensajes de error arriba.
)
echo ========================================
echo.
pause
