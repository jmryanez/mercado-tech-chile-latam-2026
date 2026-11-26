"""
Fase 4: Analizar (Analyze) — Ejecución Relacional SQLite + Análisis Descriptivo en Python
Certificado Profesional de Análisis de Datos de Google • Cursos 5, 7 y 8 (Caso Práctico)

Métodos aplicados:
- SQL: Ejecución de '04_consultas_analisis.sql' en SQLite en memoria
- Python: pandas y numpy para estadísticas no paramétricas, intervalos de confianza bootstrap al 95%,
  estratificación por seniority, análisis de sensibilidades y generación de la fuente única de cifras.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from politica_publicacion import CHILE_LOCAL, SEMI_SENIOR, SENIOR_LEAD, JUNIOR_TRAINEE, RESTO, agregar_niveles, suprimir_n_menor  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEAN_DIR = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed"
SQL_FILE = BASE_DIR / "04_Fase_Analizar_Analyze" / "sql" / "04_consultas_analisis.sql"
RES_DIR = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes"
RES_DIR.mkdir(parents=True, exist_ok=True)
DOLAR_OBSERVADO_BCCH = 969.80

NOTA_FIJA_ALCANCE = (
    "Nota metodológica: modalidad y alcance son la misma partición: "
    "Chile Local = Híbrido + Presencial; Remoto sin país declarado = Remoto Local + Remoto Total."
)


def q25(s: pd.Series) -> float:
    return float(s.quantile(0.25))


def q75(s: pd.Series) -> float:
    return float(s.quantile(0.75))


def resumen_salarios(
    df: pd.DataFrame,
    group_col: str | list[str],
    col_usd: str = "salario_mensual_usd",
    col_clp: str = "salario_mensual_clp_ref",
) -> pd.DataFrame:
    """Calcula estadísticos descriptivos (N, media, mediana, p25/p75, amplitud IQR, min, max)."""
    agg = (
        df.groupby(group_col, dropna=False)[col_usd]
        .agg(
            n="count",
            media_usd="mean",
            mediana_usd="median",
            p25_usd=q25,
            p75_usd=q75,
            min_usd="min",
            max_usd="max",
        )
        .reset_index()
    )
    out = agg.copy()
    for c in ["media_usd", "mediana_usd", "p25_usd", "p75_usd", "min_usd", "max_usd"]:
        out[c] = out[c].round(2)
    out["amplitud_p25_p75_usd"] = (out["p75_usd"] - out["p25_usd"]).round(2)
    out["mediana_clp_ref"] = (out["mediana_usd"] * DOLAR_OBSERVADO_BCCH).round(0).astype(int)
    out["media_clp_ref"] = (out["media_usd"] * DOLAR_OBSERVADO_BCCH).round(0).astype(int)
    out["cumple_n30"] = out["n"] >= 30
    return out


def diff_median_ci(s1: pd.Series | np.ndarray, s2: pd.Series | np.ndarray, n_boot: int = 10000, seed: int = 20261116) -> tuple[float, float, float, bool]:
    """Calcula la diferencia observada de medianas y el IC 95% bootstrap."""
    rng = np.random.default_rng(seed)
    a1 = np.asarray(pd.Series(s1).dropna())
    a2 = np.asarray(pd.Series(s2).dropna())
    if len(a1) == 0 or len(a2) == 0:
        return 0.0, 0.0, 0.0, False
    b1 = rng.choice(a1, size=(n_boot, len(a1)), replace=True)
    b2 = rng.choice(a2, size=(n_boot, len(a2)), replace=True)
    m1 = np.median(b1, axis=1)
    m2 = np.median(b2, axis=1)
    diffs = m1 - m2
    ci_low = round(float(np.percentile(diffs, 2.5)), 2)
    ci_high = round(float(np.percentile(diffs, 97.5)), 2)
    obs_diff = round(float(np.median(a1) - np.median(a2)), 2)
    concluyente = bool(not (ci_low <= 0 <= ci_high))
    return obs_diff, ci_low, ci_high, concluyente


def ejecutar_sql_oficial(
    vac: pd.DataFrame,
    hab: pd.DataFrame,
    so: pd.DataFrame,
    so_tech: pd.DataFrame,
    dss: pd.DataFrame,
    ine: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Carga tablas limpias en SQLite en memoria y ejecuta todas las consultas de 04_consultas_analisis.sql."""
    conn = sqlite3.connect(":memory:")
    vac.to_sql("vacantes", conn, index=False)
    hab.to_sql("vacante_habilidades", conn, index=False)
    so.to_sql("so_encuestados", conn, index=False)
    so_tech.to_sql("so_tecnologias", conn, index=False)
    dss.to_sql("dss_salarios", conn, index=False)
    ine.to_sql("ine_esi_2025", conn, index=False)

    sql_text = SQL_FILE.read_text(encoding="utf-8")
    pattern = re.compile(r"-- \[(SQL_SETUP|QUERY:\s*([a-zA-Z0-9_]+))\]\s*\n(.*?;)", re.DOTALL)
    resultados_sql: dict[str, pd.DataFrame] = {}

    for kind, qname, stmt in pattern.findall(sql_text):
        if kind == "SQL_SETUP":
            conn.executescript(stmt)
        else:
            df_q = pd.read_sql_query(stmt, conn)
            resultados_sql[qname] = df_q
            df_q.to_csv(RES_DIR / f"sql_{qname}.csv", index=False, encoding="utf-8")

    conn.close()
    return resultados_sql


