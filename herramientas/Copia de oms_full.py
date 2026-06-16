import pandas as pd
import math

# =========================
# CARGA <5 AÑOS
# =========================
df_wfa = pd.read_excel("data/wtageinf.xls")
df_hfa = pd.read_excel("data/lenageinf.xls")
df_wfh = pd.read_excel("data/wtleninf.xls")
df_bfa = pd.read_excel("data/bmiagerev.xls")
df_hc = pd.read_excel("data/hcageinf.xls")

# =========================
# CARGA 5–19 AÑOS OMS 2007
# =========================
df_hfa_boys_519 = pd.read_excel("data/hfa-boys-z-who-2007-exp.xlsx")
df_hfa_girls_519 = pd.read_excel("data/hfa-girls-z-who-2007-exp.xlsx")

df_bfa_boys_519 = pd.read_excel("data/bmi-boys-z-who-2007-exp.xlsx")
df_bfa_girls_519 = pd.read_excel("data/bmi-girls-z-who-2007-exp.xlsx")

# =========================
# LMS
# =========================
def calcular_z(valor, L, M, S):
    if L == 0:
        return math.log(valor / M) / S
    return ((valor / M) ** L - 1) / (L * S)

# =========================
# DETECTAR COLUMNA
# =========================
def detectar_columna(df, opciones):
    for col in opciones:
        if col in df.columns:
            return col
    return None

# =========================
# BUSQUEDA UNIVERSAL (CORREGIDA)
# =========================
def buscar_lms(df, variable, sexo, tipo="edad"):

    df = df.copy()

    # 🔥 MANEJO INTELIGENTE DEL SEXO (ARREGLA TODO)
    df["Sex"] = df["Sex"].astype(str).str.upper()

    if df["Sex"].str.contains("M").any() or df["Sex"].str.contains("F").any():
        # tablas tipo Male / Female
        if sexo == 1:
            df = df[df["Sex"].str.contains("M")]
        else:
            df = df[df["Sex"].str.contains("F")]
    else:
        # tablas tipo 1 / 2
        df["Sex"] = pd.to_numeric(df["Sex"], errors="coerce")
        df = df[df["Sex"] == sexo]

    # =========================
    # DETECTAR COLUMNA EDAD / TALLA
    # =========================
    if tipo == "edad":
        col = detectar_columna(df, ["Agemos", "Age", "Month", "AgeMonths", "Age (months)"])
    else:
        col = detectar_columna(df, ["Length", "Height", "Stature"])

    if col is None:
        print("ERROR columna no encontrada:", df.columns)
        return None

    df[col] = pd.to_numeric(df[col], errors="coerce")

    df["diff"] = abs(df[col] - variable)

    fila = df.sort_values("diff").head(1)

    if fila.empty:
        return None

    return fila.iloc[0]["L"], fila.iloc[0]["M"], fila.iloc[0]["S"]

# =========================
# TABLAS 5–19
# =========================
def seleccionar_tabla_519(sexo, tipo):

    if tipo == "talla":
        return df_hfa_boys_519 if sexo == 1 else df_hfa_girls_519

    if tipo == "imc":
        return df_bfa_boys_519 if sexo == 1 else df_bfa_girls_519

# =========================
# FUNCIONES
# =========================
def es_menor_5(edad_meses):
    return edad_meses < 60


def zscore_peso_edad(peso, edad, sexo):

    if not es_menor_5(edad):
        return None

    lms = buscar_lms(df_wfa, edad, sexo, "edad")
    return round(calcular_z(peso, *lms), 2) if lms else None


def zscore_talla_edad(talla, edad, sexo):

    if edad < 60:
        lms = buscar_lms(df_hfa, edad, sexo, "edad")
        return round(calcular_z(talla, *lms), 2) if lms else None

    df = seleccionar_tabla_519(sexo, "talla")
    df = df.copy()

    col = detectar_columna(df, ["Age", "Agemos", "Month", "AgeMonths", "Age (months)"])

    if col is None:
        print("ERROR: columna edad no encontrada")
        return None

    df[col] = pd.to_numeric(df[col], errors="coerce")
    df["diff"] = abs(df[col] - edad)

    fila = df.sort_values("diff").head(1)

    if fila.empty:
        return None

    L = fila.iloc[0]["L"]
    M = fila.iloc[0]["M"]
    S = fila.iloc[0]["S"]

    return round(calcular_z(talla, L, M, S), 2)


def zscore_imc_edad(imc, edad, sexo):

    if edad < 60:
        lms = buscar_lms(df_bfa, edad, sexo, "edad")
        return round(calcular_z(imc, *lms), 2) if lms else None

    df = seleccionar_tabla_519(sexo, "imc")
    df = df.copy()

    col = detectar_columna(df, ["Age", "Agemos", "Month", "AgeMonths", "Age (months)"])

    if col is None:
        print("ERROR: columna edad no encontrada")
        return None

    df[col] = pd.to_numeric(df[col], errors="coerce")
    df["diff"] = abs(df[col] - edad)

    fila = df.sort_values("diff").head(1)

    if fila.empty:
        return None

    L = fila.iloc[0]["L"]
    M = fila.iloc[0]["M"]
    S = fila.iloc[0]["S"]

    return round(calcular_z(imc, L, M, S), 2)


def zscore_peso_talla(peso, talla, sexo, edad):

    if not es_menor_5(edad):
        return None

    lms = buscar_lms(df_wfh, talla, sexo, "talla")
    return round(calcular_z(peso, *lms), 2) if lms else None


def zscore_pc_edad(pc, edad, sexo):

    if not es_menor_5(edad):
        return None

    lms = buscar_lms(df_hc, edad, sexo, "edad")
    return round(calcular_z(pc, *lms), 2) if lms else None