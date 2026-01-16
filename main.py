import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

feriados_panama = {
    2026: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-17": "Martes de Carnaval",
        "04-03": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2027: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-09": "Martes de Carnaval",
        "03-26": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2028: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-29": "Martes de Carnaval",
        "04-14": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2029: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-13": "Martes de Carnaval",
        "03-30": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2030: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "03-05": "Martes de Carnaval",
        "04-19": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    }
}


def es_feriado_o_domingo(fecha):
    """
    Verifica si una fecha es un día feriado en Panamá o domingo.
    
    Args:
        fecha: Objeto datetime o pd.Timestamp
        
    Returns:
        bool: True si es feriado o domingo, False en caso contrario
    """
    # Convertir a datetime si es necesario
    if isinstance(fecha, pd.Timestamp):
        fecha = fecha.to_pydatetime()
    elif not isinstance(fecha, datetime):
        fecha = pd.to_datetime(fecha)
    
    # Verificar si es domingo (weekday() devuelve 0 para lunes, 6 para domingo)
    if fecha.weekday() == 6:  # Domingo
        return True
    
    # Verificar si es feriado
    año = fecha.year
    mes_dia = fecha.strftime("%m-%d")
    
    if año in feriados_panama:
        if mes_dia in feriados_panama[año]:
            return True
    
    return False

def validate_attendance_records(hours_df):
    """
    Valida que cada empleado tenga exactamente 2 registros por día (entrada y salida).
    Si hay más o menos de 2, retorna una lista de errores.
    
    Args:
        hours_df: DataFrame con columnas ID, nombre, fecha, hora
        
    Returns:
        Lista de errores encontrados. Si está vacía, no hay errores.
    """
    errors = []
    
    # Agrupar por empleado (usando ID) y fecha
    for (employee_id, date), group in hours_df.groupby(['ID', 'fecha']):
        record_count = len(group)
        employee_name = group['nombre'].iloc[0]
        
        if record_count != 2:
            date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
            errors.append({
                'empleado': employee_name,
                'ID': employee_id,
                'fecha': date_str,
                'registros': record_count,
                'mensaje': f"Empleado {employee_name} (ID: {employee_id}) tiene {record_count} registro(s) el {date_str}. Se requieren exactamente 2 (entrada y salida)."
            })
    
    return errors


