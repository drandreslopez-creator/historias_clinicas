import streamlit as st


SPIRO_APP_URL = "https://spirocalc-pwoyqbbvcngpae2yzq6uvv.streamlit.app/"


def render():
    st.caption("Módulo de procedimientos respiratorios.")
    st.info("La espirometría se abre desde su app independiente para conservar todas sus funciones y compatibilidad.")

    st.link_button(
        "Abrir módulo de espirometría",
        SPIRO_APP_URL,
        use_container_width=True,
    )

    st.markdown(
        f"Si no abre automáticamente, puedes entrar aquí: [SpiroCalc]({SPIRO_APP_URL})"
    )
