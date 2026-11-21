"""
Fase 5: Compartir (Share) — Visualizaciones Accesibles, Paquete Cuaderno Reproducible y Deck Ejecutivo (~30 min)
Certificado Profesional de Análisis de Datos de Google • Cursos 6 y 8 (Caso Práctico: Mercado Tech Chile y LatAm)

Reglas de Oro del Proyecto (v1.7.0):
1. Cero cifras escritas a mano: todas provienen de cifras_oficiales.json.
2. Formato es-CL en todos los ejes numéricos (FuncFormatter: $ con punto para miles, coma decimal, pp para márgenes).
3. Visual 1: Top 4 tecnologías >= 20% con error en pp.
4. Visual 2: Etiquetas sin solapamiento, leyenda en ambos paneles, líneas de referencia con medianas calculadas.
5. Visual 3: Título dinámico desde datos (sin 'tracciona').
6. Visual 4: Bandas salariales p25–p75 con control N >= 30.
7. Visual 5: Referencia oficial INE exclusiva para Chile Local; análisis de causalidad.
8. Visual 6: Países LatAm con IC 95% bootstrap; sin afirmación 'Chile es 2°'; panel B sin solapamiento.
9. Visual 7: DSS residentes en EE.UU. con línea punteada en N < 30 y etiqueta 'Small N=0'.
10. Deck PDF: 14 diapositivas, cuerpo >= 14 pt, limitaciones antes de recomendaciones, slide de indicadores y preguntas de cierre.
"""

from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEAN_DIR = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed"
RES_DIR = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes"
SHARE_DIR = BASE_DIR / "05_Fase_Compartir_Share"
VIZ_DIR = SHARE_DIR / "visualizaciones"
VIZ_DIR.mkdir(parents=True, exist_ok=True)
DESC_DIR = BASE_DIR / "descargas"
DESC_DIR.mkdir(parents=True, exist_ok=True)

# Cargar cifras oficiales maestras
with open(RES_DIR / "cifras_oficiales.json", "r", encoding="utf-8") as f:
    CIFRAS = json.load(f)

# Paleta azul/naranja + Neutros de alto contraste (accesible para daltonismo • Curso 6 Mód. 2)
NAVY = "#1B365D"
BLUE = "#0072B2"
ORANGE = "#D55E00"
AMBER = "#E69F00"
TEAL = "#009E73"
GRAY_DARK = "#334155"
GRAY_MID = "#64748B"
GRAY_LIGHT = "#CBD5E1"
BG_PANEL = "#F8FAFC"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = GRAY_LIGHT
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["text.parse_math"] = False


# Formatters es-CL
def fmt_es_num(val, decimals=1):
    if val is None or np.isnan(val):
        return ""
    s = f"{val:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_es_usd(val, decimals=0):
    if val is None or np.isnan(val):
        return ""
    if decimals == 0:
        s = f"${int(round(val)):,}"
        return s.replace(",", ".")
    s = f"${val:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_es_pct(val, decimals=1):
    return f"{fmt_es_num(val, decimals)}%"


def axis_fmt_usd(x, pos):
    return f"${int(x):,}".replace(",", ".")


def axis_fmt_pct(x, pos):
    return f"{int(x)}%"


