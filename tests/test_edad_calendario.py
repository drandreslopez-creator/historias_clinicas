from datetime import date, timedelta
import unittest
from core.calculos import calcular_edad


class EdadCalendarioTests(unittest.TestCase):
    def test_cumpleanos_y_vispera_despues_de_bisiesto(self):
        self.assertEqual(calcular_edad(date(2020, 3, 1), date(2021, 2, 28)), (0, 11, 27))
        self.assertEqual(calcular_edad(date(2020, 3, 1), date(2021, 3, 1)), (1, 0, 0))

    def test_recien_nacido_y_meses_de_distinta_duracion(self):
        self.assertEqual(calcular_edad(date(2026, 1, 1), date(2026, 1, 1)), (0, 0, 0))
        self.assertEqual(calcular_edad(date(2026, 1, 1), date(2026, 2, 1)), (0, 1, 0))
        self.assertEqual(calcular_edad(date(2026, 1, 1), date(2026, 1, 31)), (0, 0, 30))

    def test_fin_de_mes_y_nacimiento_bisiesto(self):
        self.assertEqual(calcular_edad(date(2024, 2, 29), date(2025, 2, 28)), (1, 0, 0))
        self.assertEqual(calcular_edad(date(2026, 1, 31), date(2026, 2, 28)), (0, 1, 0))
        self.assertEqual(calcular_edad(date(2026, 1, 31), date(2026, 3, 1)), (0, 1, 1))

    def test_no_produce_doce_meses_ni_componentes_negativos(self):
        nacimiento = date(2020, 2, 29)
        for dias in range(2500):
            anios, meses, resto = calcular_edad(nacimiento, nacimiento + timedelta(days=dias))
            self.assertGreaterEqual(anios, 0)
            self.assertTrue(0 <= meses < 12)
            self.assertTrue(0 <= resto <= 30)

    def test_rechaza_fecha_futura(self):
        with self.assertRaises(ValueError):
            calcular_edad(date(2027, 1, 1), date(2026, 1, 1))
