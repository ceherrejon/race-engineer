"""La guardia se ejecuta como la lanzan Claude Code y Codex: un proceso que lee JSON por stdin."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARDIA = Path(__file__).resolve().parent.parent / "skill" / "race-engineer" / "scripts" / "guardia.py"


def decidir(datos, entrada_cruda=None):
    """Devuelve (decisión, código de salida); la decisión es None cuando la guardia deja pasar."""
    r = subprocess.run([sys.executable, str(GUARDIA)], input=entrada_cruda if entrada_cruda is not None else json.dumps(datos),
                       capture_output=True, text=True, encoding="utf-8")
    salida = r.stdout.strip()
    decision = json.loads(salida)["hookSpecificOutput"]["permissionDecision"] if salida else None
    return decision, r.returncode


class SecretosDeSerie(unittest.TestCase):
    def test_bloquea_leer_un_env(self):
        self.assertEqual(decidir({"tool_name": "Read", "tool_input": {"file_path": "config/.env"}}), ("deny", 0))

    def test_bloquea_variantes_del_env_y_claves(self):
        for ruta in ("app/.env.production", "certs/servidor.pem", "firma.jks", "~/.ssh/id_ed25519", "gcp/service-account-prod.json"):
            with self.subTest(ruta=ruta):
                self.assertEqual(decidir({"tool_name": "Read", "tool_input": {"file_path": ruta}})[0], "deny")

    def test_deja_pasar_ejemplos_y_claves_publicas(self):
        for ruta in (".env.example", ".env.sample", "~/.ssh/id_ed25519.pub", "src/environment.ts"):
            with self.subTest(ruta=ruta):
                self.assertIsNone(decidir({"tool_name": "Read", "tool_input": {"file_path": ruta}})[0])

    def test_bloquea_la_shell_de_claude(self):
        for herramienta in ("Bash", "PowerShell"):
            with self.subTest(herramienta=herramienta):
                self.assertEqual(decidir({"tool_name": herramienta, "tool_input": {"command": "cat .env | head"}})[0], "deny")

    def test_deja_pasar_comandos_normales(self):
        self.assertIsNone(decidir({"tool_name": "Bash", "tool_input": {"command": "git status && ls -la"}})[0])

    def test_bloquea_la_shell_de_codex_con_cualquier_nombre(self):
        datos = {"tool_name": "herramienta_nueva", "tool_input": {"cmd": ["cat", "server/.dev.vars"]}}
        self.assertEqual(decidir(datos)[0], "deny")

    def test_bloquea_apply_patch_sobre_un_secreto(self):
        parche = "*** Begin Patch\n*** Update File: config/.env\n@@\n-A=1\n+A=2\n*** End Patch"
        self.assertEqual(decidir({"tool_name": "apply_patch", "tool_input": {"input": parche}})[0], "deny")

    def test_no_revisa_el_contenido_que_se_escribe(self):
        datos = {"tool_name": "Write", "tool_input": {"file_path": "docs/secretos.md", "content": "No abras el .env"}}
        self.assertIsNone(decidir(datos)[0])


class PatronesDelProyecto(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / ".agents").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _bash(self, comando):
        return decidir({"tool_name": "Bash", "cwd": str(self.raiz), "tool_input": {"command": comando}})[0]

    def test_bloquear_y_preguntar_desde_guardia_txt(self):
        (self.raiz / ".agents" / "guardia.txt").write_text(
            "# comentario\nbloquear: firma\\.properties\npreguntar: \\bnpm\\s+publish\\b\n", encoding="utf-8")
        self.assertEqual(self._bash("cat app/firma.properties"), "deny")
        self.assertEqual(self._bash("npm publish --access public"), "ask")
        self.assertIsNone(self._bash("npm test"))

    def test_patrones_personales_en_guardia_local_txt(self):
        (self.raiz / ".agents" / "guardia.local.txt").write_text("bloquear: [\\\\/]\\.mis-claves[\\\\/]\n", encoding="utf-8")
        self.assertEqual(self._bash("cat ~/.mis-claves/api.txt"), "deny")

    def test_un_patron_invalido_no_rompe_la_guardia(self):
        (self.raiz / ".agents" / "guardia.txt").write_text("bloquear: [sin-cerrar\nbloquear: firma\\.properties\n", encoding="utf-8")
        self.assertEqual(self._bash("cat firma.properties"), "deny")


class EntradaRota(unittest.TestCase):
    def test_deja_pasar_sin_fallar_si_la_entrada_no_es_json(self):
        self.assertEqual(decidir(None, entrada_cruda="esto no es json"), (None, 0))


if __name__ == "__main__":
    unittest.main()