def main() -> None:
    vac = pd.read_csv(CLEAN_DIR / "GetOnBoard_Vacantes_2026_20261111_v01_clean.csv")
    hab = pd.read_csv(CLEAN_DIR / "GetOnBoard_Habilidades_2026_20261111_v01_clean.csv")
    so = pd.read_csv(CLEAN_DIR / "StackOverflow_LatAm_2024_20261111_v01_clean.csv")
    so_tech = pd.read_csv(CLEAN_DIR / "StackOverflow_Tecnologias_2024_20261111_v01_clean.csv")
    dss = pd.read_csv(CLEAN_DIR / "DataScienceSalaries_2020_2024_20261111_v01_clean.csv")
    ine = pd.read_csv(CLEAN_DIR / "INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv")

    sql_res = ejecutar_sql_oficial(vac, hab, so, so_tech, dss, ine)
    ine_mediana_clp = float(ine.loc[ine["indicador"].str.contains("Mediano"), "monto_clp_mensual"].iloc[0])
    ine_mediana_usd = float(ine.loc[ine["indicador"].str.contains("Mediano"), "monto_usd_ref_20261110"].iloc[0])
    ine_media_clp = float(ine.loc[ine["indicador"].str.contains("Medio"), "monto_clp_mensual"].iloc[0])
    ine_media_usd = round(ine_media_clp / DOLAR_OBSERVADO_BCCH, 2)

    # =========================================================================
    # 1. PREGUNTA 1: DEMANDA VS ADOPCIÓN TECNOLÓGICA
    # =========================================================================
    df_p1 = sql_res["q02_tecnologias_cruce_demanda_vs_adopcion"].copy()
    n_chile_local = int((vac["alcance_geo"] == "Chile Local").sum())
    n_remoto = int((vac["alcance_geo"] == "Remoto sin país declarado").sum())
    df_p1["pct_gob_chile_local"] = (100.0 * df_p1["n_gob_chile_local"] / n_chile_local).round(2)
    df_p1["pct_gob_remoto"] = (100.0 * df_p1["n_gob_remoto"] / n_remoto).round(2)
    p_cl = df_p1["pct_adopcion_chile"] / 100.0
    df_p1["moe95_pp_chile"] = (1.96 * np.sqrt(p_cl * (1.0 - p_cl) / 133.0) * 100.0).round(1)
    p_lat = df_p1["pct_adopcion_latam"] / 100.0
    df_p1["moe95_pp_latam"] = (1.96 * np.sqrt(p_lat * (1.0 - p_lat) / 3074.0) * 100.0).round(1)
    df_p1.to_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 2. PREGUNTA 2: BANDAS SALARIALES POR SENIORITY (CHILE LOCAL Y REMOTO)
    # =========================================================================
    gob_sal = vac[vac["salario_valido_flag"] == True].copy()
    so_sal = so[so["salario_valido_flag"] == True].copy()

    # Bandas Chile Local exclusivas (PASO 1.3)
    gob_sal_cl = gob_sal[gob_sal["alcance_geo"] == "Chile Local"].copy()
    p2_bandas_cl = resumen_salarios(gob_sal_cl, "seniority_nivel")
    p2_bandas_cl["fuente"] = "Get on Board 2026 (Chile Local)"
    p2_bandas_cl["nota"] = NOTA_FIJA_ALCANCE
    p2_bandas_cl.to_csv(RES_DIR / "resumen_p2_bandas_chile_local.csv", index=False, encoding="utf-8")

    # Bandas Remoto sin país declarado (PASO 1.3)
    gob_sal_rem = gob_sal[gob_sal["alcance_geo"] == "Remoto sin país declarado"].copy()
    p2_bandas_rem = resumen_salarios(gob_sal_rem, "seniority_nivel")
    p2_bandas_rem["fuente"] = "Get on Board 2026 (Remoto sin país declarado)"
    p2_bandas_rem["nota"] = NOTA_FIJA_ALCANCE
    p2_bandas_rem.to_csv(RES_DIR / "resumen_p2_bandas_remoto_sin_pais.csv", index=False, encoding="utf-8")

    # Resumen general de experiencia (incluyendo SO y DSS EE.UU.)
    p2_gob_tot = resumen_salarios(gob_sal, "seniority_nivel")
    p2_gob_tot["fuente"] = "Get on Board 2026 (Chile + remotas)"
    p2_so = resumen_salarios(so_sal[so_sal["tramo_experiencia"] != "Sin dato"], "tramo_experiencia")
    p2_so["fuente"] = "Stack Overflow LatAm 2024"

    dss_us = dss[dss["employee_residence"] == "United States"].copy()
    p2_dss_us = resumen_salarios(dss_us, "experiencia_es")
    p2_dss_us["fuente"] = "Data Science Salaries (residentes en EE.UU.)"

    df_p2_general = pd.concat([p2_gob_tot, p2_so, p2_dss_us], ignore_index=True)
    df_p2_general.to_csv(RES_DIR / "resumen_p2_salarios_experiencia.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 3. PREGUNTA 3: MODALIDADES Y COMPARACIÓN INE (SOLO CHILE LOCAL)
    # =========================================================================
    p3_gob_mod = resumen_salarios(gob_sal, "modalidad_grupo")
    p3_gob_mod["fuente"] = "Get on Board 2026 (Modalidad)"
    p3_gob_mod["nota"] = NOTA_FIJA_ALCANCE

    p3_gob_geo = resumen_salarios(gob_sal, "alcance_geo")
    p3_gob_geo["fuente"] = "Get on Board 2026 (Alcance)"
    p3_gob_geo["nota"] = NOTA_FIJA_ALCANCE

    # Comparación INE exclusivamente con medianas Chile Local de Get on Board (PASO 1.4)
    med_cl_senior_gob = float(p2_bandas_cl.loc[p2_bandas_cl["seniority_nivel"] == "Senior", "mediana_usd"].iloc[0])
    med_cl_semi_gob = float(p2_bandas_cl.loc[p2_bandas_cl["seniority_nivel"] == "Semi-Senior", "mediana_usd"].iloc[0])
    med_cl_tot_gob = float(gob_sal_cl["salario_mensual_usd"].median())

    df_ine_comp = pd.DataFrame([
        {
            "segmento_gob_chile_local": f"Total Chile Local (N={len(gob_sal_cl)})",
            "mediana_usd_gob": med_cl_tot_gob,
            "mediana_clp_ref_gob": int(round(med_cl_tot_gob * DOLAR_OBSERVADO_BCCH)),
            "mediana_clp_ine_esi_2025": int(ine_mediana_clp),
            "ratio_vs_ine": round((med_cl_tot_gob * DOLAR_OBSERVADO_BCCH) / ine_mediana_clp, 2),
            "etiqueta_metodologica": "referencial: oferta publicada (bruto/líquido no informado) vs ingreso líquido mediano de todos los ocupados de Chile",
        },
        {
            "segmento_gob_chile_local": f"Semi-Senior Chile Local (N={int(p2_bandas_cl.loc[p2_bandas_cl['seniority_nivel'] == 'Semi-Senior', 'n'].iloc[0])})",
            "mediana_usd_gob": med_cl_semi_gob,
            "mediana_clp_ref_gob": int(round(med_cl_semi_gob * DOLAR_OBSERVADO_BCCH)),
            "mediana_clp_ine_esi_2025": int(ine_mediana_clp),
            "ratio_vs_ine": round((med_cl_semi_gob * DOLAR_OBSERVADO_BCCH) / ine_mediana_clp, 2),
            "etiqueta_metodologica": "referencial: oferta publicada (bruto/líquido no informado) vs ingreso líquido mediano de todos los ocupados de Chile",
        },
        {
            "segmento_gob_chile_local": f"Senior Chile Local (N={int(p2_bandas_cl.loc[p2_bandas_cl['seniority_nivel'] == 'Senior', 'n'].iloc[0])})",
            "mediana_usd_gob": med_cl_senior_gob,
            "mediana_clp_ref_gob": int(round(med_cl_senior_gob * DOLAR_OBSERVADO_BCCH)),
            "mediana_clp_ine_esi_2025": int(ine_mediana_clp),
            "ratio_vs_ine": round((med_cl_senior_gob * DOLAR_OBSERVADO_BCCH) / ine_mediana_clp, 2),
            "etiqueta_metodologica": "referencial: oferta publicada (bruto/líquido no informado) vs ingreso líquido mediano de todos los ocupados de Chile",
        },
    ])
    df_ine_comp.to_csv(RES_DIR / "resumen_p3_comparacion_ine_chile_local.csv", index=False, encoding="utf-8")

    # Resumen explícito P3 Modalidad vs INE (huérfano requerido)
    p3_gob_mod_df = p3_gob_mod.copy()
    p3_gob_mod_df.rename(columns={"modalidad_grupo": "segmento"}, inplace=True)
    p3_gob_geo_df = p3_gob_geo.copy()
    p3_gob_geo_df.rename(columns={"alcance_geo": "segmento"}, inplace=True)
    p3_so_mod = resumen_salarios(so_sal, "modalidad_grupo")
    p3_so_mod["fuente"] = "Stack Overflow LatAm 2024 (Modalidad)"
    p3_so_mod.rename(columns={"modalidad_grupo": "segmento"}, inplace=True)

    df_p3_modalidad_vs_ine = pd.concat([p3_gob_mod_df, p3_gob_geo_df, p3_so_mod], ignore_index=True)
    df_p3_modalidad_vs_ine["ratio_mediana_vs_ine_esi_2025"] = (df_p3_modalidad_vs_ine["mediana_usd"] / ine_mediana_usd).round(2)
    df_p3_modalidad_vs_ine["brecha_pct_vs_ine_esi_2025"] = ((df_p3_modalidad_vs_ine["ratio_mediana_vs_ine_esi_2025"] - 1.0) * 100.0).round(1)
    df_p3_modalidad_vs_ine.to_csv(RES_DIR / "resumen_p3_salarios_modalidad_vs_ine.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 4. PREGUNTA 4: TAMAÑO DE EMPRESA Y DSS EE.UU. (PASO 1.5)
    # =========================================================================
    so_sal_org = so_sal[so_sal["org_size_grupo"] != "Sin dato / NS-NR"].copy()
    p4_so_org = resumen_salarios(so_sal_org, "org_size_grupo")
    p4_so_org["fuente"] = "Stack Overflow LatAm 2024"

    # DSS SOLO residentes en EE.UU.
    p4_dss_us_size = resumen_salarios(dss_us, "tamano_es")
    p4_dss_us_size["fuente"] = "Data Science Salaries, residentes en EE.UU. (Tamaño)"

    # Serie anual DSS EE.UU. con proporción Senior y 2024 rotulado (parcial)
    dss_us_years = []
    for yr, grp in dss_us.groupby("work_year"):
        n_yr = len(grp)
        med_yr = round(float(grp["salario_mensual_usd"].median()), 2)
        p25_yr = round(float(grp["salario_mensual_usd"].quantile(0.25)), 2)
        p75_yr = round(float(grp["salario_mensual_usd"].quantile(0.75)), 2)
        pct_sen = round(float((grp["experiencia_es"] == "Senior").mean() * 100.0), 1)
        rotulo_anio = f"{yr} (parcial)" if yr == 2024 else str(yr)
        dss_us_years.append({
            "work_year": yr,
            "anio_rotulo": rotulo_anio,
            "n": n_yr,
            "cumple_n30": n_yr >= 30,
            "mediana_usd": med_yr,
            "p25_usd": p25_yr,
            "p75_usd": p75_yr,
            "pct_senior": pct_sen,
            "fuente": "Data Science Salaries, residentes en EE.UU.",
        })
    df_dss_us_years = pd.DataFrame(dss_us_years)
    df_dss_us_years.to_csv(RES_DIR / "resumen_p4_dss_eeuu_temporal.csv", index=False, encoding="utf-8")

    # Matriz DSS EE.UU. Año x Tamaño (formato largo para Tableau y análisis)
    dss_us_anio_tam = (
        dss_us.groupby(["work_year", "tamano_es"])["salario_mensual_usd"]
        .agg(n="count", mediana_usd="median")
        .reset_index()
    )
    dss_us_anio_tam["mediana_usd"] = dss_us_anio_tam["mediana_usd"].round(2)
    dss_us_anio_tam["cumple_n30"] = dss_us_anio_tam["n"] >= 30
    dss_us_anio_tam.to_csv(RES_DIR / "resumen_p4_dss_eeuu_anio_tamano.csv", index=False, encoding="utf-8")

    # Resumen explícito P4 Tamaño de empresa SO LatAm (huérfano requerido)
    p4_so_org_grupo = p4_so_org.copy()
    p4_so_org_grupo.rename(columns={"org_size_grupo": "segmento"}, inplace=True)
    p4_so_org_grupo["fuente"] = "Stack Overflow LatAm 2024 (Grupo)"

    so_sal_detail = so_sal[so_sal["org_size_detalle"].notna() & (~so_sal["org_size_detalle"].isin(["Sin dato", "I don’t know", "I don't know"]))].copy()
    p4_so_org_det = resumen_salarios(so_sal_detail, "org_size_detalle")
    p4_so_org_det.rename(columns={"org_size_detalle": "segmento"}, inplace=True)
    p4_so_org_det["fuente"] = "Stack Overflow LatAm 2024 (Detalle)"

    # DSS Población Total (6.599 registros): Tamaño de Empresa y Evolución Temporal
    p4_dss_size = resumen_salarios(dss, "tamano_es")
    p4_dss_size.rename(columns={"tamano_es": "segmento"}, inplace=True)
    p4_dss_size["fuente"] = "Data Science Salaries 2020-2024 (Tamaño)"

    p4_dss_year = resumen_salarios(dss, "work_year")
    p4_dss_year.rename(columns={"work_year": "segmento"}, inplace=True)
    p4_dss_year["segmento"] = p4_dss_year["segmento"].astype(str)
    p4_dss_year["fuente"] = "Data Science Salaries 2020-2024 (Año)"

    df_p4_tamano_temporal = pd.concat([p4_so_org_grupo, p4_so_org_det, p4_dss_size, p4_dss_year], ignore_index=True)
    df_p4_tamano_temporal.to_csv(RES_DIR / "resumen_p4_tamano_empresa_y_dss_temporal.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 5. MATRIZ TLC 19 PAÍSES LATAM CON BOOTSTRAP 95% CI
    # =========================================================================
    def bootstrap_ci(vals, n_boot=10000, seed=20261116):
        if len(vals) < 30:
            return ("", "")
        rng = np.random.default_rng(seed)
        boots = np.empty(n_boot)
        n = len(vals)
        for i in range(n_boot):
            boots[i] = np.median(rng.choice(vals, size=n, replace=True))
        inf = float(np.percentile(boots, 2.5))
        sup = float(np.percentile(boots, 97.5))
        return (round(inf, 2), round(sup, 2))

    ISO3_MAP = {
        "Argentina": "ARG", "Bolivia": "BOL", "Brasil": "BRA", "Chile": "CHL",
        "Colombia": "COL", "Costa Rica": "CRI", "Cuba": "CUB", "Ecuador": "ECU",
        "El Salvador": "SLV", "Guatemala": "GTM", "Honduras": "HND", "México": "MEX",
        "Nicaragua": "NIC", "Panamá": "PAN", "Paraguay": "PRY", "Perú": "PER",
        "República Dominicana": "DOM", "Uruguay": "URY", "Venezuela": "VEN",
    }

    tlc_rows = []
    for p in so["pais"].value_counts().index:
        tot = int((so["pais"] == p).sum())
        sub_sal = so_sal[so_sal["pais"] == p]["salario_mensual_usd"].dropna().values
        n_sal = len(sub_sal)
        cumple = n_sal >= 30
        med = round(float(np.median(sub_sal)), 2) if n_sal > 0 else 0.0
        p25 = round(float(np.percentile(sub_sal, 25)), 2) if n_sal > 0 else 0.0
        p75 = round(float(np.percentile(sub_sal, 75)), 2) if n_sal > 0 else 0.0
        iqr = round(p75 - p25, 2)
        clp = int(round(med * DOLAR_OBSERVADO_BCCH))
        inf, sup = bootstrap_ci(sub_sal)
        trat = "Inferencia No Paramétrica Válida (N ≥ 30)" if cumple else "Muestra Exploratoria (N < 30)"
        tlc_rows.append({
            "pais": p,
            "iso3": ISO3_MAP.get(p, ""),
            "n_total": tot,
            "n_sal": n_sal,
            "cumple_n30": cumple,
            "med_usd": med,
            "p25_usd": p25,
            "p75_usd": p75,
            "iqr_usd": iqr,
            "med_clp": clp,
            "ic95_mediana_inf_usd": inf,
            "ic95_mediana_sup_usd": sup,
            "tratamiento": trat,
        })
    df_tlc = pd.DataFrame(tlc_rows)
    df_tlc.to_csv(CLEAN_DIR / "Matriz_TLC_19_Paises_LatAm.csv", index=False, encoding="utf-8")
    df_tlc.to_csv(BASE_DIR / "descargas" / "Matriz_TLC_19_Paises_LatAm.csv", index=False, encoding="utf-8")

    # Resumen explícito Países SO LatAm N >= 30 (huérfano requerido)
    so_paises_list = []
    for pais, grp in so_sal.groupby("pais"):
        if len(grp) >= 30:
            so_paises_list.append(resumen_salarios(grp, "pais"))
    if so_paises_list:
        df_paises_n30 = pd.concat(so_paises_list, ignore_index=True)
        df_paises_n30.sort_values(by="mediana_usd", ascending=False, inplace=True)
        df_paises_n30.to_csv(RES_DIR / "resumen_paises_so_latam_n30.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 6. ANÁLISIS DE SENSIBILIDADES (PASO 1.6)
    # =========================================================================
    # (a) Demanda tecnológica con y sin la empresa 9458
    n_tot_vac = len(vac)
    n_sin_9458 = len(vac[vac["company_id"] != 9458])
    hab_vac = hab.merge(vac[["job_id", "company_id"]], on="job_id")

    sens_rows = []
    for tipo in ["Lenguaje", "Cloud", "Base de datos"]:
        for t in df_p1[df_p1["tipo_tecnologia"] == tipo]["tecnologia"].unique():
            n_tot_t = int(hab[hab["tecnologia"] == t]["job_id"].nunique())
            pct_tot_t = round(100.0 * n_tot_t / n_tot_vac, 2)

            n_sin_t = int(hab_vac[(hab_vac["tecnologia"] == t) & (hab_vac["company_id"] != 9458)]["job_id"].nunique())
            pct_sin_t = round(100.0 * n_sin_t / n_sin_9458, 2)

            # (b) Adopción SO con denominador "respondió el bloque"
            col_block = "respondio_lenguaje" if tipo == "Lenguaje" else ("respondio_platform" if tipo == "Cloud" else "respondio_database")
            n_block_latam = int(so[col_block].sum())
            n_block_chile = int(so[so["es_chile"]][col_block].sum())

            n_so_latam = int(df_p1.loc[df_p1["tecnologia"] == t, "so_n_latam"].iloc[0]) if (df_p1["tecnologia"] == t).any() else 0
            n_so_chile = int(df_p1.loc[df_p1["tecnologia"] == t, "so_n_chile"].iloc[0]) if (df_p1["tecnologia"] == t).any() else 0

            pct_block_latam = round(100.0 * n_so_latam / n_block_latam, 2) if n_block_latam > 0 else 0.0
            pct_block_chile = round(100.0 * n_so_chile / n_block_chile, 2) if n_block_chile > 0 else 0.0

            sens_rows.append({
                "tipo_tecnologia": tipo,
                "tecnologia": t,
                "gob_n_ofertas": n_tot_t,
                "pct_demanda_gob_total": pct_tot_t,
                "gob_n_sin_empresa_top": n_sin_t,
                "pct_demanda_sin_empresa_top": pct_sin_t,
                "so_pct_adopcion_latam_muestra_total": round(100.0 * n_so_latam / len(so), 2),
                "so_pct_adopcion_latam_responde_bloque": pct_block_latam,
                "so_pct_adopcion_chile_muestra_total": round(100.0 * n_so_chile / 133, 2),
                "so_pct_adopcion_chile_responde_bloque": pct_block_chile,
            })
    df_sens = pd.DataFrame(sens_rows)
    df_sens.to_csv(RES_DIR / "resumen_sensibilidades.csv", index=False, encoding="utf-8")

    # (c) Medianas por país en SO solo con Employment = "Employed, full-time"
    so_ft = so_sal[so_sal["empleo_raw"] == "Employed, full-time"]
    med_ft_by_country = so_ft.groupby("pais")["salario_mensual_usd"].agg(n_ft="count", mediana_ft="median").reset_index()
    med_ft_by_country["mediana_ft"] = med_ft_by_country["mediana_ft"].round(2)
    med_ft_by_country.to_csv(RES_DIR / "resumen_sensibilidad_so_full_time.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 7. IC DE DIFERENCIAS (PASO 1.7)
    # =========================================================================
    # Diferencias de medianas bootstrap 10.000 resamples (semilla 20261116)
    diff_rows = []

    # 1. Chile - Argentina
    chile_sal = so_sal[so_sal["pais"] == "Chile"]["salario_mensual_usd"]
    arg_sal = so_sal[so_sal["pais"] == "Argentina"]["salario_mensual_usd"]
    d, lo, hi, conc = diff_median_ci(chile_sal, arg_sal)
    diff_rows.append({"comparacion": "Chile − Argentina (SO LatAm)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    # 2. Chile - México
    mex_sal = so_sal[so_sal["pais"] == "México"]["salario_mensual_usd"]
    d, lo, hi, conc = diff_median_ci(chile_sal, mex_sal)
    diff_rows.append({"comparacion": "Chile − México (SO LatAm)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    # 3. Chile - Colombia
    col_sal = so_sal[so_sal["pais"] == "Colombia"]["salario_mensual_usd"]
    d, lo, hi, conc = diff_median_ci(chile_sal, col_sal)
    diff_rows.append({"comparacion": "Chile − Colombia (SO LatAm)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    # 4. Senior Remoto - Senior Chile Local
    sr_rem = gob_sal[(gob_sal["seniority_nivel"] == "Senior") & (gob_sal["alcance_geo"] == "Remoto sin país declarado")]["salario_mensual_usd"]
    sr_loc = gob_sal[(gob_sal["seniority_nivel"] == "Senior") & (gob_sal["alcance_geo"] == "Chile Local")]["salario_mensual_usd"]
    d, lo, hi, conc = diff_median_ci(sr_rem, sr_loc)
    diff_rows.append({"comparacion": "Senior Remoto sin país − Senior Chile Local (GOB)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    # 5. Semi-Senior Remoto - Semi-Senior Chile Local
    ssr_rem = gob_sal[(gob_sal["seniority_nivel"] == "Semi-Senior") & (gob_sal["alcance_geo"] == "Remoto sin país declarado")]["salario_mensual_usd"]
    ssr_loc = gob_sal[(gob_sal["seniority_nivel"] == "Semi-Senior") & (gob_sal["alcance_geo"] == "Chile Local")]["salario_mensual_usd"]
    d, lo, hi, conc = diff_median_ci(ssr_rem, ssr_loc)
    diff_rows.append({"comparacion": "Semi-Senior Remoto sin país − Semi-Senior Chile Local (GOB)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    # 6. Cada tecnología Cloud - SQL dentro de Senior
    m_hab_sal = hab.merge(gob_sal, on="job_id")
    sr_hab_sal = m_hab_sal[m_hab_sal["seniority_nivel"] == "Senior"]
    sql_sr = sr_hab_sal[sr_hab_sal["tecnologia"] == "SQL"]["salario_mensual_usd"]
    aws_sr = sr_hab_sal[sr_hab_sal["tecnologia"] == "AWS"]["salario_mensual_usd"]
    azu_sr = sr_hab_sal[sr_hab_sal["tecnologia"] == "Microsoft Azure"]["salario_mensual_usd"]
    gcp_sr = sr_hab_sal[sr_hab_sal["tecnologia"] == "Google Cloud"]["salario_mensual_usd"]

    for cname, cseries in [("AWS − SQL (Senior GOB)", aws_sr), ("Microsoft Azure − SQL (Senior GOB)", azu_sr), ("Google Cloud − SQL (Senior GOB)", gcp_sr)]:
        d, lo, hi, conc = diff_median_ci(cseries, sql_sr)
        diff_rows.append({"comparacion": cname, "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})

    df_diff = pd.DataFrame(diff_rows)
    df_diff.to_csv(RES_DIR / "resumen_ic_diferencias.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 7B. CAPA DE PUBLICACIÓN (Kaggle y Tableau): niveles agrupados y N < 15 sin estadísticos
    # =========================================================================
    gob_pub = agregar_niveles(gob_sal)
    pub_cl = suprimir_n_menor(resumen_salarios(gob_pub[gob_pub["alcance_geo"] == CHILE_LOCAL], "seniority_pub")).rename(columns={"seniority_pub": "seniority_nivel"})
    pub_cl["fuente"] = "Get on Board 2026 (Chile Local)"
    pub_cl["nota"] = NOTA_FIJA_ALCANCE
    pub_cl.to_csv(RES_DIR / "resumen_pub_bandas_chile_local.csv", index=False, encoding="utf-8")
    pub_rem = suprimir_n_menor(resumen_salarios(gob_pub[gob_pub["alcance_geo"] != CHILE_LOCAL], "seniority_pub")).rename(columns={"seniority_pub": "seniority_nivel"})
    pub_rem["fuente"] = "Get on Board 2026 (Remoto sin país declarado)"
    pub_rem["nota"] = NOTA_FIJA_ALCANCE
    pub_rem.to_csv(RES_DIR / "resumen_pub_bandas_remoto_sin_pais.csv", index=False, encoding="utf-8")
    pub_tot = suprimir_n_menor(resumen_salarios(gob_pub, "seniority_pub2")).rename(columns={"seniority_pub2": "seniority_nivel"})
    pub_tot["fuente"] = "Get on Board 2026 (Chile + remotas)"
    pub_tot.to_csv(RES_DIR / "resumen_pub_p2_gob_total.csv", index=False, encoding="utf-8")

    pub_ine = df_ine_comp.copy()
    _sl_cl = pub_cl.set_index("seniority_nivel").loc[SENIOR_LEAD]
    pub_ine.iloc[2, pub_ine.columns.get_loc("segmento_gob_chile_local")] = f"{SENIOR_LEAD} Chile Local (N={int(_sl_cl['n'])})"
    pub_ine.iloc[2, pub_ine.columns.get_loc("mediana_usd_gob")] = float(_sl_cl["mediana_usd"])
    pub_ine.iloc[2, pub_ine.columns.get_loc("mediana_clp_ref_gob")] = int(round(float(_sl_cl["mediana_usd"]) * DOLAR_OBSERVADO_BCCH))
    pub_ine.iloc[2, pub_ine.columns.get_loc("ratio_vs_ine")] = round((float(_sl_cl["mediana_usd"]) * DOLAR_OBSERVADO_BCCH) / ine_mediana_clp, 2)
    pub_ine.to_csv(RES_DIR / "resumen_pub_p3_comparacion_ine_chile_local.csv", index=False, encoding="utf-8")

    pub_rows = [r for r in diff_rows if r["comparacion"].endswith("(SO LatAm)")]
    _sl = gob_pub["seniority_pub2"] == SENIOR_LEAD
    d, lo, hi, conc = diff_median_ci(gob_pub[_sl & (gob_pub["alcance_geo"] != CHILE_LOCAL)]["salario_mensual_usd"],
                                     gob_pub[_sl & (gob_pub["alcance_geo"] == CHILE_LOCAL)]["salario_mensual_usd"])
    pub_rows.append({"comparacion": f"{SENIOR_LEAD} Remoto sin país − {SENIOR_LEAD} Chile Local (GOB)", "diferencia_observada_usd": d, "ic95_inf_usd": lo, "ic95_sup_usd": hi, "concluyente": conc})
    _hab_sl = hab.merge(gob_pub[_sl], on="job_id")
    _sql_sl = _hab_sl[_hab_sl["tecnologia"] == "SQL"]["salario_mensual_usd"]
    for _tec, _nom in [("AWS", "AWS"), ("Microsoft Azure", "Microsoft Azure"), ("Google Cloud", "Google Cloud")]:
        d2, lo2, hi2, conc2 = diff_median_ci(_hab_sl[_hab_sl["tecnologia"] == _tec]["salario_mensual_usd"], _sql_sl)
        pub_rows.append({"comparacion": f"{_nom} − SQL ({SENIOR_LEAD} GOB)", "diferencia_observada_usd": d2, "ic95_inf_usd": lo2, "ic95_sup_usd": hi2, "concluyente": conc2})
    pd.DataFrame(pub_rows).to_csv(RES_DIR / "resumen_pub_ic_diferencias.csv", index=False, encoding="utf-8")
    pub_ic_sl = (d, lo, hi, conc)

    # =========================================================================
    # 8. Q14 Y Q15 ESTRATIFICACIONES
    # =========================================================================
    g1 = gob_sal.groupby(["seniority_nivel", "alcance_geo"])["salario_mensual_usd"].agg(
        n="count", mediana_usd="median", p25_usd=q25, p75_usd=q75
    ).reset_index()
    g1["dimension"] = "alcance_geo"
    g1.rename(columns={"alcance_geo": "estrato"}, inplace=True)

    g2 = gob_sal.groupby(["seniority_nivel", "modalidad_grupo"])["salario_mensual_usd"].agg(
        n="count", mediana_usd="median", p25_usd=q25, p75_usd=q75
    ).reset_index()
    g2["dimension"] = "modalidad_grupo"
    g2.rename(columns={"modalidad_grupo": "estrato"}, inplace=True)

    df_q14 = pd.concat([g1, g2], ignore_index=True)
    df_q14["cumple_n30"] = df_q14["n"] >= 30
    df_q14["rotulo_metodologico"] = df_q14["cumple_n30"].apply(lambda x: "Inferencia válida (N >= 30)" if x else "Exploratorio (N < 30)")
    for c in ["mediana_usd", "p25_usd", "p75_usd"]:
        df_q14[c] = df_q14[c].round(2)
    df_q14["nota"] = NOTA_FIJA_ALCANCE
    df_q14.to_csv(RES_DIR / "resumen_q14_modalidad_x_seniority.csv", index=False, encoding="utf-8")

    # Q15
    m_gob_tech = hab.merge(gob_sal, on="job_id")
    tech_counts = m_gob_tech.groupby("tecnologia")["job_id"].nunique()
    tech_n30_list = tech_counts[tech_counts >= 30].index.tolist()
    q15_rows = []
    for t in tech_n30_list:
        sub = m_gob_tech[m_gob_tech["tecnologia"] == t]
        n_tot = len(sub)
        sen_lead = (sub["seniority_nivel"].isin(["Senior", "Lead"])).sum()
        pct_sen_lead = round(sen_lead / n_tot * 100, 1)

        sub_sen = sub[sub["seniority_nivel"] == "Senior"]
        n_sen = len(sub_sen)
        med_sen = round(float(sub_sen["salario_mensual_usd"].median()), 2) if n_sen > 0 else None

        sub_semi = sub[sub["seniority_nivel"] == "Semi-Senior"]
        n_semi = len(sub_semi)
        med_semi = round(float(sub_semi["salario_mensual_usd"].median()), 2) if n_semi > 0 else None

        q15_rows.append({
            "tecnologia": t,
            "n_total_salarios": n_tot,
            "mediana_total_usd": round(float(sub["salario_mensual_usd"].median()), 2),
            "pct_senior_lead": pct_sen_lead,
            "n_senior": n_sen,
            "mediana_senior_usd": med_sen,
            "n_semi_senior": n_semi,
            "mediana_semi_senior_usd": med_semi,
        })
    df_q15 = pd.DataFrame(q15_rows).sort_values(by="pct_senior_lead", ascending=False)
    df_q15.to_csv(RES_DIR / "resumen_q15_tecnologia_x_seniority.csv", index=False, encoding="utf-8")

    # Q11 y Q12
    gob_tech_m = pd.merge(gob_sal, hab, on="job_id", how="inner")
    q11_gob_py = resumen_salarios(gob_tech_m, ["tipo_tecnologia", "tecnologia"])
    q11_gob_py = q11_gob_py[q11_gob_py["n"] >= 30].copy()
    q11_gob_py = pd.merge(
        q11_gob_py,
        df_p1[["tipo_tecnologia", "tecnologia", "gob_n_ofertas", "pct_demanda_gob_total"]],
        on=["tipo_tecnologia", "tecnologia"],
        how="left",
    ).sort_values(["tipo_tecnologia", "mediana_usd"], ascending=[True, False])
    q11_gob_py["fuente"] = "Get on Board 2026"

    so_tech_m = pd.merge(so_sal, so_tech[["ResponseId", "tipo_tecnologia", "tecnologia"]], on="ResponseId", how="inner")
    gob_techs_n30 = set(zip(q11_gob_py["tipo_tecnologia"], q11_gob_py["tecnologia"])) | {
        ("Base de datos", "MongoDB"),
        ("Base de datos", "Microsoft SQL Server"),
        ("Base de datos", "MySQL"),
    }
    so_tech_sub = so_tech_m[so_tech_m.apply(lambda r: (r["tipo_tecnologia"], r["tecnologia"]) in gob_techs_n30, axis=1)]
    q11_so_py = resumen_salarios(so_tech_sub, ["tipo_tecnologia", "tecnologia"])
    q11_so_py = q11_so_py[q11_so_py["n"] >= 30].copy()
    q11_so_py = pd.merge(
        q11_so_py,
        df_p1[["tipo_tecnologia", "tecnologia", "so_n_latam", "pct_adopcion_latam"]],
        on=["tipo_tecnologia", "tecnologia"],
        how="left",
    ).sort_values(["tipo_tecnologia", "mediana_usd"], ascending=[True, False])
    q11_so_py["fuente"] = "Stack Overflow LatAm 2024"

    pd.concat([q11_gob_py, q11_so_py], ignore_index=True).to_csv(
        RES_DIR / "resumen_q11_tecnologia_vs_salario.csv", index=False, encoding="utf-8"
    )

    q12_sql = sql_res["q12_gob_modalidad_composicion_seniority"].copy()
    q12_sql.to_csv(RES_DIR / "resumen_q12_modalidad_composicion_seniority.csv", index=False, encoding="utf-8")

    q13_py = resumen_salarios(gob_sal, "categoria").sort_values("n", ascending=False)
    tot_cat = vac.groupby("categoria")["job_id"].nunique().reset_index(name="total_ofertas_publicadas")
    q13_py = pd.merge(tot_cat, q13_py, on="categoria", how="left")
    q13_py["estado_regla_n30"] = np.where(
        q13_py["n"] >= 30,
        "Válido N >= 30 (Inferencia)",
        np.where(q13_py["n"] >= 15, "Exploratorio N < 30 (Limitación muestral)", "Excluido de inferencia (N < 15)"),
    )
    q13_py.to_csv(RES_DIR / "resumen_q13_gob_categorias.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 9. FUENTE ÚNICA DE CIFRAS (cifras_oficiales.json - PASO 2.1)
    # =========================================================================
    def _fi(n: int | float) -> str:
        return f"{int(round(n)):,}".replace(",", ".")

    def _fp(p: float, dec: int = 1) -> str:
        return f"{p:.{dec}f}%".replace(".", ",")

    def _fm(v: float, dec: int = 0) -> str:
        if dec == 0:
            return f"${int(round(v)):,}".replace(",", ".")
        return f"${v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    cifras: dict[str, dict[str, object]] = {}

    # Metadata
    cifras["meta_fecha_estudio"] = {"val": "2026-11-22", "str": "2026-11-22"}
    cifras["meta_version"] = {"val": "1.13.8", "str": "1.13.8"}
    cifras["dolar_observado_bcch"] = {
        "val": DOLAR_OBSERVADO_BCCH,
        "str": _fm(DOLAR_OBSERVADO_BCCH, 2),
        "tipo": "constante_externa",
        "fuente": "Banco Central de Chile (BCCh) 2026-11-10"
    }

    # Cargar metadata de fase 3 si existe para denominadores raw
    f3_meta_file = BASE_DIR / "03_Fase_Procesar_Process" / "scripts" / "resumen_validacion_fase3.json"
    m_f3 = json.loads(f3_meta_file.read_text(encoding="utf-8"))

    # Denominadores Get on Board
    n_gob_raw = int(m_f3["st_gob"]["raw_total"])
    n_gob_scope = int(len(vac))
    n_gob_sal_raw = int(m_f3["st_gob"]["raw_con_salario_scope"])
    n_gob_sal_val = int(len(gob_sal))
    n_gob_sal_anul = int(m_f3.get("st_gob", {}).get("salarios_anulados", 2))
    n_cl_tot = int((vac["alcance_geo"] == "Chile Local").sum())
    n_rem_tot = int((vac["alcance_geo"] == "Remoto sin país declarado").sum())
    pct_cl_tot = round(100.0 * n_cl_tot / n_gob_scope, 2)
    pct_rem_tot = round(100.0 * n_rem_tot / n_gob_scope, 2)
    n_hab_rows = int(len(hab))
    n_gob_con_tech = int(vac["menciona_tecnologia_flag"].sum())

    cifras["gob_total_raw"] = {"val": n_gob_raw, "str": _fi(n_gob_raw)}
    cifras["gob_total_scope"] = {"val": n_gob_scope, "str": _fi(n_gob_scope)}
    cifras["gob_salarios_raw"] = {"val": n_gob_sal_raw, "str": _fi(n_gob_sal_raw)}
    cifras["gob_salarios_validos"] = {"val": n_gob_sal_val, "str": _fi(n_gob_sal_val), "n_str": f"N={_fi(n_gob_sal_val)}"}
    cifras["gob_chile_local_total"] = {"val": n_cl_tot, "str": _fi(n_cl_tot), "pct": pct_cl_tot, "pct_str": _fp(pct_cl_tot, 1)}
    cifras["gob_remoto_sin_pais_total"] = {"val": n_rem_tot, "str": _fi(n_rem_tot), "pct": pct_rem_tot, "pct_str": _fp(pct_rem_tot, 1)}
    cifras["gob_habilidades_rows"] = {"val": n_hab_rows, "str": _fi(n_hab_rows)}
    cifras["gob_con_tecnologia"] = {"val": n_gob_con_tech, "str": _fi(n_gob_con_tech)}

    # Denominadores Stack Overflow
    n_so_glob = int(m_f3["st_so"]["global_total"])
    n_so_latam = int(len(so))
    n_so_chile = int((so["pais"] == "Chile").sum())
    n_so_sal_val = int(len(so_sal))
    n_so_cl_sal_val = int((so_sal["pais"] == "Chile").sum())
    n_so_tech_rows = int(len(so_tech))

    cifras["so_global_total"] = {"val": n_so_glob, "str": _fi(n_so_glob)}
    cifras["so_latam_total"] = {"val": n_so_latam, "str": _fi(n_so_latam)}
    cifras["so_chile_total"] = {"val": n_so_chile, "str": _fi(n_so_chile), "n_str": f"N={_fi(n_so_chile)}"}
    cifras["so_latam_salarios_validos"] = {"val": n_so_sal_val, "str": _fi(n_so_sal_val), "n_str": f"N={_fi(n_so_sal_val)}"}
    cifras["so_chile_salarios_validos"] = {"val": n_so_cl_sal_val, "str": _fi(n_so_cl_sal_val), "n_str": f"N={_fi(n_so_cl_sal_val)}"}
    cifras["so_tecnologias_rows"] = {"val": n_so_tech_rows, "str": _fi(n_so_tech_rows)}

    # Denominadores DSS
    n_dss_tot = int(len(dss))
    n_dss_eeuu = int(len(dss_us))
    cifras["dss_total"] = {"val": n_dss_tot, "str": _fi(n_dss_tot)}
    cifras["dss_eeuu_total"] = {"val": n_dss_eeuu, "str": _fi(n_dss_eeuu)}

    # INE ESI 2025
    cifras["ine_mediana_clp"] = {
        "val": ine_mediana_clp,
        "str": _fm(ine_mediana_clp, 0),
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv"
    }
    cifras["ine_mediana_usd"] = {
        "val": ine_mediana_usd,
        "str": _fm(ine_mediana_usd, 2),
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv / BCCh"
    }
    cifras["ine_media_clp"] = {
        "val": ine_media_clp,
        "str": _fm(ine_media_clp, 0),
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv"
    }
    cifras["ine_media_usd"] = {
        "val": ine_media_usd,
        "str": _fm(ine_media_usd, 2),
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv / BCCh"
    }
    cifras["ine_mediana_usd_ref"] = {
        "val": ine_mediana_usd,
        "str": _fm(ine_mediana_usd, 0),
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv / BCCh"
    }
    cifras["ine_esi_mediana_clp"] = {
        "val": ine_mediana_clp,
        "str": f"${_fi(int(ine_mediana_clp))} CLP",
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv"
    }
    cifras["ine_esi_mediana_usd"] = {
        "val": ine_mediana_usd,
        "str": f"${_fi(int(round(ine_mediana_usd)))} USD",
        "tipo": "constante_externa",
        "fuente": "02_Fase_Preparar_Prepare/datos_crudos_raw/INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv / BCCh"
    }

    # Tecnologías principales (Demanda GOB / Adopción SO)
    def _tech_stats(tech_name: str, key_prefix: str) -> None:
        n_gob_t = int((hab["tecnologia"] == tech_name).sum())
        pct_gob_t = round(100.0 * n_gob_t / n_gob_scope, 2)
        cifras[f"{key_prefix}_gob_n"] = {"val": n_gob_t, "str": _fi(n_gob_t), "pct": pct_gob_t, "pct_str": _fp(pct_gob_t, 2)}
        if (df_p1["tecnologia"] == tech_name).any():
            row_p1 = df_p1.loc[df_p1["tecnologia"] == tech_name].iloc[0]
            pct_so_cl = float(row_p1["pct_adopcion_chile"])
            pct_so_lat = float(row_p1["pct_adopcion_latam"])
            cifras[f"{key_prefix}_so_chile_pct"] = {"val": pct_so_cl, "str": _fp(pct_so_cl, 2), "pct_str": _fp(pct_so_cl, 2)}
            cifras[f"{key_prefix}_so_latam_pct"] = {"val": pct_so_lat, "str": _fp(pct_so_lat, 2), "pct_str": _fp(pct_so_lat, 2)}

    _tech_stats("SQL", "tech_sql")
    _tech_stats("AWS", "tech_aws")
    _tech_stats("Python", "tech_python")
    _tech_stats("Microsoft Azure", "tech_azure")
    _tech_stats("JavaScript", "tech_javascript")
    _tech_stats("TypeScript", "tech_typescript")
    _tech_stats("Google Cloud", "tech_google_cloud")
    _tech_stats("C#", "tech_csharp")
    _tech_stats("Swift", "tech_swift")
    _tech_stats("Elasticsearch", "tech_elasticsearch")
    _tech_stats("R", "tech_r")

    # Azure métricas específicas
    row_az = df_p1.loc[df_p1["tecnologia"] == "Microsoft Azure"].iloc[0]
    moe_az = float(row_az["moe95_pp_chile"])
    cifras["tech_azure_moe_chile"] = {"val": moe_az, "str": f"±{_fp(moe_az, 1)}".replace("%", " pp")}
    pct_gob_az = float(cifras["tech_azure_gob_n"]["pct"])
    pct_so_cl_az = float(cifras["tech_azure_so_chile_pct"]["val"])
    brecha_az = round(pct_gob_az - pct_so_cl_az, 2)
    cifras["tech_azure_brecha_pp"] = {"val": brecha_az, "str": f"+{_fp(brecha_az, 1)}".replace("%", " pp")}
    top_azure_sin = float(df_sens.loc[df_sens["tecnologia"] == "Microsoft Azure", "pct_demanda_sin_empresa_top"].iloc[0])
    cifras["tech_azure_sin_top"] = {"val": top_azure_sin, "pct_str": _fp(top_azure_sin, 2)}

    # Bandas Chile Local
    for sen in ["Semi-Senior", "Senior"]:
        row_s = p2_bandas_cl.loc[p2_bandas_cl["seniority_nivel"] == sen].iloc[0]
        s_norm = "semi_senior" if sen == "Semi-Senior" else "senior"
        n_s = int(row_s["n"])
        p25_s = float(row_s["p25_usd"])
        p50_s = float(row_s["mediana_usd"])
        p75_s = float(row_s["p75_usd"])
        cifras[f"banda_cl_{s_norm}_n"] = {"val": n_s, "str": _fi(n_s), "n_str": f"N={_fi(n_s)}"}
        cifras[f"banda_cl_{s_norm}_p25"] = {"val": p25_s, "str": _fm(p25_s, 0)}
        cifras[f"banda_cl_{s_norm}_mediana"] = {"val": p50_s, "str": _fm(p50_s, 0)}
        cifras[f"banda_cl_{s_norm}_p75"] = {"val": p75_s, "str": _fm(p75_s, 0)}

    m_semi_cl = float(cifras["banda_cl_semi_senior_mediana"]["val"])
    m_sr_cl = float(cifras["banda_cl_senior_mediana"]["val"])
    salto_cl_monto = round(m_sr_cl - m_semi_cl, 2)
    salto_cl_pct = round(100.0 * (m_sr_cl - m_semi_cl) / m_semi_cl, 1)
    cifras["salto_cl_semi_a_senior_monto"] = {"val": salto_cl_monto, "str": f"+{_fm(salto_cl_monto, 0)}"}
    cifras["salto_cl_semi_a_senior_pct"] = {"val": salto_cl_pct, "str": _fp(salto_cl_pct, 1), "pct_str": f"+{_fp(salto_cl_pct, 1)}"}

    # Bandas Remoto sin país declarado
    for sen in ["Semi-Senior", "Senior"]:
        row_s = p2_bandas_rem.loc[p2_bandas_rem["seniority_nivel"] == sen].iloc[0]
        s_norm = "semi_senior" if sen == "Semi-Senior" else "senior"
        n_s = int(row_s["n"])
        p25_s = float(row_s["p25_usd"])
        p50_s = float(row_s["mediana_usd"])
        p75_s = float(row_s["p75_usd"])
        cifras[f"banda_rem_{s_norm}_n"] = {"val": n_s, "str": _fi(n_s), "n_str": f"N={_fi(n_s)}"}
        cifras[f"banda_rem_{s_norm}_p25"] = {"val": p25_s, "str": _fm(p25_s, 0)}
        cifras[f"banda_rem_{s_norm}_mediana"] = {"val": p50_s, "str": _fm(p50_s, 0)}
        cifras[f"banda_rem_{s_norm}_p75"] = {"val": p75_s, "str": _fm(p75_s, 0)}

    # Salto GOB Total (Chile + remotas)
    row_tot_semi = p2_gob_tot.loc[p2_gob_tot["seniority_nivel"] == "Semi-Senior"].iloc[0]
    row_tot_sr = p2_gob_tot.loc[p2_gob_tot["seniority_nivel"] == "Senior"].iloc[0]
    n_tot_semi = int(row_tot_semi["n"])
    med_tot_semi = float(row_tot_semi["mediana_usd"])
    n_tot_sr = int(row_tot_sr["n"])
    med_tot_sr = float(row_tot_sr["mediana_usd"])
    salto_tot_monto = round(med_tot_sr - med_tot_semi, 2)
    salto_tot_pct = round(100.0 * (med_tot_sr - med_tot_semi) / med_tot_semi, 1)

    cifras["gob_total_semi_senior_mediana"] = {"val": med_tot_semi, "str": _fm(med_tot_semi, 0), "n": n_tot_semi, "n_str": f"N={_fi(n_tot_semi)}"}
    cifras["gob_total_senior_mediana"] = {"val": med_tot_sr, "str": _fm(med_tot_sr, 0), "n": n_tot_sr, "n_str": f"N={_fi(n_tot_sr)}"}
    cifras["gob_total_salto_senior_monto"] = {"val": salto_tot_monto, "str": f"+{_fm(salto_tot_monto, 0)}"}
    cifras["gob_total_salto_senior_pct"] = {"val": salto_tot_pct, "pct_str": f"+{_fp(salto_tot_pct, 1)}"}

    p75_tot_sr = float(gob_sal[gob_sal["seniority_nivel"] == "Senior"]["salario_mensual_usd"].quantile(0.75))
    p25_tot_semi = float(gob_sal[gob_sal["seniority_nivel"] == "Semi-Senior"]["salario_mensual_usd"].quantile(0.25))
    cifras["gob_total_senior_p75"] = {"val": p75_tot_sr, "str": _fm(p75_tot_sr, 0)}
    cifras["gob_total_semi_senior_p25"] = {"val": p25_tot_semi, "str": _fm(p25_tot_semi, 0)}

    # Modalidades GOB (Medianas agregadas)
    for mod in ["Presencial", "Híbrido", "Remoto Local", "Remoto Total"]:
        row_m = p3_gob_mod.loc[p3_gob_mod["modalidad_grupo"] == mod].iloc[0]
        m_norm = mod.lower().replace(" ", "_").replace("í", "i")
        n_m = int(row_m["n"])
        med_m = float(row_m["mediana_usd"])
        cifras[f"gob_modalidad_{m_norm}_mediana"] = {"val": med_m, "str": _fm(med_m, 0), "n": n_m, "n_str": f"N={_fi(n_m)}"}

    # Remoto local Senior pct
    sub_rl = gob_sal[gob_sal["modalidad_grupo"] == "Remoto Local"]
    pct_rl_sr_lead = round(100.0 * sub_rl["seniority_nivel"].isin(["Senior", "Lead"]).sum() / len(sub_rl), 1)
    cifras["gob_remoto_local_senior_lead_pct"] = {"val": pct_rl_sr_lead, "str": _fp(pct_rl_sr_lead, 1), "pct_str": _fp(pct_rl_sr_lead, 1)}

    # Países SO LatAm (calculados dinámicamente desde so_sal)
    norm_p = lambda x: re.sub(r"[^a-z]", "", x.lower().replace("é", "e").replace("á", "a").replace("ú", "u").replace("í", "i").replace("ó", "o"))
    for pais, grp in so_sal.groupby("pais"):
        p_slug = norm_p(pais)
        n_p = int(len(grp))
        med_p = round(float(grp["salario_mensual_usd"].median()), 2)
        cifras[f"so_{p_slug}_mediana"] = {
            "val": med_p,
            "str": _fm(med_p, 0),
            "n": n_p,
            "n_str": f"N={_fi(n_p)}",
        }

    # DSS EE.UU. por año
    for _, r_yr in df_dss_us_years.iterrows():
        yr_val = int(r_yr["work_year"])
        n_yr = int(r_yr["n"])
        med_yr = float(r_yr["mediana_usd"])
        pct_sen_yr = float(r_yr["pct_senior"])
        cifras[f"dss_eeuu_{yr_val}_mediana"] = {
            "val": med_yr,
            "str": _fm(med_yr, 0),
            "n": n_yr,
            "n_str": f"N={_fi(n_yr)}",
            "pct_senior": pct_sen_yr,
            "pct_senior_str": _fp(pct_sen_yr, 1),
        }
        cifras[f"dss_eeuu_{yr_val}_n"] = {
            "val": n_yr,
            "str": _fi(n_yr),
            "n_str": f"N={_fi(n_yr)}",
        }

    cifras["dss_eeuu_registros"] = cifras["dss_eeuu_total"]

    # Aliases de compatibilidad y visualización
    cifras["gob_sql_pct"] = {"val": float(cifras["tech_sql_gob_n"]["pct"]), "str": _fp(float(cifras["tech_sql_gob_n"]["pct"]), 1), "pct_str": _fp(float(cifras["tech_sql_gob_n"]["pct"]), 2)}
    cifras["gob_aws_pct"] = {"val": float(cifras["tech_aws_gob_n"]["pct"]), "str": _fp(float(cifras["tech_aws_gob_n"]["pct"]), 1), "pct_str": _fp(float(cifras["tech_aws_gob_n"]["pct"]), 2)}
    cifras["gob_python_pct"] = {"val": float(cifras["tech_python_gob_n"]["pct"]), "str": _fp(float(cifras["tech_python_gob_n"]["pct"]), 1), "pct_str": _fp(float(cifras["tech_python_gob_n"]["pct"]), 2)}
    cifras["gob_azure_pct"] = {"val": float(cifras["tech_azure_gob_n"]["pct"]), "str": _fp(float(cifras["tech_azure_gob_n"]["pct"]), 1), "pct_str": _fp(float(cifras["tech_azure_gob_n"]["pct"]), 2)}
    cifras["gob_javascript_pct"] = {"val": float(cifras["tech_javascript_gob_n"]["pct"]), "str": _fp(float(cifras["tech_javascript_gob_n"]["pct"]), 1), "pct_str": _fp(float(cifras["tech_javascript_gob_n"]["pct"]), 2)}

    # Pct tecnologías por alcance (Chile Local vs Remoto)
    row_sql_p1 = df_p1.loc[df_p1["tecnologia"] == "SQL"].iloc[0]
    row_aws_p1 = df_p1.loc[df_p1["tecnologia"] == "AWS"].iloc[0]
    cifras["gob_sql_chile_pct"] = {"val": float(row_sql_p1["pct_gob_chile_local"]), "str": _fp(float(row_sql_p1["pct_gob_chile_local"]), 1)}
    cifras["gob_sql_remoto_pct"] = {"val": float(row_sql_p1["pct_gob_remoto"]), "str": _fp(float(row_sql_p1["pct_gob_remoto"]), 1)}
    cifras["gob_aws_chile_pct"] = {"val": float(row_aws_p1["pct_gob_chile_local"]), "str": _fp(float(row_aws_p1["pct_gob_chile_local"]), 1)}
    cifras["gob_aws_remoto_pct"] = {"val": float(row_aws_p1["pct_gob_remoto"]), "str": _fp(float(row_aws_p1["pct_gob_remoto"]), 1)}

    cifras["gob_senior_salario_mediano"] = {"val": med_tot_sr, "str": _fm(med_tot_sr, 0)}
    cifras["gob_semisenior_salario_mediano"] = {"val": med_tot_semi, "str": _fm(med_tot_semi, 0)}
    med_gob_tot = float(gob_sal["salario_mensual_usd"].median())
    cifras["gob_salario_mediano_total"] = {"val": med_gob_tot, "str": _fm(med_gob_tot, 0)}
    cifras["gob_salto_senior_vs_semisenior_pct"] = {"val": salto_tot_pct, "str": _fp(salto_tot_pct, 1), "pct_str": f"+{_fp(salto_tot_pct, 1)}"}
    cifras["gob_remoto_local_salario_mediano"] = {"val": float(cifras["gob_modalidad_remoto_local_mediana"]["val"]), "str": _fm(float(cifras["gob_modalidad_remoto_local_mediana"]["val"]), 0)}
    cifras["gob_remoto_local_pct_senior_lead"] = {"val": pct_rl_sr_lead, "str": _fp(pct_rl_sr_lead, 1)}

    pct_con_sal = round(100.0 * n_gob_sal_val / n_gob_scope, 2)
    cifras["gob_pct_con_salario"] = {"val": pct_con_sal, "str": _fp(pct_con_sal, 1)}
    n_jr_tot = int((gob_sal["seniority_nivel"] == "Junior").sum())
    n_lead_tot = int((gob_sal["seniority_nivel"] == "Lead").sum())
    cifras["gob_junior_n"] = {"val": n_jr_tot, "str": _fi(n_jr_tot)}
    cifras["gob_lead_n"] = {"val": n_lead_tot, "str": _fi(n_lead_tot)}
    cifras["so_chile_salario_mediano"] = {"val": float(cifras["so_chile_mediana"]["val"]), "str": _fm(float(cifras["so_chile_mediana"]["val"]), 0)}

    # Ratios INE
    ratio_semi_ine = round(m_semi_cl / ine_mediana_usd, 2)
    ratio_sr_ine = round(m_sr_cl / ine_mediana_usd, 2)
    ratio_tot_ine = round(float(p3_gob_geo.loc[p3_gob_geo["alcance_geo"] == "Chile Local", "mediana_usd"].iloc[0]) / ine_mediana_usd, 2)
    cifras["salto_cl_semi_vs_ine_ratio"] = {"val": ratio_semi_ine, "str": f"{ratio_semi_ine:.2f}x".replace(".", ",")}
    cifras["salto_cl_senior_vs_ine_ratio"] = {"val": ratio_sr_ine, "str": f"{ratio_sr_ine:.2f}x".replace(".", ",")}
    cifras["salto_cl_total_vs_ine_ratio"] = {"val": ratio_tot_ine, "str": f"{ratio_tot_ine:.2f}x".replace(".", ",")}
    m_gob_sin = round(float(gob_sal["salario_mensual_usd"].mean()), 2)
    gob_exp = gob_sal.merge(hab, on="job_id", how="left")  # mismo LEFT JOIN que la consulta SQL Q01
    m_gob_con = round(float(gob_exp["salario_mensual_usd"].mean()), 2)
    sesgo_gob = round(m_gob_con - m_gob_sin, 2)

    m_so_sin = round(float(so_sal["salario_mensual_usd"].mean()), 2)
    so_exp = so_sal.merge(so_tech, on="ResponseId", how="left")  # mismo LEFT JOIN que la consulta SQL Q01
    m_so_con = round(float(so_exp["salario_mensual_usd"].mean()), 2)
    sesgo_so = round(m_so_con - m_so_sin, 2)

    cifras["gob_media_sin_dup"] = {"val": m_gob_sin, "str": _fm(m_gob_sin, 2)}
    cifras["so_media_sin_dup"] = {"val": m_so_sin, "str": _fm(m_so_sin, 2)}
    cifras["gob_media_con_dup"] = {"val": m_gob_con, "str": _fm(m_gob_con, 2)}
    cifras["so_media_con_dup"] = {"val": m_so_con, "str": _fm(m_so_con, 2)}
    cifras["gob_sesgo_dup"] = {"val": sesgo_gob, "str": f"+{_fm(sesgo_gob, 2)}"}
    cifras["so_sesgo_dup"] = {"val": sesgo_so, "str": f"+{_fm(sesgo_so, 2)}"}
    # Salto acumulado 10+ años en Stack Overflow
    med_so_01 = float(p2_so.loc[p2_so["tramo_experiencia"] == "0-1 años (<2)", "mediana_usd"].iloc[0])
    med_so_10 = float(p2_so.loc[p2_so["tramo_experiencia"] == "10+ años", "mediana_usd"].iloc[0])
    so_salto_10 = round((med_so_10 - med_so_01) / med_so_01 * 100.0, 1)
    cifras["so_salto_acumulado_10anios_pct"] = {"val": so_salto_10, "str": f"+{_fp(so_salto_10, 1)}"}

    # Prima Cloud vs SQL en Stack Overflow
    med_so_aws = float(q11_so_py.loc[q11_so_py["tecnologia"] == "AWS", "mediana_usd"].iloc[0])
    med_so_sql = float(q11_so_py.loc[q11_so_py["tecnologia"] == "SQL", "mediana_usd"].iloc[0])
    so_prima_aws_usd = round(med_so_aws - med_so_sql, 2)
    so_prima_aws_pct = round(so_prima_aws_usd / med_so_sql * 100.0, 2)
    cifras["so_prima_aws_vs_sql_usd"] = {"val": so_prima_aws_usd, "monto_int": int(round(so_prima_aws_usd)), "str": f"+{_fm(so_prima_aws_usd, 0)} USD"}
    cifras["so_prima_aws_vs_sql_pct"] = {"val": so_prima_aws_pct, "pct": round(so_prima_aws_pct, 1), "str": f"+{_fp(so_prima_aws_pct, 1)}"}

    # Prima Cloud vs SQL en Get on Board
    med_gob_aws = float(q11_gob_py.loc[q11_gob_py["tecnologia"] == "AWS", "mediana_usd"].iloc[0])
    med_gob_sql = float(q11_gob_py.loc[q11_gob_py["tecnologia"] == "SQL", "mediana_usd"].iloc[0])
    gob_prima_aws_usd = round(med_gob_aws - med_gob_sql, 1)
    gob_prima_aws_pct = round(gob_prima_aws_usd / med_gob_sql * 100.0, 2)
    cifras["gob_prima_aws_vs_sql_pct"] = {"val": gob_prima_aws_pct, "pct": round(gob_prima_aws_pct, 1), "str": f"+{_fp(gob_prima_aws_pct, 1)}"}
    cifras["gob_prima_aws_vs_sql_usd"] = {"val": gob_prima_aws_usd, "str": f"+{_fm(gob_prima_aws_usd, 0)} USD"}

    # Brecha Remoto sin país declarado vs Chile Local en Get on Board
    med_gob_remoto_gen = float(gob_sal.loc[gob_sal["alcance_geo"] == "Remoto sin país declarado", "salario_mensual_usd"].median())
    med_gob_local_gen = float(gob_sal.loc[gob_sal["alcance_geo"] == "Chile Local", "salario_mensual_usd"].median())
    gob_brecha_rem_loc_usd = round(med_gob_remoto_gen - med_gob_local_gen, 1)
    gob_brecha_rem_loc_pct = round(gob_brecha_rem_loc_usd / med_gob_local_gen * 100.0, 2)
    cifras["gob_brecha_remoto_vs_chile_local_pct"] = {"val": gob_brecha_rem_loc_pct, "pct": round(gob_brecha_rem_loc_pct, 1), "str": f"+{_fp(gob_brecha_rem_loc_pct, 1)}"}
    cifras["gob_brecha_remoto_vs_chile_local_usd"] = {"val": gob_brecha_rem_loc_usd, "str": f"+{_fm(gob_brecha_rem_loc_usd, 0)} USD"}

    # Data Science Salaries 2024
    dss_2024 = dss_us[dss_us["work_year"] == 2024]["salary_yearly_usd"]  # el estudio usa solo EE.UU.
    dss_med_anual = float(dss_2024.median())
    dss_med_mensual = round(dss_med_anual / 12.0, 1)
    cifras["dss_2024_mediana_anual_usd"] = {"val": dss_med_anual, "str": f"{_fm(dss_med_anual, 0)} USD"}
    cifras["dss_2024_mediana_mensual_usd"] = {"val": dss_med_mensual, "str": f"{_fm(dss_med_mensual, 0)} USD"}

    # Intervalos bootstrap diferencias
    row_diff_sr = df_diff.loc[df_diff["comparacion"].str.contains("Senior Remoto")].iloc[0]
    diff_val_sr = float(row_diff_sr["diferencia_observada_usd"])
    inf_val_sr = float(row_diff_sr["ic95_inf_usd"])
    sup_val_sr = float(row_diff_sr["ic95_sup_usd"])
    cifras["ic_senior_remoto_vs_local_diff"] = {"val": diff_val_sr, "str": f"+{_fm(diff_val_sr, 0)}"}
    cifras["ic_senior_remoto_vs_local_inf"] = {"val": inf_val_sr, "str": _fm(inf_val_sr, 0)}
    cifras["ic_senior_remoto_vs_local_sup"] = {"val": sup_val_sr, "str": _fm(sup_val_sr, 0)}

    # Aliases semánticos documentales
    cifras["so_total_latam"] = cifras["so_latam_total"]
    cifras["so_total_latam_salarios"] = cifras["so_latam_salarios_validos"]
    cifras["dss_total_registros"] = cifras["dss_total"]
    cifras["ratio_cl_semi_vs_ine_mediana"] = cifras["salto_cl_semi_vs_ine_ratio"]

    med_cl_semi_val = float(cifras["banda_cl_semi_senior_mediana"]["val"])
    med_ine_val = float(cifras["ine_esi_mediana_usd"]["val"])
    salto_ine_pct = round((med_cl_semi_val - med_ine_val) / med_ine_val * 100.0, 1)
    cifras["salto_cl_semi_vs_ine_pct"] = {"val": salto_ine_pct, "str": _fp(salto_ine_pct, 1), "pct_str": f"+{_fp(salto_ine_pct, 1)}"}

    tot_crudos = int(n_gob_raw + n_so_glob + n_dss_tot + len(ine))
    cifras["total_registros_crudos"] = {"val": tot_crudos, "str": f"{tot_crudos:,}".replace(",", ".")}

    sal_min_filtro = int(m_f3["umbrales"]["gob_salario_min_mensual_usd"])
    cifras["salario_min_filtro_usd"] = {
        "val": sal_min_filtro,
        "str": f"${sal_min_filtro}",
        "tipo": "constante_externa",
        "fuente": "Protocolo Metodológico - Umbral Piso Salarial"
    }
    for _clave, _origen in (("so_filtro_anual_min_usd", "so_salario_min_anual_usd"), ("so_filtro_anual_max_usd", "so_salario_max_anual_usd")):
        _v = int(m_f3["umbrales"][_origen])
        cifras[_clave] = {"val": _v, "str": f"${_v:,}".replace(",", "."), "tipo": "constante_externa",
                          "fuente": "Protocolo Metodológico - Rango anual plausible en Stack Overflow"}
    cifras["umbral_tlc_n"] = {
        "val": 30,
        "str": "N >= 30",
        "tipo": "constante_externa",
        "fuente": "Teorema del Límite Central (CLT) - Muestra Mínima N>=30"
    }
    cifras["meta_mejora_pct"] = {
        "val": 20.0,
        "str": "20%",
        "tipo": "constante_externa",
        "fuente": "Objetivo Métrico de Negocio - Presencia >=20%"
    }

    cifras["gob_cl_semi_senior_mediana"] = cifras["banda_cl_semi_senior_mediana"]
    cifras["gob_cl_semi_senior_n"] = cifras["banda_cl_semi_senior_n"]
    cifras["gob_cl_semi_senior_p25"] = cifras["banda_cl_semi_senior_p25"]
    cifras["gob_cl_semi_senior_p75"] = cifras["banda_cl_semi_senior_p75"]
    cifras["gob_cl_senior_mediana"] = cifras["banda_cl_senior_mediana"]
    cifras["gob_cl_senior_n"] = cifras["banda_cl_senior_n"]
    cifras["gob_cl_senior_p25"] = cifras["banda_cl_senior_p25"]
    cifras["gob_cl_senior_p75"] = cifras["banda_cl_senior_p75"]

    cifras["gob_semi_local_mediana"] = cifras["banda_cl_semi_senior_mediana"]
    cifras["gob_senior_local_mediana"] = cifras["banda_cl_senior_mediana"]
    cifras["gob_semi_remoto_mediana"] = cifras["banda_rem_semi_senior_mediana"]
    cifras["gob_senior_remoto_mediana"] = cifras["banda_rem_senior_mediana"]

    cifras["gob_azure_n"] = cifras["tech_azure_gob_n"]
    cifras["gob_gcp_n"] = cifras["tech_google_cloud_gob_n"]
    cifras["gob_gcp_pct"] = {"val": float(cifras["tech_google_cloud_gob_n"]["pct"]), "str": cifras["tech_google_cloud_gob_n"]["pct_str"]}

    n_cl_tot_float = float(n_cl_tot)
    n_rem_tot_float = float(n_rem_tot)
    m_hab_vac = hab.merge(vac, on="job_id")
    js_cl_count = float(m_hab_vac.loc[(m_hab_vac["alcance_geo"] == "Chile Local") & (m_hab_vac["tecnologia"] == "JavaScript"), "job_id"].nunique())
    js_rem_count = float(m_hab_vac.loc[(m_hab_vac["alcance_geo"] == "Remoto sin país declarado") & (m_hab_vac["tecnologia"] == "JavaScript"), "job_id"].nunique())
    js_cl_pct = round(js_cl_count / n_cl_tot_float * 100.0, 1)
    js_rem_pct = round(js_rem_count / n_rem_tot_float * 100.0, 1)
    cifras["gob_js_chile_pct"] = {"val": js_cl_pct, "str": f"{js_cl_pct:.1f}%".replace(".", ",")}
    cifras["gob_js_remoto_pct"] = {"val": js_rem_pct, "str": f"{js_rem_pct:.1f}%".replace(".", ",")}

    # Saltos
    med_cl_sr = float(cifras["banda_cl_senior_mediana"]["val"])
    salto_cl_semi_monto = float(med_cl_sr - med_cl_semi_val)
    salto_cl_semi_pct = round(salto_cl_semi_monto / med_cl_semi_val * 100.0, 1)
    cifras["gob_cl_salto_semi_senior_pct"] = {"val": salto_cl_semi_pct, "str": _fp(salto_cl_semi_pct, 1), "pct_str": f"+{_fp(salto_cl_semi_pct, 1)}"}
    cifras["gob_cl_salto_semi_senior_monto"] = {"val": salto_cl_semi_monto, "str": f"+{_fm(salto_cl_semi_monto, 0)} USD"}

    med_tot_sr = float(cifras["banda_tot_senior_mediana"]["val"]) if "banda_tot_senior_mediana" in cifras else float(cifras["gob_total_senior_mediana"]["val"])
    med_tot_semi = float(cifras["banda_tot_semi_senior_mediana"]["val"]) if "banda_tot_semi_senior_mediana" in cifras else float(cifras["gob_total_semi_senior_mediana"]["val"])
    salto_tot_semi_monto = float(med_tot_sr - med_tot_semi)
    salto_tot_semi_pct = round(salto_tot_semi_monto / med_tot_semi * 100.0, 1)
    cifras["gob_total_salto_semi_senior_pct"] = {"val": salto_tot_semi_pct, "str": _fp(salto_tot_semi_pct, 1), "pct_str": f"+{_fp(salto_tot_semi_pct, 1)}"}
    cifras["gob_total_salto_semi_senior_monto"] = {"val": salto_tot_semi_monto, "str": f"+{_fm(salto_tot_semi_monto, 0)} USD"}


    # Cloud Senior
    sr_jobs = gob_sal[gob_sal["seniority_nivel"] == "Senior"]
    cloud_jids = set(hab.loc[hab["tipo_tecnologia"] == "Cloud", "job_id"])
    sr_cloud = sr_jobs[sr_jobs["job_id"].isin(cloud_jids)]
    sr_no_cloud = sr_jobs[~sr_jobs["job_id"].isin(cloud_jids)]
    med_sr_cloud = float(sr_cloud["salario_mensual_usd"].median())
    med_sr_no_cloud = float(sr_no_cloud["salario_mensual_usd"].median())
    diff_sr_cloud = float(med_sr_cloud - med_sr_no_cloud)
    n_sr_cloud = int(len(sr_cloud))
    n_sr_no_cloud = int(len(sr_no_cloud))

    cifras["gob_senior_cloud_mediana"] = {"val": med_sr_cloud, "str": _fm(med_sr_cloud, 0)}
    cifras["gob_senior_sin_cloud_mediana"] = {"val": med_sr_no_cloud, "str": _fm(med_sr_no_cloud, 0)}
    cifras["gob_senior_cloud_diff"] = {"val": diff_sr_cloud, "str": f"+{_fm(diff_sr_cloud, 0)}"}
    cifras["gob_senior_cloud_n"] = {"val": n_sr_cloud, "str": _fi(n_sr_cloud), "n_str": f"N={_fi(n_sr_cloud)}"}
    cifras["gob_senior_sin_cloud_n"] = {"val": n_sr_no_cloud, "str": _fi(n_sr_no_cloud), "n_str": f"N={_fi(n_sr_no_cloud)}"}

    # Cifras de la capa de publicación (Kaggle y Tableau)
    def _fd(v: float) -> str:
        return f"+{_fm(v, 0)}" if v >= 0 else _fm(v, 0)

    _pcl = pub_cl.set_index("seniority_nivel")
    _prem = pub_rem.set_index("seniority_nivel")
    for _niv, _k in [(SEMI_SENIOR, "semi_senior"), (SENIOR_LEAD, "senior_lead")]:
        _r = _pcl.loc[_niv]
        cifras[f"pub_cl_{_k}_n"] = {"val": int(_r["n"]), "str": _fi(int(_r["n"])), "n_str": f"N={_fi(int(_r['n']))}"}
        for _c in ("mediana", "p25", "p75"):
            cifras[f"pub_cl_{_k}_{_c}"] = {"val": float(_r[f"{_c}_usd"]), "str": _fm(float(_r[f"{_c}_usd"]), 0)}
    cifras["pub_cl_junior_trainee_n"] = {"val": int(_pcl.loc[JUNIOR_TRAINEE, "n"]), "str": _fi(int(_pcl.loc[JUNIOR_TRAINEE, "n"])), "n_str": f"N={_fi(int(_pcl.loc[JUNIOR_TRAINEE, 'n']))}"}
    _salto = round((float(_pcl.loc[SENIOR_LEAD, "mediana_usd"]) / float(_pcl.loc[SEMI_SENIOR, "mediana_usd"]) - 1) * 100.0, 1)
    cifras["pub_cl_salto_semi_senior_lead_pct"] = {"val": _salto, "str": f"+{_fp(_salto, 1)}"}
    for _niv, _k in [(SENIOR_LEAD, "senior_lead"), (RESTO, "resto")]:
        _r = _prem.loc[_niv]
        cifras[f"pub_rem_{_k}_n"] = {"val": int(_r["n"]), "str": _fi(int(_r["n"])), "n_str": f"N={_fi(int(_r['n']))}"}
        for _c in ("mediana", "p25", "p75"):
            cifras[f"pub_rem_{_k}_{_c}"] = {"val": float(_r[f"{_c}_usd"]), "str": _fm(float(_r[f"{_c}_usd"]), 0)}
    _d, _lo, _hi, _conc = pub_ic_sl
    cifras["pub_ic_senior_lead_diff"] = {"val": float(_d), "str": _fd(float(_d))}
    cifras["pub_ic_senior_lead_inf"] = {"val": float(_lo), "str": _fm(float(_lo), 0)}
    cifras["pub_ic_senior_lead_sup"] = {"val": float(_hi), "str": _fm(float(_hi), 0)}
    cifras["pub_ic_senior_lead_lectura"] = {"val": int(bool(_conc)), "str": ("la diferencia es concluyente, así que la mayor proporción de cargos Senior y Lead en remoto no alcanza para explicar toda la brecha"
                                                                        if _conc else "la diferencia no es concluyente con estos datos")}
    _sl_jobs = gob_pub[gob_pub["seniority_pub2"] == SENIOR_LEAD]
    _sl_cloud = _sl_jobs[_sl_jobs["job_id"].isin(cloud_jids)]
    _sl_no_cloud = _sl_jobs[~_sl_jobs["job_id"].isin(cloud_jids)]
    _m1, _m2 = float(_sl_cloud["salario_mensual_usd"].median()), float(_sl_no_cloud["salario_mensual_usd"].median())
    cifras["pub_sl_cloud_mediana"] = {"val": _m1, "str": _fm(_m1, 0)}
    cifras["pub_sl_sin_cloud_mediana"] = {"val": _m2, "str": _fm(_m2, 0)}
    cifras["pub_sl_cloud_diff"] = {"val": _m1 - _m2, "str": _fd(_m1 - _m2)}

    # Top tecnologías (ordenado desc por ofertas GOB)
    df_p1_sorted = df_p1.sort_values(by="gob_n_ofertas", ascending=False).reset_index(drop=True)
    for k in (1, 2, 3):
        row_top = df_p1_sorted.iloc[k - 1]
        top_name = str(row_top["tecnologia"])
        top_n = int(row_top["gob_n_ofertas"])
        top_pct = float(row_top["pct_demanda_gob_total"])
        cifras[f"tecnologia_top{k}_nombre"] = {"nombre": top_name, "str": top_name}
        cifras[f"tecnologia_top{k}_n"] = {"val": top_n, "str": _fi(top_n), "n_str": f"N={_fi(top_n)}"}
        cifras[f"tecnologia_top{k}_pct"] = {"val": top_pct, "str": _fp(top_pct, 1), "pct_str": _fp(top_pct, 2)}

    # Países SO n y medians (solo N >= 30 con reporte inferencial)
    for pais, grp in so_sal.groupby("pais"):
        if len(grp) >= 30:
            p_slug = norm_p(pais)
            cifras[f"so_{p_slug}_n"] = {"val": int(len(grp)), "str": _fi(int(len(grp)))}

    # IC bootstrap claves
    cifras["ic_senior_remoto_vs_local_ci95_inf"] = cifras["ic_senior_remoto_vs_local_inf"]
    cifras["ic_senior_remoto_vs_local_ci95_sup"] = cifras["ic_senior_remoto_vs_local_sup"]

    row_diff_semi = df_diff.loc[df_diff["comparacion"].str.contains("Semi-Senior Remoto")].iloc[0]
    diff_val_semi = float(row_diff_semi["diferencia_observada_usd"])
    inf_val_semi = float(row_diff_semi["ic95_inf_usd"])
    sup_val_semi = float(row_diff_semi["ic95_sup_usd"])
    cifras["ic_semi_remoto_vs_local_diff"] = {"val": diff_val_semi, "str": f"{_fm(diff_val_semi, 0)} USD"}
    cifras["ic_semi_remoto_vs_local_ci95_inf"] = {"val": inf_val_semi, "str": _fm(inf_val_semi, 0)}
    cifras["ic_semi_remoto_vs_local_ci95_sup"] = {"val": sup_val_semi, "str": _fm(sup_val_semi, 0)}

    # Aliases adicionales documentales Markdown y DOCX
    cifras["gob_total_ofertas"] = cifras["gob_total_scope"]
    cifras["gob_salarios_validos_total"] = cifras["gob_salarios_validos"]
    cifras["so_latam_encuestados_total"] = cifras["so_latam_total"]
    cifras["so_latam_salarios_validos"] = cifras["so_total_latam_salarios"]
    cifras["so_chile_encuestados"] = cifras["so_chile_total"]
    so_cl_clp = round(cifras["so_chile_mediana"]["val"] * DOLAR_OBSERVADO_BCCH, 0)
    cifras["so_chile_pesos_ref"] = {"val": so_cl_clp, "str": f"~{_fm(so_cl_clp, 0)} CLP"}
    cifras["so_chile_clp"] = cifras["so_chile_pesos_ref"]
    cifras["gob_demanda_sql_pct"] = {"val": cifras["tech_sql_gob_n"]["pct"], "str": cifras["tech_sql_gob_n"]["pct_str"]}
    cifras["gob_demanda_sql_n"] = cifras["tech_sql_gob_n"]
    cifras["gob_demanda_aws_pct"] = {"val": cifras["tech_aws_gob_n"]["pct"], "str": cifras["tech_aws_gob_n"]["pct_str"]}
    cifras["gob_demanda_aws_n"] = cifras["tech_aws_gob_n"]
    cifras["gob_demanda_python_pct"] = {"val": cifras["tech_python_gob_n"]["pct"], "str": cifras["tech_python_gob_n"]["pct_str"]}
    cifras["gob_demanda_python_n"] = cifras["tech_python_gob_n"]
    cifras["gob_demanda_gcp_pct"] = {"val": cifras["gob_gcp_n"]["pct"], "str": cifras["gob_gcp_n"]["pct_str"]}
    cifras["gob_demanda_gcp_n"] = cifras["gob_gcp_n"]
    cifras["gob_demanda_azure_pct"] = {"val": cifras["tech_azure_gob_n"]["pct"], "str": cifras["tech_azure_gob_n"]["pct_str"]}
    cifras["gob_demanda_azure_n"] = cifras["tech_azure_gob_n"]
    cifras["so_chile_adopcion_azure_pct"] = {"val": cifras["tech_azure_so_chile_pct"]["val"], "str": cifras["tech_azure_so_chile_pct"]["pct_str"]}
    cifras["tree"] = {"val": "", "str": ""}

    n_so_cl_raw = int(len(so[(so["pais"] == "Chile") & so["salary_yearly_usd_raw"].notna()]))
    n_jr = int((gob_sal["seniority_nivel"] == "Junior").sum())
    n_lead = int((gob_sal["seniority_nivel"] == "Lead").sum())
    n_trainee = int((gob_sal["seniority_nivel"] == "Trainee").sum())
    cifras["so_chile_salarios_raw"] = {"val": n_so_cl_raw, "str": _fi(n_so_cl_raw), "n_str": f"N={_fi(n_so_cl_raw)}"}
    cifras["gob_junior_n"] = {"val": n_jr, "str": _fi(n_jr), "n_str": f"N={_fi(n_jr)}"}
    cifras["gob_lead_n"] = {"val": n_lead, "str": _fi(n_lead), "n_str": f"N={_fi(n_lead)}"}

    # Serializar cifras oficiales
    cifras_path = RES_DIR / "cifras_oficiales.json"
    with open(cifras_path, "w", encoding="utf-8") as f:
        json.dump(cifras, f, ensure_ascii=False, indent=2)

    resumen_completo = {
        "cifras_oficiales_resumen": {k: (v.get("str", v.get("pct_str", str(v.get("val")))) if isinstance(v, dict) else str(v)) for k, v in cifras.items()},
        "denominadores": sql_res["q01_control_integridad_left_join"].to_dict(orient="records"),
        "pregunta_1_demanda_tecnologias": df_p1.to_dict(orient="records"),
        "pregunta_2_bandas_chile_local": p2_bandas_cl.to_dict(orient="records"),
        "pregunta_2_bandas_remoto_sin_pais": p2_bandas_rem.to_dict(orient="records"),
        "pregunta_3_comparacion_ine_chile_local": df_ine_comp.to_dict(orient="records"),
        "pregunta_4_dss_eeuu_temporal": df_dss_us_years.to_dict(orient="records"),
        "pregunta_4_dss_eeuu_anio_tamano": dss_us_anio_tam.to_dict(orient="records"),
        "matriz_tlc_19_paises": df_tlc.to_dict(orient="records"),
        "resumen_sensibilidades": df_sens.to_dict(orient="records"),
        "resumen_ic_diferencias": df_diff.to_dict(orient="records"),
        "q14_estratificacion": df_q14.to_dict(orient="records"),
        "q15_tecnologias_seniority": df_q15.to_dict(orient="records"),
    }
    with open(RES_DIR / "resumen_fase4_completo.json", "w", encoding="utf-8") as f:
        json.dump(resumen_completo, f, ensure_ascii=False, indent=2)

    print("Script 04 ejecutado exitosamente. Cifras oficiales generadas en resumenes/cifras_oficiales.json.")


if __name__ == "__main__":
    main()
