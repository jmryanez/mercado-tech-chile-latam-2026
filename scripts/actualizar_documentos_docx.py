#!/usr/bin/env python3
"""
scripts/actualizar_documentos_docx.py
Renderiza todos los documentos .docx del portafolio a partir de sus plantillas
en scripts/plantillas/ sustituyendo los marcadores {{clave}} con las cifras oficiales.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
import docx

ROOT = Path(__file__).resolve().parent.parent
PLANTILLAS_DIR = ROOT / "scripts" / "plantillas"
CIFRAS_PATH = ROOT / "04_Fase_Analizar_Analyze" / "resumenes" / "cifras_oficiales.json"

RX_MARCA = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)\s*\}\}")


def render_texto(texto: str, cifras: dict) -> str:
    def _rep(m: re.Match) -> str:
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


def render_documento(origen: Path, destino: Path, cifras: dict) -> None:
    doc = docx.Document(str(origen))
    for p in doc.paragraphs:
        if "{{" in p.text:
            p.text = render_texto(p.text, cifras)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "{{" in p.text:
                        p.text = render_texto(p.text, cifras)
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(destino))


def main() -> None:
    if not CIFRAS_PATH.exists():
        raise FileNotFoundError(f"No existe {CIFRAS_PATH}")
    with open(CIFRAS_PATH, "r", encoding="utf-8") as f:
        cifras = json.load(f)

    archivos_docx = [
        "01_Fase_Preguntar_Ask/01_Declaracion_Tarea_Empresarial.docx",
        "01_Fase_Preguntar_Ask/01_Alcance_del_Trabajo_SOW.docx",
        "02_Fase_Preparar_Prepare/02_Descripcion_Fuentes_y_ROCCC.docx",
        "03_Fase_Procesar_Process/03_Documentacion_Limpieza_y_Changelog.docx",
        "04_Fase_Analizar_Analyze/04_Resumen_Analisis_SQL_y_Python.docx",
        "05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx",
        "06_Fase_Actuar_Act/06_Plan_de_Accion_y_Conclusiones_Finales.docx",
        "DIARIO_DE_DATOS_BITACORA.docx",
    ]

    for rel in archivos_docx:
        origen = PLANTILLAS_DIR / rel
        destino = ROOT / rel
        if not origen.exists():
            print(f"[WARN] No existe plantilla: {origen}")
            continue
        render_documento(origen, destino, cifras)
        print(f"[OK] {rel} renderizado exitosamente desde plantilla.")


if __name__ == "__main__":
    main()
