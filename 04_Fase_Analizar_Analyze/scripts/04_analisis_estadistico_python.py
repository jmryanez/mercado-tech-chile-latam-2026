"""
Fase 4: Analizar (Analyze) — Ejecución Relacional SQLite + Análisis Descriptivo en Python
Certificado Profesional de Análisis de Datos de Google • Cursos 5, 7 y 8 (Caso Práctico 3)

Métodos aplicados estrictamente dentro del certificado:
- SQL (Curso 5): Ejecución directa de '04_consultas_analisis.sql' en SQLite
  (CREATE TEMP TABLE, LEFT JOIN, INNER JOIN, COUNT(DISTINCT), CASE WHEN, COALESCE, HAVING).
- Python (Curso 7): pandas (boolean masking, groupby(), agg(), describe(), merge(), concat())
  y numpy para medianas, medias, percentiles/cuartiles (p25/p75), amplitud p25–p75 y diferencias porcentuales.
- Regla N >= 30 (Curso 4) y separación estricta de poblaciones sin fusionar fuentes.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEAN_DIR = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed"
SQL_FILE = BASE_DIR / "04_Fase_Analizar_Analyze" / "sql" / "04_consultas_analisis.sql"
RES_DIR = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes"
RES_DIR.mkdir(parents=True, exist_ok=True)
DOLAR_OBSERVADO_BCCH = 969.80


def q25(s: pd.Series) -> float:
    return float(s.quantile(0.25))


def q75(s: pd.Series) -> float:
    return float(s.quantile(0.75))


def resumen_salarios(df: pd.DataFrame, group_col: str, col_usd: str = "salario_mensual_usd", col_clp: str = "salario_mensual_clp_ref") -> pd.DataFrame:
    """Calcula estadísticos descriptivos oficiales (N, media, mediana, cuartiles p25/p75, amplitud p25–p75, min, max)."""
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

    # --- Pregunta 1: Top 5 tecnologías por categoría (SQLite + validación Pandas) ---
    df_p1 = sql_res["q02_tecnologias_cruce_demanda_vs_adopcion"].copy()
    df_p1["pct_gob_chile_local"] = (100.0 * df_p1["n_gob_chile_local"] / (vac["alcance_geo"] == "Chile Local").sum()).round(2)
    df_p1["pct_gob_remoto"] = (100.0 * df_p1["n_gob_remoto"] / (vac["alcance_geo"] == "Remoto Global/LatAm").sum()).round(2)
    df_p1.to_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv", index=False, encoding="utf-8")

    # Verificación cruzada Python <-> SQL en Top Python / SQL / AWS
    py_gob_sql_n = int(hab[(hab["tipo_tecnologia"] == "Lenguaje") & (hab["tecnologia"] == "SQL")]["job_id"].nunique())
    sql_gob_sql_n = int(df_p1.loc[(df_p1["tipo_tecnologia"] == "Lenguaje") & (df_p1["tecnologia"] == "SQL"), "gob_n_ofertas"].iloc[0])
    assert py_gob_sql_n == sql_gob_sql_n, "Discrepancia Python vs SQL en conteo SQL GOB"

    top5_p1 = {}
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        sub = df_p1[df_p1["tipo_tecnologia"] == tipo].sort_values("gob_n_ofertas", ascending=False).head(5)
        top5_p1[tipo] = sub[
            ["tecnologia", "gob_n_ofertas", "pct_demanda_gob_total", "pct_gob_chile_local", "pct_gob_remoto", "so_n_chile", "pct_adopcion_chile", "so_n_latam", "pct_adopcion_latam", "estado_objetivo_metrico_1"]
        ].to_dict(orient="records")

    # También Top 5 en adopción Chile SO (por si difiere del Top 5 demanda GOB, ej. HTML/CSS o DigitalOcean)
    top5_so_chile = {}
    df_so_all = sql_res["q02_tecnologias_cruce_demanda_vs_adopcion"]
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        sub_so = (
            so_tech[so_tech["es_chile"] & (so_tech["tipo_tecnologia"] == tipo)]
            .groupby("tecnologia")["ResponseId"]
            .nunique()
            .reset_index(name="n_chile")
            .sort_values("n_chile", ascending=False)
            .head(5)
        )
        sub_so["pct_chile"] = (100.0 * sub_so["n_chile"] / int(so["es_chile"].sum())).round(2)
        top5_so_chile[tipo] = sub_so.to_dict(orient="records")

    # --- Pregunta 2: Salarios por Experiencia ---
    gob_sal = vac[vac["salario_valido_flag"] == True].copy()
    so_sal = so[(so["salario_valido_flag"] == True)].copy()

    p2_gob = resumen_salarios(gob_sal, "seniority_nivel")
    p2_gob["fuente"] = "Get on Board 2026"
    p2_gob = p2_gob.rename(columns={"seniority_nivel": "segmento"})

    # Verificación Python <-> SQL en media salarial GOB Senior
    py_sen_mean = float(p2_gob.loc[p2_gob["segmento"] == "Senior", "media_usd"].iloc[0])
    sql_sen_mean = float(sql_res["q04_gob_salarios_por_seniority"].loc[sql_res["q04_gob_salarios_por_seniority"]["seniority_nivel"] == "Senior", "media_mensual_usd"].iloc[0])
    assert abs(py_sen_mean - sql_sen_mean) < 0.02

    so_sal_exp = so_sal[so_sal["tramo_experiencia"] != "Sin dato"].copy()
    p2_so = resumen_salarios(so_sal_exp, "tramo_experiencia")
    p2_so["fuente"] = "Stack Overflow LatAm 2024"
    p2_so = p2_so.rename(columns={"tramo_experiencia": "segmento"})

    p2_dss = resumen_salarios(dss, "experiencia_es")
    p2_dss["fuente"] = "Data Science Salaries 2020-2024"
    p2_dss = p2_dss.rename(columns={"experiencia_es": "segmento"})

    df_p2 = pd.concat([p2_gob, p2_so, p2_dss], ignore_index=True)
    df_p2.to_csv(RES_DIR / "resumen_p2_salarios_experiencia.csv", index=False, encoding="utf-8")

    # Chile agregado en SO (N=46 >= 30)
    so_chile_sal = so_sal[so_sal["es_chile"] == True].copy()
    p2_chile_global = resumen_salarios(so_chile_sal, "subregion").to_dict(orient="records")

    # --- Pregunta 3: Salarios por Modalidad Laboral vs INE ESI 2025 ---
    p3_gob_mod = resumen_salarios(gob_sal, "modalidad_grupo")
    p3_gob_mod["fuente"] = "Get on Board 2026 (Modalidad)"
    p3_gob_mod = p3_gob_mod.rename(columns={"modalidad_grupo": "segmento"})

    p3_gob_geo = resumen_salarios(gob_sal, "alcance_geo")
    p3_gob_geo["fuente"] = "Get on Board 2026 (Alcance Geográfico)"
    p3_gob_geo = p3_gob_geo.rename(columns={"alcance_geo": "segmento"})

    so_sal_mod = so_sal[so_sal["modalidad_grupo"] != "Sin dato"].copy()
    p3_so_mod = resumen_salarios(so_sal_mod, "modalidad_grupo")
    p3_so_mod["fuente"] = "Stack Overflow LatAm 2024 (Modalidad)"
    p3_so_mod = p3_so_mod.rename(columns={"modalidad_grupo": "segmento"})

    df_p3 = pd.concat([p3_gob_mod, p3_gob_geo, p3_so_mod], ignore_index=True)
    df_p3["ratio_mediana_vs_ine_esi_2025"] = (df_p3["mediana_clp_ref"] / ine_mediana_clp).round(2)
    df_p3["brecha_pct_vs_ine_esi_2025"] = ((df_p3["mediana_clp_ref"] / ine_mediana_clp - 1.0) * 100.0).round(1)
    df_p3.to_csv(RES_DIR / "resumen_p3_salarios_modalidad_vs_ine.csv", index=False, encoding="utf-8")

    # Brechas porcentuales exactas vs Presencial
    gob_pres = float(p3_gob_mod.loc[p3_gob_mod["segmento"] == "Presencial", "mediana_usd"].iloc[0])
    p3_gob_mod["brecha_pct_vs_presencial"] = ((p3_gob_mod["mediana_usd"] / gob_pres - 1.0) * 100.0).round(1)

    gob_cl = float(p3_gob_geo.loc[p3_gob_geo["segmento"] == "Chile Local", "mediana_usd"].iloc[0])
    gob_rem_g = float(p3_gob_geo.loc[p3_gob_geo["segmento"] == "Remoto Global/LatAm", "mediana_usd"].iloc[0])
    brecha_gob_rem_global_vs_cl = round((gob_rem_g / gob_cl - 1.0) * 100.0, 1)

    so_pres = float(p3_so_mod.loc[p3_so_mod["segmento"] == "Presencial", "mediana_usd"].iloc[0])
    p3_so_mod["brecha_pct_vs_presencial"] = ((p3_so_mod["mediana_usd"] / so_pres - 1.0) * 100.0).round(1)

    # --- Pregunta 4: Tamaño de Empresa (SO LatAm) + Evolución DSS 2020-2024 ---
    so_sal_org = so_sal[so_sal["org_size_grupo"] != "Sin dato / NS-NR"].copy()
    p4_so_org = resumen_salarios(so_sal_org, "org_size_grupo")
    p4_so_org["fuente"] = "Stack Overflow LatAm 2024 (Grupo)"
    p4_so_org = p4_so_org.rename(columns={"org_size_grupo": "segmento"})

    so_sal_org_det = so_sal[~so_sal["org_size_detalle"].isin(["Sin dato", "I don’t know"])].copy()
    p4_so_org_det = resumen_salarios(so_sal_org_det, "org_size_detalle")
    p4_so_org_det["fuente"] = "Stack Overflow LatAm 2024 (Detalle)"
    p4_so_org_det = p4_so_org_det.rename(columns={"org_size_detalle": "segmento"})

    p4_dss_size = resumen_salarios(dss, "tamano_es")
    p4_dss_size["fuente"] = "Data Science Salaries 2020-2024 (Tamaño)"
    p4_dss_size = p4_dss_size.rename(columns={"tamano_es": "segmento"})

    p4_dss_year = resumen_salarios(dss, "work_year")
    p4_dss_year["fuente"] = "Data Science Salaries 2020-2024 (Año)"
    p4_dss_year = p4_dss_year.rename(columns={"work_year": "segmento"})

    df_p4 = pd.concat([p4_so_org, p4_so_org_det, p4_dss_size, p4_dss_year], ignore_index=True)
    df_p4.to_csv(RES_DIR / "resumen_p4_tamano_empresa_y_dss_temporal.csv", index=False, encoding="utf-8")

    # Resumen describe() globales (Curso 7: describe())
    desc_gob = gob_sal["salario_mensual_usd"].describe().round(2).to_dict()
    desc_so = so_sal["salario_mensual_usd"].describe().round(2).to_dict()
    desc_dss = dss["salario_mensual_usd"].describe().round(2).to_dict()

    # Patrones inesperados / contraste por país en SO LatAm (solo países con N >= 30 salarios válidos)
    so_pais_counts = so_sal.groupby("pais")["ResponseId"].count()
    paises_n30 = so_pais_counts[so_pais_counts >= 30].index.tolist()
    p_so_paises_n30 = resumen_salarios(so_sal[so_sal["pais"].isin(paises_n30)], "pais").sort_values("mediana_usd", ascending=False)
    p_so_paises_n30.to_csv(RES_DIR / "resumen_paises_so_latam_n30.csv", index=False, encoding="utf-8")

    # --- Q11: Matriz Volumen (% Demanda/Adopción) vs Compensación por Tecnología (N >= 30) ---
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

    # Cross-check Python vs SQLite Q11A (AWS media)
    py_aws_mean = float(q11_gob_py.loc[q11_gob_py["tecnologia"] == "AWS", "media_usd"].iloc[0])
    sql_aws_mean = float(sql_res["q11a_gob_tecnologia_vs_salario"].loc[sql_res["q11a_gob_tecnologia_vs_salario"]["tecnologia"] == "AWS", "media_mensual_usd"].iloc[0])
    assert abs(py_aws_mean - sql_aws_mean) < 0.02

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

    # --- Q12: Correlación != Causalidad — Composición Modalidad x Seniority y Alcance (GOB) ---
    q12_sql = sql_res["q12_gob_modalidad_composicion_seniority"].copy()
    # Verificación Python groupby().size() vs SQL Q12 (Curso 7 Mód. 4)
    mod_sen_sizes = gob_sal.groupby(["modalidad_grupo", "seniority_nivel"]).size()
    rem_tot_n = int(gob_sal[gob_sal["modalidad_grupo"] == "Remoto Local"].shape[0])
    pct_sen_py = round(100.0 * float(mod_sen_sizes.loc[("Remoto Local", "Senior")]) / rem_tot_n, 1)
    assert abs(pct_sen_py - float(q12_sql.loc[q12_sql["modalidad_grupo"] == "Remoto Local", "pct_senior"].iloc[0])) <= 0.1
    q12_sql.to_csv(RES_DIR / "resumen_q12_modalidad_composicion_seniority.csv", index=False, encoding="utf-8")

    # --- Q13: Categorías de Puesto en Get on Board (con control N >= 30) ---
    q13_py = resumen_salarios(gob_sal, "categoria").sort_values("n", ascending=False)
    tot_cat = vac.groupby("categoria")["job_id"].nunique().reset_index(name="total_ofertas_publicadas")
    q13_py = pd.merge(tot_cat, q13_py, on="categoria", how="left")
    q13_py["estado_regla_n30"] = np.where(
        q13_py["n"] >= 30,
        "Válido N >= 30 (Inferencia)",
        np.where(q13_py["n"] >= 15, "Exploratorio N < 30 (Limitación muestral)", "Excluido de inferencia (N < 15)"),
    )
    q13_py.to_csv(RES_DIR / "resumen_q13_gob_categorias.csv", index=False, encoding="utf-8")

    resumen_completo = {
        "denominadores": sql_res["q01_control_integridad_left_join"].to_dict(orient="records"),
        "ine_referencia": {
            "mediana_clp": ine_mediana_clp,
            "mediana_usd_ref": ine_mediana_usd,
            "media_clp": ine_media_clp,
        },
        "describe_globales": {
            "gob_mensual_usd": desc_gob,
            "so_latam_mensual_usd": desc_so,
            "dss_mensual_usd": desc_dss,
        },
        "pregunta_1_top5_gob_cruce": top5_p1,
        "pregunta_1_top5_so_chile": top5_so_chile,
        "pregunta_1_having_20pct_gob": sql_res["q03_gob_tecnologias_meta_20pct_having"].to_dict(orient="records"),
        "pregunta_2_gob_seniority": p2_gob.to_dict(orient="records"),
        "pregunta_2_so_exp": p2_so.to_dict(orient="records"),
        "pregunta_2_so_chile_agregado": p2_chile_global,
        "pregunta_2_dss_exp": p2_dss.to_dict(orient="records"),
        "pregunta_3_gob_modalidad": p3_gob_mod.to_dict(orient="records"),
        "pregunta_3_gob_alcance": p3_gob_geo.to_dict(orient="records"),
        "brecha_gob_remoto_global_vs_chile_local_pct": brecha_gob_rem_global_vs_cl,
        "pregunta_3_so_modalidad": p3_so_mod.to_dict(orient="records"),
        "pregunta_4_so_org_grupo": p4_so_org.to_dict(orient="records"),
        "pregunta_4_so_org_detalle": p4_so_org_det.to_dict(orient="records"),
        "pregunta_4_dss_tamano": p4_dss_size.to_dict(orient="records"),
        "pregunta_4_dss_anual": p4_dss_year.to_dict(orient="records"),
        "so_latam_paises_n30": p_so_paises_n30.to_dict(orient="records"),
        "q11_gob_tecnologia_vs_salario": q11_gob_py.to_dict(orient="records"),
        "q11_so_latam_tecnologia_vs_salario": q11_so_py.to_dict(orient="records"),
        "q12_gob_modalidad_composicion": q12_sql.to_dict(orient="records"),
        "q13_gob_categorias": q13_py.to_dict(orient="records"),
    }

    with open(RES_DIR / "resumen_fase4_completo.json", "w", encoding="utf-8") as f:
        json.dump(resumen_completo, f, ensure_ascii=False, indent=2)

    print(json.dumps(resumen_completo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
