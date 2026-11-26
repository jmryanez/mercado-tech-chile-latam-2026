#!/usr/bin/env python3
"""Generador y ejecutor de cuaderno Jupyter reproducible desde plantillas JSON y celdas de código."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient

BASE_DIR = Path(__file__).resolve().parent.parent
PLANTILLA_PATH = BASE_DIR / "scripts" / "plantillas" / "cuaderno_plantillas.json"
CIFRAS_PATH = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes" / "cifras_oficiales.json"
NOTEBOOK_PATH = BASE_DIR / "06_Fase_Actuar_Act" / "kaggle_notebook_portafolio.ipynb"
DESCARGAS_PATH = BASE_DIR / "descargas" / "kaggle_notebook_portafolio.ipynb"

RX_MARCA = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)\s*\}\}")


def render_texto(texto: str, cifras: dict) -> str:
    def _rep(m):
        clave_completa = m.group(1).strip()
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


def build_notebook() -> nbformat.NotebookNode:
    nb = new_notebook()
    nb.metadata = {
        "language_info": {"name": "python", "version": "3.14.0"},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
    }
    with open(CIFRAS_PATH, "r", encoding="utf-8") as f:
        cifras = json.load(f)
    with open(PLANTILLA_PATH, "r", encoding="utf-8") as f:
        cell_templates = json.load(f)

    cells = []
    for item in cell_templates:
        cell_type = item.get("cell_type", "markdown")
        raw_src = item.get("source", "")
        src = render_texto(raw_src, cifras)
        if cell_type == "code":
            cells.append(new_code_cell(src))
        else:
            cells.append(new_markdown_cell(src))
    nb.cells = cells
    return nb


def main():
    print("Construyendo cuaderno Jupyter desde plantillas...")
    nb = build_notebook()

    print(f"Ejecutando cuaderno con NotebookClient en {BASE_DIR}...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute(cwd=BASE_DIR)

    print(f"Guardando cuaderno ejecutado en {NOTEBOOK_PATH}...")
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print(f"Copiando cuaderno ejecutado a {DESCARGAS_PATH}...")
    shutil.copyfile(NOTEBOOK_PATH, DESCARGAS_PATH)

    res = subprocess.run(["cmp", NOTEBOOK_PATH, DESCARGAS_PATH], capture_output=True, text=True)
    if res.returncode == 0:
        print("Verificación cmp exitosa: ambas copias del cuaderno son idénticas byte por byte.")
    else:
        print("ERROR: Las copias del cuaderno difieren:", res.stderr)
        exit(1)


if __name__ == "__main__":
    main()
