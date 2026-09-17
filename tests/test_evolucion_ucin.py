"""Regresiones de cálculos locales, sin iniciar Streamlit ni servicios externos."""
import ast
from datetime import date
from pathlib import Path
import re
import unittest


def cargar_funciones_locales():
    # Extraer las funciones puras permite probar el código real sin importar
    # la interfaz, las tablas de crecimiento ni las conexiones de la aplicación.
    ruta = Path(__file__).resolve().parents[1] / 'servicios/evolucion_ucin.py'
    arbol = ast.parse(ruta.read_text(encoding='utf-8'))
    nombres = {'_numero', '_entero', '_buscar', '_peso_texto',
               '_actualizar_balance', '_actualizar_nota_local'}
    modulo = ast.Module(body=[n for n in arbol.body
                              if isinstance(n, ast.FunctionDef) and n.name in nombres],
                        type_ignores=[])
    contexto = {'re': re}
    exec(compile(modulo, str(ruta), 'exec'), contexto)
    return contexto


FUNCIONES = cargar_funciones_locales()


class EvolucionUcinTests(unittest.TestCase):
    def test_extrapola_volumenes_pero_conserva_tasa_por_hora(self):
        for origen, destino in ((24, 12), (24, 6), (6, 24), (12, 12)):
            with self.subTest(origen=origen, destino=destino):
                nota = (f'BALANCE HÍDRICO EN {origen} HORAS:\n'
                        f'LA {origen * 10}\nLE {origen * 5}\nPI {origen}\n'
                        'GASTO URINARIO: 2,5 ML/KG/HORA\nANÁLISIS:\nSIN CAMBIOS')
                resultado = FUNCIONES['_actualizar_balance'](nota, destino)
                self.assertIn(f'LA {destino * 10:.1f} ML', resultado)
                self.assertIn(f'TOTAL EGRESOS: {destino * 6:.1f} ML', resultado)
                self.assertIn(f'BALANCE POSITIVO: {destino * 4:.1f} ML', resultado)
                self.assertIn('GASTO URINARIO: 2.50 ML/KG/HORA', resultado)
                self.assertTrue(resultado.endswith('ANÁLISIS:\nSIN CAMBIOS'))

    def test_sin_balance_no_modifica_texto(self):
        nota = 'EVOLUCIÓN\nANÁLISIS: SIN BALANCE DOCUMENTADO'
        self.assertEqual(FUNCIONES['_actualizar_balance'](nota, 12), nota)

    def actualizar(self, peso, nota=None):
        nota = nota or ('PESO AL NACER: 3000 G\n'
                        'PESO ANTERIOR: 2800 G, PESO ACTUAL: 2900 G. GANA 100 G.\n'
                        'ANÁLISIS: SIN CAMBIOS')
        return FUNCIONES['_actualizar_nota_local'](nota, date(2026, 9, 16), 0, peso, 24)

    def test_nuevo_peso_compara_con_ultima_medicion(self):
        for nuevo, esperado in ((2950, 'GANA 50 G'), (2850, 'PIERDE 50 G'),
                                (2900, 'SIN CAMBIOS 0 G')):
            with self.subTest(peso=nuevo):
                texto, nacimiento, previo, actual = self.actualizar(nuevo)
                self.assertEqual((nacimiento, previo, actual), (3000, 2900, nuevo))
                self.assertIn(f'PESO ANTERIOR: 2900 G, PESO ACTUAL: {nuevo} G', texto)
                self.assertIn(esperado, texto)

    def test_sin_medicion_nueva_conserva_bloque_de_peso(self):
        texto, _, previo, actual = self.actualizar(0)
        self.assertEqual((previo, actual), (2800, 2900))
        self.assertIn('PESO ANTERIOR: 2800 G, PESO ACTUAL: 2900 G. GANA 100 G.', texto)

    def test_si_falta_peso_actual_usa_anterior_disponible(self):
        _, _, previo, actual = self.actualizar(
            2950, 'PESO AL NACER: 3000 G\nPESO ANTERIOR: 2800 G\nANÁLISIS: ESTABLE')
        self.assertEqual((previo, actual), (2800, 2950))

    def test_evoluciones_sucesivas_actualizan_referencia(self):
        primera = self.actualizar(2950)[0]
        texto, _, previo, actual = self.actualizar(3000, primera)
        self.assertEqual((previo, actual), (2950, 3000))
        self.assertIn('GANA 50 G', texto)


if __name__ == '__main__':
    unittest.main()