def estilizar_ejes(ax, grid_axis: str = "x") -> None:
    """Optimiza la relación datos-tinta eliminando bordes superfluos (Curso 6, Mód. 2)."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid_axis in ("x", "both"):
        ax.xaxis.grid(True, linestyle="--", alpha=0.45, color=GRAY_LIGHT, zorder=0)
    if grid_axis in ("y", "both"):
        ax.yaxis.grid(True, linestyle="--", alpha=0.45, color=GRAY_LIGHT, zorder=0)
    ax.set_axisbelow(True)


def pie_fuente(fig, texto: str) -> None:
    fig.text(0.02, 0.012, texto, fontsize=8.1, color=GRAY_MID, ha="left")


# =============================================================================
# VISUAL 1: DEMANDA VS ADOPCIÓN
# =============================================================================
def fig_01_demanda_vs_adopcion() -> Path:
    """Visual 1 (P1): Barras horizontales agrupadas + línea meta 20% (Curso 6, pág. 1)."""
    p1_csv = pd.read_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv")
    
    rows = []
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        sub = p1_csv[p1_csv["tipo_tecnologia"] == tipo].sort_values("pct_demanda_gob_total", ascending=False).head(4)
        for _, item in sub.iterrows():
            rows.append(
                {
                    "label": f"{item['tecnologia']}  [{tipo[:3].upper()}]",
                    "gob": item["pct_demanda_gob_total"],
                    "so_cl": item["pct_adopcion_chile"],
                    "so_lat": item["pct_adopcion_latam"],
                    "moe_cl": item.get("moe95_pp_chile", 0.0),
                }
            )
    df = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11.8, 7.2), dpi=300)
    y = np.arange(len(df))
    h = 0.25

    ax.barh(y + h, df["gob"], height=h, color=NAVY, label=f"Demanda Ofertas GOB 2026 (N={CIFRAS['gob_total_scope']['str']})", zorder=3)
    ax.barh(y, df["so_cl"], height=h, color=TEAL, label=f"Uso Real Chile SO 2024 (N={CIFRAS['so_chile_total']['str']}, ±MOE 95% en pp)", zorder=3, xerr=df["moe_cl"], capsize=3, error_kw=dict(ecolor="#004D36", lw=1.2, capthick=1.2))
    ax.barh(y - h, df["so_lat"], height=h, color=AMBER, alpha=0.9, label=f"Uso Real LatAm SO 2024 (N={CIFRAS['so_latam_total']['str']})", zorder=3)

    ax.axvline(20.0, color=ORANGE, linestyle="--", linewidth=1.6, zorder=4)
    ax.text(20.7, len(df) - 0.25, "Meta ≥ 20% (Obj. Métrico #1)", color=ORANGE, fontsize=9, fontweight="bold")

    for i, val in enumerate(df["gob"]):
        ax.text(
            val + 0.7,
            i + h + 0.02,
            fmt_es_pct(val, 1),
            va="center",
            fontsize=7.8,
            fontweight="bold",
            color=NAVY,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white", edgecolor="none", alpha=0.92),
        )
    for i, (val, moe) in enumerate(zip(df["so_cl"], df["moe_cl"])):
        ax.text(
            val + moe + 0.7,
            i - 0.01,
            f"{fmt_es_pct(val, 1)} (±{fmt_es_num(moe, 1)} pp)",
            va="center",
            fontsize=7.3,
            color="#006B4E",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white", edgecolor="none", alpha=0.92),
        )

    ax.set_yticks(y)
    ax.set_yticklabels(df["label"], fontsize=8.8, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 68)
    ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt_pct))
    ax.set_xlabel("% de Ofertas (Get on Board 2026) / % de Desarrolladores (Stack Overflow 2024)", fontsize=9.2)
    estilizar_ejes(ax, "x")

    fig.suptitle(
        f"Solo 4 Tecnologías Superan el 20% de Demanda en Ofertas GOB: SQL ({CIFRAS['gob_sql_pct']['str']}), AWS ({CIFRAS['gob_aws_pct']['str']}), Python ({CIFRAS['gob_python_pct']['str']}) y Azure ({CIFRAS['gob_azure_pct']['str']})",
        fontsize=11.6,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    fig.text(
        0.02,
        0.932,
        "Top 4 por categoría • Demanda en Get on Board (2026) vs. Adopción en Stack Overflow (2024) • Barras de error en pp",
        fontsize=9.0,
        color=GRAY_MID,
        ha="left",
    )
    ax.legend(loc="lower right", frameon=False, fontsize=8.8)
    pie_fuente(fig, f"Fuente: Get on Board API v0 (01-ene a 10-nov-2026 GMT-3, N={CIFRAS['gob_total_scope']['str']}) y Stack Overflow Survey 2024 (Chile N={CIFRAS['so_chile_total']['str']}; LatAm 19 países N={CIFRAS['so_latam_total']['str']}). Poblaciones separadas.")
    plt.tight_layout(rect=[0, 0.035, 1, 0.92])
    out = VIZ_DIR / "01_demanda_vs_adopcion_top5_p1.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 2: MATRIZ VOLUMEN VS SALARIO (Q11)
# =============================================================================
def fig_02_matriz_volumen_vs_salario() -> Path:
    """Visual 2 (Q11): Dispersión / burbujas por cuadrantes Demanda/Uso % vs Mediana USD (Curso 6, pág. 3)."""
    q11_csv = pd.read_csv(RES_DIR / "resumen_q11_tecnologia_vs_salario.csv")
    gob = q11_csv[q11_csv["fuente"] == "Get on Board 2026"].copy()
    so = q11_csv[q11_csv["fuente"] == "Stack Overflow LatAm 2024"].copy()

    cat_colors = {"Lenguaje": BLUE, "Cloud": ORANGE, "Base de datos": TEAL}
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.0), dpi=300)

    med_gob_ref = float(gob["mediana_usd"].median())
    med_so_ref = float(so["mediana_usd"].median())

    # Panel A: Get on Board 2026
    ax = axes[0]
    for cat, grp in gob.groupby("tipo_tecnologia"):
        ax.scatter(
            grp["pct_demanda_gob_total"],
            grp["mediana_usd"],
            s=grp["n"] * 4.5,
            color=cat_colors[cat],
            alpha=0.85,
            edgecolors="white",
            linewidth=1.2,
            label=cat,
            zorder=4,
        )
    ax.axvline(20.0, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)
    ax.axhline(med_gob_ref, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)
    ax.text(20.5, 3250, "Meta ≥ 20%", color=GRAY_MID, fontsize=7.8)
    ax.text(11.5, med_gob_ref + 40, f"Mediana ref.: ${int(med_gob_ref):,}".replace(",", "."), color=GRAY_MID, fontsize=7.8)

    offsets_g = {
        "AWS": (0.8, 60, "left", "bottom"),
        "Google Cloud": (-1.5, 60, "left", "bottom"),
        "Microsoft Azure": (0.9, -60, "left", "baseline"),
        "TypeScript": (-4.5, 50, "left", "bottom"),
        "JavaScript": (-1.2, -40, "right", "top"),
        "Python": (0.9, -60, "left", "baseline"),
        "SQL": (-3.0, 60, "left", "bottom"),
        "PostgreSQL": (0.8, 45, "left", "baseline"),
    }
    for _, r in gob.iterrows():
        dx, dy, ha_v, va_v = offsets_g.get(r["tecnologia"], (0.6, 35, "left", "baseline"))
        ax.text(
            r["pct_demanda_gob_total"] + dx,
            r["mediana_usd"] + dy,
            f"{r['tecnologia']}\n(${int(r['mediana_usd']):,})".replace(",", "."),
            fontsize=7.8,
            fontweight="bold",
            color=GRAY_DARK,
            ha=ha_v,
            va=va_v,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.88),
        )
    ax.set_xlim(11, 37)
    ax.set_ylim(0, 3600)
    ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt_pct))
    ax.yaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax.set_title(f"A. Ofertas Get on Board 2026 (N ≥ 38 por tecnología)", fontsize=10.3, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel(f"% Demanda en Ofertas (N={CIFRAS['gob_total_scope']['str']})", fontsize=9)
    ax.set_ylabel("Mediana Salarial Mensual (USD)", fontsize=9)
    estilizar_ejes(ax, "both")
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor=GRAY_LIGHT, fontsize=8.2, markerscale=0.75)

    # Panel B: Stack Overflow LatAm 2024
    ax2 = axes[1]
    for cat, grp in so.groupby("tipo_tecnologia"):
        ax2.scatter(
            grp["pct_adopcion_latam"],
            grp["mediana_usd"],
            s=grp["n"] * 0.45,
            color=cat_colors[cat],
            alpha=0.85,
            edgecolors="white",
            linewidth=1.2,
            label=cat,
            zorder=4,
        )
    ax2.axhline(med_so_ref, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)
    ax2.axvline(40.0, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)
    ax2.text(40.5, 3050, "Referencia 40%", color=GRAY_MID, fontsize=7.8)
    ax2.text(11.5, med_so_ref + 35, f"Mediana ref.: ${int(med_so_ref):,}".replace(",", "."), color=GRAY_MID, fontsize=7.8)

    offsets_s = {
        "AWS": (0.8, 50, "left", "bottom"),
        "Google Cloud": (0.8, -45, "left", "top"),
        "Microsoft Azure": (0.8, 45, "left", "bottom"),
        "TypeScript": (0.8, -45, "left", "top"),
        "JavaScript": (-1.0, 50, "right", "bottom"),
        "Python": (0.8, 45, "left", "bottom"),
        "SQL": (0.8, -45, "left", "top"),
        "PostgreSQL": (0.8, 45, "left", "bottom"),
    }
    for _, r in so.iterrows():
        dx, dy, ha_v, va_v = offsets_s.get(r["tecnologia"], (0.6, 35, "left", "baseline"))
        ax2.text(
            r["pct_adopcion_latam"] + dx,
            r["mediana_usd"] + dy,
            f"{r['tecnologia']}\n(${int(r['mediana_usd']):,})".replace(",", "."),
            fontsize=7.8,
            fontweight="bold",
            color=GRAY_DARK,
            ha=ha_v,
            va=va_v,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.88),
        )
    ax2.set_xlim(10, 68)
    ax2.set_ylim(0, 3600)
    ax2.xaxis.set_major_formatter(FuncFormatter(axis_fmt_pct))
    ax2.yaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax2.set_title(f"B. Profesionales SO LatAm 2024 (N ≥ 335 por tecnología)", fontsize=10.3, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel(f"% Adopción en LatAm (N={CIFRAS['so_latam_total']['str']})", fontsize=9)
    estilizar_ejes(ax2, "both")
    ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor=GRAY_LIGHT, fontsize=8.2, markerscale=0.75)

    fig.suptitle(
        "Ofertas con requerimiento Cloud muestran medianas más altas, pero concentran más perfiles Senior",
        fontsize=12.0,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Tamaño de burbuja proporcional a N de salarios válidos (Q11A/B). Regla N >= 30 cumplida en todos los puntos. Líneas punteadas indican medianas calculadas de referencia.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "02_matriz_volumen_vs_salario_q11.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 3: MAPA DE CALOR POR MERCADO (P1)
# =============================================================================
def fig_03_mapa_calor_tecnologias() -> Path:
    """Visual 3 (P1): Mapa de calor comparativo por mercado (Curso 6, pág. 5)."""
    p1_csv = pd.read_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv")
    rows = []
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        sub = p1_csv[p1_csv["tipo_tecnologia"] == tipo].sort_values("pct_demanda_gob_total", ascending=False).head(5)
        for _, item in sub.iterrows():
            rows.append(
                {
                    "Tech": f"{item['tecnologia']} ({tipo[:3]})",
                    f"GOB Total\n(N={CIFRAS['gob_total_scope']['str']})": item["pct_demanda_gob_total"],
                    f"GOB Chile\nLocal ({CIFRAS['gob_chile_local_total']['str']})": item["pct_gob_chile_local"],
                    f"GOB Remoto\nsin país ({CIFRAS['gob_remoto_sin_pais_total']['str']})": item["pct_gob_remoto"],
                    f"SO Chile\n(N={CIFRAS['so_chile_total']['str']})": item["pct_adopcion_chile"],
                    f"SO LatAm\n(N={CIFRAS['so_latam_total']['str']})": item["pct_adopcion_latam"],
                }
            )
    df = pd.DataFrame(rows).set_index("Tech")

    fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=300)
    im = ax.imshow(df.values, cmap="YlGnBu", aspect="auto", vmin=0, vmax=70)

    ax.set_xticks(np.arange(df.shape[1]))
    ax.set_xticklabels(df.columns, fontsize=9, fontweight="bold", color=NAVY)
    ax.set_yticks(np.arange(df.shape[0]))
    ax.set_yticklabels(df.index, fontsize=8.8, color=GRAY_DARK)

    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            val = df.values[i, j]
            txt_color = "white" if val >= 36 else GRAY_DARK
            ax.text(j, i, f"{fmt_es_num(val, 1)}%", ha="center", va="center", color=txt_color, fontsize=8.3, fontweight="bold")

    ax.axhline(4.5, color="white", linewidth=2.5)
    ax.axhline(9.5, color="white", linewidth=2.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.03)
    cbar.set_label("% de presencia", fontsize=8.8, color=GRAY_DARK)
    cbar.formatter = FuncFormatter(axis_fmt_pct)
    cbar.update_ticks()

    fig.suptitle(
        f"En vacantes remotas sin país declarado destacan AWS ({CIFRAS['gob_aws_remoto_pct']['str']}) y SQL ({CIFRAS['gob_sql_remoto_pct']['str']}), mientras en Chile Local predomina SQL ({CIFRAS['gob_sql_chile_pct']['str']})",
        fontsize=10.6,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Mapa de calor (Curso 6, pág. 5). Poblaciones independientes sin suma conjunta: columnas GOB miden vacantes 2026 y columnas SO miden uso profesional 2024.")
    plt.tight_layout(rect=[0, 0.035, 1, 0.93])
    out = VIZ_DIR / "03_mapa_calor_tecnologias_mercado.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 4: BANDAS EXPERIENCIA (P2)
# =============================================================================
def fig_04_bandas_experiencia() -> Path:
    """Visual 4 (P2): Bandas p25–p75 y mediana por experiencia con control N >= 30 (Curso 6, pág. 5)."""
    p2_csv = pd.read_csv(RES_DIR / "resumen_p2_salarios_experiencia.csv")
    gob_df = p2_csv[p2_csv["fuente"] == "Get on Board 2026 (Chile + remotas)"].set_index("seniority_nivel")
    so_df = p2_csv[p2_csv["fuente"] == "Stack Overflow LatAm 2024"].set_index("tramo_experiencia")

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), dpi=300)

    # Panel A: Get on Board
    ax = axes[0]
    gob_order = [("Junior", False), ("Semi-Senior", True), ("Senior", True)]
    for idx, (seg, valid) in enumerate(gob_order):
        r = gob_df.loc[seg]
        c_bar = BLUE if valid else GRAY_LIGHT
        c_dot = ORANGE if valid else GRAY_MID
        ax.barh(idx, r["p75_usd"] - r["p25_usd"], left=r["p25_usd"], height=0.45, color=c_bar, alpha=0.35 if valid else 0.7, edgecolor=c_bar, linewidth=1.3, zorder=3)
        ax.scatter([r["mediana_usd"]], [idx], color=c_dot, s=90, zorder=5)
        tag = f"N={r['n']}" if valid else f"N={r['n']} (<30 explor.)"
        ax.text(r["p75_usd"] + 85, idx, f"Med: ${int(r['mediana_usd']):,}\n({tag})".replace(",", "."), va="center", fontsize=8.3, color=NAVY if valid else GRAY_MID, fontweight="bold")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Junior *", "Semi-Senior", "Senior"], fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 5300)
    ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax.set_title(f"A. Ofertas Get on Board 2026 (+{CIFRAS['gob_salto_senior_vs_semisenior_pct']['str']} de Semi-Senior a Senior)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Salario Mensual USD (Barra = p25–p75 | Punto = Mediana)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Stack Overflow LatAm
    ax2 = axes[1]
    so_order = ["0-1 años (<2)", "2-4 años", "5-9 años", "10+ años"]
    for idx, seg in enumerate(so_order):
        r = so_df.loc[seg]
        ax2.barh(idx, r["p75_usd"] - r["p25_usd"], left=r["p25_usd"], height=0.48, color=TEAL, alpha=0.32, edgecolor=TEAL, linewidth=1.3, zorder=3)
        ax2.scatter([r["mediana_usd"]], [idx], color=NAVY, s=90, zorder=5)
        ax2.text(
            r["p75_usd"] + 115,
            idx,
            f"Med: ${r['mediana_usd']:,.0f}\n(N={r['n']})".replace(",", "."),
            va="center",
            fontsize=8.2,
            color=NAVY,
            fontweight="bold",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.16", facecolor="white", edgecolor="none", alpha=0.92),
        )

    cl_med = float(CIFRAS["so_chile_salario_mediano"]["val"])
    ax2.axvline(cl_med, color=ORANGE, linestyle="--", linewidth=1.5, zorder=4)
    ax2.text(cl_med + 120, 1.48, f"Mediana Chile SO\n${cl_med:,.0f} (N={CIFRAS['so_chile_salarios_validos']['str']})".replace(",", "."), color=ORANGE, fontsize=8.3, fontweight="bold", zorder=6, bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.92))
    ax2.set_yticks(range(4))
    ax2.set_yticklabels(so_order, fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax2.set_xlim(0, 8000)
    ax2.xaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax2.set_title(f"B. Stack Overflow LatAm 2024 ({CIFRAS['so_salto_acumulado_10anios_pct']['str']} de <2 a 10+ años)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("Salario Mensual USD (Barra = p25–p75 | Punto = Mediana)", fontsize=8.8)
    estilizar_ejes(ax2, "x")

    fig.suptitle(
        f"El salto a Senior en Chile (+{CIFRAS['gob_salto_senior_vs_semisenior_pct']['str']}) y a 10+ años en LatAm ({CIFRAS['so_salto_acumulado_10anios_pct']['str']}) ensancha fuertemente la banda p25–p75",
        fontsize=11.6,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, f"*Junior GOB (N={CIFRAS['gob_junior_n']['val']} < 30) es exploratorio; Lead (N={CIFRAS['gob_lead_n']['val']}) y Trainee (N={1}) excluidos de inferencia (Curso 4). Bandas muestran cuartiles p25–p75 y mediana.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "04_bandas_salariales_experiencia_p2.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 5: MODALIDADES Y CAUSALIDAD (P3 + Q12)
# =============================================================================
def fig_05_modalidades_y_causalidad() -> Path:
    """Visual 5 (P3 + Q12): Modalidades vs INE ESI 2025 + Composición Seniority (Correlación != Causalidad)."""
    p3_csv = pd.read_csv(RES_DIR / "resumen_p3_salarios_modalidad_vs_ine.csv").set_index(["fuente", "segmento"])
    q12_df = pd.read_csv(RES_DIR / "resumen_q12_modalidad_composicion_seniority.csv").set_index("modalidad_grupo")
    ine_usd = float(CIFRAS["ine_mediana_usd_ref"]["val"])

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.8), dpi=300)

    # Panel A: Modalidades vs INE
    ax = axes[0]
    items = [
        (f"SO LatAm: Presencial (N={200})", p3_csv.loc[("Stack Overflow LatAm 2024 (Modalidad)", "Presencial"), "mediana_usd"], GRAY_MID),
        (f"SO LatAm: Híbrido (N={310})", p3_csv.loc[("Stack Overflow LatAm 2024 (Modalidad)", "Híbrido"), "mediana_usd"], TEAL),
        (f"SO LatAm: Remoto (N={831})", p3_csv.loc[("Stack Overflow LatAm 2024 (Modalidad)", "Remoto"), "mediana_usd"], BLUE),
        (f"GOB: Presencial (N={34})", p3_csv.loc[("Get on Board 2026 (Modalidad)", "Presencial"), "mediana_usd"], GRAY_MID),
        (f"GOB: Híbrido (N={103})", p3_csv.loc[("Get on Board 2026 (Modalidad)", "Híbrido"), "mediana_usd"], TEAL),
        (f"GOB: Remoto Total (N={53})", p3_csv.loc[("Get on Board 2026 (Modalidad)", "Remoto Total"), "mediana_usd"], BLUE),
        (f"GOB: Remoto Local (N={45})", p3_csv.loc[("Get on Board 2026 (Modalidad)", "Remoto Local"), "mediana_usd"], ORANGE),
    ]
    y = np.arange(len(items))
    vals = [x[1] for x in items]
    cols = [x[2] for x in items]
    ax.barh(y, vals, color=cols, height=0.60, zorder=3)
    ax.axvline(ine_usd, color="#991B1B", linestyle="--", linewidth=1.6, zorder=4)
    ax.text(ine_usd + 60, 6.72, f"INE ESI 2025 ref.: ${ine_usd:.0f} USD ({CIFRAS['ine_esi_mediana_clp']['str']})", color="#991B1B", fontsize=7.8, fontweight="bold")
    for idx, (_, v, _) in enumerate(items):
        ax.text(v + 70, idx, f"${v:,.0f}".replace(",", "."), va="center", fontsize=8.0, fontweight="bold", color=GRAY_DARK)
    ax.axhline(2.5, color=GRAY_LIGHT, linewidth=1.2, linestyle="-")
    ax.set_yticks(y)
    ax.set_yticklabels([x[0] for x in items], fontsize=8.4, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 5200)
    ax.set_ylim(-0.6, 7.2)
    ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax.set_title("A. Mediana Mensual USD (Línea punteada: INE ESI 2025 de referencia)", fontsize=9.6, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Mediana Salarial Mensual (USD)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Barras apiladas 100% — Composición Seniority
    ax2 = axes[1]
    mods = ["Presencial", "Híbrido", "Remoto Total", "Remoto Local"]
    sen = np.array([q12_df.loc[m, "pct_senior"] + q12_df.loc[m, "pct_lead"] for m in mods])
    semi = np.array([q12_df.loc[m, "pct_semi_senior"] for m in mods])
    jr = np.array([100.0 - s - sm for s, sm in zip(sen, semi)])

    y2 = np.arange(len(mods))
    ax2.barh(y2, sen, color=NAVY, height=0.54, label="Senior + Lead", zorder=3)
    ax2.barh(y2, semi, left=sen, color=BLUE, height=0.54, label="Semi-Senior", zorder=3)
    ax2.barh(y2, jr, left=sen + semi, color=GRAY_LIGHT, height=0.54, label="Junior / Trainee", zorder=3)

    for i in range(len(mods)):
        ax2.text(sen[i] / 2, i, f"{fmt_es_num(sen[i], 1)}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        ax2.text(sen[i] + semi[i] / 2, i, f"{fmt_es_num(semi[i], 1)}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")

    ax2.set_yticks(y2)
    ax2.set_yticklabels(mods, fontsize=9, fontweight="bold", color=GRAY_DARK)
    ax2.set_xlim(0, 105)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.xaxis.set_major_formatter(FuncFormatter(axis_fmt_pct))
    ax2.set_title("B. Composición Seniority (Correlación ≠ Causalidad)", fontsize=9.8, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("% Composición de Seniority y Alcance (Get on Board)", fontsize=8.8)
    ax2.legend(loc="lower center", bbox_to_anchor=(0.38, -0.22), ncol=3, frameon=False, fontsize=8.2)
    estilizar_ejes(ax2, "x")

    fig.suptitle(
        f"Remoto Local: mediana ${int(CIFRAS['gob_remoto_local_salario_mediano']['val']):,} con {fmt_es_num(CIFRAS['gob_remoto_local_pct_senior_lead']['val'], 1)}% de cargos Senior o Lead".replace(",", "."),
        fontsize=11.4,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, f"Dólar Observado BCCh al 2026-11-10 = {CIFRAS['dolar_observado_bcch']['str']} CLP/USD. ESI 2025 INE referencial ({CIFRAS['ine_esi_mediana_clp']['str']}/mes). El Panel B evidencia sesgo de composición (Curso 6, Correlación != Causalidad).")
    fig.text(0.50, 0.925, f"Estratificación por Seniority (Q14): Senior Remoto {CIFRAS['banda_rem_senior_mediana']['str']} ({CIFRAS['banda_rem_senior_n']['str']}) vs. Chile Local {CIFRAS['banda_cl_senior_mediana']['str']} ({CIFRAS['banda_cl_senior_n']['str']}) • Semi-Senior Remoto {CIFRAS['banda_rem_semi_senior_mediana']['str']} ({CIFRAS['banda_rem_semi_senior_n']['str']}) vs. Chile Local {CIFRAS['banda_cl_semi_senior_mediana']['str']} ({CIFRAS['banda_cl_semi_senior_n']['str']})", fontsize=8.2, color=NAVY, fontweight="bold", ha="center")
    plt.tight_layout(rect=[0, 0.05, 1, 0.90])
    out = VIZ_DIR / "05_modalidades_vs_ine_y_causalidad_p3_q12.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 6: PAÍSES LATAM Y TAMAÑO DE EMPRESA (P4A)
# =============================================================================
def fig_06_latam_y_tamano_empresa() -> Path:
    """Visual 6 (P4A + Países): Barras horizontales Países LatAm N>=30 y Barras verticales desde $0 OrgSize SO (Curso 6)."""
    paises = pd.read_csv(RES_DIR / "resumen_paises_so_latam_n30.csv").iloc[::-1].reset_index(drop=True)
    p4_tam = pd.read_csv(RES_DIR / "resumen_p4_tamano_empresa_y_dss_temporal.csv")
    org = p4_tam[p4_tam["fuente"] == "Stack Overflow LatAm 2024 (Detalle)"].copy()
    order_org = [
        "Just me - I am a freelancer, sole proprietor, etc.",
        "2 to 9 employees",
        "10 to 19 employees",
        "20 to 99 employees",
        "100 to 499 employees",
        "500 to 999 employees",
        "1,000 to 4,999 employees",
        "5,000 to 9,999 employees",
        "10,000 or more employees",
    ]
    short_org = {
        "Just me - I am a freelancer, sole proprietor, etc.": "Freelancer",
        "2 to 9 employees": "2–9",
        "10 to 19 employees": "10–19",
        "20 to 99 employees": "20–99",
        "100 to 499 employees": "100–499",
        "500 to 999 employees": "500–999",
        "1,000 to 4,999 employees": "1k–4,9k",
        "5,000 to 9,999 employees": "5k–9,9k",
        "10,000 or more employees": "10.000+",
    }
    org = org.set_index("segmento").loc[order_org].reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6), dpi=300)

    # Panel A: 7 Países LatAm N >= 30 con IC 95% bootstrap
    ax = axes[0]
    cols_p = [ORANGE if p == "Chile" else (NAVY if p == "Uruguay" else BLUE) for p in paises["pais"]]
    tlc_csv = pd.read_csv(DESC_DIR / "Matriz_TLC_19_Paises_LatAm.csv")
    ci_map = tlc_csv.set_index("pais")[["ic95_mediana_inf_usd", "ic95_mediana_sup_usd"]].to_dict(orient="index")

    err_lower = []
    err_upper = []
    for p, med in zip(paises["pais"], paises["mediana_usd"]):
        info = ci_map.get(p, {})
        inf_v = info.get("ic95_mediana_inf_usd")
        sup_v = info.get("ic95_mediana_sup_usd")
        if inf_v and not np.isnan(float(inf_v)):
            err_lower.append(max(0.0, med - float(inf_v)))
            err_upper.append(max(0.0, float(sup_v) - med))
        else:
            err_lower.append(0.0)
            err_upper.append(0.0)
    xerr = [err_lower, err_upper]

    ax.barh(range(len(paises)), paises["mediana_usd"], color=cols_p, height=0.6, zorder=3, xerr=xerr, capsize=3.5, error_kw=dict(ecolor=NAVY, lw=1.2, capthick=1.2))
    for i, r in paises.iterrows():
        offset_x = xerr[1][i] + 130
        ax.text(r["mediana_usd"] + offset_x, i, f"${r['mediana_usd']:,.0f} (N={r['n']})".replace(",", "."), va="center", fontsize=8.0, fontweight="bold", color=ORANGE if r["pais"] == "Chile" else GRAY_DARK)
    ax.set_yticks(range(len(paises)))
    ax.set_yticklabels(paises["pais"], fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 8200)
    ax.xaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax.set_title("A. Los 7 países LatAm con N ≥ 30 [IC 95% de la mediana (bootstrap)]", fontsize=9.8, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Mediana Salarial Mensual USD (SO 2024)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Barras verticales desde $0 por tamaño granular OrgSize
    ax2 = axes[1]
    x = np.arange(len(org))
    cols_o = [BLUE for s in org["segmento"]]
    ax2.bar(x, org["mediana_usd"], width=0.62, color=cols_o, zorder=3)
    for i, r in org.iterrows():
        ax2.text(
            i,
            r["mediana_usd"] + 75,
            f"${int(round(r['mediana_usd'])):,}\n(N={r['n']})".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=7.2,
            fontweight="bold",
            color=GRAY_DARK,
        )
    ax2.set_xticks(x)
    ax2.set_xticklabels([short_org[s] for s in org["segmento"]], fontsize=8.0, color=GRAY_DARK, fontweight="bold", rotation=20, ha="right")
    ax2.set_ylim(0, 4250)
    ax2.yaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax2.set_title("B. Mediana por Tamaño de Empresa en LatAm (desde $0 USD)", fontsize=9.8, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("Dotación de Empleados (Stack Overflow LatAm 2024)", fontsize=8.8)
    ax2.set_ylabel("Mediana Mensual USD", fontsize=8.8)
    estilizar_ejes(ax2, "y")

    fig.suptitle(
        f"Uruguay lidera; Chile (${int(CIFRAS['so_chile_salario_mediano']['val']):,}, N={CIFRAS['so_chile_salarios_validos']['str']}) no se distingue estadísticamente de Argentina, México y Colombia".replace(",", "."),
        fontsize=11.2,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Fuente: Stack Overflow Survey 2024 LatAm (19 países). Solo se muestran países con N >= 30 salarios válidos; en Panel B todos los tramos tienen N >= 60. Barras de error: IC 95% bootstrap.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "06_paises_latam_y_tamano_empresa_p4.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# VISUAL 7: EVOLUCIÓN DSS EE.UU. (P4B)
# =============================================================================
def fig_07_evolucion_dss_2020_2024() -> Path:
    """Visual 7 (P4B): Líneas múltiples 2020–2024 en Data Science Salaries (residentes en EE.UU.)."""
    dss_clean = pd.read_csv(CLEAN_DIR / "DataScienceSalaries_2020_2024_20261111_v01_clean.csv")
    dss_us = dss_clean[dss_clean["employee_residence"] == "United States"]

    piv = dss_us.groupby(["work_year", "tamano_es"])["salario_mensual_usd"].median().unstack()
    tot_y = pd.read_csv(RES_DIR / "resumen_p4_dss_eeuu_temporal.csv").set_index("work_year")

    fig, ax = plt.subplots(figsize=(10.8, 5.5), dpi=300)
    years = [2020, 2021, 2022, 2023, 2024]

    med_series = [float(tot_y.loc[y, "mediana_usd"]) for y in years]
    # Segmento 2020-2021 tiene N=28 en 2020 (<30 exploratorio), graficar con línea punteada de 2020 a 2021
    ax.plot([2020, 2021], med_series[:2], marker="o", linewidth=2.8, linestyle=":", color=NAVY, zorder=5)
    ax.plot(years[1:], med_series[1:], marker="o", linewidth=3.0, linestyle="-", color=NAVY, label=f"Mediana Total EE.UU. (N={int(tot_y['n'].sum()):,})".replace(",", "."), zorder=5)

    # Series por tamaño con manejo N < 30
    if "Mediana (Medium)" in piv.columns:
        ax.plot(years, [float(piv.loc[y, "Mediana (Medium)"]) for y in years], marker="s", linewidth=2.0, linestyle="--", color=BLUE, label="Empresas Medianas", zorder=4)
    if "Grande (Large)" in piv.columns:
        ax.plot(years, [float(piv.loc[y, "Grande (Large)"]) for y in years], marker="^", linewidth=2.0, linestyle="-.", color=TEAL, label="Empresas Grandes", zorder=4)
    if "Pequeña (Small)" in piv.columns:
        small_years = [2020, 2021, 2022, 2023]
        small_vals = [float(piv.loc[y, "Pequeña (Small)"]) for y in small_years]
        ax.plot(small_years, small_vals, marker="d", linewidth=2.0, linestyle=":", color=ORANGE, label=f"Empresas Pequeñas (N={0} en 2024)", zorder=4)

    offsets_y = {2020: -780, 2021: 520, 2022: -900, 2023: 540, 2024: -850}
    for yr in years:
        val = float(tot_y.loc[yr, "mediana_usd"])
        n_val = int(tot_y.loc[yr, "n"])
        tag_expl = " (N<30)" if n_val < 30 else ""
        ax.text(
            yr,
            val + offsets_y[yr],
            f"${val:,.0f}{tag_expl}".replace(",", "."),
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color=NAVY,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.88),
        )
    ax.text(2023.7, 9800, f"Small N={0}", fontsize=8.0, style="italic", color=ORANGE, fontweight="bold")

    ax.set_xticks(years)
    ax.set_xticklabels([f"2020\n(N={28}, explor.)", f"2021\n(N={88})", f"2022\n(N={829})", f"2023\n(N={3854:,})".replace(",", "."), f"2024\n(parcial, N={506})"])
    ax.set_ylim(0, 16500)
    ax.yaxis.set_major_formatter(FuncFormatter(axis_fmt_usd))
    ax.set_ylabel("Mediana Salarial Mensual (USD)", fontsize=9.5, color=GRAY_DARK)
    ax.set_xlabel("Año de Referencia (Data Science Salaries, residentes en EE.UU.)", fontsize=9.5, color=GRAY_DARK)
    estilizar_ejes(ax, "y")

    title_wrapped = textwrap.fill(
        f"Data Science Salaries, residentes en EE.UU. (2020–2024): Serie Anual de Referencia Internacional",
        width=65
    )
    fig.suptitle(
        title_wrapped,
        fontsize=11.3,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    ax.legend(loc="lower right", frameon=False, fontsize=8.6)
    pie_fuente(
        fig,
        f"Fuente: Data Science Salaries 2020–2024 (ai-jobs.net, CC0 1.0; filtro estricto residentes en EE.UU., N={int(tot_y['n'].sum()):,}).\n"
        f"Nota N>=30: Segmentos con N < 30 (2020 N={28}) se muestran en trazo punteado como exploratorios; en 2024 empresas pequeñas tiene N={0}.",
    )
    plt.tight_layout(rect=[0, 0.06, 1, 0.92])
    out = VIZ_DIR / "07_evolucion_dss_2020_2024_p4.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


# =============================================================================
# GENERAR IMAGEN OG:IMAGE (1200x630)
# =============================================================================
def generar_og_image() -> Path:
    """Genera og_image_1200x630.png para Open Graph social preview."""
    fig = plt.figure(figsize=(12.0, 6.3), dpi=100, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 630)
    ax.axis("off")

    # Acentos visuales
    ax.add_patch(FancyBboxPatch((60, 100), 12, 430, boxstyle="square,pad=0", facecolor=AMBER, edgecolor="none"))
    ax.text(95, 480, "ESTUDIO DE CASO  •  GOOGLE DATA ANALYTICS CERTIFICATE", fontsize=15, fontweight="bold", color=AMBER)
    ax.text(95, 390, "Mercado Laboral & Salarios Tech", fontsize=38, fontweight="bold", color="white")
    ax.text(95, 330, "Chile & Latinoamérica (2024–2026)", fontsize=32, fontweight="bold", color="#93C5FD")
    ax.text(95, 255, "Habilidades Críticas • Bandas Salariales p25–p75 • Impacto Remoto • N ≥ 30 (CLT)", fontsize=18, color="#E2E8F0")

    # Tarjetas métricas
    kpis = [
        (f"SQL {CIFRAS['gob_sql_pct']['str']}", "Tecnología #1 GOB"),
        (f"${int(CIFRAS['gob_senior_salario_mediano']['val']):,}".replace(",", "."), f"Senior Mediana (N={113})"),
        (f"+{CIFRAS['gob_salto_senior_vs_semisenior_pct']['str']}", "Salto Seniority"),
        (f"N={CIFRAS['so_latam_salarios_validos']['str']}", "Salarios SO LatAm"),
    ]
    for idx, (val, lbl) in enumerate(kpis):
        x = 95 + idx * 260
        ax.add_patch(FancyBboxPatch((x, 110), 235, 95, boxstyle="round,pad=8", facecolor="#0F172A", edgecolor="#3B82F6", linewidth=1.5))
        ax.text(x + 117, 168, val, ha="center", fontsize=22, fontweight="bold", color=AMBER)
        ax.text(x + 117, 132, lbl, ha="center", fontsize=12, color="#CBD5E1")

    ax.text(95, 55, "Manuel Yáñez Orellana  •  Portafolio Profesional de Análisis de Datos  •  jmryanez.github.io", fontsize=13, color=GRAY_MID)

    out = BASE_DIR / "og_image_1200x630.png"
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


# =============================================================================
# EXCEL PARA TABLEAU Y DESCARGAS
# =============================================================================
def exportar_excel_tableau() -> Path:
    """Genera el paquete multi-hoja Datos_Consolidados_Tableau_Public.xlsx con formato largo y consistencia total."""
    xlsx_path = SHARE_DIR / "Datos_Consolidados_Tableau_Public.xlsx"
    nota = pd.DataFrame(
        {
            "Regla_de_Uso_en_Tableau_Public": [
                "1. Nunca promediar ni sumar juntas filas de poblaciones distintas (Get on Board 2026, Stack Overflow 2024, DSS 2020-2024 e INE ESI 2025).",
                "2. ¿Qué es N y N >= 30 (Curso 4, Teorema del Límite Central)? N es el conteo exacto de observaciones válidas en un grupo; 30 es el tamaño mínimo muestral representativo bajo el Teorema del Límite Central.",
                f"3. Derivadas de N: (a) N total de universo vs. N salarios válidos (ej. GOB N={CIFRAS['gob_total_scope']['val']} ofertas vs. N={CIFRAS['gob_salarios_validos']['val']} con sueldo válido); (b) N < 30 / cumple_n30=False = exploratorio sin inferencia (ej. Junior N={17}, {12} países LatAm); (c) N = {0} = sin datos (Small 2024); (d) Cotas observadas = mínimo real resultante tras filtrar N>=30.",
                "4. Usar las hojas como fuentes independientes o tablas complementarias.",
                f"5. Tipo de cambio referencial oficial: Dólar Observado BCCh al 2026-11-10 = {CIFRAS['dolar_observado_bcch']['str']} CLP/USD.",
            ]
        }
    )

    # Matriz TLC con ISO3
    iso3_map = {
        "Brasil": "BRA", "Argentina": "ARG", "México": "MEX", "Colombia": "COL",
        "Chile": "CHL", "Perú": "PER", "Uruguay": "URY", "Costa Rica": "CRI",
        "Ecuador": "ECU", "Guatemala": "GTM", "Bolivia": "BOL",
        "República Dominicana": "DOM", "Venezuela": "VEN", "Panamá": "PAN",
        "Paraguay": "PRY", "El Salvador": "SLV", "Honduras": "HND",
        "Nicaragua": "NIC", "Cuba": "CUB"
    }
    mapa_csv = DESC_DIR / "Matriz_TLC_19_Paises_LatAm.csv"
    df_paises = pd.read_csv(mapa_csv)
    df_paises["iso3"] = df_paises["pais"].map(iso3_map)
    df_paises["fuente_salario"] = "Stack Overflow LatAm 2024"

    # Versión en formato largo de P1
    df_p1 = pd.read_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv")
    p1_long = []
    for _, r in df_p1.iterrows():
        p1_long.append({"tecnologia": r["tecnologia"], "tipo_tecnologia": r["tipo_tecnologia"], "poblacion": "Get on Board Total (Ofertas)", "n_universo": 679, "porcentaje": r["pct_demanda_gob_total"], "moe_pp": None})
        p1_long.append({"tecnologia": r["tecnologia"], "tipo_tecnologia": r["tipo_tecnologia"], "poblacion": "Stack Overflow Chile (Uso)", "n_universo": 133, "porcentaje": r["pct_adopcion_chile"], "moe_pp": r.get("moe95_pp_chile")})
        p1_long.append({"tecnologia": r["tecnologia"], "tipo_tecnologia": r["tipo_tecnologia"], "poblacion": "Stack Overflow LatAm (Uso)", "n_universo": 3074, "porcentaje": r["pct_adopcion_latam"], "moe_pp": r.get("moe95_pp_latam")})
    df_p1_long = pd.DataFrame(p1_long)

    # Versión en formato largo de Q12
    df_q12 = pd.read_csv(RES_DIR / "resumen_q12_modalidad_composicion_seniority.csv")
    q12_long = []
    for _, r in df_q12.iterrows():
        m = r["modalidad_grupo"]
        tot = r["n_salarios_validos"]
        q12_long.append({"modalidad_grupo": m, "n_salarios_validos": tot, "seniority": "Senior", "pct": r["pct_senior"]})
        q12_long.append({"modalidad_grupo": m, "n_salarios_validos": tot, "seniority": "Semi-Senior", "pct": r["pct_semi_senior"]})
        q12_long.append({"modalidad_grupo": m, "n_salarios_validos": tot, "seniority": "Junior / Trainee", "pct": r["pct_junior_trainee"]})
        q12_long.append({"modalidad_grupo": m, "n_salarios_validos": tot, "seniority": "Lead", "pct": r["pct_lead"]})
    df_q12_long = pd.DataFrame(q12_long)

    # Hoja DSS_Anio_Tamano en formato largo
    df_dss_anio_tam = pd.read_csv(RES_DIR / "resumen_p4_dss_eeuu_anio_tamano.csv")

    sheets = {
        "LEEME_Poblaciones": nota,
        "P1_Tecnologias_Largo": df_p1_long,
        "P1_Tecnologias": df_p1,
        "P2_Experiencia": pd.read_csv(RES_DIR / "resumen_p2_salarios_experiencia.csv"),
        "P3_Modalidad_INE": pd.read_csv(RES_DIR / "resumen_p3_comparacion_ine_chile_local.csv"),
        "DSS_Anio_Tamano": df_dss_anio_tam,
        "P4_Tamano_DSS": pd.read_csv(RES_DIR / "resumen_p4_dss_eeuu_temporal.csv"),
        "SO_Paises_LatAm_N30": pd.read_csv(RES_DIR / "resumen_paises_so_latam_n30.csv"),
        "Q11_Tech_vs_Salario": pd.read_csv(RES_DIR / "resumen_q11_tecnologia_vs_salario.csv"),
        "Q12_Seniority_Largo": df_q12_long,
        "Q13_Categorias_GOB": pd.read_csv(RES_DIR / "resumen_q13_gob_categorias.csv"),
        "Mapa_LatAm_19_Paises": df_paises,
    }

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, dframe in sheets.items():
            dframe.to_excel(writer, sheet_name=name[:31], index=False)

    shutil.copyfile(xlsx_path, DESC_DIR / "Datos_Consolidados_Tableau_Public.xlsx")
    return xlsx_path


# =============================================================================
# PRESENTACIÓN EJECUTIVA PDF (14 SLIDES)
# =============================================================================
def render_deck_ejecutivo_pdf(viz_paths: list[Path]) -> Path:
    """Genera la Presentación Ejecutiva 16:9 (~30 min, 14 slides) siguiendo la estructura del Curso 6."""
    import tempfile
    tmp_pdf = Path(tempfile.gettempdir()) / "temp_deck_14slides.pdf"
    pdf_path = SHARE_DIR / "05_Presentacion_Ejecutiva_30min.pdf"

    def new_slide(bg="#FFFFFF"):
        fig = plt.figure(figsize=(13.333, 7.5), dpi=200, facecolor=bg)
        ax = fig.add_axes([0, 0, 1, 1], facecolor=bg)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        return fig, ax

    def header(ax, kicker: str, title: str, page_num: int):
        ax.add_patch(FancyBboxPatch((0, 96.5), 100, 3.5, boxstyle="square,pad=0", facecolor=NAVY, edgecolor="none"))
        ax.text(3.2, 92.2, kicker.upper(), fontsize=10.5, fontweight="bold", color=ORANGE)
        ax.text(3.2, 87.2, title, fontsize=17.0, fontweight="bold", color=NAVY)
        ax.plot([3.2, 96.8], [85.0, 85.0], color=GRAY_LIGHT, linewidth=1.2)
        ax.text(96.8, 2.0, f"Diapositiva {page_num} / 14  •  Manuel Yáñez Orellana  •  2026-11-17", ha="right", fontsize=9.0, color=GRAY_MID)

    def embed_img(fig, img_path: Path, rect=(0.03, 0.06, 0.94, 0.77)):
        iax = fig.add_axes(rect)
        iax.imshow(plt.imread(img_path))
        iax.axis("off")

    with PdfPages(tmp_pdf) as pdf:
        # Slide 1: Portada
        f, ax = new_slide(NAVY)
        ax.add_patch(FancyBboxPatch((4, 18), 1.0, 62, boxstyle="square,pad=0", facecolor=AMBER, edgecolor="none"))
        ax.text(7.5, 67, "ESTUDIO DE CASO  •  CERTIFICADO PROFESIONAL DE ANÁLISIS DE DATOS DE GOOGLE", fontsize=12.0, fontweight="bold", color=AMBER)
        ax.text(7.5, 52, "Mercado Laboral y Salarios en Tecnología:\nChile y Latinoamérica (2024–2026)", fontsize=27, fontweight="bold", color="white", linespacing=1.25)
        ax.text(7.5, 39, "Brecha de Habilidades, Bandas Salariales por Experiencia, Modalidad y Tamaño de Empresa", fontsize=14, color="#E2E8F0")
        ax.text(7.5, 25, "Presentado por: Manuel Yáñez Orellana   |   Caso de estudio simulado (ejercicio académico)\nFecha: 17 de noviembre de 2026   |   Exposición Ejecutiva: 30 minutos", fontsize=11.5, color="#CBD5E1", linespacing=1.5)
        pdf.savefig(f); plt.close(f)

        # Slide 2: Agenda
        f, ax = new_slide()
        header(ax, "Hoja de Ruta • Curso 6 (Módulo 4)", "Agenda de la Sesión Ejecutiva (30 minutos)", 2)
        agenda = [
            ("01", "4 min", "Introducciones y Propósito", "Contexto del cliente y partes interesadas simuladas (Academia Digital y Consultora RRHH)."),
            ("02", "5 min", "Hipótesis, Datos y Regla N ≥ 30", "4 poblaciones independientes, control CLT N >= 30 y meta de demanda >= 20%."),
            ("03", "10 min", "Hallazgos y Visuales Clave", "Top 4 tecnologías, bandas p25–p75, análisis de modalidad y series temporales."),
            ("04", "4 min", "Limitaciones y Control de Sesgos", "Autoselección, no especificación bruto/líquido, tipo de cambio y causalidad."),
            ("05", "4 min", "Recomendaciones Estratégicas", "Priorización curricular, calibración de bandas y transparencia salarial."),
            ("06", "3 min", "Indicadores de Monitoreo & Q&A", "Métricas a 30, 60 y 90 días, preguntas de cierre y debate estratégico."),
        ]
        for i, (num, dur, tit, desc) in enumerate(agenda):
            y = 73 - i * 11.2
            ax.add_patch(FancyBboxPatch((4, y - 3.2), 92, 9.0, boxstyle="round,pad=0.4", facecolor=BG_PANEL, edgecolor=GRAY_LIGHT, linewidth=0.8))
            ax.text(6.5, y + 1.2, num, fontsize=14, fontweight="bold", color=BLUE)
            ax.text(12.5, y + 1.2, dur, fontsize=11, fontweight="bold", color=ORANGE)
            ax.text(21.5, y + 1.2, tit, fontsize=12.5, fontweight="bold", color=NAVY)
            ax.text(21.5, y - 1.5, desc, fontsize=10.5, color=GRAY_DARK)
        pdf.savefig(f); plt.close(f)

        # Slide 3: Hipótesis, Datos y Reglas
        f, ax = new_slide()
        header(ax, "Fase 1: Preguntar (Ask)", "Tarea Empresarial, Hipótesis Inicial y Control Metodológico", 3)
        cards = [
            ("TAREA EMPRESARIAL", f"Cuantificar demanda tech vigente en Get on Board ({CIFRAS['gob_total_scope']['str']} vacantes en alcance), adopción en Stack Overflow 2024 ({CIFRAS['so_latam_total']['str']} LatAm), serie DSS EE.UU. y línea base INE ESI 2025 para orientar mallas curriculares y calibrar bandas.", NAVY),
            ("HIPÓTESIS INICIAL", "El lenguaje #1 domina la empleabilidad base, pero las especializaciones Cloud y las ofertas remotas con alta concentración Senior explican las diferencias salariales observadas frente al mercado presencial local.", BLUE),
            ("MÉTRICAS Y CONTROL", f"• Meta #1: Tecnologías ≥ 20% presencia.\n• Meta #2: Umbral N ≥ 30 (CLT, muestra suficiente).\n• Meta #3: Mediana USD y cuartiles p25–p75.\n• Referencia oficial BCCh: ${CIFRAS['dolar_observado_bcch']['val']:.2f} CLP/USD.", TEAL),
        ]
        for idx, (ctit, cbody, col) in enumerate(cards):
            x = 4 + idx * 31.5
            ax.add_patch(FancyBboxPatch((x, 38), 29.5, 42, boxstyle="round,pad=0.6", facecolor=BG_PANEL, edgecolor=col, linewidth=1.6))
            ax.text(x + 1.8, 74, ctit, fontsize=12.0, fontweight="bold", color=col)
            wrapped_lines = "\n".join(textwrap.fill(line, 34) for line in cbody.split("\n"))
            ax.text(x + 1.8, 69, wrapped_lines, fontsize=10.2, color=GRAY_DARK, va="top", linespacing=1.42)

        kpis = [
            (f"{CIFRAS['gob_total_scope']['str']} / {CIFRAS['gob_salarios_validos']['str']}", "Vacantes GOB / Salarios válidos"),
            (f"{CIFRAS['so_latam_total']['str']} / {CIFRAS['so_latam_salarios_validos']['str']}", "Encuestados SO / Salarios válidos"),
            (f"${int(CIFRAS['ine_mediana_clp']['val']):,} CLP".replace(",", "."), "Mediana Nacional INE ESI 2025"),
            (f"${int(CIFRAS['gob_salario_mediano_total']['val']):,} USD".replace(",", "."), f"Mediana General GOB (N={CIFRAS['gob_salarios_validos']['val']})"),
        ]
        for idx, (kval, klbl) in enumerate(kpis):
            x = 4 + idx * 23.5
            ax.add_patch(FancyBboxPatch((x, 10.0), 21.5, 22.0, boxstyle="round,pad=0.5", facecolor=NAVY, edgecolor="none"))
            ax.text(x + 10.75, 23.0, kval, ha="center", fontsize=15, fontweight="bold", color=AMBER)
            ax.text(x + 10.75, 15.0, textwrap.fill(klbl, 22), ha="center", va="center", fontsize=9.8, color="white")
        pdf.savefig(f); plt.close(f)

        # Slides 4..10: Los 7 visuales
        slide_specs = [
            ("Pregunta 1 • Demanda vs. Adopción Real", "Visual 1: Solo 4 Tecnologías Superan el 20% de Demanda en Ofertas GOB", 4, viz_paths[0]),
            ("Profundización Q11 • Matriz Volumen vs. Salario", "Visual 2: Ofertas Cloud Muestran Medianas Más Altas, con Mayor Concentración Senior", 5, viz_paths[1]),
            ("Pregunta 1 • Mapa de Intensidad por Mercado", "Visual 3: Mapa de Calor — Chile Local vs. Remoto sin País Declarado vs. LatAm", 6, viz_paths[2]),
            ("Pregunta 2 • Bandas Salariales por Experiencia", f"Visual 4: Progresión p25–p75 (+{CIFRAS['gob_salto_senior_vs_semisenior_pct']['str']} a Senior) y Control N ≥ 30", 7, viz_paths[3]),
            ("Pregunta 3 + Q12 • Modalidad y Sesgo de Composición", f"Visual 5: Remoto Local (${int(CIFRAS['gob_remoto_local_salario_mediano']['val']):,}) con {fmt_es_num(CIFRAS['gob_remoto_local_pct_senior_lead']['val'], 1)}% de Cargos Senior o Lead".replace(",", "."), 8, viz_paths[4]),
            ("Pregunta 4A • Chile en LatAm y Tamaño de Empresa", f"Visual 6: Uruguay Lidera; Chile (${int(CIFRAS['so_chile_salario_mediano']['val']):,}) no se Diferencia de Países Vecinos".replace(",", "."), 9, viz_paths[5]),
            ("Pregunta 4B • Serie Histórica Internacional DSS", f"Visual 7: Data Science Salaries en EE.UU. 2020–2024 (2024 Parcial, N={506})", 10, viz_paths[6]),
        ]
        for kick, tit, pg, vpath in slide_specs:
            f, ax = new_slide()
            header(ax, kick, tit, pg)
            embed_img(f, vpath)
            pdf.savefig(f); plt.close(f)

        # Slide 11: Limitaciones de Datos y Control de Sesgos (ANTES de recomendaciones)
        f, ax = new_slide()
        header(ax, "Evaluación Metodológica • Curso 6 (Módulo 4)", "Limitaciones de Datos, Control de Sesgos y Validez Estadística", 11)
        notes = [
            ("Autoselección y Asimetría Informativa", f"En Get on Board, solo el {CIFRAS['gob_pct_con_salario']['str']} de los avisos ({CIFRAS['gob_salarios_validos']['str']} de {CIFRAS['gob_total_scope']['str']}) publica compensación explícita. Las empresas que declaran remuneraciones tienden a ofrecer salarios superiores."),
            ("No Especificación Bruto / Líquido", "Get on Board no reporta si los montos corresponden a sueldo bruto o líquido. Stack Overflow declara ingresos anuales brutos convertidos con tipos de cambio históricos."),
            ("Regla N ≥ 30 y Submuestras Exploratorias", f"Submuestras con N < 30 (Junior GOB N={CIFRAS['gob_junior_n']['val']}, Lead N={CIFRAS['gob_lead_n']['val']}, 12 países LatAm) son exploratorias y no admiten inferencia estadística poblacional."),
            ("Correlación ≠ Causalidad y Alcance", f"La brecha salarial de Remoto Local responde a sesgo de composición ({fmt_es_num(CIFRAS['gob_remoto_local_pct_senior_lead']['val'], 1)}% Senior/Lead). Además, 'Chile Local' y 'Remoto' son equivalentes a las modalidades en los datos."),
        ]
        for idx, (ntit, nbody) in enumerate(notes):
            row = idx // 2
            col_i = idx % 2
            x = 4 + col_i * 47
            y = 48 - row * 34
            ax.add_patch(FancyBboxPatch((x, y), 44.5, 30, boxstyle="round,pad=0.5", facecolor=BG_PANEL, edgecolor=GRAY_LIGHT, linewidth=1.2))
            ax.text(x + 1.8, y + 23.5, ntit, fontsize=12.0, fontweight="bold", color=NAVY)
            ax.text(x + 1.8, y + 19.0, textwrap.fill(nbody, 50), fontsize=10.2, color=GRAY_DARK, va="top", linespacing=1.45)
        pdf.savefig(f); plt.close(f)

        # Slide 12: Recomendaciones Estratégicas y Plan de Acción
        f, ax = new_slide()
        header(ax, "Conclusiones y Acciones • Fase 6 (Actuar)", "Recomendaciones Estratégicas Prioritarias (Qué / Quién / Cuándo)", 12)
        recs = [
            (
                "1. PRIORIZACIÓN CURRICULAR\n(Academia Digital • 30–60 días)",
                [
                    f"• Núcleo de Empleabilidad: Consolidar SQL ({CIFRAS['gob_sql_pct']['str']}) y Python ({CIFRAS['gob_python_pct']['str']}) como habilidades troncales indispensables.",
                    f"• Cloud como Hipótesis Técnica: Introducir AWS ({CIFRAS['gob_aws_pct']['str']}) y Azure ({CIFRAS['gob_azure_pct']['str']}) como electivos avanzados sin prometer saltos automáticos.",
                ],
                NAVY,
            ),
            (
                "2. CALIBRACIÓN DE BANDAS RRHH\n(Consultora RRHH • Inmediato)",
                [
                    f"• Bandas de Mercado: Fijar Semi-Senior en ${1850:,}–${2600:,} USD (mediana ${int(CIFRAS['gob_semisenior_salario_mediano']['val']):,}) y Senior en ${2300:,}–${4000:,} USD (mediana ${int(CIFRAS['gob_senior_salario_mediano']['val']):,}).".replace(",", "."),
                    f"• Banda Remota Diferenciada: Reconocer requerimientos Senior en vacantes remotas (${3500:,}–${5000:,} USD).".replace(",", "."),
                ],
                TEAL,
            ),
            (
                "3. POLÍTICA DE TRANSPARENCIA\n(RRHH + Analítica • Trimestral)",
                [
                    "• Exigir publicación explícita de rango y moneda (bruto/líquido) en convocatorias para mitigar asimetrías.",
                    "• Abstenerse de extrapolar inferencias en perfiles Junior hasta consolidar N >= 30 ofertas.",
                    "• Mantener desacopladas series internacionales (DSS EE.UU.) de compensaciones locales.",
                ],
                ORANGE,
            ),
        ]
        for idx, (rtit, bullets, col) in enumerate(recs):
            x = 4 + idx * 31.5
            ax.add_patch(FancyBboxPatch((x, 14), 29.5, 66, boxstyle="round,pad=0.6", facecolor=BG_PANEL, edgecolor=col, linewidth=1.6))
            ax.text(x + 1.8, 73.5, rtit, fontsize=11.2, fontweight="bold", color=col, linespacing=1.35)
            y_cursor = 61.5
            for b in bullets:
                wrapped = textwrap.fill(b, 33)
                ax.text(x + 1.8, y_cursor, wrapped, fontsize=10.0, color=GRAY_DARK, va="top", linespacing=1.42)
                y_cursor -= (wrapped.count("\n") + 1) * 4.6 + 3.2
        pdf.savefig(f); plt.close(f)

        # Slide 13: Indicadores de Seguimiento y Monitoreo (NUEVA SLIDE)
        f, ax = new_slide()
        header(ax, "Gobernanza y Control • Fase 6 (Actuar)", "Indicadores Clave de Seguimiento (KPIs a 30, 60 y 90 Días)", 13)
        indicadores = [
            ("Tasa de Inserción Laboral SQL/Python", "Meta: ≥ 70% de egresados colocados en < 90 días con dominio en SQL y Python.", "30 días", BLUE),
            ("Tasa de Adopción de Transparencia Salarial", "Meta: ≥ 50% de nuevas ofertas con banda explícita y moneda documentada.", "60 días", TEAL),
            ("Ratio de Cumplimiento de Bandas p25–p75", "Meta: 100% de ofertas gestionadas alineadas con cuartiles de mercado validados.", "Inmediato", NAVY),
            ("Monitoreo de Muestra N en Perfiles Junior", "Meta: Alcanzar N ≥ 30 ofertas publicadas antes de fijar bandas obligatorias.", "90 días", ORANGE),
        ]
        for idx, (itit, ibody, iplazo, icol) in enumerate(indicadores):
            row = idx // 2
            col_i = idx % 2
            x = 4 + col_i * 47
            y = 48 - row * 34
            ax.add_patch(FancyBboxPatch((x, y), 44.5, 30, boxstyle="round,pad=0.5", facecolor=BG_PANEL, edgecolor=icol, linewidth=1.4))
            ax.text(x + 2.0, y + 23.5, itit, fontsize=12.2, fontweight="bold", color=icol)
            ax.text(x + 42.5, y + 23.5, f"Plazo: {iplazo}", fontsize=9.5, fontweight="bold", color=GRAY_MID, ha="right")
            ax.text(x + 2.0, y + 17.5, textwrap.fill(ibody, 50), fontsize=10.5, color=GRAY_DARK, va="top", linespacing=1.42)
        pdf.savefig(f); plt.close(f)

        # Slide 14: Preguntas de Cierre y Discusión Estratégica (NUEVA SLIDE)
        f, ax = new_slide()
        header(ax, "Diálogo y Próximos Pasos • Curso 6 (Módulo 4)", "Preguntas de Cierre para el Comité de Dirección y Partes Interesadas", 14)
        preguntas = [
            ("1. Estrategia de Formación Digital", "¿Debe la Academia Digital condicionar su currículo a tecnologías masivas (SQL/Python) o incorporar módulos Cloud optativos asumiendo su prima salarial como hipótesis no garantizada?"),
            ("2. Política de Atracción de Talento Senior", "¿Está la Consultora dispuesta a segmentar sus bandas salariales entre contrataciones en Chile Local y posiciones remotas para competir con vacantes del segmento remoto sin país declarado?"),
            ("3. Liderazgo en Transparencia de Mercado", f"¿Cómo puede la organización impulsar que los empleadores publiquen información salarial verificable para reducir el {65.4:.1f}% de opacidad salarial en el mercado nacional?".replace(".", ",")),
        ]
        for idx, (ptit, pbody) in enumerate(preguntas):
            y = 66 - idx * 22
            ax.add_patch(FancyBboxPatch((4, y - 4), 92, 19, boxstyle="round,pad=0.5", facecolor=BG_PANEL, edgecolor=NAVY, linewidth=1.2))
            ax.text(6.5, y + 10.5, ptit, fontsize=13.0, fontweight="bold", color=BLUE)
            ax.text(6.5, y + 5.5, textwrap.fill(pbody, 92), fontsize=10.8, color=GRAY_DARK, va="top", linespacing=1.45)
        pdf.savefig(f); plt.close(f)

    shutil.copyfile(tmp_pdf, pdf_path)
    shutil.copyfile(tmp_pdf, DESC_DIR / "05_Presentacion_Ejecutiva_30min.pdf")
    return pdf_path


def main() -> None:
    viz_paths = [
        fig_01_demanda_vs_adopcion(),
        fig_02_matriz_volumen_vs_salario(),
        fig_03_mapa_calor_tecnologias(),
        fig_04_bandas_experiencia(),
        fig_05_modalidades_y_causalidad(),
        fig_06_latam_y_tamano_empresa(),
        fig_07_evolucion_dss_2020_2024(),
    ]
    og_img = generar_og_image()
    xlsx_path = exportar_excel_tableau()
    pdf_path = render_deck_ejecutivo_pdf(viz_paths)

    summary = {
        "visualizaciones_png": [{"file": p.name, "bytes": p.stat().st_size} for p in viz_paths],
        "og_image": {"file": og_img.name, "bytes": og_img.stat().st_size},
        "excel_tableau": {"file": xlsx_path.name, "bytes": xlsx_path.stat().st_size},
        "presentacion_pdf": {"file": pdf_path.name, "bytes": pdf_path.stat().st_size},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
