from calendar import monthrange
from datetime import date


def calcular_edad(fecha_nacimiento, fecha_referencia=None):
    """Edad calendario cumplida; el aniversario se limita al fin de cada mes."""
    hoy = fecha_referencia or date.today()
    if fecha_nacimiento > hoy:
        raise ValueError("La fecha de nacimiento no puede ser posterior a la fecha de referencia.")

    meses_totales = (hoy.year - fecha_nacimiento.year) * 12 + hoy.month - fecha_nacimiento.month

    def aniversario(meses):
        anio, mes_cero = divmod(fecha_nacimiento.year * 12 + fecha_nacimiento.month - 1 + meses, 12)
        mes = mes_cero + 1
        dia = min(fecha_nacimiento.day, monthrange(anio, mes)[1])
        return date(anio, mes, dia)

    if aniversario(meses_totales) > hoy:
        meses_totales -= 1
    anios, meses = divmod(meses_totales, 12)
    dias = (hoy - aniversario(meses_totales)).days
    return anios, meses, dias


def edad_en_meses(fecha_nacimiento):
    hoy = date.today()
    dias = (hoy - fecha_nacimiento).days

    # Convención existente de las tablas antropométricas; no es la edad calendario.
    return int(round(dias / 30.44))
