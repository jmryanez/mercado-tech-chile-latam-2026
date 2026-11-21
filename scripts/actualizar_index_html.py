#!/usr/bin/env python3
"""Actualizador de index.html a partir de su plantilla con marcadores."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
PLANTILLA = ROOT / "scripts" / "plantillas" / "index.html"
SALIDA = ROOT / "index.html"
CIFRAS = ROOT / "04_Fase_Analizar_Analyze" / "resumenes" / "cifras_oficiales.json"

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


def main():
    if not PLANTILLA.exists():
        raise FileNotFoundError(f"No existe la plantilla en {PLANTILLA}")
    if not CIFRAS.exists():
        raise FileNotFoundError(f"No existe {CIFRAS}")
    with open(CIFRAS, "r", encoding="utf-8") as f:
        cifras = json.load(f)
    with open(PLANTILLA, "r", encoding="utf-8") as f:
        plantilla_texto = f.read()

    resultado = render_texto(plantilla_texto, cifras)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(resultado)
    print(f"[OK] index.html renderizado exitosamente desde plantilla.")


if __name__ == "__main__":
    main()
