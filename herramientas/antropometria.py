def calcular_imc(peso, talla_cm):
    talla_m = talla_cm / 100
    if talla_m == 0:
        return 0
    return peso / (talla_m ** 2)


def texto_antropometria(años, peso, talla):

    if años < 5:
        return """P/T:
P/E:
T/E:
PC/E:
P. BRAQUIAL:"""

    else:
        imc = calcular_imc(peso, talla)

        return f"""IMC: {round(imc,2)}
IMC/EDAD:
T/E:"""
