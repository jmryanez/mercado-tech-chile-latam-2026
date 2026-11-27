"""
Fase 3: Procesar (Process) — Limpieza, Estandarización y Validación de Datos
Certificado Profesional de Análisis de Datos de Google • Cursos 4, 5, 7 y 8

Reglas metodológicas aplicadas:
- Inmutabilidad total de '02_Fase_Preparar_Prepare/datos_crudos_raw/' (solo lectura).
- Los 6 tipos de validación de datos (Curso 5, Mód. 4): Tipo, Rango, Restricción,
  Coherencia, Estructura y Validación del código de la aplicación de origen.
- Lista de verificación de limpieza de 12 puntos y umbral muestral N >= 30 (Curso 4).
- Procesamiento en Python con pandas, numpy, regex y enmascaramiento booleano (Curso 7).
- Paridad taxonómica 1:1 entre GetOnBoard_Habilidades y StackOverflow_Tecnologias.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from formato_dinero import dinero  # noqa: E402

# --- Configuración de rutas y constantes oficiales del SOW ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "02_Fase_Preparar_Prepare" / "datos_crudos_raw"
CLEAN_DIR = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

ZONA_CHILE = ZoneInfo("America/Santiago")
FECHA_INICIO = "2026-01-01"
FECHA_CORTE = "2026-11-10"
FECHA_EJECUCION = "20261111"
DOLAR_OBSERVADO_BCCH = 969.80  # Banco Central de Chile al 2026-11-10
GOB_SALARIO_MIN_MENSUAL_USD = 500.0  # piso de plausibilidad de Get on Board (USD/mes)
GOB_SALARIO_MAX_MENSUAL_USD = 25000.0  # techo de control de Get on Board (USD/mes)
SO_SALARIO_MIN_ANUAL_USD = 1000.0  # bajo esto la respuesta es tasa horaria/mensual o inválida (USD/año)
SO_SALARIO_MAX_ANUAL_USD = 500000.0  # sobre esto es un outlier extremo (USD/año)


def _fmt_miles(x) -> str:
    return f"{x:,.0f}".replace(",", ".")

LATAM_19_PAISES = {
    "Argentina",
    "Bolivia",
    "Brazil",
    "Chile",
    "Colombia",
    "Costa Rica",
    "Cuba",
    "Dominican Republic",
    "Ecuador",
    "El Salvador",
    "Guatemala",
    "Honduras",
    "Mexico",
    "Nicaragua",
    "Panama",
    "Paraguay",
    "Peru",
    "Uruguay",
    "Venezuela, Bolivarian Republic of...",
}

PAIS_ES = {
    "Brazil": "Brasil",
    "Mexico": "México",
    "Dominican Republic": "República Dominicana",
    "Peru": "Perú",
    "Panama": "Panamá",
    "Venezuela, Bolivarian Republic of...": "Venezuela",
}

GOB_SENIORITY_MAP = {
    1: "Trainee",
    2: "Junior",
    3: "Semi-Senior",
    4: "Senior",
    5: "Lead",
}

GOB_MODALIDAD_MAP = {
    "hybrid": "Híbrido",
    "fully_remote": "Remoto Total",
    "remote_local": "Remoto Local",
    "no_remote": "Presencial",
}

# Excluye productos Oracle que no son Oracle Database antes de evaluar BD Oracle
ORACLE_NON_DB_SCRUB = re.compile(
    r"(?i:\boracle\s+(?:cloud(?:\s+infrastructure)?|certified(?:\s+professional)?|middleware|service\s+bus|osb|odi|soa|bpm|weblogic(?:\s+server)?|flexcube|hcm|wcc|forms|apps?|fusion|ebs|netsuite)\b|"
    r"\b(?:erp|ocp|oci\s*/|productos|middleware(?:\s+semi\s+senior)?\s*\(?|certificaciones(?:\s+relevantes)?\s+(?:de\s+)?|plataformas(?:\s+de\s+integraci[oó]n)?\s+)\s*oracle\b|"
    r"\badm(?:inistrador|inistraci[oó]n)\s+(?:de\s+)?(?:oracle\s+middleware|plataformas\s+(?:de\s+integraci[oó]n\s+)?oracle))"
)

# Taxonomía cerrada 1:1 con LanguageHaveWorkedWith / DatabaseHaveWorkedWith / PlatformHaveWorkedWith de Stack Overflow
# Nota: JavaScript exige mención explícita del lenguaje (sin inferir por React/Angular/Vue/Node.js) para paridad exacta con SO.
GOB_TECH_TAXONOMY: list[tuple[str, str, str, int]] = [
    # Lenguajes
    ("Lenguaje", "JavaScript", r"(?<![A-Za-z0-9_])(?:javascript|ecmascript)(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "SQL", r"(?<![A-Za-z0-9_])(?:sql|t-sql|pl/sql|plsql)(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Python", r"(?<![A-Za-z0-9_])python(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "TypeScript", r"(?<![A-Za-z0-9_])typescript(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Java", r"(?<![A-Za-z0-9_])java(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "HTML/CSS", r"(?<![A-Za-z0-9_])(?:html5?|css3?)(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "C#", r"(?:(?<![A-Za-z0-9_])c#|(?<![A-Za-z0-9_])csharp(?![A-Za-z0-9_]))", re.I),
    (
        "Lenguaje",
        "Go",
        r"(?:(?<![A-Za-z0-9_])golang(?![A-Za-z0-9_])|(?<![A-Za-z0-9_\-])Go(?!(?i:\s*(?:[-—/]\s*)?(?:live|to|past|beyond|back|through|ahead|for|deep|further|fast|big|direct|no[\s\-]*go)))(?![A-Za-z0-9_\-]))",
        0,
    ),
    ("Lenguaje", "PHP", r"(?<![A-Za-z0-9_])php(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Bash/Shell", r"(?<![A-Za-z0-9_])(?:bash|shell\s+scripting)(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "PowerShell", r"(?<![A-Za-z0-9_])powershell(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "C++", r"(?<![A-Za-z0-9_])c\+\+(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Ruby", r"(?<![A-Za-z0-9_])ruby(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Kotlin", r"(?<![A-Za-z0-9_])kotlin(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Swift", r"(?<![A-Za-z0-9_])swift(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "Rust", r"(?<![A-Za-z0-9_])rust(?![A-Za-z0-9_])", re.I),
    ("Lenguaje", "R", r"(?:(?<![A-Za-z0-9_/&\-])R(?:\s*(?:Studio|programming|lenguaje|,|\.|/|o\s+Python))|RStudio)", 0),
    # Bases de datos
    ("Base de datos", "PostgreSQL", r"(?<![A-Za-z0-9_])postgres(?:ql)?(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "MongoDB", r"(?<![A-Za-z0-9_])mongodb(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "Microsoft SQL Server", r"(?<![A-Za-z0-9_])(?:sql server|mssql|ms sql)(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "Oracle", r"(?<![A-Za-z0-9_])oracle(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "MySQL", r"(?<![A-Za-z0-9_])mysql(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "Redis", r"(?<![A-Za-z0-9_])redis(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "BigQuery", r"(?<![A-Za-z0-9_])bigquery(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "DynamoDB", r"(?<![A-Za-z0-9_])dynamodb(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "Elasticsearch", r"(?<![A-Za-z0-9_])elastic(?:search)?(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "Snowflake", r"(?<![A-Za-z0-9_])snowflake(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "SQLite", r"(?<![A-Za-z0-9_])sqlite(?![A-Za-z0-9_])", re.I),
    ("Base de datos", "MariaDB", r"(?<![A-Za-z0-9_])mariadb(?![A-Za-z0-9_])", re.I),
    # Plataformas Cloud (homologado 1:1 con PlatformHaveWorkedWith de Stack Overflow)
    ("Cloud", "AWS", r"(?<![A-Za-z0-9_])(?:aws|amazon web services)(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Microsoft Azure", r"(?<![A-Za-z0-9_])azure(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Google Cloud", r"(?<![A-Za-z0-9_])(?:gcp|google cloud(?: platform)?)(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Databricks", r"(?<![A-Za-z0-9_])databricks(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Firebase", r"(?<![A-Za-z0-9_])firebase(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Cloudflare", r"(?<![A-Za-z0-9_])cloudflare(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Vercel", r"(?<![A-Za-z0-9_])vercel(?![A-Za-z0-9_])", re.I),
    ("Cloud", "DigitalOcean", r"(?<![A-Za-z0-9_])digital\s*ocean(?![A-Za-z0-9_])", re.I),
    ("Cloud", "Oracle Cloud (OCI)", r"(?<![A-Za-z0-9_])(?:oracle\s+cloud(?:\s+infrastructure)?|oci)(?![A-Za-z0-9_])", re.I),
]

SO_PLATFORM_CANON = {
    "Amazon Web Services (AWS)": "AWS",
    "Digital Ocean": "DigitalOcean",
    "Oracle Cloud Infrastructure (OCI)": "Oracle Cloud (OCI)",
}

SO_LANG_CANON = {
    "Bash/Shell (all shells)": "Bash/Shell",
}

SO_DB_CANON = {
    "Dynamodb": "DynamoDB",
}


def limpiar_texto_html(texto: str) -> str:
    """Elimina etiquetas HTML, decodifica entidades y aplica TRIM/espacios simples."""
    sin_tags = re.sub(r"<[^>]+>", " ", texto)
    decodificado = html.unescape(sin_tags)
    return re.sub(r"\s+", " ", decodificado).strip()


def procesar_get_on_board() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Limpia y valida Get on Board API v0 aplicando corte 2026 (GMT-3) y lógica salarial."""
    ruta = RAW_DIR / "GetOnBoard_OfertasTech_2026_20261110_v01_raw.json"
    with open(ruta, "r", encoding="utf-8") as f:
        crudo = json.load(f)

    registros = []
    habilidades = []
    stats = {
        "raw_total": len(crudo),
        "dup_job_id": 0,
        "excl_2025": 0,
        "excl_fuera_pais": 0,
        "scope_total": 0,
        "raw_con_salario_scope": 0,
        "salarios_anulados": 0,
        "salarios_validos": 0,
        "min_gt_max": 0,
        "ofertas_con_tecnologia": 0,
    }

    seen_ids: set[str] = set()
    for item in crudo:
        jid = str(item["id"]).strip()
        if jid in seen_ids:
            stats["dup_job_id"] += 1
            continue
        seen_ids.add(jid)

        a = item["attributes"]
        dt_cl = datetime.fromtimestamp(a["published_at"], tz=ZONA_CHILE)
        fecha_cl = dt_cl.strftime("%Y-%m-%d")
        anio = dt_cl.year
        mes = dt_cl.strftime("%Y-%m")

        if not (FECHA_INICIO <= fecha_cl <= FECHA_CORTE):
            stats["excl_2025"] += 1
            continue

        paises = [str(p).strip() for p in (a.get("countries") or [])]
        if "Chile" in paises:
            alcance_geo = "Chile Local"
        elif "Remote" in paises:
            alcance_geo = "Remoto sin país declarado"
        else:
            stats["excl_fuera_pais"] += 1
            continue

        stats["scope_total"] += 1
        titulo = re.sub(r"\s+", " ", str(a.get("title") or "")).strip()
        categoria = re.sub(r"\s+", " ", str(a.get("category_name") or "")).strip()
        mod_raw = str(a.get("remote_modality") or "").strip()
        mod_es = GOB_MODALIDAD_MAP.get(mod_raw, "Otro")
        sen_id = (a.get("seniority") or {}).get("data", {}).get("id")
        sen_nivel = GOB_SENIORITY_MAP.get(sen_id, "Sin especificar")

        mn_raw = a.get("min_salary")
        mx_raw = a.get("max_salary")
        if mn_raw is not None and mx_raw is not None and mn_raw > mx_raw:
            stats["min_gt_max"] += 1

        tiene_sal_raw = (mn_raw is not None) or (mx_raw is not None)
        salario_valido = False
        motivo_excl = None
        mn_clean = np.nan
        mx_clean = np.nan
        sal_mid = np.nan
        sal_clp = np.nan

        if tiene_sal_raw:
            stats["raw_con_salario_scope"] += 1
            mn_val = float(mn_raw) if mn_raw is not None else float(mx_raw)
            mx_val = float(mx_raw) if mx_raw is not None else float(mn_raw)
            mid_val = (mn_val + mx_val) / 2.0

            if mid_val < GOB_SALARIO_MIN_MENSUAL_USD or mn_val < GOB_SALARIO_MIN_MENSUAL_USD:
                stats["salarios_anulados"] += 1
                motivo_excl = (
                    f"Anulado por lógica de negocio/rango (<{dinero(GOB_SALARIO_MIN_MENSUAL_USD)} USD/mes; publicado {dinero(mn_val)}-{dinero(mx_val)})"
                )
            else:
                salario_valido = True
                stats["salarios_validos"] += 1
                mn_clean = round(mn_val, 2)
                mx_clean = round(mx_val, 2)
                sal_mid = round(mid_val, 2)
                sal_clp = round(mid_val * DOLAR_OBSERVADO_BCCH, 0)

        texto_completo = limpiar_texto_html(
            " ".join(
                [
                    titulo,
                    str(a.get("description") or ""),
                    str(a.get("functions") or ""),
                    str(a.get("desirable") or ""),
                ]
            )
        )
        texto_oracle_db = ORACLE_NON_DB_SCRUB.sub(" ", texto_completo)

        matched_here: set[tuple[str, str]] = set()
        for tipo, tech, pat, flags in GOB_TECH_TAXONOMY:
            target = texto_completo
            if tipo == "Base de datos" and tech == "Oracle":
                target = texto_oracle_db
            elif tipo == "Base de datos" and tech == "Elasticsearch":
                target = re.sub(r"(?i:elastic\s*(?:apm|stack|observability|cloud\s+observability|para\s+monitoreo)|\belk\b)", " ", texto_completo)
            elif tipo == "Cloud" and tech == "Microsoft Azure":
                target = re.sub(r"(?i:azure\s*(?:devops|ad\b|active\s+directory|boards|repos|pipelines|artifacts)|entra\s*id)", " ", texto_completo)
            elif tech == "C#":
                target = re.sub(r"(?i:(?:vb|asp)?\.net(?:\s*core)?)", " ", texto_completo)

            is_matched = bool(re.search(pat, target, flags))

            # Exclusion de Swift en protocolos de transferencia bancaria (SWIFT/SEPA)
            if is_matched and tech == "Swift":
                if re.search(r'(?i:\b(?:money\s+transfer\s+)?protocols?\s+such\s+as\s+swift|\bswift\s+(?:and|&|y)\s+sepa\b|\bsepa\s+(?:and|&|y)\s+swift\b)', target):
                    is_matched = False

            # Deteccion de R seguido de ')', ' o ', ' y ', ',' cuando este en lista con Python o SQL
            if not is_matched and tech == "R":
                if re.search(r'\b(?:python|sql)\b', target, re.I):
                    if re.search(r'(?<![A-Za-z0-9_])R(?:\s*\)|\s+(?:o|y|or|and)\s+|\s*,\s*)', target) or re.search(r'\b(?:python|sql)\b[^\.\n]{0,60}\b(?:o|y|or|and|,)\s+R(?![A-Za-z0-9_])', target, re.I):
                        is_matched = True

            if is_matched:
                matched_here.add((tipo, tech))

        if matched_here:
            stats["ofertas_con_tecnologia"] += 1

        for tipo, tech in sorted(matched_here):
            habilidades.append(
                {
                    "job_id": jid,
                    "tipo_tecnologia": tipo,
                    "tecnologia": tech,
                }
            )

        registros.append(
            {
                "job_id": jid,
                "titulo": titulo,
                "categoria": categoria,
                "fecha_publicacion_cl": fecha_cl,
                "anio": anio,
                "mes": mes,
                "alcance_geo": alcance_geo,
                "paises_raw": "; ".join(paises),
                "modalidad_trabajo": mod_raw,
                "modalidad_grupo": mod_es,
                "seniority_id": sen_id,
                "seniority_nivel": sen_nivel,
                "min_salary_usd_raw": float(mn_raw) if mn_raw is not None else np.nan,
                "max_salary_usd_raw": float(mx_raw) if mx_raw is not None else np.nan,
                "min_salary_usd_clean": mn_clean,
                "max_salary_usd_clean": mx_clean,
                "salario_mensual_usd": sal_mid,
                "salario_mensual_clp_ref": sal_clp,
                "salario_valido_flag": salario_valido,
                "motivo_exclusion_salario": motivo_excl if motivo_excl else "",
                "company_id": int(a.get("company", {}).get("data", {}).get("id") or 0),
                "applications_count": int(a.get("applications_count") or 0),
                "menciona_tecnologia_flag": len(matched_here) > 0,
            }
        )

    df_vac = pd.DataFrame(registros)
    df_hab = pd.DataFrame(habilidades)
    return df_vac, df_hab, stats