def calculate_hours_per_day(hours_df):
    """
    Calcula las horas trabajadas por día para cada empleado.
    Asume que hay exactamente 2 registros por día (entrada y salida).
    
    Args:
        hours_df: DataFrame con columnas ID, nombre, fecha, hora
        
    Returns:
        DataFrame con columnas: ID, nombre, fecha, horas_trabajadas, horas_extra
    """
    daily_hours = []
    
    # Convertir fecha a datetime si es necesario
    if not pd.api.types.is_datetime64_any_dtype(hours_df['fecha']):
        hours_df['fecha'] = pd.to_datetime(hours_df['fecha'], format='%d/%m/%Y', errors='coerce')
    
    # Función para convertir hora a objeto time (sin AM/PM)
    def parse_time_str(time_str):
        """Convierte string de hora a objeto time."""
        if pd.isna(time_str):
            return None
        
        time_str = str(time_str).strip()
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                return datetime.min.time().replace(hour=hour, minute=minute)
            else:
                return None
        except:
            return None
    
    # Agrupar por empleado y fecha
    for (employee_id, date), group in hours_df.groupby(['ID', 'fecha']):
        employee_name = group['nombre'].iloc[0]
        
        # Obtener las dos horas del día
        horas_raw = []
        for _, row in group.iterrows():
            time_obj = parse_time_str(row['hora'])
            if time_obj:
                horas_raw.append(time_obj.hour)
        
        if len(horas_raw) == 2:
            # Obtener los minutos de los registros originales
            horas_con_minutos = []
            for _, row in group.iterrows():
                time_obj = parse_time_str(row['hora'])
                if time_obj:
                    horas_con_minutos.append((time_obj.hour, time_obj.minute))
            
            # Ordenar por hora
            horas_con_minutos.sort()
            
            # Determinar cuál es entrada y cuál salida
            if len(horas_con_minutos) == 2:
                h1, m1 = horas_con_minutos[0]
                h2, m2 = horas_con_minutos[1]
                
                # Si ambas son < 12 y la diferencia es >= 2, entonces:
                # - h2 (mayor) es la entrada (AM)
                # - h1 (menor) es la salida (PM, se suma 12)
                # Ejemplo: [3, 7] -> entrada 7 AM, salida 3 PM (15:00)
                # Ejemplo: [3, 8] -> entrada 8 AM, salida 3 PM (15:00)
                # Ejemplo: [4, 7] -> entrada 7 AM, salida 4 PM (16:00)
                # Ejemplo: [5, 7] -> entrada 7 AM, salida 5 PM (17:00)
                if h1 < 12 and h2 < 12 and (h2 - h1) >= 2:
                    entrada_hour_final = h2
                    entrada_minute = m2
                    salida_hour_final = h1 + 12
                    salida_minute = m1
                elif h1 < 12 and h2 >= 12:
                    # h1 es AM, h2 ya es PM (formato 24h)
                    entrada_hour_final = h1
                    entrada_minute = m1
                    salida_hour_final = h2
                    salida_minute = m2
                else:
                    # Ambas son >= 12 o diferencia pequeña
                    entrada_hour_final = h1
                    entrada_minute = m1
                    salida_hour_final = h2
                    salida_minute = m2
            else:
                entrada_minute = 0
                salida_minute = 0
                entrada_hour_final = horas_raw[0] if horas_raw else 7
                salida_hour_final = horas_raw[1] if len(horas_raw) > 1 else 15
            
            # Crear objetos datetime
            date_obj = date.date() if isinstance(date, pd.Timestamp) else date
            entrada = datetime.combine(date_obj, 
                                      datetime.min.time().replace(hour=entrada_hour_final, minute=entrada_minute))
            salida = datetime.combine(date_obj, 
                                     datetime.min.time().replace(hour=salida_hour_final, minute=salida_minute))
            
            # Si la salida es antes que la entrada, asumir que es del día siguiente (turno nocturno)
            if salida < entrada:
                salida = salida + timedelta(days=1)
            
            # Calcular horas trabajadas
            horas_trabajadas = (salida - entrada).total_seconds() / 3600
            
            # Calcular horas extra (después de las 3 PM / 15:00, no incluyendo las 3:00 PM)
            horas_extra = 0.0
            
            # Solo contar horas extra si la salida es DESPUÉS de las 3:00 PM (no igual)
            # Usar salida_hour_final que ya tiene la hora correcta en formato 24h
            if salida_hour_final > 15:
                # Si la salida es después de las 3 PM, calcular horas extra
                if entrada_hour_final < 15:
                    # La entrada fue antes de las 3 PM, calcular solo las horas después de las 3 PM
                    horas_extra = salida_hour_final - 15
                    # Si hay minutos en la salida, agregar la fracción correspondiente
                    if salida_minute > 0:
                        horas_extra += salida_minute / 60.0
                else:
                    # La entrada fue después de las 3 PM, todas las horas son extra
                    horas_extra = horas_trabajadas
            # Si salida_hour_final == 15 (exactamente 3:00 PM), horas_extra = 0
            
            # Validar que las horas sean razonables (entre 1 y 16 horas por día)
            if horas_trabajadas < 1 or horas_trabajadas > 16:
                print(f"[ADVERTENCIA] Horas calculadas para {employee_name} el {date} parecen incorrectas: {horas_trabajadas:.2f} horas")
            
            # Verificar si es feriado o domingo
            es_feriado_domingo = es_feriado_o_domingo(date)
            
            daily_hours.append({
                'ID': employee_id,
                'nombre': employee_name,
                'fecha': date,
                'horas_trabajadas': horas_trabajadas,
                'horas_extra': horas_extra,  # Horas trabajadas después de las 3 PM
                'es_feriado_domingo': es_feriado_domingo  # True si es feriado o domingo
            })
    
    return pd.DataFrame(daily_hours)


def get_quincena_periods(daily_hours_df):
    """
    Agrupa las fechas en períodos quincenales (15 días).
    
    Args:
        daily_hours_df: DataFrame con columnas ID, nombre, fecha, horas_trabajadas
        
    Returns:
        DataFrame con columna adicional 'quincena'
    """
    if daily_hours_df.empty:
        return daily_hours_df
    
    # Asegurar que fecha es datetime
    if not pd.api.types.is_datetime64_any_dtype(daily_hours_df['fecha']):
        daily_hours_df['fecha'] = pd.to_datetime(daily_hours_df['fecha'])
    
    # Calcular el inicio de la quincena (día 1 o 16 del mes)
    def get_quincena_start(date):
        day = date.day
        if day <= 15:
            return date.replace(day=1)
        else:
            return date.replace(day=16)
    
    daily_hours_df['quincena_inicio'] = daily_hours_df['fecha'].apply(get_quincena_start)
    daily_hours_df['quincena_fin'] = daily_hours_df['quincena_inicio'] + timedelta(days=14)
    
    return daily_hours_df


