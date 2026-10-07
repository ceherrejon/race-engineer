#!/usr/bin/env python3
"""Inventario de un proyecto para configurarlo o auditarlo con Claude Code y/o Codex.

Uso:
  python inventario.py [ruta_proyecto] [--json]

Solo lee. No abre archivos de secretos (solo comprueba que existen y si git los ignora);
de los archivos de configuración extrae claves concretas, nunca valores de `env`.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guardia  # noqa: E402  (misma lista de secretos que el hook)

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

EXCLUIR = {".git", "node_modules", "build", "dist", ".gradle", "vendor", "__pycache__", ".venv", "venv",
           "target", ".idea", "out", ".next", ".turbo", "graphify-out", ".kotlin", ".wrangler", "worktrees",
           "Pods", ".dart_tool", "coverage", ".cache"}
INSTRUCCIONES = {"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "AGENTS.override.md"}
CARPETAS_DE_EJEMPLO = {"templates", "plantillas", "fixtures", "examples", "ejemplos", "testdata", "__fixtures__"}
LIMITE_LINEAS_CLAUDE = 200
LIMITE_BYTES_AGENTS = 32 * 1024
SECRETOS = re.compile(r"(^\.env(\..+)?$|^\.dev\.vars$|\.(key|pem|jks|keystore|p12|pfx)$|^id_(rsa|ed25519)$|"
                      r"credentials?\.json$|service[-_]?account.*\.json$|^firma\.properties$|^local\.properties$)", re.I)
SECRETOS_PERMITIDOS = re.compile(r"\.(example|sample|template|dist)$", re.I)
MARCADORES_STACK = [
    ("package.json", "Node/JavaScript"), ("tsconfig.json", "TypeScript"), ("pyproject.toml", "Python"),
    ("requirements.txt", "Python"), ("setup.py", "Python"), ("Pipfile", "Python"),
    ("build.gradle.kts", "Gradle (Kotlin DSL)"), ("build.gradle", "Gradle"), ("settings.gradle.kts", "Gradle"),
    ("AndroidManifest.xml", "Android"), ("pom.xml", "Maven/Java"), ("Cargo.toml", "Rust"), ("go.mod", "Go"),
    ("Gemfile", "Ruby"), ("composer.json", "PHP"), ("Package.swift", "Swift"), ("pubspec.yaml", "Flutter/Dart"),
    ("wrangler.toml", "Cloudflare Workers"), ("wrangler.jsonc", "Cloudflare Workers"), ("Dockerfile", "Docker"),
    ("docker-compose.yml", "Docker Compose"), ("deno.json", "Deno"), ("bun.lockb", "Bun"),
]
EXT_STACK = {".csproj": ".NET", ".sln": ".NET", ".xcodeproj": "iOS/macOS (Xcode)", ".tf": "Terraform"}
SDK_IA = re.compile(r"(@anthropic-ai/sdk|^\s*(import|from)\s+anthropic\b|com\.anthropic|anthropic-sdk|"
                    r"\bopenai\b.*(import|require)|(import|from)\s+openai\b|google\.generativeai|@google/genai)", re.M)
EXT_CODIGO = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".kt", ".java", ".go", ".rb", ".php", ".cs", ".rs"}
RUTA_CITADA = re.compile(r"`([^`\s]+)`|\]\(([^)\s]+)\)")
EXT_ARCHIVO = re.compile(r"\.(md|txt|json|jsonc|ya?ml|toml|ini|cfg|py|js|mjs|cjs|ts|tsx|jsx|kt|kts|java|gradle|xml|html?|css|scss|"
                         r"sh|ps1|bat|sql|rb|go|rs|cs|swift|dart|php|lock|env|properties|rules|csv)$", re.I)


# ---------------------------------------------------------------- utilidades
def recorrer(raiz: Path, max_prof=6):
    raiz_prof = len(raiz.parts)
    for actual, dirs, files in os.walk(raiz):
        p = Path(actual)
        dirs[:] = [d for d in dirs if d not in EXCLUIR and not (d.startswith(".") and d not in {".claude", ".codex", ".agents", ".github"})]
        if len(p.parts) - raiz_prof >= max_prof:
            dirs[:] = []
        yield p, dirs, files


def leer(p: Path, limite=400_000):
    try:
        if p.stat().st_size > limite:
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def ejecutar(*cmd, cwd=None, timeout=15):
    # En Windows los CLI de npm son .cmd: hay que lanzar la ruta completa que resuelve which().
    ruta = shutil.which(cmd[0])
    if not ruta:
        return None
    try:
        r = subprocess.run((ruta, *cmd[1:]), capture_output=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, text=True, encoding="utf-8", errors="replace", cwd=cwd, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def frontmatter(texto: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", texto or "", re.S)
    if not m:
        return {}
    campos = {}
    for linea in m.group(1).splitlines():
        if re.match(r"^[\w-]+\s*:", linea):
            k, v = linea.split(":", 1)
            campos[k.strip()] = v.strip().strip("\"'") or "(bloque)"
    return campos


_INDICE = {}


def existe_en_arbol(raiz: Path, ruta: str) -> bool:
    """¿Alguna ruta del árbol termina en `ruta`? (p. ej. «ui/narrar/» dentro de un paquete Kotlin)."""
    if raiz not in _INDICE:
        rutas = set()
        for p, dirs, files in recorrer(raiz, max_prof=12):
            rel = p.relative_to(raiz).as_posix()
            rutas.update(f"{rel}/{n}".lstrip("./") for n in dirs + files)
        _INDICE[raiz] = rutas
    sufijo = ruta.strip("/").replace("\\", "/")
    return any(r == sufijo or r.endswith("/" + sufijo) for r in _INDICE[raiz])


def rutas_rotas(archivo: Path, texto: str, raiz: Path):
    """Rutas relativas citadas en un .md que no existen (candidatas, no veredicto)."""
    faltan = set()
    for m in RUTA_CITADA.finditer(texto):
        ruta = (m.group(1) or m.group(2) or "").strip().rstrip(".,:;)")
        ruta = ruta.split("#")[0]
        if not ruta or len(ruta) > 160 or "://" in ruta or ruta.startswith(("~", "$", "/", "-", "@", "<", "%")):
            continue
        if re.search(r"[*?{}<>|\"'\s=…]|^\w+\(|^[A-Z]:|^\.\w+$", ruta):
            continue
        segmentos = [s for s in ruta.split("/") if s]
        if "/" not in ruta.rstrip("/") and not EXT_ARCHIVO.search(ruta):
            continue  # sin barra solo cuenta si parece un nombre de archivo (evita «Clase.Miembro»)
        if ruta.endswith("/") and len(segmentos) == 1:
            continue  # «jobs/» suele ser relativo a otra ruta mencionada en la misma frase
        if not ((archivo.parent / ruta).exists() or (raiz / ruta).exists() or existe_en_arbol(raiz, ruta)):
            faltan.add(ruta)
    return sorted(faltan)


# ---------------------------------------------------------------- secciones
def entorno():
    sistema = platform.system()
    wsl = sistema == "Linux" and "microsoft" in (leer(Path("/proc/version")) or "").lower()
    return {
        "sistema": "WSL2" if wsl else sistema,
        "windows_nativo": sistema == "Windows",
        "python": platform.python_version(),
        "interpretes": {n: ejecutar(n, "--version") for n in ("python3", "python", "py")},
        "claude_code": ejecutar("claude", "--version"),
        "codex": ejecutar("codex", "--version"),
    }


def git(raiz: Path):
    top = ejecutar("git", "rev-parse", "--show-toplevel", cwd=raiz)
    if not top:
        return {"es_repo": False}
    estado = ejecutar("git", "status", "--porcelain", cwd=raiz) or ""
    return {"es_repo": True, "raiz": top, "rama": ejecutar("git", "branch", "--show-current", cwd=raiz),
            "cambios_sin_commit": len([l for l in estado.splitlines() if l.strip()]),
            "remoto": bool(ejecutar("git", "remote", cwd=raiz))}


def stack(raiz: Path):
    encontrados, ia = {}, set()
    vistos = 0
    for p, dirs, files in recorrer(raiz, max_prof=4):
        rel = str(p.relative_to(raiz)) or "."
        for f in files:
            for marcador, nombre in MARCADORES_STACK:
                if f == marcador:
                    encontrados.setdefault(nombre, set()).add(rel)
            ext = Path(f).suffix
            if ext in EXT_STACK:
                encontrados.setdefault(EXT_STACK[ext], set()).add(rel)
            if ext in EXT_CODIGO and vistos < 3000 and (p / f).resolve() != Path(__file__).resolve():
                vistos += 1
                texto = leer(p / f, limite=200_000) or ""
                if SDK_IA.search(texto):
                    ia.add(str((p / f).relative_to(raiz)))
        for d in dirs:
            if d.endswith(".xcodeproj"):
                encontrados.setdefault("iOS/macOS (Xcode)", set()).add(rel)
    ci = [str(p.relative_to(raiz)) for p in (raiz / ".github" / "workflows").glob("*.y*ml")] if (raiz / ".github" / "workflows").is_dir() else []
    return {"tecnologias": {k: sorted(v)[:5] for k, v in sorted(encontrados.items())},
            "codigo_que_llama_a_modelos": sorted(ia)[:20], "ci": ci}


def instrucciones(raiz: Path):
    archivos, avisos = [], []
    for p, _, files in recorrer(raiz):
        if set(p.relative_to(raiz).parts) & CARPETAS_DE_EJEMPLO:
            continue  # una plantilla de AGENTS.md no es una instrucción que alguien cargue
        candidatos = [p / f for f in files if f in INSTRUCCIONES]
        if (p / ".claude" / "CLAUDE.md").is_file():
            candidatos.append(p / ".claude" / "CLAUDE.md")
        for a in candidatos:
            texto = leer(a) or ""
            archivos.append({"ruta": str(a.relative_to(raiz)), "lineas": texto.count("\n") + 1,
                             "bytes": a.stat().st_size, "importa_agents": "@AGENTS.md" in texto,
                             "rutas_citadas_que_no_existen": rutas_rotas(a, texto, raiz)})
    por_dir = {}
    for a in archivos:
        por_dir.setdefault(str(Path(a["ruta"]).parent), []).append(a)

    def ancestros_con(nombres, d):
        partes = Path(d).parts
        for i in range(len(partes), -1, -1):
            sub = str(Path(*partes[:i])) if i else "."
            for a in por_dir.get(sub, []):
                if Path(a["ruta"]).name in nombres or a["ruta"].endswith(".claude/CLAUDE.md") and "CLAUDE.md" in nombres:
                    return a
        return None

    for d, lista in por_dir.items():
        nombres = {Path(a["ruta"]).name for a in lista}
        if "AGENTS.md" in nombres:
            bloqueante = ancestros_con({"CLAUDE.md", "CLAUDE.local.md"}, d)
            importado = any(a["importa_agents"] for a in archivos if Path(a["ruta"]).name == "CLAUDE.md")
            if bloqueante and not importado:
                avisos.append(f"Claude Code NO lee {d}/AGENTS.md: existe {bloqueante['ruta']} y ningún CLAUDE.md importa @AGENTS.md "
                              "(correcto solo si los papeles son distintos a propósito; P-INS-04).")
        if "AGENTS.override.md" in nombres:
            avisos.append(f"{d}/AGENTS.override.md: Codex lo usa en lugar de AGENTS.md, pero Claude Code lo ignora (P-INS-04).")
        if "CLAUDE.local.md" in nombres and "AGENTS.md" in nombres and "CLAUDE.md" not in nombres:
            avisos.append(f"{d}/CLAUDE.local.md hace que Claude deje de leer {d}/AGENTS.md (P-INS-04).")
    for a in archivos:
        if Path(a["ruta"]).name == "CLAUDE.md" and a["lineas"] > LIMITE_LINEAS_CLAUDE:
            avisos.append(f"{a['ruta']}: {a['lineas']} líneas (> {LIMITE_LINEAS_CLAUDE}); mover a .claude/rules/ o skills (P-INS-01, C-01).")
        if a["rutas_citadas_que_no_existen"]:
            avisos.append(f"{a['ruta']}: cita rutas que no existen: {', '.join(a['rutas_citadas_que_no_existen'][:8])} (P-INS-13; revisar: pueden ser rutas generadas, de ejemplo o relativas a otra carpeta).")
    superiores = []
    for d in raiz.resolve().parents:
        for nombre in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md"):
            if (d / nombre).is_file() and (d / nombre).resolve() != (Path.home() / ".claude" / "CLAUDE.md").resolve():
                superiores.append(str(d / nombre))
    if superiores:
        avisos.append(f"Hay instrucciones de Claude por encima del proyecto ({', '.join(superiores)}): Claude las carga y, si el proyecto "
                      "depende de AGENTS.md sin CLAUDE.md propio, dejan de leerse sus AGENTS.md (P-INS-04).")
    total_agents = sum(a["bytes"] for a in archivos if Path(a["ruta"]).name in {"AGENTS.md", "AGENTS.override.md"})
    if total_agents > LIMITE_BYTES_AGENTS:
        avisos.append(f"AGENTS.md del proyecto suman {total_agents} bytes (> 32 KiB): Codex corta lo que exceda (P-CDX-01).")
    return {"archivos": archivos, "avisos": avisos}


def skills_en(carpeta: Path, raiz: Path):
    resultado = []
    if not carpeta.is_dir():
        return resultado
    for skill_md in sorted(carpeta.glob("*/SKILL.md")):
        texto = leer(skill_md) or ""
        fm = frontmatter(texto)
        resultado.append({"nombre": fm.get("name", skill_md.parent.name), "ruta": str(skill_md.relative_to(raiz)),
                          "lineas": texto.count("\n") + 1, "campos": sorted(fm),
                          "falta_description": "description" not in fm,
                          "archivos_citados_que_no_existen": rutas_rotas(skill_md, texto, skill_md.parent)})
    return resultado


def config_claude(raiz: Path):
    c = {"settings": {}, "reglas": [], "skills": skills_en(raiz / ".claude" / "skills", raiz), "agentes": [], "mcp": []}
    for nombre in ("settings.json", "settings.local.json"):
        p = raiz / ".claude" / nombre
        if not p.is_file():
            continue
        try:
            datos = json.loads(leer(p) or "{}")
        except json.JSONDecodeError as e:
            c["settings"][nombre] = {"error": f"JSON inválido: {e}"}
            continue
        perm = datos.get("permissions", {}) or {}
        hooks = {ev: [h.get("matcher", "*") for h in lst] for ev, lst in (datos.get("hooks") or {}).items()}
        c.setdefault("comandos_hooks", []).extend(
            (nombre, h2.get("command", "")) for lst in (datos.get("hooks") or {}).values() for h in lst
            for h2 in (h.get("hooks") or []) if isinstance(h2, dict))
        c["settings"][nombre] = {"allow": perm.get("allow", []), "deny": perm.get("deny", []), "ask": perm.get("ask", []),
                                 "defaultMode": perm.get("defaultMode"), "hooks": hooks,
                                 "plugins": sorted(k for k, v in (datos.get("enabledPlugins") or {}).items() if v),
                                 "otras_claves": sorted(k for k in datos if k not in {"permissions", "hooks", "enabledPlugins", "env"}),
                                 "versionado": bool(ejecutar("git", "ls-files", "--error-unmatch", str(p), cwd=raiz))}
    for r in sorted((raiz / ".claude" / "rules").glob("**/*.md")) if (raiz / ".claude" / "rules").is_dir() else []:
        fm = frontmatter(leer(r) or "")
        c["reglas"].append({"ruta": str(r.relative_to(raiz)), "paths": fm.get("paths", "(sin paths: se carga siempre)")})
    for a in sorted((raiz / ".claude" / "agents").glob("*.md")) if (raiz / ".claude" / "agents").is_dir() else []:
        fm = frontmatter(leer(a) or "")
        c["agentes"].append({"ruta": str(a.relative_to(raiz)), "campos": {k: fm[k] for k in ("name", "tools", "model", "effort", "maxTurns") if k in fm}})
    instalada = raiz / ".agents" / "hooks" / "guardia.py"
    if instalada.is_file():
        c["guardia"] = "al día" if instalada.read_bytes() == (Path(__file__).resolve().parent / "guardia.py").read_bytes() \
            else "DESACTUALIZADA respecto a la de la skill: volver a copiar scripts/guardia.py"
    mcp = raiz / ".mcp.json"
    if mcp.is_file():
        try:
            c["mcp"] = sorted((json.loads(leer(mcp) or "{}").get("mcpServers") or {}).keys())
        except json.JSONDecodeError:
            c["mcp"] = ["(.mcp.json inválido)"]
    return c


def toml(p: Path):
    if not tomllib or not p.is_file():
        return None
    try:
        return tomllib.loads(leer(p) or "")
    except tomllib.TOMLDecodeError as e:
        return {"__error__": str(e)}


def config_codex(raiz: Path):
    c = {"config_proyecto": None, "agentes": [], "reglas": [], "hooks_json": (raiz / ".codex" / "hooks.json").is_file(),
         "skills": skills_en(raiz / ".agents" / "skills", raiz), "skills_obsoletas": skills_en(raiz / ".codex" / "skills", raiz)}
    datos = toml(raiz / ".codex" / "config.toml")
    if datos is not None:
        sep = datos.get("shell_environment_policy", {}) or {}
        c["config_proyecto"] = {
            "error": datos.get("__error__"), "sandbox_mode": datos.get("sandbox_mode"),
            "approval_policy": datos.get("approval_policy"), "hooks": sorted((datos.get("hooks") or {}).keys()),
            "comandos_hooks": [h2.get("command", "") for lst in (datos.get("hooks") or {}).values() if isinstance(lst, list)
                               for h in lst if isinstance(h, dict) for h2 in (h.get("hooks") or []) if isinstance(h2, dict)],
            "mcp_servers": sorted((datos.get("mcp_servers") or {}).keys()),
            "filtra_secretos_env": sep.get("ignore_default_excludes") is False or sep.get("inherit") in {"core", "none"},
            "claves_ignoradas_en_proyecto": sorted(set(datos) & {"notify", "profile", "profiles", "model_provider", "model_providers"}),
        }
    for a in sorted((raiz / ".codex" / "agents").glob("*.toml")) if (raiz / ".codex" / "agents").is_dir() else []:
        d = toml(a) or {}
        c["agentes"].append({"ruta": str(a.relative_to(raiz)), "faltan": [k for k in ("name", "description", "developer_instructions") if k not in d]})
    if (raiz / ".codex" / "rules").is_dir():
        c["reglas"] = [str(r.relative_to(raiz)) for r in (raiz / ".codex" / "rules").glob("*.rules")]
    return c


def usuario(raiz: Path):
    home = Path.home()
    u = {"claude": {"CLAUDE.md": (home / ".claude" / "CLAUDE.md").is_file(),
                    "skills": sorted(p.name for p in (home / ".claude" / "skills").glob("*") if p.is_dir()) if (home / ".claude" / "skills").is_dir() else []},
         "codex": {}}
    cfg = toml(home / ".codex" / "config.toml")
    if cfg is not None:
        proyectos = cfg.get("projects", {}) or {}
        raiz_n = os.path.normcase(str(raiz.resolve()))
        confianza = next((v.get("trust_level") for k, v in proyectos.items()
                          if raiz_n == os.path.normcase(str(Path(k).resolve())) or raiz_n.startswith(os.path.normcase(str(Path(k).resolve())) + os.sep)), None)
        sep = cfg.get("shell_environment_policy", {}) or {}
        u["codex"] = {"confianza_de_este_proyecto": confianza or "no declarada (la capa .codex/ del proyecto no se carga)",
                      "model": cfg.get("model"), "model_reasoning_effort": cfg.get("model_reasoning_effort"),
                      "sandbox_mode": cfg.get("sandbox_mode"), "approval_policy": cfg.get("approval_policy"),
                      "filtra_secretos_env": sep.get("ignore_default_excludes") is False or sep.get("inherit") in {"core", "none"},
                      "hooks_activos": (cfg.get("features") or {}).get("hooks", True)}
    for nombre in ("AGENTS.md", "AGENTS.override.md"):
        p = home / ".codex" / nombre
        if p.is_file():
            texto = leer(p) or ""
            u["codex"][nombre] = {"lineas": texto.count("\n") + 1,
                                   "rutas_citadas_que_no_existen": [r for r in re.findall(r"`(~/[^`]+)`", texto)
                                                                    if not (home / r[2:]).exists()]}
    reglas = home / ".codex" / "rules"
    if reglas.is_dir():
        lineas = [l for r in reglas.glob("*.rules") for l in (leer(r) or "").splitlines() if l.startswith("prefix_rule(")]
        # Más de 4 piezas o una ruta absoluta: aprobación de un comando concreto, no un prefijo reutilizable.
        puntuales = [l for l in lineas if len(re.findall(r'"[^"]*"', l.split("decision")[0])) > 4
                     or re.search(r"[A-Za-z]:\\\\|/Users/|\\\\Users\\\\", l)]
        u["codex"]["rules"] = {"total": len(lineas), "puntuales_o_con_rutas": len(puntuales)}
    u["codex"]["skills_usuario"] = sorted(p.name for p in (home / ".agents" / "skills").glob("*") if p.is_dir()) if (home / ".agents" / "skills").is_dir() else []
    return u


RUTA_EXTERNA = re.compile(r"(?:~|%USERPROFILE%|\$HOME|[A-Za-z]:)[\\/][^\s`'\"),;]+"
                          r"|Path\.home\(\)(?:\s*/\s*[\"'][^\"'\n]+[\"'])+"
                          r"|user\.home[\"']\)\s*,\s*[\"'][^\"'\n]+[\"']")


def secretos_citados_fuera(raiz: Path):
    """Rutas a secretos fuera del proyecto que aparecen en instrucciones o código (no se abren)."""
    citados = {}
    for p, _, files in recorrer(raiz, max_prof=5):
        for f in files:
            # Solo instrucciones, skills/reglas y código: la documentación puede citar rutas sin usarlas.
            es_instruccion = f in INSTRUCCIONES or (f.endswith(".md") and {".claude", ".agents", ".codex"} & set(p.parts))
            if not (es_instruccion or Path(f).suffix in EXT_CODIGO | {".kts", ".gradle", ".toml"}):
                continue
            if set(p.relative_to(raiz).parts) & CARPETAS_DE_EJEMPLO:
                continue
            texto = leer(p / f, limite=200_000) or ""
            for m in RUTA_EXTERNA.finditer(texto):
                cita = re.sub(r"[\"'\s]+", "", m.group(0)).replace("user.home),", "~/")
                nombre = re.split(r"[\\/]", cita.rstrip("/\\"))[-1]
                if SECRETOS.search(nombre) or guardia.secreto_tocado(" " + nombre):
                    citados.setdefault(cita, set()).add(str((p / f).relative_to(raiz)))
    return [{"ruta": k, "citado_en": sorted(v)[:4]} for k, v in sorted(citados.items())]


def secretos(raiz: Path):
    hallados = []
    for p, _, files in recorrer(raiz, max_prof=5):
        for f in files:
            if SECRETOS.search(f) and not SECRETOS_PERMITIDOS.search(f):
                rel = str((p / f).relative_to(raiz))
                ignorado = ejecutar("git", "check-ignore", "-q", rel, cwd=raiz) is not None
                versionado = ejecutar("git", "ls-files", "--error-unmatch", rel, cwd=raiz) is not None
                hallados.append({"ruta": rel, "ignorado_por_git": ignorado, "versionado_en_git": versionado,
                                 "bloqueado_por_guardia_de_serie": bool(guardia.secreto_tocado(" " + f))})
    return hallados


RUTA_DE_MAQUINA = re.compile(r"[A-Za-z]:[\\/]|/Users/|/home/")


def portabilidad(inv):
    """Avisos sobre configuración versionada que solo funcionaría en esta máquina o con este intérprete."""
    avisos = []
    comandos = [("Claude " + n, c) for n, c in inv["claude"].get("comandos_hooks", [])]
    comandos += [("Codex", c) for c in ((inv["codex"]["config_proyecto"] or {}).get("comandos_hooks") or [])]
    disponibles = {n for n, v in inv["entorno"]["interpretes"].items() if v}
    for origen, cmd in comandos:
        if RUTA_DE_MAQUINA.search(cmd):
            avisos.append(f"Hook de {origen} con ruta absoluta de una máquina: `{cmd}`. En otra máquina fallará y un hook que falla deja pasar. "
                          "Usar `$CLAUDE_PROJECT_DIR` (Claude) o `$(git rev-parse --show-toplevel)` (Codex).")
        primero = cmd.strip().split(" ", 1)[0].strip('"')
        if primero in {"python", "python3", "py"} and primero not in disponibles:
            avisos.append(f"Hook de {origen} usa `{primero}`, que no existe en esta máquina (hay: {', '.join(sorted(disponibles)) or 'ninguno'}).")
        if "git rev-parse" in cmd and not inv["git"]["es_repo"]:
            avisos.append(f"Hook de {origen} depende de git, pero el proyecto no es un repositorio: fallará y dejará pasar.")
    if comandos and inv["entorno"]["windows_nativo"] and "python3" not in disponibles:
        avisos.append("En esta máquina no existe `python3`: si el equipo comparte la configuración, acordar el intérprete (ver INCORPORACION.md).")
    return avisos


# ---------------------------------------------------------------- informe
def inventario(raiz: Path):
    inv = {"proyecto": str(raiz), "entorno": entorno(), "git": git(raiz), "stack": stack(raiz),
           "instrucciones": instrucciones(raiz), "claude": config_claude(raiz), "codex": config_codex(raiz),
           "usuario": usuario(raiz), "secretos_en_el_arbol": secretos(raiz),
           "secretos_fuera_citados": secretos_citados_fuera(raiz)}
    usa_claude = bool(inv["claude"]["settings"] or inv["claude"]["skills"] or any(Path(a["ruta"]).name.startswith("CLAUDE") for a in inv["instrucciones"]["archivos"]))
    usa_codex = bool(inv["codex"]["config_proyecto"] or inv["codex"]["skills"] or any(Path(a["ruta"]).name.startswith("AGENTS") for a in inv["instrucciones"]["archivos"]))
    inv["portabilidad"] = portabilidad(inv)
    inv["deducido"] = {"herramientas": [h for h, s in (("Claude Code", usa_claude), ("Codex", usa_codex)) if s] or ["ninguna configurada (proyecto nuevo)"],
                       "llama_a_modelos": bool(inv["stack"]["codigo_que_llama_a_modelos"])}
    return inv


def markdown(inv):
    e, g, d = inv["entorno"], inv["git"], inv["deducido"]
    out = [f"# Inventario de {inv['proyecto']}", "",
           f"- **Sistema:** {e['sistema']}{' (sin sandbox de Bash para Claude; Codex sí tiene sandbox)' if e['windows_nativo'] else ''}",
           f"- **Claude Code:** {e['claude_code'] or 'no encontrado'} · **Codex:** {e['codex'] or 'no encontrado'}",
           f"- **Intérpretes de Python:** " + (", ".join(f"`{n}` ({v})" for n, v in e["interpretes"].items() if v) or "ninguno"),
           f"- **Git:** " + (f"rama `{g.get('rama')}`, {g['cambios_sin_commit']} cambios sin commit, remoto: {'sí' if g['remoto'] else 'no'}" if g["es_repo"] else "no es un repositorio"),
           f"- **Herramientas configuradas:** {', '.join(d['herramientas'])}",
           f"- **Stack:** " + (", ".join(f"{k} ({', '.join(v)})" for k, v in inv['stack']['tecnologias'].items()) or "sin marcadores"),
           f"- **Código que llama a modelos:** " + (", ".join(inv["stack"]["codigo_que_llama_a_modelos"][:6]) or "no"),
           f"- **CI:** " + (", ".join(inv["stack"]["ci"]) or "no"), "", "## Instrucciones", ""]
    for a in inv["instrucciones"]["archivos"]:
        out.append(f"- `{a['ruta']}`: {a['lineas']} líneas, {a['bytes']} bytes" + (" · importa @AGENTS.md" if a["importa_agents"] else ""))
    out += ["", "## Avisos", ""] + [f"- {x}" for x in inv["instrucciones"]["avisos"] + inv["portabilidad"]] + [""]
    c = inv["claude"]
    out += ["## Claude Code (proyecto)", ""]
    for n, s in c["settings"].items():
        if "error" in s:
            out.append(f"- `{n}`: {s['error']}")
            continue
        out.append(f"- `{n}` ({'versionado' if s['versionado'] else 'NO versionado'}): allow={len(s['allow'])}, deny={len(s['deny'])}, ask={len(s['ask'])}, "
                   f"hooks={s['hooks'] or 'ninguno'}, plugins={s['plugins'] or 'ninguno'}")
    out.append(f"- Reglas `.claude/rules`: {len(c['reglas'])} · Subagentes: {len(c['agentes'])} · MCP (.mcp.json): {c['mcp'] or 'ninguno'}"
               + (f" · Guardia `.agents/hooks/guardia.py`: {c['guardia']}" if c.get("guardia") else ""))
    for s in c["skills"]:
        out.append(f"- Skill `{s['nombre']}`: {s['lineas']} líneas, campos {s['campos']}"
                   + (f" · **cita archivos que no existen:** {s['archivos_citados_que_no_existen']}" if s["archivos_citados_que_no_existen"] else ""))
    x = inv["codex"]
    out += ["", "## Codex (proyecto)", "", f"- `.codex/config.toml`: {x['config_proyecto'] or 'no existe'}",
            f"- Subagentes: {len(x['agentes'])} · reglas: {x['reglas'] or 'ninguna'} · skills `.agents/skills`: {[s['nombre'] for s in x['skills']] or 'ninguna'}"
            + (f" · **skills en ruta obsoleta `.codex/skills`:** {[s['nombre'] for s in x['skills_obsoletas']]}" if x["skills_obsoletas"] else "")]
    u = inv["usuario"]
    out += ["", "## Nivel de usuario (solo informar; editar solo si el usuario lo pide)", "",
            f"- `~/.claude/CLAUDE.md`: {'sí' if u['claude']['CLAUDE.md'] else 'no'} · skills de usuario Claude: {len(u['claude']['skills'])}",
            f"- Codex: {json.dumps(u['codex'], ensure_ascii=False)}", "", "## Posibles secretos en el árbol (no se abrieron)", ""]
    for s in inv["secretos_en_el_arbol"]:
        if s["versionado_en_git"]:
            estado = "**VERSIONADO en git**: .gitignore no basta; proponer `git rm --cached` y rotar el secreto (con aprobación)"
        else:
            estado = "ignorado por git" if s["ignorado_por_git"] else "**NO ignorado por git**: añadir a .gitignore"
        if not s["bloqueado_por_guardia_de_serie"]:
            estado += " · la guardia de serie no lo cubre: añadir patrón a `.agents/guardia.txt`"
        out.append(f"- `{s['ruta']}` · {estado}")
    if not inv["secretos_en_el_arbol"]:
        out.append("- ninguno")
    out += ["", "## Secretos fuera del proyecto citados en instrucciones o código (no se abrieron)", ""]
    out += [f"- `{s['ruta']}` · citado en {', '.join(s['citado_en'])} · proteger con `bloquear:` en `.agents/guardia.txt`"
            for s in inv["secretos_fuera_citados"]] or ["- ninguno"]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a != "--json"]
    raiz = Path(args[0] if args else ".").resolve()
    datos = inventario(raiz)
    print(json.dumps(datos, ensure_ascii=False, indent=1) if "--json" in sys.argv else markdown(datos))
