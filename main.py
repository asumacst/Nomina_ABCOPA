import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

DEFAULT_PRESTAMOS_FILE = "prestamos.xlsx"


def _money_to_cents(amount) -> int:
    """
    Convierte un monto (float/str/Decimal) a centavos (int) de forma determinista.
    """
    if amount is None or pd.isna(amount):
        return 0
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)


def _cents_to_money(cents: int) -> float:
    """
    Convierte centavos (int) a dólares (float) para reportes/UI.
    """
    try:
        return float(Decimal(int(cents)) / Decimal(100))
    except Exception:
        return 0.0


def ensure_prestamos_file(prestamos_file: str = DEFAULT_PRESTAMOS_FILE) -> None:
    """
    Crea el archivo de préstamos si no existe.
    Guarda:
      - Hoja 'Prestamos' (estado del préstamo)
      - Hoja 'PagosPrestamo' (bitácora de descuentos aplicados)
    """
    if os.path.exists(prestamos_file):
        return

    prestamos_columns = [
        "loan_id",
        "employee_id",
        "employee_name",
        "fecha_inicio",
        "monto_original_centavos",
        "cuota_quincenal_centavos",
        "saldo_centavos",
        "estado",  # ACTIVO | PAUSADO | CERRADO
        "nota",
        "creado_en",
    ]
    pagos_columns = [
        "payment_id",
        "loan_id",
        "employee_id",
        "tipo_pago",  # NOMINA | MANUAL
        "fecha_pago_nomina",
        "quincena_inicio",
        "quincena_fin",
        "monto_pagado_centavos",
        "saldo_antes_centavos",
        "saldo_despues_centavos",
        "nota",
        "creado_en",
    ]

    prestamos_df = pd.DataFrame(columns=prestamos_columns)
    pagos_df = pd.DataFrame(columns=pagos_columns)

    with pd.ExcelWriter(prestamos_file, engine="openpyxl") as writer:
        prestamos_df.to_excel(writer, sheet_name="Prestamos", index=False)
        pagos_df.to_excel(writer, sheet_name="PagosPrestamo", index=False)


