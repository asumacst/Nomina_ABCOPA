# Sistema de Nómina ABCOPA - Interfaz Gráfica

## Descripción

Esta es la interfaz gráfica de usuario para el Sistema de Nómina ABCOPA. Permite al encargado realizar el cálculo de nómina de manera sencilla e intuitiva.

## Requisitos

- Python 3.x
- tkinter (incluido con Python en la mayoría de instalaciones)
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

### 2. Gestionar Empleados

**Ver Lista de Empleados:**
- Muestra todos los empleados registrados en una tabla
- Permite ver toda la información de cada empleado

**Agregar Empleado:**
- Formulario completo para agregar nuevos empleados
- Generación automática de ID si no se especifica
- Validación de campos requeridos

**Modificar Empleado:**
- Buscar empleado por ID
- Modificar cualquier campo del empleado
- Mantener valores actuales presionando Enter

**Eliminar Empleado:**
- Eliminar empleados por ID
- Confirmación antes de eliminar

### 3. Ver Información

- Muestra información general sobre el sistema
- Explica las funcionalidades y requisitos

## Archivos Requeridos

La aplicación requiere los siguientes archivos Excel:

1. **employees_information.xlsx**: Archivo con la información de los empleados
   - Columnas requeridas: ID, nombre, cargo, salario, n_de_cuenta, banco, tipo_de_cuenta, fijo

2. **hours_worked.xlsx**: Archivo con los registros de asistencia
   - Columnas requeridas: ID, nombre, fecha, hora
   - Debe tener exactamente 2 registros por día por empleado (entrada y salida)

## Notas

- La interfaz es intuitiva y fácil de usar
- Todos los errores se muestran en mensajes claros
- Los resultados se guardan automáticamente en archivos Excel
- La fecha de pago se calcula automáticamente según la quincena

## Características

- ✅ Interfaz gráfica moderna y profesional
- ✅ Validación de datos en tiempo real
- ✅ Mensajes informativos claros
- ✅ Manejo de errores robusto
- ✅ Fácil navegación entre funciones
- ✅ Compatible con Windows, Linux y macOS
