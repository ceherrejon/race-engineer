#!/usr/bin/env python3
"""Inventario de comentarios y verificación de que una limpieza solo tocó comentarios.

Uso:
  python comentarios.py inventario [rutas...]        cuenta y lista comentarios por categoría
  python comentarios.py inventario --json [rutas...]
  python comentarios.py verificar [--base REF]       compara el árbol de trabajo con REF (por defecto HEAD)

`verificar` sale con código 1 si algún archivo cambió algo más que comentarios.
Python se compara por AST (exacto). El resto de lenguajes se compara con un léxico
que entiende cadenas y comentarios; ante la duda marca "CAMBIA CÓDIGO", nunca al revés
en los casos soportados. Siempre conviene además compilar y correr las pruebas.
"""
import ast
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

C_LIKE = {".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".java", ".kt", ".kts", ".scala", ".go",
          ".rs", ".swift", ".dart", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".php", ".css",
          ".scss", ".less", ".gradle"}
NESTED_BLOCKS = {".kt", ".kts", ".scala", ".rs", ".swift", ".dart"}
TRIPLE_QUOTES = {".kt", ".kts", ".scala", ".swift", ".dart", ".java"}
BACKTICK = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go"}
HASH = {".sh", ".bash", ".zsh", ".rb", ".yml", ".yaml", ".toml", ".ps1", ".psm1", ".r", ".pl",
        ".cfg", ".conf", ".properties", ".dockerfile", ".mk"}
SQL = {".sql", ".lua"}
MARKUP = {".html", ".htm", ".xml", ".svg", ".vue", ".xaml"}
EXCLUIR = {".git", "node_modules", "build", "dist", ".gradle", "vendor", "__pycache__", ".venv",
           "venv", "target", ".idea", "out", "graphify-out"}

CATEGORIAS = [
    ("directiva", re.compile(r"noqa|type:\s*ignore|pylint:|eslint|@ts-|prettier-ignore|istanbul|"
                             r"NOLINT|#pragma|@Suppress|SuppressWarnings|nolint|ktlint-disable|"
                             r"fmt:\s*(off|on)|isort:|region\b|endregion|<editor-fold|shellcheck|"
                             r"^!|^\s*-\*-|coding[:=]|swiftlint|rubocop", re.I)),
    ("licencia", re.compile(r"copyright|SPDX-License|licen[cs]e|all rights reserved", re.I)),
    ("pendiente", re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")),
    ("documentacion", re.compile(r"^(/\*\*|///|//!|\"\"\"|''')")),
]
# Cinco palabras seguidas suenan a prosa: ante la duda el comentario queda "a_revisar", nunca "codigo_comentado".
PROSA = re.compile(r"(?:[^\W\d_]{2,} ){4}[^\W\d_]{2,}")
CODIGO_COMENTADO = re.compile(
    r"^\s*(?:[\w.\[\]]+\s*(?:=|\+=|-=)\s*\S|(?:return|import|from|if|for|while|val|var|let|const|"
    r"def|fun|class|public|private|func)\b.*|[\w.]+\(.*\)\s*;?\s*$|.*[;{}]\s*$)")


# ---------------------------------------------------------------- léxicos
def _scan_c_like(text, ext):
    """Devuelve (código_sin_comentarios, [(línea, comentario)])."""
    out, comments = [], []
    i, n, line = 0, len(text), 1
    nested = ext in NESTED_BLOCKS
    while i < n:
        ch = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            comments.append((line, text[i:j]))
            i = j
            continue
        if text.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if nested and text.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            chunk = text[i:j]
            comments.append((line, chunk))
            line += chunk.count("\n")
            out.append(" ")
            i = j
            continue
        if ext in TRIPLE_QUOTES and text.startswith('"""', i):
            j = text.find('"""', i + 3)
            j = n if j == -1 else j + 3
            out.append(text[i:j]); line += text[i:j].count("\n"); i = j
            continue
        if ch in "\"'" or (ch == "`" and ext in BACKTICK):
            j = i + 1
            while j < n and text[j] != ch:
                if text[j] == "\\":
                    j += 1
                elif text[j] == "\n" and ch != "`":
                    break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); line += text[i:j].count("\n"); i = j
            continue
        if ch == "\n":
            line += 1
        out.append(ch)
        i += 1
    return "".join(out), comments


def _scan_hash(text, ext, marker="#", block=None):
    out, comments = [], []
    i, n, line = 0, len(text), 1
    while i < n:
        ch = text[i]
        if block and text.startswith(block[0], i):
            j = text.find(block[1], i + len(block[0]))
            j = n if j == -1 else j + len(block[1])
            chunk = text[i:j]
            comments.append((line, chunk)); line += chunk.count("\n"); out.append(" "); i = j
            continue
        if text.startswith(marker, i) and (i == 0 or text[i - 1] in " \t\n;("):
            j = text.find("\n", i)
            j = n if j == -1 else j
            comments.append((line, text[i:j])); i = j
            continue
        if ch in "\"'":
            j = i + 1
            while j < n and text[j] != ch:
                if text[j] == "\\" and ch == '"':
                    j += 1
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); line += text[i:j].count("\n"); i = j
            continue
        if ch == "\n":
            line += 1
        out.append(ch)
        i += 1
    return "".join(out), comments