def leer_prestamos(prestamos_file: str = DEFAULT_PRESTAMOS_FILE):
    """
    Lee el archivo `prestamos.xlsx` y normaliza tipos/columnas.

    Returns:
        (prestamos_df, pagos_df)
    """
    ensure_prestamos_file(prestamos_file)

    try:
        xls = pd.ExcelFile(prestamos_file)
        prestamos_df = (
            pd.read_excel(prestamos_file, sheet_name="Prestamos")
            if "Prestamos" in xls.sheet_names
            else pd.DataFrame()
        )
        pagos_df = (
            pd.read_excel(prestamos_file, sheet_name="PagosPrestamo")
            if "PagosPrestamo" in xls.sheet_names
            else pd.DataFrame()
        )
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de préstamos '{prestamos_file}': {e}")
        raise

    # Asegurar columnas mínimas
    prestamos_required = [
        "loan_id",
        "employee_id",
        "employee_name",
        "fecha_inicio",
        "monto_original_centavos",
        "cuota_quincenal_centavos",
        "saldo_centavos",
        "estado",
        "nota",
        "creado_en",
    ]
    for col in prestamos_required:
        if col not in prestamos_df.columns:
            prestamos_df[col] = None

    pagos_required = [
        "payment_id",
        "loan_id",
        "employee_id",
        "tipo_pago",
        "fecha_pago_nomina",
        "quincena_inicio",
        "quincena_fin",
        "monto_pagado_centavos",
        "saldo_antes_centavos",
        "saldo_despues_centavos",
        "nota",
        "creado_en",
    ]
    for col in pagos_required:
        if col not in pagos_df.columns:
            pagos_df[col] = None

    # Normalizar tipos
    for col in ["loan_id", "employee_id", "employee_name", "estado", "nota"]:
        prestamos_df[col] = prestamos_df[col].astype(str).where(prestamos_df[col].notna(), "")
        prestamos_df[col] = prestamos_df[col].astype(str).str.strip()

    if "fecha_inicio" in prestamos_df.columns:
        prestamos_df["fecha_inicio"] = pd.to_datetime(prestamos_df["fecha_inicio"], errors="coerce")
    if "creado_en" in prestamos_df.columns:
        prestamos_df["creado_en"] = pd.to_datetime(prestamos_df["creado_en"], errors="coerce")

    for cent_col in ["monto_original_centavos", "cuota_quincenal_centavos", "saldo_centavos"]:
        prestamos_df[cent_col] = (
            pd.to_numeric(prestamos_df[cent_col], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    if "estado" in prestamos_df.columns:
        prestamos_df["estado"] = prestamos_df["estado"].replace({"": "ACTIVO"}).fillna("ACTIVO")
        prestamos_df["estado"] = prestamos_df["estado"].astype(str).str.upper().str.strip()

    for col in ["payment_id", "loan_id", "employee_id", "tipo_pago", "nota"]:
        pagos_df[col] = pagos_df[col].astype(str).where(pagos_df[col].notna(), "")
        pagos_df[col] = pagos_df[col].astype(str).str.strip()

    if "tipo_pago" in pagos_df.columns:
        pagos_df["tipo_pago"] = pagos_df["tipo_pago"].replace({"": "NOMINA"}).fillna("NOMINA")
        pagos_df["tipo_pago"] = pagos_df["tipo_pago"].astype(str).str.upper().str.strip()

    for date_col in ["fecha_pago_nomina", "quincena_inicio", "quincena_fin", "creado_en"]:
        if date_col in pagos_df.columns:
            pagos_df[date_col] = pd.to_datetime(pagos_df[date_col], errors="coerce")

    for cent_col in ["monto_pagado_centavos", "saldo_antes_centavos", "saldo_despues_centavos"]:
        pagos_df[cent_col] = (
            pd.to_numeric(pagos_df[cent_col], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    return prestamos_df[prestamos_required], pagos_df[pagos_required]


def guardar_prestamos(prestamos_df: pd.DataFrame, pagos_df: pd.DataFrame, prestamos_file: str = DEFAULT_PRESTAMOS_FILE) -> None:
    ensure_prestamos_file(prestamos_file)
    with pd.ExcelWriter(prestamos_file, engine="openpyxl") as writer:
        prestamos_df.to_excel(writer, sheet_name="Prestamos", index=False)
        pagos_df.to_excel(writer, sheet_name="PagosPrestamo", index=False)


def crear_prestamo(
    employee_id,
    employee_name: str,
    monto,
    cuota_quincenal,
    fecha_inicio=None,
    nota: str = "",
    prestamos_file: str = DEFAULT_PRESTAMOS_FILE,
) -> str:
    """
    Crea un préstamo nuevo (estado ACTIVO) y lo guarda en `prestamos.xlsx`.

    Returns:
        loan_id
    """
    prestamos_df, pagos_df = leer_prestamos(prestamos_file)

    employee_id_str = str(employee_id).strip()
    employee_name = (employee_name or "").strip()

    monto_cent = _money_to_cents(monto)
    cuota_cent = _money_to_cents(cuota_quincenal)
    if monto_cent <= 0:
        raise ValueError("El monto del préstamo debe ser mayor a 0")
    if cuota_cent <= 0:
        raise ValueError("La cuota quincenal debe ser mayor a 0")
    if cuota_cent > monto_cent:
        raise ValueError("La cuota quincenal no puede ser mayor al monto del préstamo")

    fecha_inicio_dt = pd.to_datetime(fecha_inicio, errors="coerce") if fecha_inicio is not None else pd.Timestamp(datetime.now().date())
    if pd.isna(fecha_inicio_dt):
        raise ValueError("Fecha de inicio inválida")

    loan_id = f"LN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
    creado_en = pd.Timestamp(datetime.now())

    nuevo = {
        "loan_id": loan_id,
        "employee_id": employee_id_str,
        "employee_name": employee_name,
        "fecha_inicio": fecha_inicio_dt,
        "monto_original_centavos": monto_cent,
        "cuota_quincenal_centavos": cuota_cent,
        "saldo_centavos": monto_cent,
        "estado": "ACTIVO",
        "nota": (nota or "").strip(),
        "creado_en": creado_en,
    }

    prestamos_df = pd.concat([prestamos_df, pd.DataFrame([nuevo])], ignore_index=True)
    guardar_prestamos(prestamos_df, pagos_df, prestamos_file)
    return loan_id


def actualizar_estado_prestamo(loan_id: str, nuevo_estado: str, prestamos_file: str = DEFAULT_PRESTAMOS_FILE) -> None:
    prestamos_df, pagos_df = leer_prestamos(prestamos_file)
    loan_id = str(loan_id).strip()
    nuevo_estado = str(nuevo_estado).strip().upper()
    if nuevo_estado not in {"ACTIVO", "PAUSADO", "CERRADO"}:
        raise ValueError("Estado inválido (use ACTIVO, PAUSADO o CERRADO)")

    mask = prestamos_df["loan_id"].astype(str).str.strip() == loan_id
    if not mask.any():
        raise ValueError(f"No se encontró el préstamo con loan_id={loan_id}")

    prestamos_df.loc[mask, "estado"] = nuevo_estado
    guardar_prestamos(prestamos_df, pagos_df, prestamos_file)


def cerrar_prestamo(loan_id: str, condonar: bool = False, prestamos_file: str = DEFAULT_PRESTAMOS_FILE) -> None:
    """
    Cierra un préstamo. Si `condonar=True`, pone el saldo en 0.
    """
    prestamos_df, pagos_df = leer_prestamos(prestamos_file)
    loan_id = str(loan_id).strip()
    mask = prestamos_df["loan_id"].astype(str).str.strip() == loan_id
    if not mask.any():
        raise ValueError(f"No se encontró el préstamo con loan_id={loan_id}")

    if condonar:
        prestamos_df.loc[mask, "saldo_centavos"] = 0
    prestamos_df.loc[mask, "estado"] = "CERRADO"
    guardar_prestamos(prestamos_df, pagos_df, prestamos_file)


def obtener_prestamos(prestamos_file: str = DEFAULT_PRESTAMOS_FILE) -> pd.DataFrame:
    prestamos_df, _ = leer_prestamos(prestamos_file)
    return prestamos_df.copy()


def obtener_pagos_prestamo(
    prestamos_file: str = DEFAULT_PRESTAMOS_FILE,
    loan_id: Optional[str] = None,
    employee_id: Optional[str] = None,
) -> pd.DataFrame:
    _, pagos_df = leer_prestamos(prestamos_file)
    df = pagos_df.copy()
    if loan_id:
        df = df[df["loan_id"].astype(str).str.strip() == str(loan_id).strip()]
    if employee_id:
        df = df[df["employee_id"].astype(str).str.strip() == str(employee_id).strip()]
    df = df.sort_values(["fecha_pago_nomina", "creado_en"], na_position="last")
    return df


def aplicar_descuento_prestamos_en_memoria(
    prestamos_df: pd.DataFrame,
    pagos_df: pd.DataFrame,
    employee_id,
    employee_name: str,
    fecha_pago,
    quincena_inicio=None,
    quincena_fin=None,
    max_descuento_centavos: Optional[int] = None,
):
    """
    Aplica el descuento de préstamos (si existen) para un empleado.
    Modifica `prestamos_df` y `pagos_df` en memoria (sin guardar).

    Returns:
        (descuento_total_centavos, saldo_total_centavos, pagos_df_actualizado)
    """
    employee_id_str = str(employee_id).strip()
    employee_name = (employee_name or "").strip()

    fecha_pago_dt = pd.to_datetime(fecha_pago, errors="coerce")
    if pd.isna(fecha_pago_dt):
        return 0, 0, pagos_df

    quincena_inicio_dt = pd.to_datetime(quincena_inicio, errors="coerce") if quincena_inicio is not None else pd.NaT
    quincena_fin_dt = pd.to_datetime(quincena_fin, errors="coerce") if quincena_fin is not None else pd.NaT

    df_emp = prestamos_df[
        (prestamos_df["employee_id"].astype(str).str.strip() == employee_id_str)
        & (prestamos_df["estado"].astype(str).str.upper().str.strip() == "ACTIVO")
        & (prestamos_df["saldo_centavos"] > 0)
    ].copy()

    if df_emp.empty:
        saldo_total = prestamos_df[
            (prestamos_df["employee_id"].astype(str).str.strip() == employee_id_str)
            & (prestamos_df["estado"].astype(str).str.upper().str.strip().isin(["ACTIVO", "PAUSADO"]))
        ]["saldo_centavos"].sum()
        return 0, int(saldo_total) if pd.notna(saldo_total) else 0, pagos_df

    # Solo préstamos cuya fecha_inicio sea <= fecha_pago
    df_emp["fecha_inicio"] = pd.to_datetime(df_emp["fecha_inicio"], errors="coerce")
    df_emp = df_emp[df_emp["fecha_inicio"].notna() & (df_emp["fecha_inicio"] <= fecha_pago_dt)]
    if df_emp.empty:
        saldo_total = prestamos_df[
            (prestamos_df["employee_id"].astype(str).str.strip() == employee_id_str)
            & (prestamos_df["estado"].astype(str).str.upper().str.strip().isin(["ACTIVO", "PAUSADO"]))
        ]["saldo_centavos"].sum()
        return 0, int(saldo_total) if pd.notna(saldo_total) else 0, pagos_df

    df_emp = df_emp.sort_values(["fecha_inicio", "creado_en"], na_position="last")

    disponible = int(max_descuento_centavos) if max_descuento_centavos is not None else 10**18
    descuento_total = 0
    now_ts = pd.Timestamp(datetime.now())
    nuevos_pagos = []

    # Evitar doble descuento NOMINA si se recalcula la misma quincena (idempotencia por loan_id + fecha_pago_nomina)
    existing_keys = set()
    try:
        if (
            pagos_df is not None
            and (not pagos_df.empty)
            and ("loan_id" in pagos_df.columns)
            and ("fecha_pago_nomina" in pagos_df.columns)
        ):
            # Solo bloquear duplicados de pagos tipo NOMINA
            if "tipo_pago" in pagos_df.columns:
                tmp = pagos_df[["loan_id", "fecha_pago_nomina", "tipo_pago"]].copy()
                tmp["tipo_pago"] = tmp["tipo_pago"].astype(str).str.upper().str.strip().replace({"": "NOMINA"})
                tmp = tmp[tmp["tipo_pago"] == "NOMINA"]
            else:
                tmp = pagos_df[["loan_id", "fecha_pago_nomina"]].copy()
            tmp["loan_id"] = tmp["loan_id"].astype(str).str.strip()
            tmp["fecha_pago_nomina"] = pd.to_datetime(tmp["fecha_pago_nomina"], errors="coerce").dt.normalize()
            tmp = tmp.dropna(subset=["loan_id", "fecha_pago_nomina"])
            existing_keys = set(zip(tmp["loan_id"], tmp["fecha_pago_nomina"].astype("datetime64[ns]")))
    except Exception:
        existing_keys = set()
    fecha_pago_key = fecha_pago_dt.normalize().to_datetime64()

    for _, loan in df_emp.iterrows():
        if disponible <= 0:
            break

        loan_id = str(loan["loan_id"]).strip()
        if (loan_id, fecha_pago_key) in existing_keys:
            # Ya se registró un pago para este préstamo en esta fecha de nómina
            continue
        saldo = int(loan["saldo_centavos"]) if pd.notna(loan["saldo_centavos"]) else 0
        cuota = int(loan["cuota_quincenal_centavos"]) if pd.notna(loan["cuota_quincenal_centavos"]) else 0
        if saldo <= 0 or cuota <= 0:
            continue

        pagar = min(cuota, saldo, disponible)
        if pagar <= 0:
            continue

        # Actualizar préstamo en DF principal
        mask = prestamos_df["loan_id"].astype(str).str.strip() == loan_id
        saldo_antes = int(prestamos_df.loc[mask, "saldo_centavos"].iloc[0])
        saldo_despues = max(0, saldo_antes - pagar)
        prestamos_df.loc[mask, "saldo_centavos"] = saldo_despues
        if saldo_despues == 0:
            prestamos_df.loc[mask, "estado"] = "CERRADO"
        if employee_name and (prestamos_df.loc[mask, "employee_name"].astype(str).str.strip() == "").any():
            prestamos_df.loc[mask, "employee_name"] = employee_name

        payment_id = f"PM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        nuevos_pagos.append(
            {
                "payment_id": payment_id,
                "loan_id": loan_id,
                "employee_id": employee_id_str,
                "tipo_pago": "NOMINA",
                "fecha_pago_nomina": fecha_pago_dt,
                "quincena_inicio": quincena_inicio_dt,
                "quincena_fin": quincena_fin_dt,
                "monto_pagado_centavos": int(pagar),
                "saldo_antes_centavos": int(saldo_antes),
                "saldo_despues_centavos": int(saldo_despues),
                "nota": "",
                "creado_en": now_ts,
            }
        )
        existing_keys.add((loan_id, fecha_pago_key))

        descuento_total += pagar
        disponible -= pagar

    if nuevos_pagos:
        pagos_df = pd.concat([pagos_df, pd.DataFrame(nuevos_pagos)], ignore_index=True)

    saldo_total = prestamos_df[
        (prestamos_df["employee_id"].astype(str).str.strip() == employee_id_str)
        & (prestamos_df["estado"].astype(str).str.upper().str.strip().isin(["ACTIVO", "PAUSADO"]))
    ]["saldo_centavos"].sum()

    return int(descuento_total), int(saldo_total) if pd.notna(saldo_total) else 0, pagos_df


def registrar_pago_manual_prestamo(
    loan_id: str,
    monto,
    fecha_pago=None,
    nota: str = "",
    prestamos_file: str = DEFAULT_PRESTAMOS_FILE,
) -> None:
    """
    Registra un pago manual a un préstamo:
      - Actualiza saldo
      - Registra en 'PagosPrestamo' con tipo_pago='MANUAL'
      - Cierra el préstamo si llega a 0
    """
    prestamos_df, pagos_df = leer_prestamos(prestamos_file)
    loan_id = str(loan_id).strip()

    mask = prestamos_df["loan_id"].astype(str).str.strip() == loan_id
    if not mask.any():
        raise ValueError(f"No se encontró el préstamo con loan_id={loan_id}")

    estado = str(prestamos_df.loc[mask, "estado"].iloc[0]).strip().upper()
    saldo_antes = int(prestamos_df.loc[mask, "saldo_centavos"].iloc[0])
    if saldo_antes <= 0:
        raise ValueError("Este préstamo ya no tiene saldo.")
    if estado == "CERRADO":
        raise ValueError("Este préstamo está cerrado.")

    monto_cent = _money_to_cents(monto)
    if monto_cent <= 0:
        raise ValueError("El monto del pago debe ser mayor a 0")
    if monto_cent > saldo_antes:
        raise ValueError("El monto del pago no puede ser mayor al saldo pendiente")

    fecha_pago_dt = pd.to_datetime(fecha_pago, errors="coerce") if fecha_pago is not None else pd.Timestamp(datetime.now().date())
    if pd.isna(fecha_pago_dt):
        raise ValueError("Fecha de pago inválida")

    saldo_despues = saldo_antes - monto_cent
    prestamos_df.loc[mask, "saldo_centavos"] = saldo_despues
    if saldo_despues == 0:
        prestamos_df.loc[mask, "estado"] = "CERRADO"

    employee_id = str(prestamos_df.loc[mask, "employee_id"].iloc[0]).strip()

    payment_id = f"PM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
    now_ts = pd.Timestamp(datetime.now())
    nuevo_pago = {
        "payment_id": payment_id,
        "loan_id": loan_id,
        "employee_id": employee_id,
        "tipo_pago": "MANUAL",
        "fecha_pago_nomina": fecha_pago_dt,
        "quincena_inicio": pd.NaT,
        "quincena_fin": pd.NaT,
        "monto_pagado_centavos": int(monto_cent),
        "saldo_antes_centavos": int(saldo_antes),
        "saldo_despues_centavos": int(saldo_despues),
        "nota": (nota or "").strip(),
        "creado_en": now_ts,
    }

    pagos_df = pd.concat([pagos_df, pd.DataFrame([nuevo_pago])], ignore_index=True)
    guardar_prestamos(prestamos_df, pagos_df, prestamos_file)

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
    },
    2031: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-25": "Martes de Carnaval",
        "04-11": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2032: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-10": "Martes de Carnaval",
        "03-26": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2033: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "03-01": "Martes de Carnaval",
        "04-15": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2034: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-21": "Martes de Carnaval",
        "04-07": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
        "11-04": "Día de los Símbolos Patrios", "11-05": "Grito de Colón", "11-10": "Grito de Los Santos",
        "11-28": "Independencia de España", "12-08": "Día de las Madres", "12-20": "Día de los Caídos (Invasión)",
        "12-25": "Navidad"
    },
    2035: {
        "01-01": "Año Nuevo", "01-09": "Día de los Mártires", "02-06": "Martes de Carnaval",
        "03-23": "Viernes Santo", "05-01": "Día del Trabajo", "11-03": "Separación de Panamá de Colombia",
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

def leer_reporte_asistencia(archivo="Reporte de Asistencia.xlsx"):
    """
    Lee el archivo de Reporte de Asistencia del escáner biométrico y lo convierte
    al formato esperado por el sistema.
    
    Args:
        archivo: Ruta al archivo Excel del reporte de asistencia
        
    Returns:
        DataFrame con columnas: ID, nombre, fecha, hora
    """
    try:
        # Leer el archivo sin encabezados primero para encontrar la fila de encabezados
        df_raw = pd.read_excel(archivo, header=None)
        
        # Buscar la fila que contiene los encabezados (First Name, Last Name, ID, Date, Time)
        header_row = None
        for idx, row in df_raw.iterrows():
            if pd.notna(row[0]) and str(row[0]).strip() == 'First Name':
                header_row = idx
                break
        
        if header_row is None:
            raise ValueError("No se encontró la fila de encabezados en el archivo")
        
        # Leer el archivo con los encabezados correctos
        df = pd.read_excel(archivo, header=header_row)
        
        # Limpiar nombres de columnas (eliminar espacios extra)
        df.columns = df.columns.str.strip()
        
        # Verificar que las columnas necesarias existan
        required_columns = ['First Name', 'Last Name', 'ID', 'Date', 'Time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
        
        # Crear el DataFrame en el formato esperado
        result_df = pd.DataFrame()
        
        # Combinar First Name y Last Name para crear el nombre completo
        result_df['nombre'] = (df['First Name'].astype(str).str.strip() + ' ' + 
                              df['Last Name'].astype(str).str.strip()).str.strip()
        
        # ID - normalizar: convertir a string y eliminar espacios
        # Si el ID es un número float (ej: 170660927.0), convertirlo a int primero
        def normalizar_id(id_val):
            if pd.isna(id_val):
                return None
            # Si es float y es entero, convertir a int
            if isinstance(id_val, float) and id_val.is_integer():
                return str(int(id_val))
            # Convertir a string y limpiar
            return str(id_val).strip()
        
        result_df['ID'] = df['ID'].apply(normalizar_id)
        
        # Fecha - convertir a datetime
        result_df['fecha'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Hora - convertir a string en formato HH:MM
        # Si es datetime.time, convertir a formato HH:MM
        def convertir_hora(time_val):
            if pd.isna(time_val):
                return None
            # Si es datetime.time, convertir a string HH:MM
            if isinstance(time_val, pd.Timestamp):
                return time_val.strftime('%H:%M')
            elif hasattr(time_val, 'hour') and hasattr(time_val, 'minute'):
                # Es un objeto time
                return f"{time_val.hour:02d}:{time_val.minute:02d}"
            else:
                # Es string, intentar parsearlo
                time_str = str(time_val).strip()
                # Si tiene formato HH:MM:SS, tomar solo HH:MM
                if ':' in time_str:
                    parts = time_str.split(':')
                    return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
                return time_str
        
        result_df['hora'] = df['Time'].apply(convertir_hora)
        
        # Eliminar filas con datos inválidos (fechas, horas o IDs nulos)
        result_df = result_df.dropna(subset=['fecha', 'hora', 'ID', 'nombre'])
        
        # Filtrar filas donde la hora no sea válida (debe tener formato HH:MM)
        mask = result_df['hora'].str.match(r'^\d{1,2}:\d{2}$', na=False)
        result_df = result_df[mask]
        
        # Filtrar filas donde el nombre no sea válido (no debe ser 'nan' o vacío)
        mask = (result_df['nombre'] != 'nan') & (result_df['nombre'].str.len() > 0)
        result_df = result_df[mask]
        
        # Resetear índice
        result_df = result_df.reset_index(drop=True)
        
        print(f"[OK] Archivo de asistencia leído: {len(result_df)} registros procesados")
        
        return result_df
        
    except Exception as e:
        print(f"[ERROR] Error al leer el archivo de asistencia: {e}")
        raise


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
    # El archivo de asistencia usa formato YYYY-MM-DD, pero también puede venir en otros formatos
    if not pd.api.types.is_datetime64_any_dtype(hours_df['fecha']):
        # Intentar primero con formato del reporte de asistencia (YYYY-MM-DD)
        hours_df['fecha'] = pd.to_datetime(hours_df['fecha'], errors='coerce')
        # Si hay valores nulos, intentar con formato DD/MM/YYYY
        if hours_df['fecha'].isna().any():
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
            
            # NORMALIZAR HORA DE ENTRADA (regla de 7:00 AM)
            # - Si llega ANTES de las 7:00 AM: se registra como 7:00 AM (sin importar la hora)
            # - Si llega entre 7:00 y 7:05 AM (incluyente): se registra como 7:00 AM
            # - Después de 7:05 AM: se registra la hora real (para que aplique descuento/retardo)
            if entrada_hour_final < 7:
                entrada_hour_final = 7
                entrada_minute = 0
            elif entrada_hour_final == 7 and entrada_minute <= 5:
                entrada_minute = 0
            
            # Calcular horas extra
            # - Días normales (lunes a viernes): después de las 3 PM / 15:00
            # - Sábados: después de las 12 PM / 12:00 (mediodía)
            # - Domingos y feriados: no aplica (se pagan con 50% adicional)
            horas_extra = 0.0
            
            # Verificar si es sábado (weekday() devuelve 5 para sábado)
            es_sabado = date.weekday() == 5 if isinstance(date, pd.Timestamp) else date.weekday() == 5
            
            # Determinar la hora límite para horas extra
            if es_sabado:
                hora_limite_extra = 12  # Sábados: después de las 12 PM
            else:
                hora_limite_extra = 15  # Días normales: después de las 3 PM
            
            # APLICAR MARGEN DE ERROR DE 10 MINUTOS PARA LA SALIDA
            # Si la salida está dentro del rango de 10 minutos después de la hora límite,
            # se cuenta como si salió exactamente a la hora límite (sin horas extra)
            salida_hour_ajustada = salida_hour_final
            salida_minute_ajustada = salida_minute
            
            # Verificar si está dentro del margen de 10 minutos
            if salida_hour_final == hora_limite_extra and salida_minute <= 10:
                # Sale entre la hora límite y 10 minutos después: se cuenta como salida exacta a la hora límite
                salida_hour_ajustada = hora_limite_extra
                salida_minute_ajustada = 0
                # No hay horas extra en este caso
                horas_extra = 0.0
            elif salida_hour_final > hora_limite_extra or (salida_hour_final == hora_limite_extra and salida_minute > 10):
                # Sale después del margen de 10 minutos: SÍ hay horas extra
                # Las horas extra se cuentan desde la hora límite exacta (no desde hora_limite + 10 min)
                if entrada_hour_final < hora_limite_extra:
                    # La entrada fue antes de la hora límite
                    # Calcular horas extra desde la hora límite exacta
                    horas_extra = salida_hour_final - hora_limite_extra
                    # Agregar los minutos de la salida (estos SÍ cuentan como horas extra)
                    if salida_minute > 0:
                        horas_extra += salida_minute / 60.0
                elif entrada_hour_final == hora_limite_extra:
                    # La entrada fue exactamente a la hora límite
                    # Calcular horas extra desde la hora límite
                    horas_extra = salida_hour_final - hora_limite_extra
                    if salida_minute > entrada_minute:
                        horas_extra += (salida_minute - entrada_minute) / 60.0
                else:
                    # La entrada fue después de la hora límite, todas las horas son extra
                    # Pero primero necesitamos calcular horas_trabajadas
                    pass
            
            # Crear objetos datetime (usar horas ajustadas para el cálculo de horas trabajadas)
            date_obj = date.date() if isinstance(date, pd.Timestamp) else date
            entrada = datetime.combine(date_obj, 
                                      datetime.min.time().replace(hour=entrada_hour_final, minute=entrada_minute))
            # Para el cálculo de horas trabajadas, usar la salida ajustada si aplicó el margen
            salida_para_calculo = datetime.combine(date_obj, 
                                                   datetime.min.time().replace(hour=salida_hour_ajustada, minute=salida_minute_ajustada))
            
            # Si la salida es antes que la entrada, asumir que es del día siguiente (turno nocturno)
            if salida_para_calculo < entrada:
                salida_para_calculo = salida_para_calculo + timedelta(days=1)
            
            # Calcular horas trabajadas usando las horas ajustadas
            horas_trabajadas = (salida_para_calculo - entrada).total_seconds() / 3600
            
            # Si la entrada fue después de la hora límite y hay horas extra, calcular correctamente
            if entrada_hour_final > hora_limite_extra or (entrada_hour_final == hora_limite_extra and entrada_minute > 10):
                # La entrada fue después de la hora límite, todas las horas son extra
                horas_extra = horas_trabajadas
            
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
                                 hours_file="Reporte de Asistencia.xlsx",
                                 output_file=None,
                                 quincena_fecha=None,
                                 prestamos_file: str = DEFAULT_PRESTAMOS_FILE):
    """
    Calcula la nómina quincenal para todos los empleados de UNA quincena específica.
    
    Args:
        employees_file: Archivo Excel con información de empleados
        hours_file: Archivo Excel del reporte de asistencia del escáner biométrico
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
    
    # Leer archivo de horas trabajadas desde el reporte de asistencia
    print(f"\nLeyendo reporte de asistencia desde: {hours_file}")
    try:
        hours_df = leer_reporte_asistencia(hours_file)
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

    # Determinar fecha de pago según la quincena (se usa también para préstamos)
    if quincena_inicio_target.day == 1:
        # Primera quincena: pago el día 15
        fecha_pago = quincena_inicio_target.replace(day=15)
    else:
        # Segunda quincena: pago el último día del mes
        if quincena_inicio_target.month == 12:
            fecha_pago = quincena_inicio_target.replace(day=31)
        else:
            siguiente_mes = quincena_inicio_target.replace(month=quincena_inicio_target.month + 1, day=1)
            fecha_pago = siguiente_mes - timedelta(days=1)
    
    # Filtrar solo los datos de la quincena objetivo
    daily_hours_df = daily_hours_df[daily_hours_df['quincena_inicio'] == quincena_inicio_target]
    
    if daily_hours_df.empty:
        print(f"[ERROR] No se encontraron datos para la quincena del {quincena_inicio_target.strftime('%d/%m/%Y')} a {quincena_fin_target.strftime('%d/%m/%Y')}")
        return None
    
    print(f"[OK] Encontrados datos para {len(daily_hours_df)} días en esta quincena")
    
    def get_column_value(row, candidates, default=None):
        """Obtiene el primer valor disponible de una lista de columnas."""
        for col in candidates:
            if col in row and pd.notna(row[col]):
                return row[col]
        return default

    def parse_bool(value):
        """Normaliza valores de contrato a booleano."""
        if pd.isna(value):
            return False
        if isinstance(value, (int, float, np.integer)):
            return value != 0
        text = str(value).strip().lower()
        return text in ['s', 'si', 'sí', 'y', 'yes', 'true', '1']

    # Crear diccionario de empleados para acceso rápido
    employees_dict = {}
    for _, emp in employees_df.iterrows():
        contrato_val = get_column_value(
            emp,
            ['Empleado por contrato', 'empleado_por_contrato', 'empleado por contrato'],
            default=False
        )
        isl_val = get_column_value(emp, ['ISL', 'isl', 'Impuesto sobre la renta'], default=0)
        try:
            isl_val = float(isl_val) if pd.notna(isl_val) else 0.0
        except (TypeError, ValueError):
            isl_val = 0.0
        # Usar ID como clave principal, pero también nombre como alternativa
        employees_dict[str(emp['ID'])] = {
            'nombre': emp['nombre'],
            'salario_fijo': bool(emp.get('salario_fijo', False)),
            'empleado_fijo': bool(emp.get('empleado_fijo', False)),
            'salario_minimo': float(emp.get('salario_minimo', 0)) if pd.notna(emp.get('salario_minimo')) else 0.0,
            'salario': float(emp['salario']) if pd.notna(emp['salario']) else 0.0,
            'cargo': emp.get('cargo', ''),
            'n_de_cuenta': emp.get('n_de_cuenta', ''),
            'banco': emp.get('banco', ''),
            'tipo_de_cuenta': emp.get('tipo_de_cuenta', ''),
            'empleado_por_contrato': parse_bool(contrato_val),
            'isl': isl_val
        }
    
    # Calcular nómina por quincena (solo una quincena ahora)
    print("\nCalculando nómina...")
    payroll_results = []

    # Cargar préstamos una sola vez (si existe el archivo)
    prestamos_enabled = True
    any_prestamo_changes = False
    try:
        prestamos_df, pagos_df = leer_prestamos(prestamos_file)
    except Exception:
        prestamos_enabled = False
        prestamos_df, pagos_df = pd.DataFrame(), pd.DataFrame()
        print(f"[ADVERTENCIA] No se pudo cargar '{prestamos_file}'. Se omitirá el descuento de préstamos.")
    
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
        
        # Inicializar variables de pago
        pago_extra = 0.0
        pago_feriado_domingo = 0.0
        bono_horas_extra = 0.0
        
        # Calcular pago según el tipo de empleado
        if emp_info['salario_fijo']:
            # Empleado con salario fijo: recibe el mismo salario sin importar horas (no recibe pago extra)
            pago_quincenal = emp_info['salario'] / 2  # Salario mensual dividido en 2 quincenas
            pago_extra = 0.0  # Los empleados con salario fijo no reciben pago extra
            pago_feriado_domingo = 0.0  # Los empleados con salario fijo no reciben pago extra por feriados/domingos
            tipo_pago = "Salario Fijo"
        elif emp_info['empleado_fijo']:
            # Empleado fijo con sueldo mínimo: cobra salario mínimo garantizado + bono por horas extra
            salario_minimo = emp_info['salario_minimo']
            salario_por_hora = emp_info['salario']
            
            # Calcular horas requeridas para el salario mínimo (mensual)
            # Para la quincena, necesitamos las horas requeridas quincenales
            if salario_por_hora > 0:
                horas_requeridas_mensual = salario_minimo / salario_por_hora
                horas_requeridas_quincenal = horas_requeridas_mensual / 2  # Dividir entre 2 quincenas
            else:
                horas_requeridas_quincenal = 0
            
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
            
            # Pago base: salario mínimo garantizado (quincenal)
            pago_base = salario_minimo / 2  # Salario mínimo mensual dividido en 2 quincenas
            
            # Calcular horas trabajadas totales para determinar el bono
            # IMPORTANTE: El bono NO debe incluir las horas extra después de 3 PM (o 12 PM en sábados)
            # porque esas horas ya se pagan con 25% adicional por separado
            # El bono se calcula solo sobre horas normales + horas en feriados/domingos
            horas_para_bono = horas_normales + horas_feriado_domingo
            
            # Bono por horas extra: si trabajó más de las horas requeridas, se paga como bono adicional
            # El bono se calcula solo sobre horas normales (sin horas extra después 3 PM) y se paga a precio normal
            horas_extra_para_bono = max(0, horas_para_bono - horas_requeridas_quincenal)
            bono_horas_extra = horas_extra_para_bono * salario_por_hora
            
            # Pago extra: 25% adicional sobre el salario por hora para horas después de las 3 PM en días normales
            salario_hora_extra = salario_por_hora * 1.25
            pago_extra = salario_hora_extra * horas_extra_normales
            
            # Pago feriado/domingo: 50% adicional sobre el salario por hora para TODAS las horas trabajadas en feriados/domingos
            salario_hora_feriado_domingo = salario_por_hora * 1.50
            pago_feriado_domingo = salario_hora_feriado_domingo * horas_feriado_domingo
            
            # Pago total: salario mínimo + bono por horas extra + pago extra (25%) + pago feriado/domingo (50%)
            pago_quincenal = pago_base + bono_horas_extra + pago_extra + pago_feriado_domingo
            tipo_pago = "Empleado Fijo"
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
        
        # Calcular descuentos por contrato
        seguro_social = 0.0
        seguro_educativo = 0.0
        descuento_isl = 0.0
        if emp_info['empleado_por_contrato']:
            seguro_social = pago_quincenal * 0.0975
            seguro_educativo = pago_quincenal * 0.0125
            descuento_isl = emp_info['isl']
        total_descuentos_base = seguro_social + seguro_educativo + descuento_isl

        # Descuento por préstamos (si aplica). Se capea para no dejar neto negativo.
        descuento_prestamo = 0.0
        saldo_prestamo_total = 0.0
        if prestamos_enabled:
            try:
                pago_cent = _money_to_cents(pago_quincenal)
                base_desc_cent = _money_to_cents(total_descuentos_base)
                max_prestamo_cent = max(0, pago_cent - base_desc_cent)
                prestamo_cent, saldo_total_cent, pagos_df = aplicar_descuento_prestamos_en_memoria(
                    prestamos_df,
                    pagos_df,
                    employee_id_str,
                    emp_info['nombre'],
                    fecha_pago,
                    quincena_inicio,
                    quincena_fin,
                    max_prestamo_cent,
                )
                descuento_prestamo = _cents_to_money(prestamo_cent)
                saldo_prestamo_total = _cents_to_money(saldo_total_cent)
                if prestamo_cent > 0:
                    any_prestamo_changes = True
            except Exception as e:
                print(f"[ADVERTENCIA] No se pudo aplicar préstamo para empleado {employee_id_str}: {e}")

        total_descuentos = total_descuentos_base + descuento_prestamo

        # Preparar datos para el resultado
        resultado = {
            'ID': employee_id,
            'Nombre': emp_info['nombre'],
            'Cargo': emp_info['cargo'],
            'Tipo': tipo_pago,
            'Salario Fijo': 'Sí' if emp_info['salario_fijo'] else 'No',
            'Empleado Fijo': 'Sí' if emp_info['empleado_fijo'] else 'No',
            'Empleado por contrato': 'Sí' if emp_info['empleado_por_contrato'] else 'No',
            'Salario Base': emp_info['salario'],
            'Quincena Inicio': quincena_inicio.strftime('%d/%m/%Y'),
            'Quincena Fin': quincena_fin.strftime('%d/%m/%Y'),
            'Total Horas Trabajadas': round(total_horas, 2),
            'Horas Extra (después 3 PM)': round(total_horas_extra, 2),
            'Pago Extra (25% adicional)': round(pago_extra, 2),
            'Pago Quincenal': round(pago_quincenal, 2),
            'Seguro Social (9.75%)': round(seguro_social, 2),
            'Seguro Educativo (1.25%)': round(seguro_educativo, 2),
            'ISL': round(descuento_isl, 2),
            'Descuento Préstamo': round(descuento_prestamo, 2),
            'Total Descuentos': round(total_descuentos, 2),
            'Total Saldo Préstamo': round(saldo_prestamo_total, 2),
            'Número de Cuenta': emp_info['n_de_cuenta'],
            'Banco': emp_info['banco'],
            'Tipo de Cuenta': emp_info['tipo_de_cuenta']
        }
        
        # Agregar información de feriados/domingos y bono
        horas_feriado_domingo_total = group[group['es_feriado_domingo'] == True]['horas_trabajadas'].sum()
        resultado['Horas Feriado/Domingo'] = round(horas_feriado_domingo_total, 2)
        resultado['Pago Feriado/Domingo (50% adicional)'] = round(pago_feriado_domingo, 2)
        resultado['Bono Horas Extra'] = round(bono_horas_extra, 2)
        
        payroll_results.append(resultado)
    
    if not payroll_results:
        print("[ERROR] No se pudo calcular la nomina. Verifique los datos.")
        return None
    
    # Crear DataFrame con resultados
    payroll_df = pd.DataFrame(payroll_results)
    
    # Ordenar por nombre
    payroll_df = payroll_df.sort_values(['Nombre'])

    # Guardar cambios de préstamos si se aplicaron descuentos
    if prestamos_enabled and any_prestamo_changes:
        try:
            guardar_prestamos(prestamos_df, pagos_df, prestamos_file)
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudieron guardar los cambios en préstamos: {e}")
    
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
    if 'Bono Horas Extra' in payroll_df.columns:
        print(f"Total bono horas extra: ${payroll_df['Bono Horas Extra'].sum():,.2f}")
    print(f"Total horas feriado/domingo: {payroll_df['Horas Feriado/Domingo'].sum():.2f}")
    print(f"Total pago feriado/domingo (50% adicional): ${payroll_df['Pago Feriado/Domingo (50% adicional)'].sum():,.2f}")
    
    # Agregar columna de fecha de pago al DataFrame
    payroll_df['Fecha de Pago'] = fecha_pago.strftime('%d/%m/%Y')
    
    # Reordenar columnas: renombrar pago quincenal a total neto
    if 'Pago Quincenal' in payroll_df.columns:
        payroll_df = payroll_df.rename(columns={'Pago Quincenal': 'Total Pago a Empleados'})
        if 'Total Descuentos' in payroll_df.columns:
            payroll_df['Total Pago a Empleados'] = payroll_df['Total Pago a Empleados'] - payroll_df['Total Descuentos']
    
    # Mostrar total a pagar usando el nuevo nombre de columna
    if 'Total Pago a Empleados' in payroll_df.columns:
        total_pagar = payroll_df['Total Pago a Empleados'].sum()
    else:
        total_pagar = payroll_df['Pago Quincenal'].sum() if 'Pago Quincenal' in payroll_df.columns else 0
    
    print(f"Total a pagar: ${total_pagar:,.2f}")
    print("="*80)
    
    # Definir orden de columnas (sin "Total Pago a Empleados" que va al final)
    columnas = ['ID', 'Nombre', 'Cargo', 'Tipo', 'Salario Fijo', 'Empleado Fijo', 'Empleado por contrato',
                'Salario Base', 
                'Quincena Inicio', 'Quincena Fin', 'Fecha de Pago',
                'Total Horas Trabajadas', 'Horas Extra (después 3 PM)', 
                'Pago Extra (25% adicional)', 'Bono Horas Extra', 'Horas Feriado/Domingo',
                'Pago Feriado/Domingo (50% adicional)', 
                'Seguro Social (9.75%)', 'Seguro Educativo (1.25%)', 'ISL', 'Descuento Préstamo', 'Total Descuentos', 'Total Saldo Préstamo',
                'Número de Cuenta', 'Banco', 'Tipo de Cuenta']
    
    # Solo incluir columnas que existen en el DataFrame
    columnas_existentes = [col for col in columnas if col in payroll_df.columns]
    
    # Agregar "Total Pago a Empleados" al final si existe
    if 'Total Pago a Empleados' in payroll_df.columns:
        columnas_existentes.append('Total Pago a Empleados')
    
    # Reordenar DataFrame
    payroll_df = payroll_df[columnas_existentes]
    
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
    salario_str = input('Salario (por hora): ').strip()
    n_de_cuenta = input('Numero de cuenta: ').strip()
    banco = input('Banco: ').strip()
    tipo_de_cuenta = input('Tipo de cuenta: ').strip()
    salario_fijo = input('Salario Fijo (S/N) - Cobra lo mismo sin importar horas: ').strip().upper()
    empleado_fijo = input('Empleado Fijo (S/N) - Tiene sueldo mínimo + bono por horas extra: ').strip().upper()
    empleado_contrato = input('Empleado por contrato (S/N): ').strip().upper()
    isl_str = input('ISL (Impuesto sobre la renta): ').strip()
    
    # Validar y convertir salario
    try:
        salario = float(salario_str)
    except ValueError:
        print("[ERROR] El salario debe ser un número válido")
        return None
    
    # Convertir salario_fijo a booleano
    salario_fijo_bool = (salario_fijo == 'S')
    
    # Convertir empleado_fijo a booleano
    empleado_fijo_bool = (empleado_fijo == 'S')

    # Convertir empleado_por_contrato a booleano
    empleado_contrato_bool = (empleado_contrato == 'S')

    # Validar y convertir ISL
    if empleado_contrato_bool:
        try:
            isl = float(isl_str) if isl_str else 0.0
        except ValueError:
            print("[ERROR] El ISL debe ser un número válido")
            return None
    else:
        isl = 0.0
    
    # Validar que no sean ambos tipos a la vez
    if salario_fijo_bool and empleado_fijo_bool:
        print("[ERROR] Un empleado no puede ser 'Salario Fijo' y 'Empleado Fijo' al mismo tiempo")
        return None
    
    # Si es empleado_fijo, solicitar salario_minimo
    salario_minimo = 0.0
    if empleado_fijo_bool:
        salario_minimo_str = input('Salario Mínimo (mensual): ').strip()
        try:
            salario_minimo = float(salario_minimo_str)
            if salario_minimo <= 0:
                print("[ERROR] El salario mínimo debe ser mayor a 0")
                return None
        except ValueError:
            print("[ERROR] El salario mínimo debe ser un número válido")
            return None
    
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
        'salario_fijo': [1 if salario_fijo_bool else 0],
        'empleado_fijo': [1 if empleado_fijo_bool else 0],
        'salario_minimo': [salario_minimo if empleado_fijo_bool else 0],
        'Empleado por contrato': ['Sí' if empleado_contrato_bool else 'No'],
        'ISL': [isl]
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
    salario_fijo_actual = bool(empleado_actual.get('salario_fijo', False))
    empleado_fijo_actual = bool(empleado_actual.get('empleado_fijo', False))
    salario_minimo_actual = empleado_actual.get('salario_minimo', 0) if pd.notna(empleado_actual.get('salario_minimo')) else 0
    empleado_contrato_actual = str(empleado_actual.get('Empleado por contrato', 'No')).strip().lower() in ['sí', 'si', 's', 'yes', 'y', 'true', '1']
    isl_actual = empleado_actual.get('ISL', 0) if pd.notna(empleado_actual.get('ISL')) else 0
    print(f"  Salario Fijo: {'Sí' if salario_fijo_actual else 'No'}")
    print(f"  Empleado Fijo: {'Sí' if empleado_fijo_actual else 'No'}")
    print(f"  Empleado por contrato: {'Sí' if empleado_contrato_actual else 'No'}")
    print(f"  ISL: {isl_actual}")
    if empleado_fijo_actual:
        print(f"  Salario Mínimo: {salario_minimo_actual}")
    
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
    
    salario_fijo_str = input(f'Salario Fijo (S/N) [{"S" if salario_fijo_actual else "N"}]: ').strip().upper()
    if not salario_fijo_str:
        salario_fijo_bool = salario_fijo_actual
    else:
        salario_fijo_bool = (salario_fijo_str == 'S')
    
    empleado_fijo_str = input(f'Empleado Fijo (S/N) [{"S" if empleado_fijo_actual else "N"}]: ').strip().upper()
    if not empleado_fijo_str:
        empleado_fijo_bool = empleado_fijo_actual
    else:
        empleado_fijo_bool = (empleado_fijo_str == 'S')
    
    empleado_contrato_str = input(f'Empleado por contrato (S/N) [{"S" if empleado_contrato_actual else "N"}]: ').strip().upper()
    if not empleado_contrato_str:
        empleado_contrato_bool = empleado_contrato_actual
    else:
        empleado_contrato_bool = (empleado_contrato_str == 'S')

    isl_str = input(f'ISL (Impuesto sobre la renta) [{isl_actual}]: ').strip()
    if isl_str:
        try:
            isl = float(isl_str)
        except ValueError:
            print("[ERROR] El ISL debe ser un número válido. Se mantendrá el valor actual.")
            isl = isl_actual
    else:
        isl = isl_actual

    # Validar que no sean ambos tipos a la vez
    if salario_fijo_bool and empleado_fijo_bool:
        print("[ERROR] Un empleado no puede ser 'Salario Fijo' y 'Empleado Fijo' al mismo tiempo")
        return None
    
    # Si es empleado_fijo, solicitar salario_minimo
    salario_minimo = salario_minimo_actual
    if empleado_fijo_bool:
        salario_minimo_str = input(f'Salario Mínimo (mensual) [{salario_minimo_actual}]: ').strip()
        if salario_minimo_str:
            try:
                salario_minimo = float(salario_minimo_str)
                if salario_minimo <= 0:
                    print("[ERROR] El salario mínimo debe ser mayor a 0. Se mantendrá el valor actual.")
                    salario_minimo = salario_minimo_actual
            except ValueError:
                print("[ERROR] El salario mínimo debe ser un número válido. Se mantendrá el valor actual.")
                salario_minimo = salario_minimo_actual
    elif not empleado_fijo_bool:
        salario_minimo = 0.0
    
    # Modificar el DataFrame usando .loc
    employees_df.loc[indice, 'nombre'] = nombre
    employees_df.loc[indice, 'cargo'] = cargo
    employees_df.loc[indice, 'salario'] = salario
    employees_df.loc[indice, 'n_de_cuenta'] = n_de_cuenta
    employees_df.loc[indice, 'banco'] = banco
    employees_df.loc[indice, 'tipo_de_cuenta'] = tipo_de_cuenta
    employees_df.loc[indice, 'salario_fijo'] = 1 if salario_fijo_bool else 0
    employees_df.loc[indice, 'empleado_fijo'] = 1 if empleado_fijo_bool else 0
    employees_df.loc[indice, 'salario_minimo'] = salario_minimo if empleado_fijo_bool else 0
    employees_df.loc[indice, 'Empleado por contrato'] = 'Sí' if empleado_contrato_bool else 'No'
    employees_df.loc[indice, 'ISL'] = isl if empleado_contrato_bool else 0
    
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
            hours_file="Reporte de Asistencia.xlsx",
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
