#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generar_descargas.py
Generador reproducible de datasets de descarga, explorador JSON y paquete Kaggle.
Segunda ronda de correcciones (v1.7.0).
Elimina cifras escritas a mano, error_est y descripciones inconsistentes.
"""

from __future__ import annotations
import json
import shutil
import zipfile
from pathlib import Path
import pandas as pd
import numpy as np
import celdas_vacias

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed"
RES_DIR = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes"
DESC_DIR = BASE_DIR / "descargas"
DESC_DIR.mkdir(parents=True, exist_ok=True)
CIFRAS = json.loads((RES_DIR / "cifras_oficiales.json").read_text(encoding="utf-8"))


def _c(clave: str, campo: str = "str"):
    return CIFRAS[clave][campo]


def _miles(n) -> str:
    return f"{n:,.0f}".replace(",", ".")

FLAGS = {
    "Brasil": "🇧🇷", "Argentina": "🇦🇷", "México": "🇲🇽", "Colombia": "🇨🇴",
    "Chile": "🇨🇱", "Perú": "🇵🇪", "Uruguay": "🇺🇾", "Costa Rica": "🇨🇷",
    "Ecuador": "🇪🇨", "Guatemala": "🇬🇹", "Bolivia": "🇧🇴",
    "República Dominicana": "🇩🇴", "Venezuela": "🇻🇪", "Panamá": "🇵🇦",
    "Paraguay": "🇵🇾", "El Salvador": "🇸🇻", "Honduras": "🇭🇳",
    "Nicaragua": "🇳🇮", "Cuba": "🇨🇺"
}


def bootstrap_median_ci(series: pd.Series, n_boot: int = 2000, seed: int = 20261116) -> tuple[float | None, float | None]:
    clean = series.dropna().values
    if len(clean) < 5:
        return None, None
    rng = np.random.default_rng(seed)
    boot_meds = [float(np.median(rng.choice(clean, size=len(clean), replace=True))) for _ in range(n_boot)]
    return round(float(np.percentile(boot_meds, 2.5)), 2), round(float(np.percentile(boot_meds, 97.5)), 2)


def generar_explorador_y_descargas():
    # 1. Cargar datasets limpios
    vac = pd.read_csv(CLEAN_DIR / "GetOnBoard_Vacantes_2026_20261111_v01_clean.csv")
    so = pd.read_csv(CLEAN_DIR / "StackOverflow_LatAm_2024_20261111_v01_clean.csv")
    tlc = pd.read_csv(BASE_DIR / "descargas" / "Matriz_TLC_19_Paises_LatAm.csv")
    
    # Cargar bandas salariales procesadas
    b_cl = pd.read_csv(RES_DIR / "resumen_p2_bandas_chile_local.csv")
    b_rem = pd.read_csv(RES_DIR / "resumen_p2_bandas_remoto_sin_pais.csv")
    d_dss = pd.read_csv(RES_DIR / "resumen_p4_dss_eeuu_temporal.csv")
    
    # 1.A Get on Board Vacantes para explorador y CSV
    gob_vac_list = []
    for _, r in vac.iterrows():
        sal_usd = float(r["salario_mensual_usd"]) if bool(r["salario_valido_flag"]) and pd.notna(r["salario_mensual_usd"]) else None
        sal_clp = int(round(r["salario_mensual_clp_ref"])) if bool(r["salario_valido_flag"]) and pd.notna(r["salario_mensual_clp_ref"]) else None
        gob_vac_list.append({
            "id": str(r["job_id"]),
            "company_id": int(r["company_id"]) if pd.notna(r["company_id"]) else None,
            "pais_geo": str(r["alcance_geo"]),
            "paises_det": str(r["paises_raw"]) if pd.notna(r["paises_raw"]) else "",
            "titulo": str(r["titulo"]),
            "categoria": str(r["categoria"]),
            "modalidad": str(r["modalidad_grupo"]),
            "seniority": str(r["seniority_nivel"]),
            "sal_usd": sal_usd,
            "sal_clp": sal_clp,
            "postulaciones": int(r["applications_count"]) if pd.notna(r["applications_count"]) else 0,
        })
    
    df_gob_export = pd.DataFrame(gob_vac_list)
    df_gob_export.to_csv(DESC_DIR / "GetOnBoard_Vacantes_Auditadas_679.csv", index=False, encoding="utf-8")

    # 1.B Stack Overflow LatAm CSV export
    so.to_csv(DESC_DIR / "StackOverflow_LatAm_19_Paises_2024.csv", index=False, encoding="utf-8")

    # 1.C Matriz Países TLC
    paises_matrix = []
    for _, r in tlc.iterrows():
        p_name = r["pais"]
        paises_matrix.append({
            "pais": p_name,
            "flag": FLAGS.get(p_name, "🌎"),
            "n_total": int(r["n_total"]),
            "n_sal": int(r["n_sal"]),
            "cumple_n30": bool(r["cumple_n30"]),
            "med_usd": round(float(r["med_usd"]), 1) if pd.notna(r["med_usd"]) else None,
            "p25_usd": round(float(r["p25_usd"]), 1) if pd.notna(r["p25_usd"]) else None,
            "p75_usd": round(float(r["p75_usd"]), 1) if pd.notna(r["p75_usd"]) else None,
            "iqr_usd": round(float(r["iqr_usd"]), 1) if pd.notna(r["iqr_usd"]) else None,
            "med_clp": int(round(r["med_clp"])) if pd.notna(r["med_clp"]) else None,
            "ic95_mediana_inf_usd": round(float(r["ic95_mediana_inf_usd"]), 1) if pd.notna(r["ic95_mediana_inf_usd"]) else None,
            "ic95_mediana_sup_usd": round(float(r["ic95_mediana_sup_usd"]), 1) if pd.notna(r["ic95_mediana_sup_usd"]) else None,
            "tratamiento": str(r["tratamiento"]),
        })

    # 1.D Bandas Salariales y Saltos de Seniority
    # Construcción unificada desde datos limpios y calculados
    ORDEN_NIVELES = ["Trainee", "Junior", "Semi-Senior", "Senior", "Lead"]
    b_cl = b_cl[b_cl["seniority_nivel"].isin(ORDEN_NIVELES)].copy()
    b_cl["sort_idx"] = b_cl["seniority_nivel"].map(ORDEN_NIVELES.index)
    b_cl = b_cl.sort_values("sort_idx").drop(columns=["sort_idx"])

    b_rem = b_rem[b_rem["seniority_nivel"].isin(ORDEN_NIVELES)].copy()
    b_rem["sort_idx"] = b_rem["seniority_nivel"].map(ORDEN_NIVELES.index)
    b_rem = b_rem.sort_values("sort_idx").drop(columns=["sort_idx"])

    salarios_saltos = []
    # Chile Local
    vac_sal = vac[(vac["salario_valido_flag"] == 1) | (vac["salario_valido_flag"] == True)]
    vac_cl = vac_sal[vac_sal["alcance_geo"] == "Chile Local"]
    prev_med_cl = None
    for _, r in b_cl.iterrows():
        lvl = r["seniority_nivel"]
        sub_s = vac_cl[vac_cl["seniority_nivel"] == lvl]["salario_mensual_usd"]
        inf, sup = bootstrap_median_ci(sub_s)
        p25 = float(r["p25_usd"])
        med = float(r["mediana_usd"])
        p75 = float(r["p75_usd"])
        iqr = float(r.get("amplitud_p25_p75_usd", p75 - p25))
        salto_txt = "Base Inicial"
        if prev_med_cl is not None and prev_med_cl > 0:
            diff_pct = ((med - prev_med_cl) / prev_med_cl) * 100.0
            sign = "+" if diff_pct >= 0 else "−"
            salto_txt = f"{sign}{abs(diff_pct):.1f}%".replace(".", ",")
        prev_med_cl = med
        salarios_saltos.append({
            "ambito": "🇨🇱 Chile Local (Get on Board)",
            "alcance": "Chile Local",
            "nivel": lvl,
            "fuente": "Get on Board 2026",
            "n": int(r["n"]),
            "p25": int(round(p25)),
            "mediana": int(round(med)),
            "p75": int(round(p75)),
            "iqr": int(round(iqr)),
            "salto": salto_txt,
            "clp": int(round(r["mediana_clp_ref"])),
            "tlc": "✓ Válido (N ≥ 30)" if r["n"] >= 30 else f"Exploratorio (N < 30)",
            "ic95_mediana_inf_usd": round(float(inf), 1) if pd.notna(inf) else None,
            "ic95_mediana_sup_usd": round(float(sup), 1) if pd.notna(sup) else None,
        })
    # Remoto sin país declarado
    vac_rem = vac_sal[vac_sal["alcance_geo"] == "Remoto sin país declarado"]
    prev_med_rem = None
    for _, r in b_rem.iterrows():
        lvl = r["seniority_nivel"]
        sub_s = vac_rem[vac_rem["seniority_nivel"] == lvl]["salario_mensual_usd"]
        inf, sup = bootstrap_median_ci(sub_s)
        p25 = float(r["p25_usd"])
        med = float(r["mediana_usd"])
        p75 = float(r["p75_usd"])
        iqr = float(r.get("amplitud_p25_p75_usd", p75 - p25))
        salto_txt = "Base Inicial"
        if prev_med_rem is not None and prev_med_rem > 0:
            diff_pct = ((med - prev_med_rem) / prev_med_rem) * 100.0
            sign = "+" if diff_pct >= 0 else "−"
            salto_txt = f"{sign}{abs(diff_pct):.1f}%".replace(".", ",")
        prev_med_rem = med
        salarios_saltos.append({
            "ambito": "🌎 Remoto sin país declarado (Get on Board)",
            "alcance": "Remoto sin país declarado",
            "nivel": lvl,
            "fuente": "Get on Board 2026",
            "n": int(r["n"]),
            "p25": int(round(p25)),
            "mediana": int(round(med)),
            "p75": int(round(p75)),
            "iqr": int(round(iqr)),
            "salto": salto_txt,
            "clp": int(round(r["mediana_clp_ref"])),
            "tlc": "✓ Válido (N ≥ 30)" if r["n"] >= 30 else f"Exploratorio (N < 30)",
            "ic95_mediana_inf_usd": round(float(inf), 1) if pd.notna(inf) else None,
            "ic95_mediana_sup_usd": round(float(sup), 1) if pd.notna(sup) else None,
        })
    # Stack Overflow LatAm 2024
    so_sal = so[(so["salario_valido_flag"] == 1) | (so["salario_valido_flag"] == True)]
    tramos_order = [
        ("0-1 años (<2)", "0 a 1 años exp.", "Base Inicial"),
        ("2-4 años", "2 a 4 años exp.", None),
        ("5-9 años", "5 a 9 años exp.", None),
        ("10+ años", "10+ años exp.", None),
    ]
    prev_med_so = None
    for tramo_id, tramo_label, salto_txt in tramos_order:
        sub = so_sal[so_sal["tramo_experiencia"] == tramo_id]["salario_mensual_usd"]
        if len(sub) > 0:
            inf, sup = bootstrap_median_ci(sub)
            p25 = float(np.percentile(sub, 25))
            med = float(np.median(sub))
            p75 = float(np.percentile(sub, 75))
            if prev_med_so is not None and prev_med_so > 0:
                d = (med - prev_med_so) / prev_med_so * 100.0
                salto_txt = f"{'+' if d >= 0 else '−'}{abs(d):.1f}%".replace(".", ",")
            prev_med_so = med
            salarios_saltos.append({
                "ambito": "🌎 América Latina (19 Países)",
                "alcance": "América Latina (19 Países)",
                "nivel": tramo_label,
                "fuente": "Stack Overflow LatAm 2024",
                "n": int(len(sub)),
                "p25": int(round(p25)),
                "mediana": int(round(med)),
                "p75": int(round(p75)),
                "iqr": int(round(p75 - p25)),
                "salto": salto_txt,
                "clp": int(round(med * float(_c("dolar_observado_bcch", "val")))),
                "tlc": "✓ Válido (N ≥ 30)" if len(sub) >= 30 else "Exploratorio (N < 30)",
                "ic95_mediana_inf_usd": inf,
                "ic95_mediana_sup_usd": sup,
            })

    # Data Science Salaries (residentes en EE.UU.)
    dss = pd.read_csv(CLEAN_DIR / "DataScienceSalaries_2020_2024_20261111_v01_clean.csv")
    dss_us = dss[dss["employee_residence"] == "United States"]
    exp_order = [
        ("EN", "Entry-level/Junior", "Base EE.UU."),
        ("MI", "Mid/Semi-Senior", None),
        ("SE", "Senior", None),
        ("EX", "Executive/Lead", None),
    ]
    prev_med = None
    for code, label, salto_txt in exp_order:
        sub = dss_us[dss_us["experience_level"] == code]["salario_mensual_usd"]
        if len(sub) > 0:
            inf, sup = bootstrap_median_ci(sub)
            p25 = float(np.percentile(sub, 25))
            med = float(np.median(sub))
            p75 = float(np.percentile(sub, 75))
            salto_real = salto_txt
            if prev_med is not None and prev_med > 0:
                diff_pct = ((med - prev_med) / prev_med) * 100.0
                sign = "+" if diff_pct >= 0 else "−"
                salto_real = f"{sign}{abs(diff_pct):.1f}%".replace(".", ",")
            prev_med = med
            salarios_saltos.append({
                "ambito": "🇺🇸 Data Science Salaries, residentes en EE.UU.",
                "alcance": "Estados Unidos",
                "nivel": label,
                "fuente": "Data Science Salaries, residentes en EE.UU.",
                "n": int(len(sub)),
                "p25": int(round(p25)),
                "mediana": int(round(med)),
                "p75": int(round(p75)),
                "iqr": int(round(p75 - p25)),
                "salto": salto_real,
                "clp": int(round(med * float(_c("dolar_observado_bcch", "val")))),
                "tlc": "✓ Válido (N ≥ 30)" if len(sub) >= 30 else "Exploratorio (N < 30)",
                "ic95_mediana_inf_usd": inf,
                "ic95_mediana_sup_usd": sup,
            })

    df_saltos = pd.DataFrame(salarios_saltos)
    df_saltos.to_csv(DESC_DIR / "Bandas_Salariales_y_Saltos_Seniority.csv", index=False, encoding="utf-8")

    # 1.E Matriz de Validación de Integridad y Calidad
    n_so_sal_raw = int(so["salary_yearly_usd_raw"].notna().sum())
    pct_sin_salario = f"{100 - float(_c('gob_pct_con_salario', 'val')):.1f}%".replace(".", ",")
    validacion_matrix = [
        {
            "tipo": "1. Tipo de Datos (Data Type)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": "Coerción estricta de variables numéricas (salarios float, postulaciones int) y normalización tipográfica de cadenas de texto (skills, títulos, países).",
            "poblacion": f"{_c('total_registros_crudos')} registros crudos",
            "excluidos": "0 errores de tipo no resueltos",
            "resultado": "100% de esquemas tipados y compatibles en SQL/Python",
            "impacto": "Garantiza cálculos agregados matemáticamente consistentes sin coerciones silenciosas."
        },
        {
            "tipo": "2. Rango de Datos (Data Range)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": f"Filtro de plausibilidad económica: salarios mensuales >= {_c('salario_min_filtro_usd')} USD en GOB y anuales entre {_c('so_filtro_anual_min_usd')} y {_c('so_filtro_anual_max_usd')} USD en SO LatAm; anulación estricta de outliers espurios.",
            "poblacion": f"{_c('so_latam_total')} SO LatAm / {_c('gob_total_scope')} GOB",
            "excluidos": f"{int(_c('gob_salarios_raw', 'val')) - int(_c('gob_salarios_validos', 'val'))} vacantes GOB (<{_c('salario_min_filtro_usd')} USD) / {n_so_sal_raw - int(_c('so_latam_salarios_validos', 'val'))} respuestas SO (fuera del rango anual)",
            "resultado": f"{_c('gob_salarios_validos')} salarios válidos GOB (de {_c('gob_salarios_raw')}) / {_c('so_latam_salarios_validos')} salarios válidos SO (de {_miles(n_so_sal_raw)})",
            "impacto": "Previene distorsiones artificiales en la media aritmética y centra el análisis en la mediana."
        },
        {
            "tipo": "3. Restricciones de Dominio (Constraints)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": "Homologación a taxonomías finitas: Modalidad en [Híbrido, Presencial, Remoto Local, Remoto Total] y Seniority en [Junior, Semi-Senior, Senior, Lead, Trainee].",
            "poblacion": f"{_c('gob_total_scope')} vacantes / {_c('so_latam_total')} encuestados",
            "excluidos": "0 vacantes sin categoría estándar",
            "resultado": "100% registros categorizados bajo taxonomía estándar",
            "impacto": "Permite segmentación unívoca y comparabilidad de resultados entre plataformas."
        },
        {
            "tipo": "4. Consistencia Cruzada (Consistency)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": f"Verificación lógica: min_salary <= max_salary en cada registro salarial. Control cruzado de tasa cambiaria fija de referencia ({_c('dolar_observado_bcch')} CLP/USD).",
            "poblacion": f"{_c('gob_salarios_validos')} vacantes con salario GOB",
            "excluidos": "0 inconsistencias lógicas detectadas",
            "resultado": "100% de coherencia matemática en rangos salariales",
            "impacto": "Garantiza que ningún salario mínimo sobrepase al máximo ni genere rangos negativos."
        },
        {
            "tipo": "5. Completitud de Datos (Completeness)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": f"Identificación de nulos estructurales: el {pct_sin_salario} de las vacantes de Get on Board no publica salario explícito (patrón de asimetría informativa).",
            "poblacion": f"{_c('gob_total_scope')} vacantes GOB",
            "excluidos": "0 vacantes eliminadas por falta de salario",
            "resultado": "Bandera booleana 'salario_valido_flag' sin imputación forzada",
            "impacto": "Evita el sesgo de imputar salarios inventados a ofertas que legítimamente no lo publican."
        },
        {
            "tipo": "6. Unicidad e Integridad 1:N (Uniqueness)",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": "Deduplicación por clave primaria compuesta. Control riguroso de producto cartesiano en relaciones 1:N (vacantes vs múltiples tecnologías requeridas).",
            "poblacion": f"{_c('gob_total_scope')} vacantes ({_c('gob_habilidades_rows')} filas 1:N) / {_c('so_latam_total')} encuestados ({_c('so_tecnologias_rows')} filas 1:N)",
            "excluidos": "0 duplicaciones artificiales en agregaciones",
            "resultado": "Cálculo salarial ejecutado a nivel de entidad única",
            "impacto": "Previene el sesgo de sobredimensionar el salario promedio de vacantes con múltiples tecnologías."
        },
        {
            "tipo": "7. Protección de Datos y Privacidad",
            "ambito": "🇨🇱 Chile & 🌎 19 Países LatAm",
            "descripcion": "Exclusión y filtrado preventivo de datos de contacto o identificadores personales directos en los conjuntos analizados (Directiva Google Privacy & Data Ethics).",
            "poblacion": f"{_c('total_registros_crudos')} registros crudos",
            "excluidos": "100% identificadores personales purgados",
            "resultado": "Datos agregados sin datos personales identificables",
            "impacto": "Blindaje ético y legal total del repositorio público en GitHub y GitHub Pages."
        }
    ]
    pd.DataFrame(validacion_matrix).to_csv(DESC_DIR / "Matriz_Validacion_Integridad_Calidad.csv", index=False, encoding="utf-8")

    # 1.F Datasets complementarios
    df_q14 = pd.read_csv(RES_DIR / "resumen_q14_modalidad_x_seniority.csv")
    q14_list = df_q14.to_dict(orient="records")

    df_q15 = pd.read_csv(RES_DIR / "resumen_q15_tecnologia_x_seniority.csv")
    q15_list = df_q15.to_dict(orient="records")

    # Matriz TLC completa
    matriz_tlc_list = tlc.to_dict(orient="records")

    # Estructura del Explorador Consolidado
    explorador_dict = {
        "gob_vacantes": gob_vac_list,
        "paises_matrix": paises_matrix,
        "salarios_saltos": salarios_saltos,
        "validacion_matrix": validacion_matrix,
        "matriz_tlc": matriz_tlc_list,
        "q14_modalidad_x_seniority": q14_list,
        "q15_tecnologia_x_seniority": q15_list,
    }

    def clean_nans(obj):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        elif isinstance(obj, dict):
            return {k: clean_nans(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nans(v) for v in obj]
        return obj

    explorador_dict = clean_nans(explorador_dict)

    # Guardar en raíz y en descargas (idénticos)
    with open(BASE_DIR / "explorador_datasets.json", "w", encoding="utf-8") as f:
        json.dump(explorador_dict, f, ensure_ascii=False, indent=2)
    with open(DESC_DIR / "Explorador_Datasets_Consolidados.json", "w", encoding="utf-8") as f:
        json.dump(explorador_dict, f, ensure_ascii=False, indent=2)

    # 1.G Empaquetar Datos_Limpios_Completos_GitHub.zip (solo para GitHub; no es un dataset de Kaggle)
    zip_path = DESC_DIR / "Datos_Limpios_Completos_GitHub.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in [
            "GetOnBoard_Vacantes_2026_20261111_v01_clean.csv",
            "GetOnBoard_Habilidades_2026_20261111_v01_clean.csv",
            "StackOverflow_LatAm_2024_20261111_v01_clean.csv",
            "StackOverflow_Tecnologias_2024_20261111_v01_clean.csv",
            "DataScienceSalaries_2020_2024_20261111_v01_clean.csv",
            "INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv",
        ]:
            zf.write(CLEAN_DIR / fname, arcname=fname)
        zf.write(DESC_DIR / "Matriz_TLC_19_Paises_LatAm.csv", arcname="Matriz_TLC_19_Paises_LatAm.csv")
        zf.write(RES_DIR / "resumen_ic_diferencias.csv", arcname="resumen_ic_diferencias.csv")

    # 1.G-bis Celdas vacías de los archivos de GitHub: se comprueban contra scripts/celdas_vacias.json y se explican
    # en descargas/LEEME_Celdas_Vacias.md (el mismo registro explica el Excel de Tableau y las columnas de Kaggle)
    reg_vac = celdas_vacias.cargar()
    for f in sorted(DESC_DIR.glob("*.csv")):
        celdas_vacias.comprobar(pd.read_csv(f), reg_vac["archivos"].get(f.name, {}), f.name)
    with zipfile.ZipFile(zip_path) as zf:
        for n in zf.namelist():
            if n.endswith(".csv"):
                with zf.open(n) as fh:
                    celdas_vacias.comprobar(pd.read_csv(fh), reg_vac["archivos"].get(n, {}), f"{zip_path.name}/{n}")
    (DESC_DIR / "LEEME_Celdas_Vacias.md").write_text(celdas_vacias.guia_markdown(reg_vac), encoding="utf-8")

    # 1.H Paquete para Kaggle con agregados de Get on Board (R22)
    generar_paquete_kaggle()

    print("Descargas y explorador_datasets.json generados con éxito.")


def generar_paquete_kaggle():
    """Genera de forma reproducible el paquete de datos para Kaggle en descargas/kaggle_dataset/."""
    kaggle_dir = DESC_DIR / "kaggle_dataset"
    shutil.rmtree(kaggle_dir, ignore_errors=True)
    kaggle_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copias exactas de los 5 CSV limpios permitidos
    clean_files = [
        "StackOverflow_LatAm_2024_20261111_v01_clean.csv",
        "StackOverflow_Tecnologias_2024_20261111_v01_clean.csv",
        "DataScienceSalaries_2020_2024_20261111_v01_clean.csv",
        "INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv",
        "Matriz_TLC_19_Paises_LatAm.csv"
    ]
    for cf in clean_files:
        src = CLEAN_DIR / cf
        if not src.exists():
            src = DESC_DIR / cf
        shutil.copy2(src, kaggle_dir / cf)

    # 2. Agregados oficiales de Get on Board (sin PII, sin identificadores, N >= 5, sin min/max)
    gob_files = [
        ("resumen_p1_tecnologias_gob_vs_so.csv", "gob_agregado_tecnologias.csv", "Agregados de demanda laboral en Get on Board y adopción en Stack Overflow por tecnología (grupos con N >= 5)."),
        ("resumen_pub_bandas_chile_local.csv", "gob_agregado_bandas_chile_local.csv", "Bandas salariales agregadas (mediana, p25, p75) por nivel de experiencia en Chile Local (N >= 5, sin extremos mín/máx)."),
        ("resumen_pub_bandas_remoto_sin_pais.csv", "gob_agregado_bandas_remoto_sin_pais.csv", "Bandas salariales agregadas (mediana, p25, p75) por nivel de experiencia en Remoto sin país (N >= 5, sin extremos mín/máx)."),
        ("resumen_q12_modalidad_composicion_seniority.csv", "gob_agregado_modalidad.csv", "Composición porcentual agregada de niveles de seniority por modalidad de trabajo en Get on Board."),
        ("resumen_p3_salarios_modalidad_vs_ine.csv", "gob_agregado_modalidad_vs_ine.csv", "Medianas salariales agregadas por modalidad de trabajo comparadas contra la línea base nacional INE ESI 2025 (sin mín/máx)."),
        ("resumen_pub_ic_diferencias.csv", "gob_agregado_ic_diferencias.csv", "Intervalos de confianza bootstrap al 95% para diferencias de medianas salariales entre segmentos clave."),
        ("sql_q01_control_integridad_left_join.csv", "gob_agregado_control_integridad.csv", "Control de integridad relacional agregado y comparación de medias join 1:N sin duplicación.")
    ]

    descriptions = {
        "StackOverflow_LatAm_2024_20261111_v01_clean.csv": "Datos limpios de encuestados tech en 19 países de Latinoamérica (Stack Overflow 2024).",
        "StackOverflow_Tecnologias_2024_20261111_v01_clean.csv": "Relación normalizada 1:N de tecnologías adoptadas profesionalmente por desarrolladores de LatAm.",
        "DataScienceSalaries_2020_2024_20261111_v01_clean.csv": "Serie salarial internacional de roles analíticos y de ciencia de datos 2020-2024.",
        "INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv": "Línea base oficial de ingresos laborales en Chile según Encuesta Suplementaria de Ingresos (INE ESI 2025).",
        "Matriz_TLC_19_Paises_LatAm.csv": "Matriz de suficiencia muestral y medianas bootstrap de compensación en 19 países de América Latina."
    }

    for src_name, dst_name, desc in gob_files:
        df = pd.read_csv(RES_DIR / src_name)
        # Eliminar columnas de mínimo y máximo
        drop_cols = [c for c in df.columns if c.lower() in {"min_usd", "max_usd", "min_mensual_usd", "max_mensual_usd"}]
        if drop_cols:
            df = df.drop(columns=drop_cols)
        # Filtrar grupos con N < 5
        n_cols = [c for c in df.columns if c.lower() in {"n", "n_salarios_validos", "n_ofertas", "gob_n_ofertas", "n_total_salarios", "n_ofertas_con_salario_valido"}]
        for nc in n_cols:
            df = df[pd.to_numeric(df[nc], errors="coerce") >= 5]
        df.to_csv(kaggle_dir / dst_name, index=False, encoding="utf-8")
        descriptions[dst_name] = desc

    # 3. dataset-metadata.json generado desde la lista real de archivos con descriptores y tipos
    dict_path = BASE_DIR / "scripts" / "diccionario_columnas_kaggle.json"
    if not dict_path.exists():
        raise FileNotFoundError(f"No existe el diccionario de columnas en {dict_path}")
    with open(dict_path, "r", encoding="utf-8") as f:
        col_dict = json.load(f)

    def map_dtype(dtype) -> str:
        d = str(dtype).lower()
        if "int" in d:
            return "integer"
        elif "float" in d or "double" in d:
            return "number"
        elif "bool" in d:
            return "boolean"
        elif "date" in d:
            return "datetime"
        return "string"

    reg_vac = celdas_vacias.cargar()["archivos"]
    resources = []
    for f in sorted(kaggle_dir.iterdir()):
        if f.is_file() and f.suffix == ".csv":
            if f.name not in col_dict:
                raise ValueError(f"Archivo {f.name} no se encuentra en {dict_path.name}")
            df_sample = pd.read_csv(f)
            vac_arch = reg_vac.get(f.name, {})
            celdas_vacias.comprobar(df_sample, vac_arch, f.name)
            desc_archivo = col_dict[f.name].get("__archivo__", descriptions.get(f.name, "Dataset del estudio."))
            fields = []
            for col in df_sample.columns:
                if col == "__archivo__":
                    continue
                if col not in col_dict[f.name]:
                    raise ValueError(f"Columna '{col}' de {f.name} no se encuentra en {dict_path.name}")
                desc_col = col_dict[f.name][col]
                if col in vac_arch:  # la explicación de sus celdas vacías (scripts/celdas_vacias.json)
                    desc_col = f"{desc_col} {vac_arch[col]['texto']}"
                type_col = map_dtype(df_sample[col].dtype)
                fields.append({
                    "name": col,
                    "description": desc_col,
                    "type": type_col
                })
            resources.append({
                "path": f.name,
                "description": desc_archivo,
                "schema": {
                    "fields": fields
                }
            })

    meta = {
        "title": "Mercado Tech Chile y LatAm 2024-2026",
        "id": "manuelyanezorellana/mercado-tech-chile-y-latam-2024-2026",
        "licenses": [{"name": "ODbL-1.0"}],
        "description": (
            "Los archivos gob_agregado_* son estadísticas agregadas calculadas por el autor a partir de la API pública "
            "de Get on Board (fuente: Get on Board, getonbrd.com, corte 2026-11-10); no se redistribuyen las ofertas individuales. "
            "El paquete incluye además datos limpios de encuestas y fuentes de referencia: Stack Overflow Developer Survey 2024 "
            "(ODbL-1.0), Data Science Salaries 2020-2024 (CC0-1.0), estadísticas oficiales del INE ESI 2025 (Ley N° 17.374) y la matriz "
            "regional de suficiencia muestral de 19 países de Latinoamérica (DATA_LICENSES.md). "
            "Celdas vacías: no son datos perdidos. La descripción de cada columna dice en qué filas quedan vacías y por qué."
        ),
        "resources": resources
    }

    with open(kaggle_dir / "dataset-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Paquete para Kaggle generado con éxito en {kaggle_dir} ({len(resources)} archivos CSV + metadata).")


if __name__ == "__main__":
    generar_explorador_y_descargas()