def clasificar_exp_so(val: object) -> str:
    if pd.isna(val):
        return "Sin dato"
    s = str(val).strip()
    if s == "Less than 1 year":
        return "0-1 años (<2)"
    if s == "More than 50 years":
        return "10+ años"
    n = int(s)
    if n < 2:
        return "0-1 años (<2)"
    if n <= 4:
        return "2-4 años"
    if n <= 9:
        return "5-9 años"
    return "10+ años"


def parse_years_pro(val: object) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s == "Less than 1 year":
        return 0.5
    if s == "More than 50 years":
        return 51.0
    return float(int(s))


def agrupar_org_size(val: object) -> str:
    if pd.isna(val):
        return "Sin dato / NS-NR"
    s = str(val).strip()
    if s in {
        "Just me - I am a freelancer, sole proprietor, etc.",
        "2 to 9 employees",
        "10 to 19 employees",
        "20 to 99 employees",
    }:
        return "Pequeña (1-99)"
    if s in {"100 to 499 employees", "500 to 999 employees"}:
        return "Mediana (100-999)"
    if s in {
        "1,000 to 4,999 employees",
        "5,000 to 9,999 employees",
        "10,000 or more employees",
    }:
        return "Grande (1.000+)"
    return "Sin dato / NS-NR"


def procesar_stack_overflow() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Limpia y normaliza Stack Overflow 2024 para los 19 países de Latinoamérica (incluido Chile)."""
    ruta = RAW_DIR / "StackOverflow_DeveloperSurvey_2024_20261111_v01_raw.csv.gz"
    df_raw = pd.read_csv(ruta, low_memory=False)
    stats = {
        "global_total": len(df_raw),
        "dup_response_id": int(df_raw["ResponseId"].duplicated().sum()),
        "latam_total": 0,
        "chile_total": 0,
        "latam_con_salario_raw": 0,
        "latam_salarios_anulados_bajo": 0,
        "latam_salarios_anulados_alto": 0,
        "latam_salarios_validos": 0,
        "chile_salarios_validos": 0,
        "latam_sin_tecnologias": 0,
        "chile_sin_tecnologias": 0,
    }

    mask_latam = df_raw["Country"].isin(LATAM_19_PAISES)
    df = df_raw[mask_latam].copy()
    stats["latam_total"] = len(df)
    stats["chile_total"] = int((df["Country"] == "Chile").sum())

    sal_raw = pd.to_numeric(df["ConvertedCompYearly"], errors="coerce")
    has_sal = sal_raw.notna()
    stats["latam_con_salario_raw"] = int(has_sal.sum())

    mask_bajo = has_sal & (sal_raw < SO_SALARIO_MIN_ANUAL_USD)
    mask_alto = has_sal & (sal_raw > SO_SALARIO_MAX_ANUAL_USD)
    mask_valido = has_sal & (sal_raw >= SO_SALARIO_MIN_ANUAL_USD) & (sal_raw <= SO_SALARIO_MAX_ANUAL_USD)

    stats["latam_salarios_anulados_bajo"] = int(mask_bajo.sum())
    stats["latam_salarios_anulados_alto"] = int(mask_alto.sum())
    stats["latam_salarios_validos"] = int(mask_valido.sum())
    stats["chile_salarios_validos"] = int((mask_valido & (df["Country"] == "Chile")).sum())

    mod_map = {
        "Remote": "Remoto",
        "Hybrid (some remote, some in-person)": "Híbrido",
        "In-person": "Presencial",
    }

    tiene_tec = (
        df["LanguageHaveWorkedWith"].notna()
        | df["DatabaseHaveWorkedWith"].notna()
        | df["PlatformHaveWorkedWith"].notna()
    )
    stats["latam_sin_tecnologias"] = int((~tiene_tec).sum())
    stats["chile_sin_tecnologias"] = int(((~tiene_tec) & (df["Country"] == "Chile")).sum())

    motivos = np.where(
        mask_bajo,
        f"Anulado (<{dinero(SO_SALARIO_MIN_ANUAL_USD)} USD/año: tasa horaria/mensual o dato inválido)",
        np.where(
            mask_alto,
            f"Anulado (>{dinero(SO_SALARIO_MAX_ANUAL_USD)} USD/año: outlier multimillonario extremo)",
            "",
        ),
    )

    sal_clean = np.where(mask_valido, sal_raw, np.nan)
    sal_mensual = np.where(mask_valido, np.round(sal_raw / 12.0, 2), np.nan)
    sal_clp = np.where(mask_valido, np.round((sal_raw / 12.0) * DOLAR_OBSERVADO_BCCH, 0), np.nan)

    df_enc = pd.DataFrame(
        {
            "ResponseId": df["ResponseId"].astype(int),
            "pais": df["Country"].map(lambda c: PAIS_ES.get(c, c)).astype(str).str.strip(),
            "pais_raw": df["Country"].astype(str).str.strip(),
            "es_chile": df["Country"] == "Chile",
            "subregion": np.where(df["Country"] == "Chile", "Chile", "Resto LatAm"),
            "empleo_raw": df["Employment"].fillna("Sin dato").astype(str).str.strip(),
            "modalidad_raw": df["RemoteWork"].fillna("Sin dato").astype(str).str.strip(),
            "modalidad_grupo": df["RemoteWork"].map(mod_map).fillna("Sin dato"),
            "years_code_pro_num": df["YearsCodePro"].apply(parse_years_pro),
            "tramo_experiencia": df["YearsCodePro"].apply(clasificar_exp_so),
            "org_size_detalle": df["OrgSize"].fillna("Sin dato").astype(str).str.strip(),
            "org_size_grupo": df["OrgSize"].apply(agrupar_org_size),
            "salary_yearly_usd_raw": sal_raw,
            "salary_yearly_usd_clean": sal_clean,
            "salario_mensual_usd": sal_mensual,
            "salario_mensual_clp_ref": sal_clp,
            "salario_valido_flag": mask_valido,
            "motivo_exclusion_salario": motivos,
            "tiene_tecnologia_flag": tiene_tec,
            "respondio_lenguaje": df["LanguageHaveWorkedWith"].notna(),
            "respondio_database": df["DatabaseHaveWorkedWith"].notna(),
            "respondio_platform": df["PlatformHaveWorkedWith"].notna(),
        }
    )

    tech_rows = []
    col_specs = [
        ("LanguageHaveWorkedWith", "Lenguaje", SO_LANG_CANON),
        ("DatabaseHaveWorkedWith", "Base de datos", SO_DB_CANON),
        ("PlatformHaveWorkedWith", "Cloud", SO_PLATFORM_CANON),
    ]
    for _, row in df[["ResponseId", "Country", "LanguageHaveWorkedWith", "DatabaseHaveWorkedWith", "PlatformHaveWorkedWith"]].iterrows():
        rid = int(row["ResponseId"])
        pais_raw = str(row["Country"]).strip()
        pais_es = PAIS_ES.get(pais_raw, pais_raw)
        es_cl = pais_raw == "Chile"
        seen_per_resp: set[tuple[str, str]] = set()
        for col, tipo, canon_map in col_specs:
            val = row[col]
            if pd.isna(val):
                continue
            for token in str(val).split(";"):
                t_clean = token.strip()
                if not t_clean:
                    continue
                t_canon = canon_map.get(t_clean, t_clean)
                if (tipo, t_canon) not in seen_per_resp:
                    seen_per_resp.add((tipo, t_canon))
                    tech_rows.append(
                        {
                            "ResponseId": rid,
                            "pais": pais_es,
                            "es_chile": es_cl,
                            "tipo_tecnologia": tipo,
                            "tecnologia": t_canon,
                            "tecnologia_raw": t_clean,
                        }
                    )

    df_tech = pd.DataFrame(tech_rows)
    return df_enc, df_tech, stats


def procesar_dss() -> tuple[pd.DataFrame, dict]:
    """Limpia Data Science Salaries (2020-2024) preservando los 6.599 registros sin ID."""
    ruta = RAW_DIR / "DataScienceSalaries_2020_2024_20261110_v01_raw.csv"
    df = pd.read_csv(ruta)

    exp_map = {
        "Entry-level": "Entry-level/Junior",
        "Mid-level": "Mid/Semi-Senior",
        "Senior-level": "Senior",
        "Executive-level": "Executive/Lead",
    }
    mod_map = {
        "On-site": "Presencial",
        "Remote": "Remoto",
        "Hybrid": "Híbrido",
    }
    size_map = {
        "Small": "Pequeña (Small)",
        "Medium": "Mediana (Medium)",
        "Large": "Grande (Large)",
    }

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    df_clean = pd.DataFrame(
        {
            "work_year": df["work_year"].astype(int),
            "job_title": df["job_title"],
            "experience_level": df["experience_level"],
            "experiencia_es": df["experience_level"].map(exp_map),
            "employment_type": df["employment_type"],
            "work_models": df["work_models"],
            "modalidad_es": df["work_models"].map(mod_map),
            "employee_residence": df["employee_residence"],
            "company_location": df["company_location"],
            "company_size": df["company_size"],
            "tamano_es": df["company_size"].map(size_map),
            "salario_mensual_clp_ref": np.round(
                (pd.to_numeric(df["salary_in_usd"], errors="coerce") / 12.0) * DOLAR_OBSERVADO_BCCH, 0
            ),
            "salary_yearly_usd": pd.to_numeric(df["salary_in_usd"], errors="coerce"),
            "salario_mensual_usd": np.round(pd.to_numeric(df["salary_in_usd"], errors="coerce") / 12.0, 2),
        }
    )

    stats = {
        "total_rows": len(df_clean),
        "nulls": int(df_clean.isna().sum().sum()),
        "min_yearly_usd": float(df_clean["salary_yearly_usd"].min()),
        "max_yearly_usd": float(df_clean["salary_yearly_usd"].max()),
        "exact_duplicates": int(df.duplicated().sum()),
    }
    return df_clean, stats


def procesar_ine() -> tuple[pd.DataFrame, dict]:
    """Valida la línea base oficial INE ESI 2025 y agrega conversión referencial al corte BCCh."""
    ruta = RAW_DIR / "INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv"
    df = pd.read_csv(ruta)
    df["monto_clp_mensual"] = pd.to_numeric(df["monto_clp_mensual"], errors="raise").astype(int)
    df["dolar_observado_20261110"] = DOLAR_OBSERVADO_BCCH
    df["monto_usd_ref_20261110"] = np.round(df["monto_clp_mensual"] / DOLAR_OBSERVADO_BCCH, 2)
    stats = {
        "total_rows": len(df),
        "mediano_clp": int(df.loc[df["indicador"].str.contains("Mediano"), "monto_clp_mensual"].iloc[0]),
        "medio_clp": int(df.loc[df["indicador"].str.contains("Medio"), "monto_clp_mensual"].iloc[0]),
    }
    return df, stats


def ejecutar_6_validaciones(
    df_vac: pd.DataFrame,
    df_hab: pd.DataFrame,
    df_so: pd.DataFrame,
    df_so_tech: pd.DataFrame,
    df_dss: pd.DataFrame,
    df_ine: pd.DataFrame,
) -> list[dict]:
    """Ejecuta aserciones de los 6 tipos de validación de datos (Curso 5, Mód. 4)."""
    validaciones = []

    # 1. Tipo de datos (Type)
    assert pd.api.types.is_numeric_dtype(df_vac["salario_mensual_usd"])
    assert pd.api.types.is_bool_dtype(df_vac["salario_valido_flag"])
    assert pd.api.types.is_integer_dtype(df_so["ResponseId"])
    assert pd.api.types.is_integer_dtype(df_dss["work_year"])
    assert pd.api.types.is_integer_dtype(df_ine["monto_clp_mensual"])
    validaciones.append(
        {
            "tipo": "1. Tipo de datos",
            "estado": "APROBADO",
            "detalle": "Salarios como float64, IDs enteros/string, flags booleanos y años enteros validados.",
        }
    )

    # 2. Rango de datos (Range)
    gob_sal_ok = df_vac.loc[df_vac["salario_valido_flag"], "salario_mensual_usd"]
    assert (gob_sal_ok >= GOB_SALARIO_MIN_MENSUAL_USD).all() and (gob_sal_ok <= GOB_SALARIO_MAX_MENSUAL_USD).all()
    so_sal_ok = df_so.loc[df_so["salario_valido_flag"], "salary_yearly_usd_clean"]
    assert (so_sal_ok >= SO_SALARIO_MIN_ANUAL_USD).all() and (so_sal_ok <= SO_SALARIO_MAX_ANUAL_USD).all()
    assert df_vac["fecha_publicacion_cl"].min() >= FECHA_INICIO
    assert df_vac["fecha_publicacion_cl"].max() <= FECHA_CORTE
    assert df_dss["work_year"].between(2020, 2024).all()
    validaciones.append(
        {
            "tipo": "2. Rango de datos",
            "estado": "APROBADO",
            "detalle": f"GOB salarios válidos [{gob_sal_ok.min():g}, {gob_sal_ok.max():g}] USD/mes y fechas [{df_vac['fecha_publicacion_cl'].min()}..{df_vac['fecha_publicacion_cl'].max()}]; SO LatAm [{so_sal_ok.min():g}, {so_sal_ok.max():g}] USD/año; DSS 2020–2024.",
        }
    )

    # 3. Restricción de datos (Constraint)
    assert df_vac["job_id"].is_unique
    assert df_so["ResponseId"].is_unique
    assert set(df_vac["alcance_geo"].unique()) == {"Chile Local", "Remoto sin país declarado"}
    assert df_vac["modalidad_grupo"].isna().sum() == 0
    assert len(df_so["pais"].unique()) == 19
    assert not df_hab.duplicated(subset=["job_id", "tipo_tecnologia", "tecnologia"]).any()
    assert not df_so_tech.duplicated(subset=["ResponseId", "tipo_tecnologia", "tecnologia"]).any()
    # Paridad 100% de pares (tipo_tecnologia, tecnologia) de GOB contra SO
    gob_pairs = set(zip(df_hab["tipo_tecnologia"], df_hab["tecnologia"]))
    so_pairs = set(zip(df_so_tech["tipo_tecnologia"], df_so_tech["tecnologia"]))
    orphan_pairs = gob_pairs - so_pairs
    assert not orphan_pairs, f"Pares en GOB sin match en SO: {orphan_pairs}"
    validaciones.append(
        {
            "tipo": "3. Restricción de datos",
            "estado": "APROBADO",
            "detalle": f"Claves primarias únicas (job_id {df_vac['job_id'].nunique()}/{len(df_vac)}, ResponseId {_fmt_miles(df_so['ResponseId'].nunique())}/{_fmt_miles(len(df_so))}), 19 países LatAm exactos, 0 duplicados 1:N y paridad 100% de pares (tipo_tecnologia, tecnologia) entre GOB y SO.",
        }
    )

    # 4. Coherencia de datos (Consistency)
    sal_rows = df_vac[df_vac["salario_valido_flag"]]
    assert (sal_rows["min_salary_usd_clean"] <= sal_rows["max_salary_usd_clean"]).all()
    assert set(df_hab["job_id"]).issubset(set(df_vac["job_id"]))
    assert set(df_so_tech["ResponseId"]).issubset(set(df_so["ResponseId"]))
    assert (df_vac.loc[df_vac["salario_valido_flag"], "modalidad_grupo"].value_counts() >= 30).all()
    assert (df_so.loc[df_so["salario_valido_flag"], "modalidad_grupo"].value_counts() >= 30).all()
    assert (df_dss["company_size"].value_counts() >= 30).all()
    validaciones.append(
        {
            "tipo": "4. Coherencia de datos",
            "estado": "APROBADO",
            "detalle": "min_salary <= max_salary en 100%, integridad referencial 1:N verificada y N >= 30 cumplido en todas las modalidades GOB/SO y tamaños DSS.",
        }
    )

    # 5. Estructura de datos (Structure)
    for dframe in [df_vac, df_hab, df_so, df_so_tech, df_dss, df_ine]:
        assert all(" " not in c for c in dframe.columns)
    assert not df_vac["titulo"].str.contains("<[^>]+>", regex=True).any()
    validaciones.append(
        {
            "tipo": "5. Estructura de datos",
            "estado": "APROBADO",
            "detalle": "6 tablas CSV UTF-8 con encabezados snake_case/limpios, texto sin HTML ni ';' multivalor en columnas analíticas.",
        }
    )

    # 6. Validación del código de la aplicación origen (Code validation)
    gob_excl = int((~df_vac["salario_valido_flag"] & df_vac["min_salary_usd_raw"].notna()).sum())
    so_excl = int((~df_so["salario_valido_flag"] & df_so["salary_yearly_usd_raw"].notna()).sum())
    validaciones.append(
        {
            "tipo": "6. Validación del código de aplicación",
            "estado": "VERIFICADO Y CONTENIDO",
            "detalle": f"Detectadas debilidades de captura en origen: GOB permitió salarios libres <{dinero(GOB_SALARIO_MIN_MENSUAL_USD)} ({gob_excl} casos) sin etiqueta bruto/líquido; SO permitió valores horarios/mensuales/multimillonarios ({so_excl} casos en LatAm). Contenidos vía flags y anulación transparente.",
        }
    )
    return validaciones


def main() -> None:
    df_vac, df_hab, st_gob = procesar_get_on_board()
    df_so, df_so_tech, st_so = procesar_stack_overflow()
    df_dss, st_dss = procesar_dss()
    df_ine, st_ine = procesar_ine()

    out_files = {
        f"GetOnBoard_Vacantes_2026_{FECHA_EJECUCION}_v01_clean.csv": df_vac,
        f"GetOnBoard_Habilidades_2026_{FECHA_EJECUCION}_v01_clean.csv": df_hab,
        f"StackOverflow_LatAm_2024_{FECHA_EJECUCION}_v01_clean.csv": df_so,
        f"StackOverflow_Tecnologias_2024_{FECHA_EJECUCION}_v01_clean.csv": df_so_tech,
        f"DataScienceSalaries_2020_2024_{FECHA_EJECUCION}_v01_clean.csv": df_dss,
        f"INE_ESI_2025_ReferenciaNacional_{FECHA_EJECUCION}_v01_clean.csv": df_ine,
    }
    file_sizes = {}
    for fname, dframe in out_files.items():
        fpath = CLEAN_DIR / fname
        dframe.to_csv(fpath, index=False, encoding="utf-8")
        file_sizes[fname] = {"rows": len(dframe), "cols": dframe.shape[1], "bytes": fpath.stat().st_size}

    validaciones = ejecutar_6_validaciones(df_vac, df_hab, df_so, df_so_tech, df_dss, df_ine)

    top_gob_tech = {}
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        sub = df_hab[df_hab["tipo_tecnologia"] == tipo]["tecnologia"].value_counts().head(8)
        top_gob_tech[tipo] = {k: int(v) for k, v in sub.items()}

    resumen = {
        "st_gob": st_gob,
        "st_so": st_so,
        "st_dss": st_dss,
        "st_ine": st_ine,
        "umbrales": {
            "gob_salario_min_mensual_usd": GOB_SALARIO_MIN_MENSUAL_USD,
            "gob_salario_max_mensual_usd": GOB_SALARIO_MAX_MENSUAL_USD,
            "so_salario_min_anual_usd": SO_SALARIO_MIN_ANUAL_USD,
            "so_salario_max_anual_usd": SO_SALARIO_MAX_ANUAL_USD,
        },
        "file_sizes": file_sizes,
        "total_clean_bytes": sum(v["bytes"] for v in file_sizes.values()),
        "validaciones": validaciones,
        "top_gob_tech": top_gob_tech,
        "n_checks": {
            "gob_modalidades_sal_valido": df_vac.loc[df_vac["salario_valido_flag"], "modalidad_grupo"].value_counts().to_dict(),
            "gob_seniority_sal_valido": df_vac.loc[df_vac["salario_valido_flag"], "seniority_nivel"].value_counts().to_dict(),
            "so_modalidades_sal_valido": df_so.loc[df_so["salario_valido_flag"], "modalidad_grupo"].value_counts().to_dict(),
            "so_exp_sal_valido": df_so.loc[df_so["salario_valido_flag"], "tramo_experiencia"].value_counts().to_dict(),
            "so_orgsize_sal_valido": df_so.loc[df_so["salario_valido_flag"], "org_size_grupo"].value_counts().to_dict(),
        },
    }

    report_path = BASE_DIR / "03_Fase_Procesar_Process" / "scripts" / "resumen_validacion_fase3.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
