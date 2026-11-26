"""Celdas vacías de los datos publicados: qué significa cada una y en qué filas ocurre.

El registro está en scripts/celdas_vacias.json. El script del Excel de Tableau y el del paquete de descargas y Kaggle
llaman a comprobar() con cada tabla antes de publicarla: se detienen si una columna tiene celdas vacías sin explicación,
si una explicación sobra o si las celdas vacías no están exactamente en las filas que dice la condición registrada.
El validador externo (R37) repite la comprobación por su cuenta sobre los archivos ya escritos.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RUTA = Path(__file__).resolve().parent / "celdas_vacias.json"


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def vacias(df: pd.DataFrame) -> pd.DataFrame:
    """Celdas que quedan vacías al escribir la tabla (NaN, None o texto vacío)."""
    return df.isna() | df.astype(object).eq("")


def como_texto(df: pd.DataFrame) -> pd.DataFrame:
    """La tabla como la ve quien la abre: celdas vacías como texto vacío y el resto como texto."""
    return df.astype(object).where(~vacias(df), "").astype(str)


def mascara(df_txt: pd.DataFrame, cond: dict) -> pd.Series:
    if "todas" in cond:
        m = pd.Series(True, index=df_txt.index)
        for c in cond["todas"]:
            m &= mascara(df_txt, c)
        return m
    if "alguna" in cond:
        m = pd.Series(False, index=df_txt.index)
        for c in cond["alguna"]:
            m |= mascara(df_txt, c)
        return m
    s = df_txt[cond["columna"]]
    op, v = cond["operador"], cond["valor"]
    if op == "empieza_con":
        return s.str.startswith(v)
    if op == "no_empieza_con":
        return ~s.str.startswith(v)
    if op == "igual_a":
        return s == str(v)
    if op == "menor_que":
        return pd.to_numeric(s, errors="coerce") < float(v)
    raise ValueError(f"operador desconocido en celdas_vacias.json: {op}")


def comprobar(df: pd.DataFrame, registro_tabla: dict, nombre: str) -> None:
    txt = como_texto(df)
    vac = vacias(df)
    sin_explicar = [c for c in df.columns if vac[c].any() and c not in registro_tabla]
    if sin_explicar:
        raise ValueError(f"{nombre}: columnas con celdas vacías sin explicación en {RUTA.name}: {', '.join(map(str, sin_explicar))}")
    for col, e in registro_tabla.items():
        if col not in df.columns or not vac[col].any():
            raise ValueError(f"{nombre}: {RUTA.name} explica la columna '{col}', pero no tiene celdas vacías (explicación sobrante)")
        if not str(e.get("texto", "")).strip():
            raise ValueError(f"{nombre}: la explicación de '{col}' está vacía")
        if e.get("condicion") is not None and not (vac[col] == mascara(txt, e["condicion"])).all():
            raise ValueError(f"{nombre}: las celdas vacías de '{col}' no están exactamente en las filas que dice su condición")


def guia_markdown(registro: dict) -> str:
    """Texto de descargas/LEEME_Celdas_Vacias.md, generado desde el mismo registro."""
    lineas = [
        "# Celdas vacías en los datos publicados",
        "",
        "Las celdas vacías no son datos perdidos: cada columna con celdas vacías tiene un motivo, explicado aquí. "
        "En Tableau aparecen como NULL. Este archivo se genera desde scripts/celdas_vacias.json, el mismo registro que usan "
        "la hoja LEEME_Poblaciones del Excel de Tableau y las descripciones de columnas del dataset de Kaggle.",
        "",
        "## Archivos CSV (carpeta descargas, zip de GitHub y dataset de Kaggle)",
        "",
    ]
    for archivo, cols in registro["archivos"].items():
        lineas += [f"### {archivo}", ""] + [f"- `{c}`: {e['texto']}" for c, e in cols.items()] + [""]
    lineas += ["## Excel de Tableau Public (Datos_Consolidados_Tableau_Public.xlsx)", ""]
    for hoja, cols in registro["tableau"].items():
        lineas += [f"### Hoja {hoja}", ""] + [f"- `{c}`: {e['texto'][:1].upper()}{e['texto'][1:]}" for c, e in cols.items()] + [""]
    return "\n".join(lineas).rstrip() + "\n"