def calculate_payroll_quincenal(employees_file="employees_information.xlsx", 
                                 hours_file="hours_worked.xlsx",
                                 output_file=None,
                                 quincena_fecha=None):
    """
    Calcula la nómina quincenal para todos los empleados de UNA quincena específica.
    
    Args:
        employees_file: Archivo Excel con información de empleados
        hours_file: Archivo Excel con horas trabajadas
        output_file: Nombre del archivo Excel de salida (si es None, se genera automáticamente)
        quincena_fecha: Fecha de referencia para determinar qué quincena calcular (si es None, usa la más reciente)
        
    Returns:
        DataFrame con la nómina calculada o None si hay errores
    """
    print("="*80)
    print("SISTEMA DE NOMINA QUINCENAL")
    print("="*80)
    
    # Leer archivo de empleados
    print(f"\nLeyendo informacion de empleados desde: {employees_file}")
    try:
        employees_df = pd.read_excel(employees_file)
        print(f"[OK] Encontrados {len(employees_df)} empleados")
    except Exception as e:
        print(f"[ERROR] Error al leer {employees_file}: {e}")
        return None
    
    # Leer archivo de horas trabajadas
    print(f"\nLeyendo horas trabajadas desde: {hours_file}")
    try:
        hours_df = pd.read_excel(hours_file)
        print(f"[OK] Encontrados {len(hours_df)} registros de asistencia")
    except Exception as e:
        print(f"[ERROR] Error al leer {hours_file}: {e}")
        return None
    
    # Validar que cada empleado tenga exactamente 2 registros por día
    print("\nValidando registros de asistencia...")
    errors = validate_attendance_records(hours_df)
    
    if errors:
        print("\n" + "="*80)
        print("ERRORES ENCONTRADOS - CORRIJA ANTES DE CONTINUAR")
        print("="*80)
        for error in errors:
            print(f"\n{error['mensaje']}")
        print("\n" + "="*80)
        return None
    
    print("[OK] Todos los registros son validos (2 registros por empleado por dia)")
    
    # Calcular horas trabajadas por día
    print("\nCalculando horas trabajadas por dia...")
    daily_hours_df = calculate_hours_per_day(hours_df)
    print(f"[OK] Horas calculadas para {len(daily_hours_df)} dias")
    
    # Agrupar en períodos quincenales
    print("\nAgrupando en períodos quincenales...")
    daily_hours_df = get_quincena_periods(daily_hours_df)
    
    # Determinar qué quincena calcular
    if quincena_fecha is None:
        # Usar la quincena más reciente (la última fecha en los datos)
        fecha_maxima = daily_hours_df['fecha'].max()
        quincena_fecha = fecha_maxima
        print(f"Calculando nómina para la quincena más reciente (fecha de referencia: {quincena_fecha.strftime('%d/%m/%Y')})")
    else:
        # Convertir quincena_fecha a datetime si es string
        if isinstance(quincena_fecha, str):
            quincena_fecha = pd.to_datetime(quincena_fecha, format='%d/%m/%Y', errors='coerce')
        elif not isinstance(quincena_fecha, pd.Timestamp):
            quincena_fecha = pd.to_datetime(quincena_fecha)
        print(f"Calculando nómina para quincena que contiene la fecha: {quincena_fecha.strftime('%d/%m/%Y')}")
    
    # Determinar el inicio de la quincena para la fecha especificada
    day = quincena_fecha.day
    if day <= 15:
        quincena_inicio_target = quincena_fecha.replace(day=1)
    else:
        quincena_inicio_target = quincena_fecha.replace(day=16)
    quincena_fin_target = quincena_inicio_target + timedelta(days=14)
    
    print(f"Período de la quincena: {quincena_inicio_target.strftime('%d/%m/%Y')} a {quincena_fin_target.strftime('%d/%m/%Y')}")
    
    # Filtrar solo los datos de la quincena objetivo
    daily_hours_df = daily_hours_df[daily_hours_df['quincena_inicio'] == quincena_inicio_target]
    
    if daily_hours_df.empty:
        print(f"[ERROR] No se encontraron datos para la quincena del {quincena_inicio_target.strftime('%d/%m/%Y')} a {quincena_fin_target.strftime('%d/%m/%Y')}")
        return None
    
    print(f"[OK] Encontrados datos para {len(daily_hours_df)} días en esta quincena")
    
    # Crear diccionario de empleados para acceso rápido
    employees_dict = {}
    for _, emp in employees_df.iterrows():
        # Usar ID como clave principal, pero también nombre como alternativa
        employees_dict[str(emp['ID'])] = {
            'nombre': emp['nombre'],
            'fijo': bool(emp['fijo']),
            'salario': float(emp['salario']),
            'cargo': emp.get('cargo', ''),
            'n_de_cuenta': emp.get('n_de_cuenta', ''),
            'banco': emp.get('banco', ''),
            'tipo_de_cuenta': emp.get('tipo_de_cuenta', '')
        }
    
    # Calcular nómina por quincena (solo una quincena ahora)
    print("\nCalculando nómina...")
    payroll_results = []
    
    for (employee_id, quincena_inicio), group in daily_hours_df.groupby(['ID', 'quincena_inicio']):
        employee_id_str = str(employee_id)
        
        # Buscar información del empleado
        if employee_id_str not in employees_dict:
            print(f"[ADVERTENCIA] Empleado con ID {employee_id} no encontrado en archivo de empleados")
            continue
        
        emp_info = employees_dict[employee_id_str]
        total_horas = group['horas_trabajadas'].sum()
        total_horas_extra = group['horas_extra'].sum()  # Horas trabajadas después de las 3 PM
        quincena_fin = group['quincena_fin'].iloc[0]
        
        # Calcular pago según si es fijo o no
        if emp_info['fijo']:
            # Empleado fijo: recibe el mismo salario sin importar horas (no recibe pago extra)
            pago_quincenal = emp_info['salario'] / 2  # Salario mensual dividido en 2 quincenas
            pago_extra = 0.0  # Los empleados fijos no reciben pago extra
            pago_feriado_domingo = 0.0  # Los empleados fijos no reciben pago extra por feriados/domingos
            tipo_pago = "Fijo"
        else:
            # Empleado no fijo: salario por horas trabajadas
            # Asumimos que el salario es por hora
            
            # Separar horas normales, horas extra (después 3 PM) y horas en feriados/domingos
            horas_normales = 0.0
            horas_extra_normales = 0.0  # Horas extra en días normales
            horas_feriado_domingo = 0.0  # Horas trabajadas en feriados/domingos (todas)
            
            for _, row in group.iterrows():
                horas_dia = row['horas_trabajadas']
                horas_extra_dia = row['horas_extra']
                es_feriado_domingo = row['es_feriado_domingo']
                
                if es_feriado_domingo:
                    # Si es feriado o domingo, todas las horas se pagan con 50% adicional
                    horas_feriado_domingo += horas_dia
                else:
                    # Día normal
                    horas_normales += (horas_dia - horas_extra_dia)
                    horas_extra_normales += horas_extra_dia
            
            # Calcular pagos
            # Pago normal: horas normales (antes de 3 PM en días normales)
            pago_normal = emp_info['salario'] * horas_normales
            
            # Pago extra: 25% adicional sobre el salario por hora para horas después de las 3 PM en días normales
            salario_hora_extra = emp_info['salario'] * 1.25
            pago_extra = salario_hora_extra * horas_extra_normales
            
            # Pago feriado/domingo: 50% adicional sobre el salario por hora para TODAS las horas trabajadas en feriados/domingos
            # Salario por hora en feriado/domingo = salario base * 1.50 (50% adicional)
            salario_hora_feriado_domingo = emp_info['salario'] * 1.50
            pago_feriado_domingo = salario_hora_feriado_domingo * horas_feriado_domingo
            
            pago_quincenal = pago_normal + pago_extra + pago_feriado_domingo
            tipo_pago = "Por horas"
        
        # Preparar datos para el resultado
        resultado = {
            'ID': employee_id,
            'Nombre': emp_info['nombre'],
            'Cargo': emp_info['cargo'],
            'Tipo': tipo_pago,
            'Fijo': 'Sí' if emp_info['fijo'] else 'No',
            'Salario Base': emp_info['salario'],
            'Quincena Inicio': quincena_inicio.strftime('%d/%m/%Y'),
            'Quincena Fin': quincena_fin.strftime('%d/%m/%Y'),
            'Total Horas Trabajadas': round(total_horas, 2),
            'Horas Extra (después 3 PM)': round(total_horas_extra, 2),
            'Pago Extra (25% adicional)': round(pago_extra, 2),
            'Pago Quincenal': round(pago_quincenal, 2),
            'Número de Cuenta': emp_info['n_de_cuenta'],
            'Banco': emp_info['banco'],
            'Tipo de Cuenta': emp_info['tipo_de_cuenta']
        }
        
        # Agregar información de feriados/domingos solo para empleados no fijos
        if not emp_info['fijo']:
            horas_feriado_domingo_total = group[group['es_feriado_domingo'] == True]['horas_trabajadas'].sum()
            resultado['Horas Feriado/Domingo'] = round(horas_feriado_domingo_total, 2)
            resultado['Pago Feriado/Domingo (50% adicional)'] = round(pago_feriado_domingo, 2)
        else:
            resultado['Horas Feriado/Domingo'] = 0.0
            resultado['Pago Feriado/Domingo (50% adicional)'] = 0.0
        
        payroll_results.append(resultado)
    
    if not payroll_results:
        print("[ERROR] No se pudo calcular la nomina. Verifique los datos.")
        return None
    
    # Crear DataFrame con resultados
    payroll_df = pd.DataFrame(payroll_results)
    
    # Ordenar por nombre
    payroll_df = payroll_df.sort_values(['Nombre'])
    
    # Determinar fecha de pago según la quincena
    # Si la quincena empieza el día 1: fecha de pago es el día 15 del mismo mes
    # Si la quincena empieza el día 16: fecha de pago es el último día del mismo mes
    if quincena_inicio_target.day == 1:
        # Primera quincena: pago el día 15
        fecha_pago = quincena_inicio_target.replace(day=15)
    else:
        # Segunda quincena: pago el último día del mes
        # Obtener el último día del mes
        if quincena_inicio_target.month == 12:
            # Si es diciembre, el último día es 31
            fecha_pago = quincena_inicio_target.replace(day=31)
        else:
            # Para otros meses, el último día del mes es el día antes del día 1 del mes siguiente
            siguiente_mes = quincena_inicio_target.replace(month=quincena_inicio_target.month + 1, day=1)
            fecha_pago = siguiente_mes - timedelta(days=1)
    
    # Generar nombre de archivo si no se especificó
    if output_file is None:
        fecha_pago_str = fecha_pago.strftime('%Y%m%d')
        output_file = f"nomina_quincenal_pago_{fecha_pago_str}.xlsx"
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE NOMINA")
    print("="*80)
    print(f"Quincena: {quincena_inicio_target.strftime('%d/%m/%Y')} a {quincena_fin_target.strftime('%d/%m/%Y')}")
    print(f"Fecha de pago: {fecha_pago.strftime('%d/%m/%Y')}")
    print(f"Total de empleados: {payroll_df['Nombre'].nunique()}")
    print(f"Total de pagos: {len(payroll_df)}")
    print(f"Total horas extra (después 3 PM): {payroll_df['Horas Extra (después 3 PM)'].sum():.2f}")
    print(f"Total pago extra (25% adicional): ${payroll_df['Pago Extra (25% adicional)'].sum():,.2f}")
    print(f"Total horas feriado/domingo: {payroll_df['Horas Feriado/Domingo'].sum():.2f}")
    print(f"Total pago feriado/domingo (50% adicional): ${payroll_df['Pago Feriado/Domingo (50% adicional)'].sum():,.2f}")
    print(f"Total a pagar: ${payroll_df['Pago Quincenal'].sum():,.2f}")
    print("="*80)
    
    # Agregar columna de fecha de pago al DataFrame
    payroll_df['Fecha de Pago'] = fecha_pago.strftime('%d/%m/%Y')
    
    # Reordenar columnas para que la fecha de pago esté más visible
    columnas = ['ID', 'Nombre', 'Cargo', 'Tipo', 'Fijo', 'Salario Base', 
                'Quincena Inicio', 'Quincena Fin', 'Fecha de Pago',
                'Total Horas Trabajadas', 'Horas Extra (después 3 PM)', 
                'Pago Extra (25% adicional)', 'Horas Feriado/Domingo',
                'Pago Feriado/Domingo (50% adicional)', 'Pago Quincenal', 
                'Número de Cuenta', 'Banco', 'Tipo de Cuenta']
    payroll_df = payroll_df[columnas]
    
    # Guardar en Excel
    print(f"\nGuardando nomina en: {output_file}")
    try:
        payroll_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"[OK] Nomina guardada exitosamente")
        print(f"\nArchivo generado: {output_file}")
        print(f"Fecha de pago: {fecha_pago.strftime('%d/%m/%Y')}")
    except Exception as e:
        print(f"[ERROR] Error al guardar archivo: {e}")
        return None
    
    return payroll_df

