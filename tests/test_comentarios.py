"""La verificación de limpiar-comentarios: distingue un cambio de comentarios de un cambio de código."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skill" / "limpiar-comentarios" / "scripts"))
import comentarios  # noqa: E402


class Comparar(unittest.TestCase):
    def test_python_solo_comentarios(self):
        viejo = "x = 1  # suma uno\n# narración\ny = x + 1\n"
        nuevo = "x = 1\ny = x + 1\n"
        self.assertEqual(comentarios.comparar(Path("a.py"), viejo, nuevo), "OK")

    def test_python_cambio_de_codigo(self):
        self.assertEqual(comentarios.comparar(Path("a.py"), "x = 1\n", "x = 2\n"), "CAMBIA CÓDIGO")

    def test_python_solo_docstrings(self):
        viejo = 'def f():\n    """Devuelve uno."""\n    return 1\n'
        nuevo = "def f():\n    return 1\n"
        self.assertEqual(comentarios.comparar(Path("a.py"), viejo, nuevo), "SOLO DOCSTRINGS")

    def test_javascript_comentarios_y_cadenas(self):
        viejo = 'const url = "http://x"; // la URL\n/* bloque */\nlet a = 1;\n'
        self.assertEqual(comentarios.comparar(Path("a.js"), viejo, 'const url = "http://x";\nlet a = 1;\n'), "OK")
        self.assertEqual(comentarios.comparar(Path("a.js"), viejo, 'const url = "http://y";\nlet a = 1;\n'), "CAMBIA CÓDIGO")

    def test_un_comentario_dentro_de_una_cadena_es_codigo(self):
        viejo = 'const s = "// no es comentario";\n'
        self.assertEqual(comentarios.comparar(Path("a.ts"), viejo, 'const s = "";\n'), "CAMBIA CÓDIGO")


class Categorias(unittest.TestCase):
    def test_categorias_deterministas(self):
        casos = {
            "# noqa: E501": "directiva",
            "// Copyright 2026 Alguien": "licencia",
            "// TODO: quitar cuando salga la v2": "pendiente",
            "/** Documentación pública. */": "documentacion",
            "// x = calcular(y);": "codigo_comentado",
            "// incrementa el contador de visitas del usuario": "a_revisar",
        }
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(comentarios.categoria(texto), esperado)


if __name__ == "__main__":
    unittest.main()
