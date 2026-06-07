from __future__ import annotations

from pathlib import Path
import runpy
import sys

import streamlit as st


SPIRO_APP_DIR = Path("/Users/apple/Documents/alpediatra/spiro_calc")
SPIRO_APP_PATH = SPIRO_APP_DIR / "app.py"


def render():
    st.caption("Módulo de procedimientos respiratorios.")

    if not SPIRO_APP_PATH.exists():
        st.error(f"No se encontró la app de espirometría en: {SPIRO_APP_PATH}")
        return

    st.info("Espirometría integrada desde el proyecto `spiro_calc`.")

    original_set_page_config = st.set_page_config
    path_insertado = False

    try:
        st.set_page_config = lambda *args, **kwargs: None

        spiro_dir_texto = str(SPIRO_APP_DIR)
        if spiro_dir_texto not in sys.path:
            sys.path.insert(0, spiro_dir_texto)
            path_insertado = True

        runpy.run_path(str(SPIRO_APP_PATH), run_name="__spiro_calc_embedded__")
    except Exception as e:
        st.error(f"No se pudo cargar el módulo de espirometría: {e}")
    finally:
        st.set_page_config = original_set_page_config
        if path_insertado:
            try:
                sys.path.remove(spiro_dir_texto)
            except ValueError:
                pass