def leer_empleados_normalizado(employees_file="employees_information.xlsx"):
    """
    Lee el archivo de empleados y normaliza los IDs (convierte floats enteros a int).
    
    Returns:
        DataFrame con IDs normalizados o None si hay error
    """
    try:
        employees_df = pd.read_excel(employees_file)
        # Normalizar IDs: convertir floats enteros a int, pero preservar strings
        if 'ID' in employees_df.columns:
            def normalizar_id_lectura(id_val):
                if pd.isna(id_val):
                    return id_val
                # Si es float y es entero (ej: 171572201.0), convertir a int
                if isinstance(id_val, float) and id_val.is_integer():
                    return int(id_val)
                # Si es int, mantenerlo
                if isinstance(id_val, (int, np.integer)):
                    return id_val
                # Si es string, mantenerlo (puede ser pasaporte con letras)
                return id_val
            employees_df['ID'] = employees_df['ID'].apply(normalizar_id_lectura)
        return employees_df
    except Exception as e:
        print(f"[ERROR] Error al leer el archivo: {e}")
        return None

def agregar_empleado(employees_file="employees_information.xlsx"):
    '''Funcion para agregar un empleado a la base de datos'''
    employees_df = leer_empleados_normalizado(employees_file)
    if employees_df is None:
        return None
    
    # Función auxiliar para verificar si un ID ya existe
    def id_existe(id_buscado, df):
        """Verifica si un ID ya existe en el DataFrame"""
        if df.empty or 'ID' not in df.columns:
            return False
        
        # Normalizar el ID buscado: convertir a string y eliminar espacios
        id_buscado_str = str(id_buscado).strip()
        
        # Normalizar todos los IDs del DataFrame a string para comparación
        # Esto maneja casos donde Excel convierte números a float (ej: 171572201.0)
        def normalizar_id(id_val):
            """Normaliza un ID a string, manejando floats y números"""
            if pd.isna(id_val):
                return None
            # Si es float, convertir a int primero para eliminar .0
            if isinstance(id_val, float):
                # Verificar si es un número entero (sin decimales significativos)
                if id_val.is_integer():
                    return str(int(id_val))
                else:
                    return str(id_val)
            # Si es número, convertir a string
            elif isinstance(id_val, (int, np.integer)):
                return str(id_val)
            # Si ya es string, solo limpiar espacios
            else:
                return str(id_val).strip()
        
        # Aplicar normalización a todos los IDs
        ids_normalizados = df['ID'].apply(normalizar_id)
        
        # Comparar el ID buscado con los IDs normalizados
        return (ids_normalizados == id_buscado_str).any()
    
    # Función auxiliar para obtener el siguiente ID disponible
    def obtener_siguiente_id(df):
        """Obtiene el siguiente ID disponible"""
        if df.empty or 'ID' not in df.columns:
            return 1
        try:
            ids_numericos = pd.to_numeric(df['ID'], errors='coerce')
            max_id = ids_numericos.max()
            if pd.isna(max_id):
                return 1
            # Buscar el siguiente ID disponible (por si hay huecos)
            siguiente_id = int(max_id) + 1
            # Verificar que no exista (por si acaso)
            while id_existe(siguiente_id, df):
                siguiente_id += 1
            return siguiente_id
        except:
            return len(df) + 1
    
    # Solicitar ID del empleado
    print('\nIngrese el ID del empleado:')
    print('(Presione Enter para generar automáticamente el siguiente ID disponible)')
    id_input = input('ID: ').strip()
    
    # Determinar el ID a usar
    if not id_input:
        # Generar ID automático
        nuevo_id = obtener_siguiente_id(employees_df)
        print(f'ID generado automáticamente: {nuevo_id}')
    else:
        # Validar que el ID no exista
        if id_existe(id_input, employees_df):
            print(f"[ERROR] El ID {id_input} ya existe. Por favor, use otro ID.")
            return None
        
        # Intentar convertir a entero si es posible
        try:
            nuevo_id = int(id_input)
        except ValueError:
            nuevo_id = id_input  # Mantener como string si no es numérico
    
    print('\nIngrese los datos del empleado:')
    nombre = input('Nombre: ').strip()
    cargo = input('Cargo: ').strip()
    salario_str = input('Salario: ').strip()
    n_de_cuenta = input('Numero de cuenta: ').strip()
    banco = input('Banco: ').strip()
    tipo_de_cuenta = input('Tipo de cuenta: ').strip()
    fijo = input('Fijo (S/N): ').strip().upper()
    
    # Validar y convertir salario
    try:
        salario = float(salario_str)
    except ValueError:
        print("[ERROR] El salario debe ser un número válido")
        return None
    
    # Convertir fijo a booleano
    fijo_bool = (fijo == 'S')
    
    # Validación final: verificar que el ID no exista (por si el archivo cambió)
    try:
        employees_df_actualizado = leer_empleados_normalizado(employees_file)
        if employees_df_actualizado is not None and id_existe(nuevo_id, employees_df_actualizado):
            print(f"[ERROR] El ID {nuevo_id} ya existe en el archivo. Por favor, use otro ID.")
            return None
    except:
        pass  # Si hay error al leer, continuar con el DataFrame que ya tenemos
    
    # Crear nuevo empleado como DataFrame
    nuevo_empleado = pd.DataFrame({
        'ID': [nuevo_id],
        'nombre': [nombre],
        'cargo': [cargo],
        'salario': [salario],
        'n_de_cuenta': [n_de_cuenta],
        'banco': [banco],
        'tipo_de_cuenta': [tipo_de_cuenta],
        'fijo': [fijo_bool]
    })
    
    # Concatenar con el DataFrame existente
    employees_df = pd.concat([employees_df, nuevo_empleado], ignore_index=True)
    
    # Verificación final de duplicados antes de guardar
    if 'ID' in employees_df.columns:
        ids_duplicados = employees_df[employees_df.duplicated(subset=['ID'], keep=False)]
        if not ids_duplicados.empty:
            print(f"[ERROR] Se detectaron IDs duplicados. No se guardará el empleado.")
            print("IDs duplicados encontrados:")
            print(ids_duplicados[['ID', 'nombre']])
            return None
    
    # Guardar en Excel
    try:
        employees_df.to_excel(employees_file, index=False, engine='openpyxl')
        print(f'\n[OK] Empleado agregado exitosamente con ID: {nuevo_id}')
        return employees_df
    except Exception as e:
        print(f"[ERROR] Error al guardar el archivo: {e}")
        return None

