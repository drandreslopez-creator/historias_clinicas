import ast
from pathlib import Path
import re
import unittest
from streamlit.testing.v1 import AppTest
from herramientas.checklist_consulta import quitar_edad_del_inicio, resumen_cuadro, incorporar_checklist

APP = '''
import streamlit as st
from herramientas.checklist_consulta import render_checklist
conducta = st.selectbox("Conducta", ["OBSERVACIÓN", "EGRESO", "HOSPITALIZACIÓN", "PENDIENTE DEFINIR"], key="conducta")
contenedores = {k: st.container() for k in ("inicial", "evaluacion", "cierre")}
st.session_state["bloques"] = render_checklist(st, "prueba", contenedores, conducta, "44", "92", "RECOMENDACIÓN SUGERIDA")
'''


class ChecklistConsultaTests(unittest.TestCase):
    def test_no_hay_normalidad_preseleccionada(self):
        app = AppTest.from_string(APP).run()
        self.assertFalse(app.exception)
        self.assertTrue(all(not valor for valor in app.session_state['bloques'].values()))
        self.assertTrue(all(s.value == 'Pendiente' for s in app.selectbox if s.key != 'conducta'))
        self.assertTrue(all(not c.value for c in app.checkbox))

    def test_observacion_no_copia_egreso_previamente_registrado(self):
        app = AppTest.from_string(APP).run()
        app.selectbox(key='conducta').select('EGRESO').run()
        app.text_area(key='prueba_checklist_egreso_texto').set_value('INDICACIÓN DE SALIDA').run()
        app.checkbox(key='prueba_checklist_egreso_sugerido').check().run()
        self.assertIn('INDICACIÓN DE SALIDA', app.session_state['bloques']['egreso'])
        app.selectbox(key='conducta').select('OBSERVACIÓN').run()
        self.assertEqual(app.session_state['bloques']['egreso'], '')
        app.text_input(key='prueba_checklist_condiciones_egreso').set_value('REVALORAR INGESTA').run()
        self.assertEqual(app.session_state['bloques']['pendientes'], 'REVALORAR INGESTA')
        self.assertEqual(app.session_state['bloques']['reevaluacion'], '')

    def test_solo_educacion_y_estudios_confirmados(self):
        app = AppTest.from_string(APP).run()
        app.selectbox(key='prueba_checklist_estudios').select('No').run()
        self.assertIn('No se solicitan', app.session_state['bloques']['plan'])
        app.selectbox(key='prueba_checklist_estudios').select('Sí').run()
        self.assertEqual(app.session_state['bloques']['plan'], '')
        app.text_input(key='prueba_checklist_estudios_detalle').set_value('ESTUDIO ESPECIFICADO: MOTIVO').run()
        self.assertIn('MOTIVO', app.session_state['bloques']['plan'])
        app.checkbox(key='prueba_checklist_educacion_realizada').check().run()
        app.text_input(key='prueba_checklist_educacion_texto').set_value('MADRE: PLAN ACTUAL').run()
        self.assertNotIn('Comprensión', app.session_state['bloques']['educacion'])
        app.checkbox(key='prueba_checklist_educacion_realizada').uncheck().run()
        self.assertEqual(app.session_state['bloques']['educacion'], '')

    def test_secciones_sin_volcado_al_analisis(self):
        bloques = {'inicial': 'INGESTA DISMINUIDA.', 'evaluacion': 'AIRE AMBIENTE.', 'plan': 'NO SE SOLICITAN ESTUDIOS.', 'pendientes': 'REVALORAR INGESTA'}
        salida = dict(incorporar_checklist([('ENFERMEDAD ACTUAL','TOS.'),('EXAMEN FÍSICO','SIBILANCIAS.'),('ANÁLISIS','SÍNTESIS.'),('PLAN','OBSERVACIÓN.')], bloques))
        self.assertEqual(salida['ANÁLISIS'], 'SÍNTESIS.')
        self.assertIn('INGESTA DISMINUIDA', salida['ENFERMEDAD ACTUAL'])
        self.assertNotIn('RECOMENDACIONES DE EGRESO', salida)
        self.assertEqual(salida['CONDICIONES PENDIENTES PARA EVENTUAL EGRESO'], 'REVALORAR INGESTA')

    def test_edad_inicial_no_borra_antecedentes(self):
        texto = 'LACTANTE DE 8 MESES CON 3 DÍAS DE TOS. HOSPITALIZADO A LOS 2 MESES.'
        self.assertEqual(quitar_edad_del_inicio(texto), '3 DÍAS DE TOS. HOSPITALIZADO A LOS 2 MESES.')
        self.assertEqual(quitar_edad_del_inicio('MADRE DE 32 AÑOS REFIERE TOS'), 'MADRE DE 32 AÑOS REFIERE TOS')

    def test_resumen_no_repite_encabezado_ni_toda_historia(self):
        texto = 'SE TRATA DE LACTANTE MENOR, DE 9 MESES, 2 DÍAS DE EDAD, QUIEN ES TRAÍDA POR MADRE POR LACTANTE DE 8 MESES CON 3 DÍAS DE TOS. NIEGA APNEAS.'
        self.assertEqual(resumen_cuadro(texto), '3 DÍAS DE TOS')

    def test_conducta_no_inventa_estudios_estabilidad_o_educacion(self):
        p = Path(__file__).resolve().parents[1] / 'servicios/pediatria_urgencias.py'
        nombres = {'construir_conducta_final_analisis', 'generar_analisis_asistido_urgencias', 'limpiar_fragmento_analisis'}
        nodos = [n for n in ast.parse(p.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in nombres]
        ns = {'re': re, 'resumen_cuadro': resumen_cuadro}
        exec(compile(ast.Module(body=nodos,type_ignores=[]),str(p),'exec'),ns)
        for conducta in ('OBSERVACIÓN','HOSPITALIZACIÓN','EGRESO'):
            texto = ns['construir_conducta_final_analisis'](conducta, '')
            analisis = ns['generar_analisis_asistido_urgencias']('TOS. OTRA FRASE.', '', '', '', '', texto)
            for frase in ('EXÁMENES', 'PARACLÍNICOS DE EXTENSIÓN', 'BUEN ESTADO GENERAL', 'ENTENDER Y ACEPTAR', 'SE BRINDA INFORMACIÓN', 'OTRA FRASE'):
                self.assertNotIn(frase, analisis)

    def test_no_aparecen_escapes_markdown_en_texto(self):
        salida = dict(incorporar_checklist([('PLAN', '\\- ORDEN'), ('DIAGNÓSTICO', '1\\. EJEMPLO')], {}))
        self.assertEqual(salida['PLAN'], '- ORDEN')
        self.assertEqual(salida['DIAGNÓSTICO'], '1. EJEMPLO')

    def test_encabezado_sin_edad_no_inventa_un_recien_nacido(self):
        p = Path(__file__).resolve().parents[1] / 'servicios/pediatria_urgencias.py'
        nombres = {'construir_encabezado_analisis_pediatrico', 'limpiar_fragmento_analisis'}
        nodos = [n for n in ast.parse(p.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in nombres]
        ns = {'re': re, 'quitar_edad_del_inicio': quitar_edad_del_inicio, 'extraer_destinatario_informacion': lambda valor: 'MADRE'}
        exec(compile(ast.Module(body=nodos,type_ignores=[]),str(p),'exec'),ns)
        encabezado = ns['construir_encabezado_analisis_pediatrico']('', 0, 0, 0, 'Femenino', 'MADRE', 'TOS.', edad_conocida=False)
        self.assertIn('EDAD NO REGISTRADA', encabezado)
        self.assertNotIn('0 DÍAS', encabezado)
        self.assertEqual(resumen_cuadro(encabezado), 'TOS')

    def test_checklist_se_conserva_en_borrador_y_cambia_la_huella(self):
        from herramientas.estado_historia import snapshot_formulario, restaurar_formulario, huella_formulario
        estado = {'urgencias_checklist_ingesta': 'Disminuida', 'urgencias_checklist_revision': [{'etiqueta': 'Ingesta'}]}
        datos = snapshot_formulario(estado, {}, 'urgencias')
        self.assertNotIn('urgencias_checklist_revision', datos)
        restaurado = {}
        restaurar_formulario(restaurado, datos, {}, 'urgencias')
        self.assertEqual(restaurado['urgencias_checklist_ingesta'], 'Disminuida')
        antes = huella_formulario(restaurado, {}, 'urgencias')
        restaurado['urgencias_checklist_ingesta'] = 'No tolera'
        self.assertNotEqual(antes, huella_formulario(restaurado, {}, 'urgencias'))
