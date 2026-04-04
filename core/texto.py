def sexo_texto(sexo):
    if sexo == "Masculino":
        return {
            "paciente": "paciente masculino",
            "pronombre": "el",
            "terminacion": "o"
        }
    else:
        return {
            "paciente": "paciente femenina",
            "pronombre": "la",
            "terminacion": "a"
        }
