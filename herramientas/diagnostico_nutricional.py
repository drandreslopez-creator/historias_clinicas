def diagnostico_menor_5(pt, pe, te, pc):
    """Resume por indicadores OMS, listo para la impresión diagnóstica pediátrica.

    El P/E se calcula y se muestra en antropometría, pero P/T y T/E son los
    indicadores que se priorizan en el diagnóstico nutricional de este grupo.
    """
    dx = []

    if te is not None:
        if te < -2:
            dx.append("TALLA BAJA PARA LA EDAD")
        elif te < -1:
            dx.append("RIESGO DE TALLA BAJA PARA LA EDAD")
        elif te <= 1:
            dx.append("TALLA NORMAL PARA LA EDAD")
        else:
            dx.append("TALLA ALTA PARA LA EDAD")

    if pt is not None:
        if pt < -3:
            dx.append("DESNUTRICIÓN AGUDA SEVERA")
        elif pt < -2:
            dx.append("DESNUTRICIÓN AGUDA MODERADA")
        elif pt < -1:
            dx.append("RIESGO DE DESNUTRICIÓN AGUDA")
        elif pt <= 1:
            dx.append("PESO/TALLA NORMAL")
        elif pt <= 2:
            dx.append("RIESGO DE SOBREPESO")
        elif pt <= 3:
            dx.append("SOBREPESO")
        else:
            dx.append("OBESIDAD")

    # Solo se añade cuando se diligenció perímetro cefálico y se obtuvo su Z.
    if pc is not None:
        if pc < -2:
            dx.append("PERÍMETRO CEFÁLICO BAJO PARA LA EDAD")
        elif pc > 2:
            dx.append("PERÍMETRO CEFÁLICO ALTO PARA LA EDAD")
        else:
            dx.append("PERÍMETRO CEFÁLICO NORMAL PARA LA EDAD")

    return ", ".join(dx) if dx else "ESTADO NUTRICIONAL NO EVALUADO"


def diagnostico_mayor_5(imc, te):
    """Resume IMC/E y T/E para mayores de 5 años."""
    dx = []

    if imc is not None:
        if imc < -2:
            dx.append("DELGADEZ")
        elif imc < -1:
            dx.append("RIESGO DE DELGADEZ")
        elif imc <= 1:
            dx.append("IMC NORMAL PARA LA EDAD")
        elif imc <= 2:
            dx.append("SOBREPESO")
        else:
            dx.append("OBESIDAD")

    if te is not None:
        if te < -2:
            dx.append("TALLA BAJA PARA LA EDAD")
        elif te < -1:
            dx.append("RIESGO DE TALLA BAJA PARA LA EDAD")
        elif te <= 1:
            dx.append("TALLA NORMAL PARA LA EDAD")
        else:
            dx.append("TALLA ALTA PARA LA EDAD")

    return ", ".join(dx) if dx else "ESTADO NUTRICIONAL NO EVALUADO"
