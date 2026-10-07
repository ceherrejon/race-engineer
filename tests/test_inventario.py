"""El inventario sobre un proyecto de juguete: solo lee y devuelve lo que la skill necesita para decidir."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

INVENTARIO = Path(__file__).resolve().parent.parent / "skill" / "race-engineer" / "scripts" / "inventario.py"


def git(raiz, *args):
    subprocess.run(["git", *args], cwd=raiz, check=True, capture_output=True)


@unittest.skipUnless(shutil.which("git"), "requiere git")
class InventarioDeUnProyecto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        raiz = cls.raiz = Path(cls.tmp.name)
        git(raiz, "init", "-q")
        (raiz / "package.json").write_text('{"name": "juguete"}', encoding="utf-8")
        (raiz / "AGENTS.md").write_text("# Juguete\n\nLas pruebas están en `tests/no-existe.py`.\n", encoding="utf-8")
        (raiz / "CLAUDE.md").write_text("Instrucciones solo para Claude.\n", encoding="utf-8")
        (raiz / "src").mkdir()
        (raiz / "src" / "ia.py").write_text("import anthropic\n", encoding="utf-8")
        (raiz / ".env").write_text("CLAVE=falsa\n", encoding="utf-8")
        (raiz / "local.properties").write_text("sdk.dir=x\n", encoding="utf-8")
        (raiz / ".gitignore").write_text("local.properties\n", encoding="utf-8")
        cls.antes = sorted(p.relative_to(raiz).as_posix() for p in raiz.rglob("*") if ".git" not in p.parts)
        r = subprocess.run([sys.executable, str(INVENTARIO), str(raiz), "--json"], capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        cls.inv = json.loads(r.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_detecta_el_stack_y_el_codigo_que_llama_a_modelos(self):
        self.assertIn("Node/JavaScript", self.inv["stack"]["tecnologias"])
        self.assertTrue(self.inv["deducido"]["llama_a_modelos"])

    def test_avisa_que_claude_no_lee_agents_md(self):
        avisos = " ".join(self.inv["instrucciones"]["avisos"])
        self.assertIn("NO lee", avisos)
        self.assertIn("tests/no-existe.py", avisos)

    def test_clasifica_los_secretos_sin_abrirlos(self):
        secretos = {s["ruta"]: s for s in self.inv["secretos_en_el_arbol"]}
        self.assertFalse(secretos[".env"]["ignorado_por_git"])
        self.assertTrue(secretos[".env"]["bloqueado_por_guardia_de_serie"])
        self.assertTrue(secretos["local.properties"]["ignorado_por_git"])
        self.assertFalse(secretos["local.properties"]["bloqueado_por_guardia_de_serie"])

    def test_no_escribe_nada_en_el_proyecto(self):
        despues = sorted(p.relative_to(self.raiz).as_posix() for p in self.raiz.rglob("*") if ".git" not in p.parts)
        self.assertEqual(self.antes, despues)

    def test_el_informe_en_markdown_se_genera(self):
        r = subprocess.run([sys.executable, str(INVENTARIO), str(self.raiz)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("## Posibles secretos en el árbol", r.stdout)


class InventarioSinGit(unittest.TestCase):
    def test_funciona_en_una_carpeta_que_no_es_repositorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(INVENTARIO), tmp, "--json"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            inv = json.loads(r.stdout)
            self.assertFalse(inv["git"]["es_repo"])
            self.assertEqual(inv["deducido"]["herramientas"], ["ninguna configurada (proyecto nuevo)"])


if __name__ == "__main__":
    unittest.main()
