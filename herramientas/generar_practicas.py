#!/usr/bin/env python3
"""Genera skill/race-engineer/references/practicas.md a partir de conocimiento/.

La skill cita prácticas (P-INS-04, D-12, C-01…) que viven en la base de conocimiento de este proyecto,
que no se distribuye con la skill. Este script copia, de cada práctica citada, el título, el «qué» y el
«por qué», para que la skill se entienda sola. Hay que volver a ejecutarlo cuando cambie una práctica.

Uso: python herramientas/generar_practicas.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skill" / "race-engineer"
SALIDA = SKILL / "references" / "practicas.md"
ID = re.compile(r"\b(P-[A-Z]{3}-\d+|D-\d{2}|C-\d{2})\b")
CABECERA = re.compile(r"^### (P-[A-Z]{3}-\d+|D-\d{2}|C-\d{2})\b\s*·?\s*(.*)$")
CAMPO = re.compile(r"^- \*\*(Qué|Decisión|Por qué|Resolución[^*]*|Actualización[^*]*):\*\*\s*(.*)$")


def citadas():
    ids = set()
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py", ".toml", ".json"} and p != SALIDA:
            ids |= set(ID.findall(p.read_text(encoding="utf-8")))
    return ids


def limpiar(texto: str, limite=420):
    texto = re.sub(r"\s*\((?:ver )?F0\d\d[^)]*\)", "", texto)  # las fichas de fuentes no viajan con la skill
    texto = re.sub(r"\s*(?:de|según|en) F0\d\d\b", "", texto)
    texto = re.sub(r"\bF0\d\d\b", "una fuente del proyecto", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = re.sub(r"`\[(Claude|Codex|Ambos)\]`", r"[\1]", texto)
    return texto if len(texto) <= limite else texto[:limite].rsplit(" ", 1)[0] + "…"


def practicas():
    datos = {}
    for archivo in sorted((RAIZ / "conocimiento").glob("[0-9]*.md")):
        actual, campo = None, None
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            m = CABECERA.match(linea)
            if m:
                actual = m.group(1)
                titulo = re.sub(r"\s*`\[[^\]]+\]`(\s*`\[[^\]]+\]`)*\s*$", "", m.group(2)).strip()
                etiquetas = re.findall(r"`\[(Claude|Codex|Ambos)\]`", m.group(2))
                datos[actual] = {"titulo": titulo, "aplica": "/".join(etiquetas), "que": "", "porque": "",
                                 "tema": archivo.stem}
                campo = None
                continue
            if actual is None:
                continue
            if linea.startswith("## ") or linea.startswith("### "):
                actual = None
                continue
            m = CAMPO.match(linea)
            if m:
                nombre = m.group(1)
                campo = "porque" if nombre == "Por qué" else "que"
                acumula = nombre.startswith(("Resolución", "Actualización"))  # en conflictos vale la última
                if not datos[actual][campo] or acumula:
                    datos[actual][campo] = (datos[actual][campo] + " " if acumula and datos[actual][campo] else "") + m.group(2)
                else:
                    campo = None
                continue
            if campo and linea.startswith("  ") and not datos[actual][campo].endswith("…"):
                # Continuación con viñetas del mismo campo: se resume en una línea.
                datos[actual][campo] += " " + linea.strip().lstrip("-").strip()
            elif linea.startswith("- **"):
                campo = None
    return datos


def main():
    ids, datos = citadas(), practicas()
    faltan = sorted(i for i in ids if i not in datos)
    orden = lambda i: (i[0], i.split("-")[1] if i.startswith("P-") else "", int(re.findall(r"\d+", i)[-1]))
    lineas = ["# Prácticas citadas por la skill", "",
              "Resumen de cada práctica que aparece en `SKILL.md`, `references/` o los scripts: qué pide y por qué.",
              "Las fuentes completas y el razonamiento están en la base de conocimiento del repositorio race-engineer (`conocimiento/` y `fuentes/`).",
              "Este archivo se genera con `herramientas/generar_practicas.py`: no se edita a mano.", ""]
    for i in sorted(ids & set(datos), key=orden):
        d = datos[i]
        aplica = f" `[{d['aplica']}]`" if d["aplica"] else ""
        lineas.append(f"### {i} · {d['titulo']}{aplica}")
        if d["que"]:
            lineas.append(f"- **Qué:** {limpiar(d['que'], 900 if i.startswith('C-') else 480)}")
        if d["porque"]:
            lineas.append(f"- **Por qué:** {limpiar(d['porque'], 300)}")
        lineas.append("")
    SALIDA.write_text("\n".join(lineas), encoding="utf-8")
    print(f"{len(ids & set(datos))} prácticas escritas en {SALIDA.relative_to(RAIZ)}")
    if faltan:
        print("Citadas pero no encontradas en conocimiento/:", ", ".join(faltan))
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
