@echo off
echo ========================================
echo Generando ejecutable de Nomina ABCOPA
echo ========================================
echo.

REM Activar entorno virtual
call env\Scripts\activate.bat

REM Limpiar builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Compilando ejecutable...
echo.

REM Generar ejecutable usando PyInstaller
python -m PyInstaller nomina_abcopa.spec --clean

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