def eliminar_empleado(employees_file="employees_information.xlsx"):
    '''Funcion para eliminar un empleado de la base de datos'''
    employees_df = leer_empleados_normalizado(employees_file)
    if employees_df is None:
        return None
    
    if employees_df.empty:
        print("[ERROR] No hay empleados en la base de datos")
        return None
    
    # Función auxiliar para buscar empleado por ID (usando la misma lógica de normalización)
    def buscar_empleado_por_id(id_buscado, df):
        """Busca un empleado por ID usando normalización"""
        id_buscado_str = str(id_buscado).strip()
        
        def normalizar_id(id_val):
            if pd.isna(id_val):
                return None
            if isinstance(id_val, float) and id_val.is_integer():
                return str(int(id_val))
            elif isinstance(id_val, (int, np.integer)):
                return str(id_val)
            else:
                return str(id_val).strip()
        
        ids_normalizados = df['ID'].apply(normalizar_id)
        mask = ids_normalizados == id_buscado_str
        return df[mask]
    
    print('\nIngrese el ID del empleado a eliminar:')
    id_input = input('ID: ').strip()
    
    # Buscar empleado usando la función auxiliar
    empleado_encontrado = buscar_empleado_por_id(id_input, employees_df)
    
    if empleado_encontrado.empty:
        print(f"[ERROR] No se encontró un empleado con ID: {id_input}")
        return None
    
    # Mostrar información del empleado a eliminar
    nombre_empleado = empleado_encontrado['nombre'].iloc[0]
    print(f"\nEmpleado encontrado: {nombre_empleado} (ID: {id_input})")
    confirmar = input('¿Está seguro de eliminar este empleado? (S/N): ').strip().upper()
    
    if confirmar != 'S':
        print("Operación cancelada")
        return employees_df
    
    # Eliminar empleado usando la misma lógica de normalización
    def normalizar_id(id_val):
        if pd.isna(id_val):
            return None
        if isinstance(id_val, float) and id_val.is_integer():
            return str(int(id_val))
        elif isinstance(id_val, (int, np.integer)):
            return str(id_val)
        else:
            return str(id_val).strip()
    
    ids_normalizados = employees_df['ID'].apply(normalizar_id)
    id_input_normalizado = str(id_input).strip()
    employees_df = employees_df[ids_normalizados != id_input_normalizado]
    
    # Guardar en Excel
    try:
        employees_df.to_excel(employees_file, index=False, engine='openpyxl')
        print(f'\n[OK] Empleado eliminado exitosamente')
        return employees_df
    except Exception as e:
        print(f"[ERROR] Error al guardar el archivo: {e}")
        return None

