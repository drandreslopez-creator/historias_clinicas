def diagnostico_menor_5(pt, pe, te, pc):

    dx = []

    # =========================
    # TALLA/EDAD (T/E)
    # =========================
    if te is not None:
        if te < -2:
            dx.append("RETRASO DE TALLA")
        elif -2 <= te < -1:
            dx.append("RIESGO DE TALLA BAJA")
        elif te > 1:
            dx.append("TALLA ALTA")

    # =========================
    # PESO/TALLA (P/T)
    # =========================
    if pt is not None:
        if pt < -3:
            dx.append("DESNUTRICIÓN AGUDA SEVERA")
        elif -3 <= pt < -2:
            dx.append("DESNUTRICIÓN AGUDA MODERADA")
        elif -2 <= pt < -1:
            dx.append("RIESGO DE DESNUTRICIÓN AGUDA")
        elif -1 <= pt <= 1:
            dx.append("NORMAL")
        elif 1 < pt <= 2:
            dx.append("RIESGO DE SOBREPESO")
        elif 2 < pt <= 3:
            dx.append("SOBREPESO")
        elif pt > 3:
            dx.append("OBESIDAD")

    # =========================
    # PESO/EDAD (P/E)
    # =========================
    if pe is not None:
        if pe < -2:
            dx.append("DESNUTRICIÓN GLOBAL")
        elif -2 <= pe < -1:
            dx.append("RIESGO DE DESNUTRICIÓN GLOBAL")
        elif -1 <= pe <= 1:
            dx.append("PESO ADECUADO PARA LA EDAD")

    # =========================
    # PERÍMETRO CEFÁLICO (PC/E)
    # =========================
    if pc is not None:
        if pc < -2:
            dx.append("MICROCEFALIA")
        elif pc > 2:
            dx.append("MACROCEFALIA")

    if not dx:
        return "ESTADO NUTRICIONAL NORMAL"

    return ", ".join(dx)


def diagnostico_mayor_5(imc, te):

    dx = []

    # =========================
    # IMC/EDAD
    # =========================
    if imc is not None:
        if imc < -2:
            dx.append("DELGADEZ")
        elif -2 <= imc < -1:
            dx.append("RIESGO DE DELGADEZ")
        elif -1 <= imc <= 1:
            dx.append("IMC NORMAL")
        elif imc > 2:
            dx.append("OBESIDAD")
        elif imc > 1:
            dx.append("SOBREPESO")

    # =========================
    # TALLA/EDAD
    # =========================
    if te is not None:
        if te < -2:
            dx.append("TALLA BAJA")
        elif -2 <= te < -1:
            dx.append("RIESGO DE TALLA BAJA")
        elif te > 1:
            dx.append("TALLA ALTA")

    if not dx:
        return "ESTADO NUTRICIONAL NORMAL"

    return ", ".join(dx)