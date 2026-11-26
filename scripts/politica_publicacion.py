"""Política de publicación de Get on Board para Kaggle y Tableau Public (única fuente de la regla).

GitHub publica las filas limpias por decisión del dueño. Lo que va a Kaggle (paquete y cuaderno) y al Excel de
Tableau usa niveles de seniority agrupados para que ningún grupo de menos de 5 ofertas pueda deducirse cruzando
tablas, y los grupos con N menor a N_MIN_ESTADISTICOS muestran solo su N. El validador externo (R29) lo comprueba.
"""
from __future__ import annotations

import pandas as pd

SENIOR_LEAD = "Senior + Lead"
JUNIOR_TRAINEE = "Junior + Trainee"
SEMI_SENIOR = "Semi-Senior"
RESTO = "Junior + Trainee + Semi-Senior"
CHILE_LOCAL = "Chile Local"
N_MIN_ESTADISTICOS = 15
PREFIJOS_ESTADISTICOS = ("media", "mediana", "p25", "p75", "min", "max", "amplitud", "ic95")


def nivel_publicable(seniority: str, alcance: str) -> str:
    """Chile Local: Junior + Trainee / Semi-Senior / Senior + Lead. Ofertas remotas: Junior + Trainee + Semi-Senior / Senior + Lead."""
    if seniority in ("Senior", "Lead"):
        return SENIOR_LEAD
    if alcance == CHILE_LOCAL:
        return SEMI_SENIOR if seniority == "Semi-Senior" else JUNIOR_TRAINEE
    return RESTO


def nivel_publicable_2(seniority: str) -> str:
    """Total de Get on Board y modalidades: Junior + Trainee + Semi-Senior / Senior + Lead."""
    return SENIOR_LEAD if seniority in ("Senior", "Lead") else RESTO


def agregar_niveles(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["seniority_pub"] = [nivel_publicable(s, a) for s, a in zip(out["seniority_nivel"], out["alcance_geo"])]
    out["seniority_pub2"] = out["seniority_nivel"].map(nivel_publicable_2)
    return out


def suprimir_n_menor(df: pd.DataFrame, col_n: str = "n") -> pd.DataFrame:
    """Deja vacíos los estadísticos de sueldo de los grupos con N < N_MIN_ESTADISTICOS (solo se publica su N)."""
    out = df.copy()
    chicos = out[col_n] < N_MIN_ESTADISTICOS
    for c in out.columns:
        if str(c).lower().startswith(PREFIJOS_ESTADISTICOS):
            out[c] = out[c].where(~chicos)
    return out
