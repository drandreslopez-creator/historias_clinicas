import streamlit as st

# IMPORTAR SERVICIOS
from servicios import pediatria_urgencias
from servicios import neonatologia_adaptacion

st.set_page_config(page_title="Historias Clínicas", layout="wide")

st.title("🩺 FORMATO DE HISTORIA CLÍNICA DEL DR. ANDRÉS LÓPEZ RUIZ")

tipo_historia = st.selectbox(
    "Seleccione tipo de historia clínica",
    [
        "Pediatría Urgencias",
        "Pediatría Hospitalización",
        "Adaptación Neonatal",
        "Evolución Neonatal",
        "Consulta Externa",
        "Homeopatía"
    ]
)

# ENRUTADOR 🔥
if tipo_historia == "Pediatría Urgencias":
    pediatria_urgencias.render()

elif tipo_historia == "Adaptación Neonatal":
    neonatologia_adaptacion.render()
