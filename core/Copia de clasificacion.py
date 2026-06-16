def grupo_etario(años):
    if años < 1:
        return "lactante menor"
    elif años < 2:
        return "lactante mayor"
    elif años < 5:
        return "preescolar"
    elif años < 12:
        return "escolar"
    else:
        return "adolescente"
