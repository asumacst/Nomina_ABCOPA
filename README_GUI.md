# Sistema de Nómina ABCOPA - Interfaz Gráfica

## Descripción

Esta es la interfaz gráfica de usuario para el Sistema de Nómina ABCOPA. Permite al encargado realizar el cálculo de nómina de manera sencilla e intuitiva.

## Requisitos

- Python 3.x
- PyQt5
- pandas
- openpyxl
- matplotlib
- numpy

## Cómo Ejecutar

Para ejecutar la interfaz gráfica, simplemente ejecute:

```bash
python gui.py
```

## Funcionalidades

### 1. Calcular Nómina Quincenal

- Permite seleccionar los archivos de empleados y horas trabajadas
- Opción de especificar una fecha de referencia (o usar la más reciente)
- Muestra mensajes detallados del proceso de cálculo
- Genera automáticamente el archivo Excel con la nómina calculada
- Incluye deducciones automáticas (Seguro Social/Educativo/ISL) y préstamos (si aplica)
- Para Seguridad, calcula turnos según `seguridad_horario.xlsx` y genera alertas si hay inconsistencias

### 2. Gestionar Empleados

**Ver Lista de Empleados:**
- Muestra todos los empleados registrados en una tabla
- Permite ver toda la información de cada empleado

**Agregar Empleado:**
- Formulario completo para agregar nuevos empleados
- Generación automática de ID si no se especifica
- Validación de campos requeridos
- Permite marcar empleados como **Seguridad (S/N)**

**Modificar Empleado:**
- Buscar empleado por ID
- Modificar cualquier campo del empleado
- Mantener valores actuales presionando Enter

**Eliminar Empleado:**
- Eliminar empleados seleccionándolos desde una lista (ID - Nombre)
- Confirmación antes de eliminar

### 3. Gestionar Préstamos

- Se crea `prestamos.xlsx` automáticamente si no existe
- Crear préstamo (monto, cuota quincenal, fecha inicio)
- Pausar / reanudar
- Registrar **pago manual**
- Ver pagos (tipo `NOMINA` / `MANUAL`) y saldo
- Cierre automático al saldar (o cierre con condonación)

### 4. Empleados de Seguridad (Turnos)

- Los empleados marcados como **Seguridad** cobran como “Por Horas”, con turnos configurables.
- Configuración en `seguridad_horario.xlsx` (auto-creado):
  - `horas_turno` (por defecto 12)
  - `hora_cambio_turno`
  - `margen_salida_minutos` (± minutos)
  - `tolerancia_turno_minutos` (alerta si duración real se sale del rango)
  - `vigente_desde` para cambios por fecha

### 5. Ver Información

- Muestra información general sobre el sistema
- Explica las funcionalidades y requisitos

## Archivos Requeridos

La aplicación requiere los siguientes archivos Excel:

1. **employees_information.xlsx**: Archivo con la información de los empleados
   - Columnas usadas por el sistema: `ID`, `nombre`, `cargo`, `salario`, `n_de_cuenta`, `banco`, `tipo_de_cuenta`,
     `salario_fijo`, `empleado_fijo`, `salario_minimo`, `Empleado por contrato`, `ISL`, `seguridad`

2. **Reporte de Asistencia.xlsx**: Archivo con los registros de asistencia
   - Columnas requeridas: ID, nombre, fecha, hora
   - Debe tener exactamente 2 registros por día por empleado (entrada y salida)
     - **Excepto Seguridad**: puede cruzar medianoche; se valida por pares de registros

3. **prestamos.xlsx**: Control de préstamos y bitácora (auto-creado)
4. **seguridad_horario.xlsx**: Configuración de turnos de seguridad (auto-creado)

## Notas

- La interfaz es intuitiva y fácil de usar
- Todos los errores se muestran en mensajes claros
- Los resultados se guardan automáticamente en archivos Excel
- La fecha de pago se calcula automáticamente según la quincena
- La UI se ajusta al tamaño de pantalla (ventanas/botones adaptables)

## Características

- ✅ Interfaz gráfica moderna y profesional
- ✅ Validación de datos en tiempo real
- ✅ Mensajes informativos claros
- ✅ Manejo de errores robusto
- ✅ Fácil navegación entre funciones
- ✅ Compatible con Windows, Linux y macOS
