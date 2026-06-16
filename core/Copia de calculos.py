from datetime import date

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    dias = (hoy - fecha_nacimiento).days

    anios = dias // 365
    meses = (dias % 365) // 30
    dias_restantes = (dias % 365) % 30

    return anios, meses, dias_restantes


def edad_en_meses(fecha_nacimiento):
    hoy = date.today()
    dias = (hoy - fecha_nacimiento).days

    # 🔥 redondeo clínico correcto
    return int(round(dias / 30.44))
