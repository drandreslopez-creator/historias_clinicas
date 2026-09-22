import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from streamlit.testing.v1 import AppTest
from herramientas.estado_historia import snapshot_formulario, restaurar_formulario, huella_formulario


class EstadoHistoriaTests(unittest.TestCase):
    def test_borrador_conserva_guias_y_plantillas_no_confirmaciones(self):
        for prefix, base in [('urgencias', ''), ('ped', 'ped_')]:
            estado = {base+'gpc_registro_criterio_0': 'CRITERIO', base+'aiepi_registro': 'NOTA', base+'aiepi_apoyo': 'FIEBRE', prefix+'_ejemplo_confirmado': 'HUELLA', prefix+'_informe_final': {'historia': 'PRIVADO'}}
            datos = snapshot_formulario(estado, {}, prefix)
            restaurado = {}
            restaurar_formulario(restaurado, datos, {}, prefix)
            self.assertEqual(restaurado[base+'gpc_registro_criterio_0'], 'CRITERIO')
            self.assertEqual(restaurado[base+'aiepi_registro'], 'NOTA')
            self.assertNotIn(prefix+'_ejemplo_confirmado', restaurado)
            self.assertNotIn(prefix+'_informe_final', restaurado)

    def test_limpieza_real_elimina_analisis_diferido(self):
        path = Path(__file__).resolve().parents[1] / 'servicios/pediatria_urgencias.py'
        arbol = ast.parse(path.read_text())
        nodo = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == 'limpiar_formulario')
        estado = {'_analisis_recalculado_pendiente': 'CASO ANTERIOR', 'urgencias_informe_final': {'historia': 'ANTERIOR'}, '_plan_ejemplo_template': 'ANTERIOR', 'gpc_registro_criterio_0': 'ANTERIOR'}
        ns = dict(st=SimpleNamespace(session_state=estado), FORM_DEFAULTS={}, borrar_borrador_urgencias=lambda:None)
        exec(compile(ast.Module(body=[nodo], type_ignores=[]),str(path),'exec'),ns)
        ns['limpiar_formulario']()
        self.assertFalse(estado)

    def test_huella_detecta_cambios_de_criterio_no_caches(self):
        estado = {'plan': 'A', 'plan_base': 'BASE', 'gpc_registro_criterio_0': 'UNO'}
        defaults = {'plan':'', 'plan_base':''}
        anterior = huella_formulario(estado, defaults, 'urgencias')
        estado['plan_base'] = 'OTRA BASE'
        self.assertEqual(anterior, huella_formulario(estado, defaults, 'urgencias'))
        estado['gpc_registro_criterio_0'] = 'DOS'
        self.assertNotEqual(anterior, huella_formulario(estado, defaults, 'urgencias'))

    def test_vista_previa_no_guarda_sin_confirmar_ni_duplica(self):
        codigo = '''
import streamlit as st
from herramientas.estado_historia import preparar_informe, revisar_informe
texto = st.text_input("Dato", key="dato")
if st.button("Generar"):
    preparar_informe(st, "test", texto, "TITULO", [("SECCION", texto)], texto, "FICTICIO", "0")
def guardar(informe):
    st.session_state["envios"] = st.session_state.get("envios", 0) + 1
    st.session_state["texto_guardado"] = informe["historia"]
revisar_informe(st, "test", texto, guardar)
'''
        app = AppTest.from_string(codigo).run()
        app.text_input[0].set_value('TEXTO FINAL').run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertNotIn('envios', app.session_state)
        app.button(key='test_guardar_final').click().run()
        self.assertEqual(app.session_state['texto_guardado'], 'TEXTO FINAL')
        app.run()
        self.assertEqual(app.session_state['envios'], 1)
        app.text_input[0].set_value('OTRO PACIENTE').run()
        self.assertNotIn('test_informe_final', app.session_state)
        self.assertFalse(any(b.key == 'test_guardar_final' for b in app.button))
