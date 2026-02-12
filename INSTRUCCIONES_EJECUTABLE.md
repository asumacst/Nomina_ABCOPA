# Instrucciones para Usar el Ejecutable de Nómina ABCOPA

## 📦 Archivo Ejecutable

El ejecutable se encuentra en la carpeta `dist` con el nombre:
- **NominaABCOPA.exe**

## 🚀 Cómo Usar el Ejecutable

### Requisitos
- **Sistema Operativo**: Windows 7 o superior (64 bits)
- **No se requiere instalar Python ni ninguna dependencia adicional**
- El ejecutable es completamente independiente

### Pasos para Usar

1. **Copiar el ejecutable**
   - Copia el archivo `NominaABCOPA.exe` a la computadora donde se va a usar
   - Puedes copiarlo a cualquier ubicación (Escritorio, carpeta de documentos, etc.)

2. **Preparar los archivos necesarios**
   - Crea una carpeta llamada `datos` en la misma ubicación que el ejecutable.
   - Dentro de `datos`, coloca los siguientes archivos:
     - `employees_information.xlsx` - Archivo con la información de los empleados
     - `Reporte de Asistencia.xlsx` - Archivo con los registros de asistencia (biométrico)
     - `prestamos.xlsx` - Control de préstamos (se crea automáticamente si no existe)
     - `seguridad_horario.xlsx` - Configuración de turnos de seguridad (se crea automáticamente si no existe)
     - `logo.png` - Logo de la empresa (opcional, para la interfaz)

3. **Ejecutar el programa**
   - Haz doble clic en `NominaABCOPA.exe`
   - Se abrirá la interfaz gráfica del sistema

4. **Usar el sistema**
   - **Calcular Nómina Quincenal**: Selecciona los archivos y calcula la nómina
   - **Gestionar Empleados**: Agrega, modifica o elimina empleados
   - **Gestionar Préstamos**: Crea préstamos, registra pagos manuales, revisa pagos
   - **Ver Información**: Consulta información sobre el sistema

## 📋 Estructura de Archivos Recomendada

```
Carpeta del Ejecutable/
├── NominaABCOPA.exe
├── employees_information.xlsx
├── Reporte de Asistencia.xlsx
├── prestamos.xlsx
└── seguridad_horario.xlsx
```

## ⚠️ Notas Importantes

1. **Primera ejecución**: La primera vez que ejecutes el programa, Windows puede mostrar una advertencia de seguridad. Esto es normal. Haz clic en "Más información" y luego en "Ejecutar de todas formas".

2. **Antivirus**: Algunos antivirus pueden marcar el ejecutable como sospechoso. Esto es un falso positivo común con programas compilados con PyInstaller. Puedes agregar una excepción en tu antivirus.

3. **Archivos Excel**: Los archivos Excel deben estar dentro de la carpeta `datos` junto al ejecutable, o puedes usar la función "Buscar" en la interfaz para seleccionarlos desde otra ubicación.

4. **Archivos generados**: Los archivos de nómina generados se guardarán dentro de la carpeta `datos`.

## 🔄 Regenerar el Ejecutable

Si necesitas regenerar el ejecutable (por ejemplo, después de hacer cambios en el código):

1. Abre una terminal en la carpeta del proyecto
2. Activa el entorno virtual: `.\env\Scripts\activate`
3. Ejecuta: `python -m PyInstaller nomina_abcopa.spec --clean`

O simplemente ejecuta el archivo `build_executable.bat` (doble clic).

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que los archivos Excel tengan el formato correcto
2. Asegúrate de que los archivos estén en la ubicación correcta
3. Revisa que el sistema tenga permisos para leer/escribir archivos

## 📝 Formato de Archivos Excel

### employees_information.xlsx
Debe contener las siguientes columnas:
- ID
- nombre
- cargo
- salario
- n_de_cuenta
- banco
- tipo_de_cuenta
- empleado_confianza (0/1)
- obrero_fijo (0/1)
- obrero_fijo_sal_min
- Empleado por contrato (Sí/No)
- ISLR
- seguridad (Sí/No)

### Reporte de Asistencia.xlsx
Debe contener las siguientes columnas:
- ID
- nombre
- fecha (formato: DD/MM/YYYY)
- hora (formato: HH:MM)

**Importante**:
- Cada empleado debe tener exactamente 2 registros por día (entrada y salida).
- **Seguridad**: puede cruzar medianoche; se validan por pares de registros.

### prestamos.xlsx (auto-creado)
- Hoja `Prestamos`: estado/saldo/cuota/estado del préstamo
- Hoja `PagosPrestamo`: bitácora de pagos con tipo `NOMINA` / `MANUAL`

### seguridad_horario.xlsx (auto-creado)
- Hoja `Config`: controla turnos y tolerancias para Seguridad:
  - `horas_turno`, `hora_cambio_turno`, `margen_salida_minutos`, `tolerancia_turno_minutos`
  - `vigente_desde` para cambios por fecha
