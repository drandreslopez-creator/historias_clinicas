import streamlit as st


SPIRO_APP_URL = "https://spirocalc-pwoyqbbvcngpae2yzq6uvv.streamlit.app/"


def render():
    st.caption("Módulo de procedimientos respiratorios.")

    st.link_button(
        "Abrir módulo de espirometría",
        SPIRO_APP_URL,
        use_container_width=True,
    )