def modificar_empleado(employees_file="employees_information.xlsx"):
    '''Funcion para modificar la informacion de un empleado de la base de datos'''
    employees_df = leer_empleados_normalizado(employees_file)
    if employees_df is None:
        return None
    
    if employees_df.empty:
        print("[ERROR] No hay empleados en la base de datos")
        return None
    
    # Función auxiliar para buscar empleado por ID (usando la misma lógica de normalización)
    def buscar_empleado_por_id(id_buscado, df):
        """Busca un empleado por ID usando normalización"""
        id_buscado_str = str(id_buscado).strip()
        
        def normalizar_id(id_val):
            if pd.isna(id_val):
                return None
            if isinstance(id_val, float) and id_val.is_integer():
                return str(int(id_val))
            elif isinstance(id_val, (int, np.integer)):
                return str(id_val)
            else:
                return str(id_val).strip()
        
        ids_normalizados = df['ID'].apply(normalizar_id)
        mask = ids_normalizados == id_buscado_str
        return df[mask], mask
    
    print('\nIngrese el ID del empleado a modificar:')
    id_input = input('ID: ').strip()
    
    # Buscar empleado usando la función auxiliar
    empleado_encontrado, mask = buscar_empleado_por_id(id_input, employees_df)
    
    if not mask.any():
        print(f"[ERROR] No se encontró un empleado con ID: {id_input}")
        return None
    
    # Obtener índice del empleado
    indice = empleado_encontrado.index[0]
    empleado_actual = empleado_encontrado.iloc[0]
    
    # Mostrar información actual
    print(f"\nEmpleado encontrado: {empleado_actual['nombre']} (ID: {id_input})")
    print("\nDatos actuales:")
    print(f"  Nombre: {empleado_actual['nombre']}")
    print(f"  Cargo: {empleado_actual['cargo']}")
    print(f"  Salario: {empleado_actual['salario']}")
    print(f"  Número de cuenta: {empleado_actual.get('n_de_cuenta', 'N/A')}")
    print(f"  Banco: {empleado_actual.get('banco', 'N/A')}")
    print(f"  Tipo de cuenta: {empleado_actual.get('tipo_de_cuenta', 'N/A')}")
    print(f"  Fijo: {'Sí' if empleado_actual['fijo'] else 'No'}")
    
    print('\nIngrese los nuevos datos (presione Enter para mantener el valor actual):')
    
    # Solicitar nuevos datos
    nombre = input(f'Nombre [{empleado_actual["nombre"]}]: ').strip()
    if not nombre:
        nombre = empleado_actual['nombre']
    
    cargo = input(f'Cargo [{empleado_actual["cargo"]}]: ').strip()
    if not cargo:
        cargo = empleado_actual['cargo']
    
    salario_str = input(f'Salario [{empleado_actual["salario"]}]: ').strip()
    if not salario_str:
        salario = empleado_actual['salario']
    else:
        try:
            salario = float(salario_str)
        except ValueError:
            print("[ERROR] El salario debe ser un número válido. Se mantendrá el valor actual.")
            salario = empleado_actual['salario']
    
    n_de_cuenta = input(f'Número de cuenta [{empleado_actual.get("n_de_cuenta", "")}]: ').strip()
    if not n_de_cuenta:
        n_de_cuenta = empleado_actual.get('n_de_cuenta', '')
    
    banco = input(f'Banco [{empleado_actual.get("banco", "")}]: ').strip()
    if not banco:
        banco = empleado_actual.get('banco', '')
    
    tipo_de_cuenta = input(f'Tipo de cuenta [{empleado_actual.get("tipo_de_cuenta", "")}]: ').strip()
    if not tipo_de_cuenta:
        tipo_de_cuenta = empleado_actual.get('tipo_de_cuenta', '')
    
    fijo_str = input(f'Fijo (S/N) [{"S" if empleado_actual["fijo"] else "N"}]: ').strip().upper()
    if not fijo_str:
        fijo_bool = empleado_actual['fijo']
    else:
        fijo_bool = (fijo_str == 'S')
    
    # Modificar el DataFrame usando .loc
    employees_df.loc[indice, 'nombre'] = nombre
    employees_df.loc[indice, 'cargo'] = cargo
    employees_df.loc[indice, 'salario'] = salario
    employees_df.loc[indice, 'n_de_cuenta'] = n_de_cuenta
    employees_df.loc[indice, 'banco'] = banco
    employees_df.loc[indice, 'tipo_de_cuenta'] = tipo_de_cuenta
    employees_df.loc[indice, 'fijo'] = fijo_bool
    
    # Guardar en Excel
    try:
        employees_df.to_excel(employees_file, index=False, engine='openpyxl')
        print(f'\n[OK] Empleado modificado exitosamente')
        return employees_df
    except Exception as e:
        print(f"[ERROR] Error al guardar el archivo: {e}")
        return None

def main():
    '''Funcion principal del sistema de nomina'''
    print('\n¿Qué desea hacer?')
    print('1. Calcular nomina quincenal')
    print('2. Agregar empleado')
    print('3. Eliminar empleado')
    print('4. Modificar empleado')
    print('5. Salir')
    opcion = input('Ingrese la opcion: ')
    if opcion == '1':
        print('Calculando nomina quincenal...')
        result = calculate_payroll_quincenal(
            employees_file="employees_information.xlsx",
            hours_file="hours_worked.xlsx",
            output_file=None,
            quincena_fecha=None)
        if result is not None:
            print('Nomina quincenal calculada exitosamente')
        else:
            print('Error al calcular nomina quincenal')
    elif opcion == '2':
        print('Agregando empleado...')
        agregar_empleado()
    elif opcion == '3':
        print('Eliminando empleado...')
        eliminar_empleado()
    elif opcion == '4':
        print('Modificando empleado...')
        modificar_empleado()
    elif opcion == '5':
        print('Saliendo...')
        exit()
    else:
        print('Opcion no valida')
        main()


if __name__ == "__main__":
    main()