def _scan_markup(text):
    comments, out, last = [], [], 0
    for m in re.finditer(r"<!--.*?-->", text, re.S):
        comments.append((text.count("\n", 0, m.start()) + 1, m.group()))
        out.append(text[last:m.start()]); out.append(" "); last = m.end()
    out.append(text[last:])
    return "".join(out), comments


def _python_comments(text):
    comments = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                comments.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc is not None and node.body:
                    comments.append((node.body[0].lineno, '"""' + doc.strip().split("\n")[0]))
    except SyntaxError:
        pass
    return sorted(comments)


def scan(path: Path, text: str):
    """(código_normalizado | None, comentarios). None = lenguaje no soportado."""
    ext = path.suffix.lower() or ("." + path.name.lower())
    if ext == ".py":
        return None, _python_comments(text)
    if ext in C_LIKE:
        code, com = _scan_c_like(text, ext)
    elif ext in HASH:
        block = ("<#", "#>") if ext in {".ps1", ".psm1"} else None
        code, com = _scan_hash(text, ext, block=block)
    elif ext in SQL:
        code, com = _scan_hash(text, ext, marker="--", block=("/*", "*/") if ext == ".sql" else ("--[[", "]]"))
    elif ext in MARKUP:
        code, com = _scan_markup(text)
    else:
        return "NO_SOPORTADO", []
    return " ".join(code.split()), com


# ---------------------------------------------------------------- inventario
def categoria(comentario: str) -> str:
    cuerpo = comentario.strip()
    for nombre, rx in CATEGORIAS:
        if rx.search(cuerpo):
            return nombre
    limpio = re.sub(r"^(#|//+|/\*+|\*+|--|<!--)\s?", "", cuerpo).rstrip("*/ ->")
    lineas = [l.strip(" *#/") for l in limpio.splitlines() if l.strip(" *#/")]
    if any(PROSA.search(l) for l in lineas):
        return "a_revisar"
    if lineas and sum(bool(CODIGO_COMENTADO.match(l)) for l in lineas) / len(lineas) >= 0.6:
        return "codigo_comentado"
    return "a_revisar"


def archivos(rutas):
    for r in rutas or ["."]:
        p = Path(r)
        if p.is_file():
            yield p
            continue
        for f in p.rglob("*"):
            if f.is_file() and not (set(f.parts) & EXCLUIR):
                yield f


def cmd_inventario(rutas, como_json=False):
    filas, totales = [], {}
    for f in archivos(rutas):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        code, com = scan(f, text)
        if code == "NO_SOPORTADO":
            continue
        for linea, c in com:
            cat = categoria(c)
            totales[cat] = totales.get(cat, 0) + 1
            filas.append({"archivo": str(f), "linea": linea, "categoria": cat,
                          "texto": " ".join(c.split())[:160]})
    if como_json:
        print(json.dumps({"totales": totales, "comentarios": filas}, ensure_ascii=False, indent=1))
        return
    print("Totales:", ", ".join(f"{k}={v}" for k, v in sorted(totales.items())) or "sin comentarios")
    for fila in filas:
        print(f"{fila['archivo']}:{fila['linea']} [{fila['categoria']}] {fila['texto']}")


# ---------------------------------------------------------------- verificación
def _sin_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree


def comparar(path: Path, viejo: str, nuevo: str) -> str:
    ext = path.suffix.lower()
    if ext == ".py":
        try:
            a, b = ast.parse(viejo), ast.parse(nuevo)
        except SyntaxError:
            return "CAMBIA CÓDIGO (no compila)"
        if ast.dump(a) == ast.dump(b):
            return "OK"
        if ast.dump(_sin_docstrings(a)) == ast.dump(_sin_docstrings(b)):
            return "SOLO DOCSTRINGS"
        return "CAMBIA CÓDIGO"
    a, _ = scan(path, viejo)
    b, _ = scan(path, nuevo)
    if a == "NO_SOPORTADO":
        return "NO SOPORTADO (revisar a mano)"
    return "OK" if a == b else "CAMBIA CÓDIGO"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def cmd_verificar(base="HEAD"):
    raiz = Path(git("rev-parse", "--show-toplevel").strip())
    cambios = [l.split("\t") for l in git("diff", "--name-status", base).splitlines() if l.strip()]
    if not cambios:
        print("Sin cambios respecto a", base)
        return 0
    malo = False
    for estado, *rutas in cambios:
        ruta = rutas[-1]
        if estado != "M":
            print(f"{'CAMBIA CÓDIGO':<18}{ruta} (archivo {'añadido' if estado == 'A' else 'borrado/renombrado'})")
            malo = True
            continue
        viejo = git("show", f"{base}:{ruta}")
        nuevo = (raiz / ruta).read_text(encoding="utf-8")
        res = comparar(Path(ruta), viejo, nuevo)
        malo |= res.startswith("CAMBIA")
        print(f"{res:<18}{ruta}")
    print("\nResultado:", "HAY CAMBIOS DE CÓDIGO: revisar antes de continuar" if malo else "solo comentarios")
    return 1 if malo else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0] not in {"inventario", "verificar"}:
        print(__doc__)
        sys.exit(2)
    if args[0] == "inventario":
        como_json = "--json" in args
        cmd_inventario([a for a in args[1:] if a != "--json"], como_json)
    else:
        base = args[args.index("--base") + 1] if "--base" in args else "HEAD"
        sys.exit(cmd_verificar(base))
