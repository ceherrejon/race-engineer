"""Lo que se publica es coherente: manifiesto del plugin, skills, plantillas y resumen de prácticas."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skill"
PLANTILLAS = SKILLS / "race-engineer" / "templates"
RUTA_DE_MAQUINA = re.compile(r"[A-Za-z]:[\\/]|/Users/|/home/")


def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---", texto, re.S)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else {}


class Marketplace(unittest.TestCase):
    def test_cada_plugin_apunta_a_skills_que_existen(self):
        datos = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        nombres = [p["name"] for p in datos["plugins"]]
        self.assertEqual(len(nombres), len(set(nombres)))
        for plugin in datos["plugins"]:
            origen = RAIZ / plugin["source"]
            for ruta in plugin["skills"]:
                with self.subTest(plugin=plugin["name"], skill=ruta):
                    self.assertTrue((origen / ruta / "SKILL.md").is_file())

    def test_la_licencia_viaja_con_el_plugin(self):
        self.assertEqual((RAIZ / "LICENSE").read_text(encoding="utf-8"), (SKILLS / "LICENSE").read_text(encoding="utf-8"))


class Skills(unittest.TestCase):
    def test_frontmatter_valido(self):
        for skill in sorted(p.parent for p in SKILLS.glob("*/SKILL.md")):
            with self.subTest(skill=skill.name):
                campos = frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
                self.assertEqual(campos.get("name", "").strip(), skill.name)
                self.assertTrue(0 < len(campos.get("description", "").strip()) <= 1024)

    def test_skill_md_por_debajo_de_500_lineas(self):
        for skill_md in SKILLS.glob("*/SKILL.md"):
            with self.subTest(skill=skill_md.parent.name):
                self.assertLess(len(skill_md.read_text(encoding="utf-8").splitlines()), 500)

    def test_la_guardia_instalada_en_este_repo_es_la_de_la_skill(self):
        self.assertEqual((RAIZ / ".agents" / "hooks" / "guardia.py").read_text(encoding="utf-8"),
                         (SKILLS / "race-engineer" / "scripts" / "guardia.py").read_text(encoding="utf-8"))


class Plantillas(unittest.TestCase):
    def test_settings_de_claude_es_json_valido_y_portable(self):
        datos = json.loads((PLANTILLAS / "claude" / "settings.json").read_text(encoding="utf-8"))
        comandos = [h["command"] for grupo in datos["hooks"]["PreToolUse"] for h in grupo["hooks"]]
        self.assertTrue(comandos)
        for comando in comandos:
            self.assertNotRegex(comando, RUTA_DE_MAQUINA)
            self.assertIn("$CLAUDE_PROJECT_DIR", comando)

    @unittest.skipIf(tomllib is None, "requiere Python 3.11+")
    def test_config_de_codex_es_toml_valido_y_portable(self):
        datos = tomllib.loads((PLANTILLAS / "codex" / "config.toml").read_text(encoding="utf-8"))
        comandos = [h["command"] for grupo in datos["hooks"]["PreToolUse"] for h in grupo["hooks"]]
        self.assertTrue(comandos)
        for comando in comandos:
            self.assertNotRegex(comando, RUTA_DE_MAQUINA)
            self.assertIn("git rev-parse --show-toplevel", comando)


class Practicas(unittest.TestCase):
    def test_el_resumen_de_practicas_esta_al_dia(self):
        salida = SKILLS / "race-engineer" / "references" / "practicas.md"
        antes = salida.read_bytes()
        try:
            r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "generar_practicas.py")],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # Sin distinguir finales de línea: dependen de cómo git haya hecho el checkout en cada sistema.
            self.assertEqual(salida.read_bytes().replace(b"\r\n", b"\n"), antes.replace(b"\r\n", b"\n"),
                             "references/practicas.md está desactualizado: ejecuta herramientas/generar_practicas.py")
        finally:
            salida.write_bytes(antes)


if __name__ == "__main__":
    unittest.main()
