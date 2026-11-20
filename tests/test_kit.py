import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kit_veeduria import fichas, peticion  # noqa: E402

LIMITE = 6000  # caracteres por respuesta: cabe de sobra en un contexto de 16k


class TestFichas(unittest.TestCase):
    def test_menu_lista_todas(self):
        m = fichas.menu()
        for id_ in fichas.cargar():
            self.assertIn(id_, m)

    def test_cada_ficha_cabe_y_tiene_fuentes(self):
        for id_, f in fichas.cargar().items():
            txt = fichas.ficha(id_)
            self.assertLess(len(txt), LIMITE, id_)
            self.assertTrue(f["fuentes"], id_)
            self.assertIn("revisión jurídica", txt)

    def test_ficha_por_numero(self):
        self.assertIn("#", fichas.ficha("1"))

    def test_ficha_inexistente_lista_validos(self):
        r = fichas.ficha("no-existe")
        self.assertIn("Ids válidos", r)
        self.assertIn("derecho-de-peticion", r)


class TestPeticion(unittest.TestCase):
    def test_tipos_y_plazos(self):
        t = peticion.tipos()
        self.assertIn("10 días", t)
        self.assertIn("15 días", t)
        self.assertIn("30 días", t)

    def test_generar_cada_tipo(self):
        for tipo, (_, plazo, _) in peticion.TIPOS.items():
            r = peticion.generar(tipo, "Alcaldía de X", "Copia del contrato Y",
                                 ["Fecha", "Valor"], "PDF")
            self.assertIn("[NOMBRE COMPLETO]", r)
            self.assertIn("[NÚMERO DE CÉDULA]", r)
            self.assertIn("[CORREO ELECTRÓNICO DE RESPUESTA]", r)
            self.assertIn(f"{plazo} días hábiles", r)
            self.assertIn("Alcaldía de X", r)
            self.assertLess(len(r), LIMITE + 2000)

    def test_no_repite_el_error_de_la_ley(self):
        r = peticion.generar("informacion", "Entidad", "algo")
        self.assertNotIn("1447", r)
        self.assertIn("Ley 1437 de 2011", r)
        self.assertIn("Ley 1755 de 2015", r)

    def test_errores_utiles(self):
        self.assertIn("Claves válidas", peticion.generar("xx", "E", "S"))
        self.assertIn("Faltan datos", peticion.generar("informacion", "", "S"))
        self.assertIn("demasiado largo",
                      peticion.generar("informacion", "E", "x" * 2000))

    def test_items_se_limitan(self):
        r = peticion.generar("informacion", "E", "S", [f"i{n}" for n in range(30)])
        self.assertIn("j. i9", r)
        self.assertNotIn("k. ", r)


class TestResumenTemas(unittest.TestCase):
    def test_lista_todos_los_temas_con_resumen(self):
        r = fichas.resumen_temas()
        for id_, f in fichas.cargar().items():
            self.assertIn(f"- {id_}: {f['resumen']}", r)


class TestGuardar(unittest.TestCase):
    def test_guarda_archivo_y_no_devuelve_la_carta(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            os.environ["KIT_VEEDURIA_SALIDA"] = d
            try:
                r = peticion.guardar("copia_documentos", "Alcaldía de Soacha", "Copia del contrato Z")
            finally:
                del os.environ["KIT_VEEDURIA_SALIDA"]
            archivos = list(Path(d).iterdir())
            self.assertEqual(len(archivos), 1)
            self.assertIn(str(archivos[0]), r)
            self.assertNotIn("FUNDAMENTOS DE DERECHO", r)
            self.assertLess(len(r), 1200)
            if archivos[0].suffix == ".txt":
                txt = archivos[0].read_text(encoding="utf-8")
                self.assertIn("FUNDAMENTOS DE DERECHO", txt)
                self.assertIn("[NOMBRE COMPLETO]", txt)

    def test_error_no_crea_archivo(self):
        self.assertIn("Claves válidas", peticion.guardar("xx", "E", "S"))


if __name__ == "__main__":
    unittest.main()
