#!/usr/bin/env python3
"""
scripts/actualizar_readme.py
Genera y actualiza el README.md del repositorio renderizando la plantilla scripts/plantillas/README.md
con las cifras oficiales y el árbol de estructura generado dinámicamente.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLANTILLA_PATH = BASE_DIR / "scripts" / "plantillas" / "README.md"
README_PATH = BASE_DIR / "README.md"
CIFRAS_PATH = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes" / "cifras_oficiales.json"

RX_MARCA = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)\s*\}\}")


def generate_tree(prefix: str = "") -> list[str]:
    """Árbol de archivos construido solo con lo versionado en git (git ls-files)."""
    r = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
    arbol: dict = {}
    for rel in sorted(r.stdout.splitlines()):
        partes = rel.split("/")
        if any(p.startswith(".") for p in partes):
            continue
        nodo = arbol
        for p in partes[:-1]:
            nodo = nodo.setdefault(p + "/", {})
        nodo[partes[-1]] = rel

    def pintar(nodo: dict, pre: str) -> list[str]:
        out = []
        items = sorted(nodo.items(), key=lambda kv: kv[0].lower())
        for i, (nombre, val) in enumerate(items):
            ultimo = i == len(items) - 1
            con, sub = ("└── ", "    ") if ultimo else ("├── ", "│   ")
            if isinstance(val, dict):
                out.append(f"{pre}{con}{nombre} ({len(val)} elementos)")
                out.extend(pintar(val, pre + sub))
            elif val == "README.md":  # el propio README no informa su tamaño (se está generando)
                out.append(f"{pre}{con}{nombre}")
            else:
                kb = (BASE_DIR / val).stat().st_size / 1024
                out.append(f"{pre}{con}{nombre} ({kb:.1f} KB)")
        return out

    return pintar(arbol, prefix)


def render_texto(texto: str, cifras: dict, tree_str: str) -> str:
    def _rep(m: re.Match) -> str:
        clave_completa = m.group(1).strip()
        if clave_completa == "tree":
            return tree_str
        partes = clave_completa.split(".")
        c = partes[0]
        if c not in cifras:
            raise ValueError(f"Marcador no existe en cifras_oficiales: {m.group(0)}")
        obj = cifras[c]
        if len(partes) == 1:
            if isinstance(obj, dict):
                if "str" in obj:
                    return str(obj["str"])
                if "val" in obj:
                    return str(obj["val"])
                raise ValueError(f"Clave {c} no tiene campo 'str' ni 'val'")
            return str(obj)
        campo = partes[1]
        if isinstance(obj, dict):
            if campo in obj:
                return str(obj[campo])
            raise ValueError(f"Clave {c} no tiene el campo '{campo}' (disponibles: {list(obj.keys())})")
        val_attr = getattr(obj, campo, None)
        if val_attr is not None:
            return str(val_attr)
        raise ValueError(f"Clave {c} no tiene atributo ni campo '{campo}'")

    res = RX_MARCA.sub(_rep, texto)
    if "{{" in res or "}}" in res:
        raise ValueError(f"Quedó marcador sin reemplazar en texto: {res[:120]}...")
    return res


def main() -> None:
    if not PLANTILLA_PATH.exists():
        raise FileNotFoundError(f"No existe la plantilla en {PLANTILLA_PATH}")
    if not CIFRAS_PATH.exists():
        raise FileNotFoundError(f"No existe {CIFRAS_PATH}")

    with open(CIFRAS_PATH, "r", encoding="utf-8") as f:
        cifras = json.load(f)

    with open(PLANTILLA_PATH, "r", encoding="utf-8") as f:
        plantilla_texto = f.read()

    # Iteración hasta convergencia exacta del tamaño del árbol (punto fijo)
    for _ in range(5):
        tree_lines = generate_tree()
        tree_text = "\n".join(tree_lines)
        resultado = render_texto(plantilla_texto, cifras, tree_text)
        prev_content = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else None
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(resultado)
        if prev_content == resultado:
            break

    print("[OK] README.md renderizado exitosamente desde plantilla (convergencia a punto fijo).")

if __name__ == "__main__":
    main()
