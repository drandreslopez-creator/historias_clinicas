"""Pruebas documentales con datos sintéticos, sin servicios externos."""
import unittest
from streamlit.testing.v1 import AppTest
from herramientas.revision_documental import estado_registro, huella_revision, marcar_ejemplo
from test_guias_etapas import APP

PANEL = '''
from herramientas.revision_documental import render_revision_documental, marcar_ejemplo
st.text_input("Identificación", key="nombre")
st.button("Cargar ejemplo de prueba", key="cargar", on_click=marcar_ejemplo, args=(st, "prueba", "Caso sintético"))
listo = render_revision_documental(st, prefix="prueba", registros=("gpc_registro", "aiepi_registro"), claves_revision=("nombre", "gpc_ruta", "aiepi_apoyo", "gpc_justificacion"))
st.button("Generar", key="generar", disabled=not listo)
'''


class RevisionDocumentalTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_string(APP + PANEL).run()
        self.assertFalse(app.exception)
        return app

    def test_estados_no_confunden_texto_con_adherencia(self):
        for valor, esperado in ((None, 'Sin registrar'), ('  ', 'Sin registrar'), ('No aplica', 'No aplica sin justificación'), ('N/A: ', 'No aplica sin justificación'), ('No aplica: razón documentada', 'No aplica con justificación'), ('N/A — motivo', 'No aplica con justificación'), ('Náuseas', 'Con registro'), ('NIEGA FIEBRE', 'Con registro')):
            self.assertEqual(estado_registro(valor), esperado)

    def test_huella_solo_datos_seleccionados(self):
        self.assertEqual(huella_revision({'a': 1, 'cache': 2}, ['a']), huella_revision({'a': 1, 'cache': 3}, ['a']))
        self.assertNotEqual(huella_revision({'a': 1}, ['a']), huella_revision({'a': 2}, ['a']))

    def test_pendientes_no_bloquean_y_enlaces_tienen_destino(self):
        app = self.app()
        self.assertFalse(app.button(key='generar').disabled)
        enlaces = [m.value for m in app.markdown if '**Sin registrar**' in m.value]
        self.assertTrue(enlaces)
        for enlace in enlaces:
            ancla = enlace.split('](#')[1].split(')')[0]
            self.assertTrue(any(f'id="{ancla}"' in m.value for m in app.markdown))
        app.text_input(key='gpc_registro_criterio_0').set_value('No aplica').run()
        self.assertTrue(any('**No aplica sin justificación**' in m.value for m in app.markdown))
        app.text_input(key='gpc_registro_criterio_0').set_value('No aplica: motivo documentado').run()
        self.assertTrue(any('**No aplica con justificación**' in m.value for m in app.markdown))

    def test_ejemplo_exige_revision_y_edicion_la_invalida(self):
        app = self.app()
        app.button(key='cargar').click().run()
        self.assertTrue(app.button(key='generar').disabled)
        app.button(key='prueba_confirmar_ejemplo').click().run()
        self.assertFalse(app.button(key='generar').disabled)
        app.run()
        self.assertFalse(app.button(key='generar').disabled)
        app.text_input(key='nombre').set_value('PACIENTE SINTÉTICO').run()
        self.assertTrue(app.button(key='generar').disabled)
        app.button(key='prueba_confirmar_ejemplo').click().run()
        app.text_input(key='gpc_registro_criterio_0').set_value('DATO NUEVO').run()
        self.assertTrue(app.button(key='generar').disabled)
        self.assertFalse(app.exception)

    def test_recargar_ejemplo_requiere_nueva_confirmacion(self):
        app = self.app()
        app.button(key='cargar').click().run()
        app.button(key='prueba_confirmar_ejemplo').click().run()
        app.button(key='cargar').click().run()
        self.assertTrue(app.button(key='generar').disabled)

    def test_pregunta_compartida_se_revisa_una_vez(self):
        app = self.app()
        enlaces = [m.value for m in app.markdown if '](#criterio-' in m.value]
        anclas = [m.split('](#')[1].split(')')[0] for m in enlaces]
        self.assertEqual(len(anclas), len(set(anclas)))
        app.selectbox(key='gpc_ruta').select('').run()
        self.assertEqual(app.session_state['gpc_registro_revision'], [])
        self.assertFalse(app.exception)

if __name__ == '__main__':
    unittest.main()
