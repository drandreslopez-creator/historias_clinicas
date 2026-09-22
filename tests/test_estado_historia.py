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
        self.assertEqual(estado, {"_urgencias_adjuntos_version": 1})

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

    def test_regenerar_con_iguales_entradas_muestra_nuevo_resultado(self):
        app = AppTest.from_string('''
import streamlit as st
from herramientas.estado_historia import preparar_informe, revisar_informe
if st.button("Generar"):
    numero = st.session_state.get("numero", 0) + 1
    st.session_state["numero"] = numero
    preparar_informe(st, "test", "MISMAS ENTRADAS", "T", [], f"RESULTADO {numero}", "", "")
def guardar(informe):
    st.session_state["guardado"] = informe["historia"]
revisar_informe(st, "test", "MISMAS ENTRADAS", guardar)
''').run()
        app.button[0].click().run()
        self.assertEqual(app.text_area[0].value, "RESULTADO 1")
        app.button[0].click().run()
        self.assertEqual(app.text_area[0].value, "RESULTADO 2")
        app.button(key="test_guardar_final").click().run()
        self.assertEqual(app.session_state["guardado"], "RESULTADO 2")

    def test_borrar_borrador_invalida_cache(self):
        import tempfile
        path = Path(__file__).resolve().parents[1] / 'servicios/pediatria_urgencias.py'
        nodo = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'borrar_borrador_urgencias')
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / 'borrador.json'
            archivo.write_text('{}')
            estado = {'_borrador_urgencias_hash': 'HUELLA ANTERIOR'}
            ns = dict(st=SimpleNamespace(session_state=estado), DRAFT_URGENCIAS_PATH=archivo)
            exec(compile(ast.Module(body=[nodo], type_ignores=[]), str(path), 'exec'), ns)
            ns['borrar_borrador_urgencias']()
            self.assertFalse(archivo.exists())
            self.assertNotIn('_borrador_urgencias_hash', estado)

    def test_limpieza_renueva_adjuntos_en_ambos_formularios(self):
        root = Path(__file__).resolve().parents[1]
        for archivo, funcion, prefix in [('pediatria_urgencias.py', 'limpiar_formulario', 'urgencias'), ('consulta_externa_base.py', '_clear_state', 'ped')]:
            path = root / 'servicios' / archivo
            nodo = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == funcion)
            version_key = f'_{prefix}_adjuntos_version'
            pdf_key = 'pdf_paraclinicos_uploader_v9_2' if prefix == 'urgencias' else 'ped_paraclinicos_pdf_v1_2'
            estado = {version_key: 2, pdf_key: ['PDF DEL CASO ANTERIOR']}
            ns = dict(st=SimpleNamespace(session_state=estado), FORM_DEFAULTS={}, borrar_borrador_urgencias=lambda:None)
            exec(compile(ast.Module(body=[nodo], type_ignores=[]), str(path), 'exec'), ns)
            ns[funcion](*(() if prefix == 'urgencias' else (prefix, {})))
            self.assertNotIn(pdf_key, estado)
            self.assertEqual(estado[version_key], 3)

    def test_cambiar_historia_guardada_actualiza_texto(self):
        app = AppTest.from_string('''
import streamlit as st
from herramientas.estado_historia import clave_texto_informe
seleccion = st.selectbox("Historia", ["A", "B"])
texto = "INFORME " + seleccion
st.text_area("Informe guardado", texto, key=clave_texto_informe("guardada", texto), disabled=True)
''').run()
        self.assertEqual(app.text_area[0].value, 'INFORME A')
        app.selectbox[0].select('B').run()
        self.assertEqual(app.text_area[0].value, 'INFORME B')
        app.selectbox[0].select('A').run()
        self.assertEqual(app.text_area[0].value, 'INFORME A')

    def test_fecha_serializada_se_restaura_como_fecha(self):
        from datetime import date
        for prefix, key in [('urgencias', 'fecha_1'), ('ped', 'ped_fecha_nacimiento')]:
            estado = {}
            restaurar_formulario(estado, {key: '2025-12-20'}, {key: None}, prefix)
            self.assertEqual(estado[key], date(2025, 12, 20))
            restaurar_formulario(estado, {key: 'fecha incorrecta'}, {key: None}, prefix)
            self.assertIsNone(estado[key])
