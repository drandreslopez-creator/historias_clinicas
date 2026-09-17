"""Pruebas de ubicación, conservación y cambio de ruta en Streamlit."""
from pathlib import Path
import sys
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from herramientas.rutas_gpc_pediatria import ETAPAS_AIEPI, ETAPAS_GPC, APOYOS_AIEPI, RUTAS_GPC

APP = '''
import streamlit as st
from herramientas.rutas_gpc_pediatria import crear_etapa_guias, render_trazabilidad_gpc, render_apoyo_aiepi, limpiar_registros_al_cambiar_ruta
st.text_area("Enfermedad actual")
etapas = {"inicial": crear_etapa_guias(st, "inicial")}
st.text_area("Examen físico")
etapas["evaluacion"] = crear_etapa_guias(st, "evaluacion")
st.text_area("Plan")
etapas["cierre"] = crear_etapa_guias(st, "cierre")
registros = ("gpc_registro", "gpc_justificacion", "aiepi_registro")
compartidos = {}
st.session_state["resultado_gpc"] = render_trazabilidad_gpc(st, clave="NEUMONIA", diagnostico="J18 NEUMONIA", texto_clinico="", justificacion_key="gpc_justificacion", registro_key="gpc_registro", selector_key="gpc_ruta", contenedores=etapas, registros_limpieza=registros, compartidos=compartidos)
st.session_state["resultado_aiepi"] = render_apoyo_aiepi(st, diagnostico="NEUMONIA", texto_clinico="", selector_key="aiepi_apoyo", registro_key="aiepi_registro", contenedores=etapas, registros_limpieza=registros, compartidos=compartidos)
st.button("Limpiar", on_click=limpiar_registros_al_cambiar_ruta, args=(st, registros))
'''


class GuiasEtapasTests(unittest.TestCase):
    def app(self, ruta='NEUMONIA', apoyo='RESPIRATORIO', datos=None):
        app = AppTest.from_string(APP)
        app.session_state['gpc_ruta'] = ruta
        app.session_state['aiepi_apoyo'] = apoyo
        for k, v in (datos or {}).items():
            app.session_state[k] = v
        app.run()
        self.assertFalse(app.exception)
        return app

    def test_todos_los_criterios_tienen_una_etapa(self):
        for catalogo, campo, etapas in ((RUTAS_GPC, 'verificaciones', ETAPAS_GPC), (APOYOS_AIEPI, 'criterios', ETAPAS_AIEPI)):
            self.assertEqual(set(catalogo), set(etapas))
            for clave, definicion in catalogo.items():
                self.assertEqual(len(definicion[campo]), len(etapas[clave]))
                self.assertLessEqual(set(etapas[clave]), {'inicial', 'evaluacion', 'cierre'})

    def test_render_todas_las_rutas_y_apoyos(self):
        for ruta in ['', *RUTAS_GPC]:
            with self.subTest(ruta=ruta):
                self.app(ruta)
        for apoyo in APOYOS_AIEPI:
            with self.subTest(apoyo=apoyo):
                self.app(apoyo=apoyo)

    def test_ubicacion_visual_y_campo_compartido(self):
        app = self.app()
        bloques = app.main.children
        etapas = [elemento for elemento in bloques.values() if getattr(elemento, 'type', '') == 'flex_container' or getattr(elemento, 'type', '') == 'vertical']
        # Se comprueba pertenencia al contenedor, no solo el orden de llamadas Python.
        inicial = next(b for b in etapas if b.subheader and b.subheader[0].value.startswith('1.'))
        evaluacion = next(b for b in etapas if b.subheader and b.subheader[0].value.startswith('2.'))
        cierre = next(b for b in etapas if b.subheader and b.subheader[0].value.startswith('3.'))
        self.assertIn('gpc_registro_criterio_0', [x.key for x in inicial.text_input])
        self.assertIn('gpc_registro_criterio_3', [x.key for x in evaluacion.text_input])
        self.assertIn('gpc_registro_criterio_9', [x.key for x in cierre.text_input])
        self.assertEqual(sum('SIGNOS GENERALES DE PELIGRO (GPC / AIEPI)' == x.label for x in app.text_input), 1)

    def test_respuestas_de_tres_etapas_llegan_al_informe(self):
        app = self.app()
        for i, texto in ((0, 'EVOLUCIÓN REGISTRADA'), (3, 'HALLAZGO DE EXAMEN'), (9, 'CONTROL REGISTRADO')):
            app.text_input(key=f'gpc_registro_criterio_{i}').set_value(texto)
        app.text_input(key='gpc_registro_criterio_2').set_value('SIN SIGNOS DE PELIGRO DOCUMENTADOS')
        app.run()
        self.assertFalse(app.exception)
        for texto in ('EVOLUCIÓN REGISTRADA','HALLAZGO DE EXAMEN','CONTROL REGISTRADO'):
            self.assertIn(texto, app.session_state['resultado_gpc'][1])
        self.assertIn('SIN SIGNOS DE PELIGRO DOCUMENTADOS', app.session_state['resultado_aiepi'][1])

    def test_cambio_de_ruta_no_reasigna_respuestas(self):
        app = self.app(datos={'gpc_registro_criterio_0':'DATO PREVIO','aiepi_registro_criterio_1':'OTRO DATO'})
        app.selectbox(key='gpc_ruta').select('EDA').run()
        self.assertFalse(app.exception)
        self.assertNotIn('DATO', app.session_state['resultado_gpc'][1])
        self.assertNotIn('DATO', app.session_state['resultado_aiepi'][1])

    def test_no_descarta_dos_respuestas_distintas_del_ejemplo(self):
        app=self.app(datos={'gpc_registro_criterio_2':'REGISTRO A','aiepi_registro_criterio_0':'REGISTRO B'})
        self.assertIn('REGISTRO A',app.session_state['resultado_gpc'][1])
        self.assertIn('REGISTRO B',app.session_state['resultado_aiepi'][1])
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['resultado_gpc'][1], '')
        self.assertEqual(app.session_state['resultado_aiepi'][1], '')


if __name__ == '__main__':
    unittest.main()
