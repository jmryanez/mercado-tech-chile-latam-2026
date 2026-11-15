"""
Fase 5: Compartir (Share) — Visualizaciones Accesibles, Paquete Tableau Public y Deck Ejecutivo (~30 min)
Certificado Profesional de Análisis de Datos de Google • Cursos 6 y 8 (Caso Práctico 3 - Pista B)

Principios del Curso 6 aplicados literalmente:
- Guía 'Cómo elegir una visualización de datos.pdf': barras horizontales agrupadas/apiladas,
  dispersión/burbujas, mapas de calor, gráficos de línea (<= 5 líneas), barras de rango p25-p75.
- 'Principios de diseño esenciales.md': relación datos-tinta optimizada, eje Y/X desde 0 en barras,
  paleta accesible para daltonismo (azul/naranja • Curso 6), etiquetas directas, sin leyendas redundantes.
- 'Guía: Comparta los hallazgos de los datos en las presentaciones.md': portada (título, subtítulo, fecha),
  agenda cronometrada de 30 minutos (4+5+10+3+3+5), regla de 5 segundos, flujo general->específico,
  recomendaciones y apéndice técnico / advertencias.
"""

from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RES_DIR = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes"
SHARE_DIR = BASE_DIR / "05_Fase_Compartir_Share"
VIZ_DIR = SHARE_DIR / "visualizaciones"
VIZ_DIR.mkdir(parents=True, exist_ok=True)

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
# Desactiva interpretación LaTeX cuando aparecen dos símbolos '$' de moneda en el mismo texto
plt.rcParams["text.parse_math"] = False


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


def fig_01_demanda_vs_adopcion(R: dict) -> Path:
    """Visual 1 (P1): Barras horizontales agrupadas + línea meta 20% (Curso 6, pág. 1)."""
    rows = []
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        for item in R["pregunta_1_top5_gob_cruce"][tipo][:4]:
            rows.append(
                {
                    "label": f"{item['tecnologia']}  [{tipo[:3].upper()}]",
                    "gob": item["pct_demanda_gob_total"],
                    "so_cl": item["pct_adopcion_chile"],
                    "so_lat": item["pct_adopcion_latam"],
                }
            )
    df = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11.8, 7.2), dpi=300)
    y = np.arange(len(df))
    h = 0.25

    ax.barh(y + h, df["gob"], height=h, color=NAVY, label="Demanda Ofertas GOB 2026 (N=679)", zorder=3)
    ax.barh(y, df["so_cl"], height=h, color=TEAL, label="Uso Real Chile SO 2024 (N=133)", zorder=3)
    ax.barh(y - h, df["so_lat"], height=h, color=AMBER, alpha=0.9, label="Uso Real LatAm SO 2024 (N=3.074)", zorder=3)

    ax.axvline(20.0, color=ORANGE, linestyle="--", linewidth=1.6, zorder=4)
    ax.text(20.7, len(df) - 0.25, "Meta ≥ 20% (Obj. Métrico #1)", color=ORANGE, fontsize=9, fontweight="bold")

    for i, val in enumerate(df["gob"]):
        ax.text(
            val + 0.7,
            i + h + 0.02,
            f"{val:.1f}%",
            va="center",
            fontsize=7.8,
            fontweight="bold",
            color=NAVY,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white", edgecolor="none", alpha=0.92),
        )
    for i, val in enumerate(df["so_cl"]):
        ax.text(
            val + 0.7,
            i - 0.01,
            f"{val:.1f}%",
            va="center",
            fontsize=7.5,
            color="#006B4E",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white", edgecolor="none", alpha=0.92),
        )

    ax.set_yticks(y)
    ax.set_yticklabels(df["label"], fontsize=9.0, color=GRAY_DARK, fontweight="bold")
    ax.set_xlim(0, 80)
    ax.set_ylim(-0.6, len(df) - 0.1)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlabel("% de aparición en ofertas vigentes (2026) o desarrolladores activos (2024)", fontsize=9.2, color=GRAY_DARK)
    estilizar_ejes(ax, "x")

    fig.suptitle(
        "Solo 5 tecnologías superan el 20% de demanda en Chile (SQL 32,8%, AWS 30,0%, Python 28,4%, JS 27,4%, Azure 20,8%)",
        fontsize=11.0,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.975,
    )
    fig.text(
        0.02,
        0.935,
        "Top 4 por categoría • Microsoft Azure muestra brecha positiva de demanda (20,8%) vs. adopción actual en Chile (15,0%)",
        fontsize=9.0,
        color=GRAY_MID,
        ha="left",
    )
    ax.legend(loc="lower right", frameon=False, fontsize=8.8)
    pie_fuente(fig, "Fuente: Get on Board API v0 (01-ene a 10-nov-2026 GMT-3, N=679) y Stack Overflow Survey 2024 (Chile N=133; LatAm 19 países N=3.074). Poblaciones separadas.")
    plt.tight_layout(rect=[0, 0.035, 1, 0.92])
    out = VIZ_DIR / "01_demanda_vs_adopcion_top5_p1.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def fig_02_matriz_volumen_vs_salario(R: dict) -> Path:
    """Visual 2 (Q11): Dispersión / burbujas por cuadrantes Demanda/Uso % vs Mediana USD (Curso 6, pág. 3)."""
    gob = pd.DataFrame(R["q11_gob_tecnologia_vs_salario"])
    so = pd.DataFrame(R["q11_so_latam_tecnologia_vs_salario"])

    cat_colors = {"Lenguaje": BLUE, "Cloud": ORANGE, "Base de datos": TEAL}
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.9), dpi=300)

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
    ax.axhline(2700.0, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)

    offsets_g = {
        "AWS": (0.8, 45, "left", "bottom"),
        "Google Cloud": (-1.5, 55, "left", "bottom"),
        "Microsoft Azure": (0.9, -45, "left", "baseline"),
        "TypeScript": (-4.5, 40, "left", "bottom"),
        "JavaScript": (-0.95, -26, "right", "top"),
        "Python": (0.9, -50, "left", "baseline"),
        "SQL": (-3.0, 50, "left", "bottom"),
        "PostgreSQL": (0.8, 35, "left", "baseline"),
    }
    for _, r in gob.iterrows():
        dx, dy, ha_v, va_v = offsets_g.get(r["tecnologia"], (0.6, 30, "left", "baseline"))
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
    ax.set_ylim(2120, 3060)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.set_title("A. Ofertas Get on Board 2026 (N ≥ 38 por tecnología)", fontsize=10.3, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("% Demanda en Ofertas (N=679)", fontsize=9)
    ax.set_ylabel("Mediana Salarial Mensual (USD)", fontsize=9)
    estilizar_ejes(ax, "both")
    ax.legend(loc="lower right", frameon=False, fontsize=8.2, markerscale=0.75)

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
    ax2.axhline(2246.0, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)
    ax2.axvline(40.0, color=GRAY_MID, linestyle="--", linewidth=1.1, zorder=2)

    offsets_s = {
        "AWS": (1.4, 42, "left", "baseline"),
        "Microsoft Azure": (1.4, 38, "left", "baseline"),
        "Google Cloud": (1.4, -75, "left", "baseline"),
        "PostgreSQL": (1.3, 45, "left", "baseline"),
        "Python": (-3.5, 62, "left", "baseline"),
        "TypeScript": (-1.35, -36, "right", "top"),
        "MongoDB": (1.2, 42, "left", "baseline"),
        "JavaScript": (-3.8, 65, "left", "baseline"),
        "SQL": (-3.5, -108, "left", "baseline"),
        "Microsoft SQL Server": (1.3, -68, "left", "baseline"),
        "MySQL": (1.4, -55, "left", "baseline"),
    }
    for _, r in so.iterrows():
        dx, dy, ha_v, va_v = offsets_s.get(r["tecnologia"], (1.0, 30, "left", "baseline"))
        ax2.text(
            r["pct_adopcion_latam"] + dx,
            r["mediana_usd"] + dy,
            f"{r['tecnologia']}\n(${int(round(r['mediana_usd'])):,})".replace(",", "."),
            fontsize=7.6,
            fontweight="bold",
            color=GRAY_DARK,
            ha=ha_v,
            va=va_v,
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.88),
        )
    ax2.set_xlim(18, 76)
    ax2.set_ylim(1720, 2900)
    ax2.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax2.set_title("B. Profesionales SO LatAm 2024 (N ≥ 335 por tecnología)", fontsize=10.3, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("% Adopción en LatAm (N=3.074)", fontsize=9)
    estilizar_ejes(ax2, "both")

    fig.suptitle(
        "SQL abre el mayor volumen (32,8%), pero Cloud (AWS/GCP/Azure) eleva la mediana salarial +23% a +32%",
        fontsize=12.0,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Tamaño de burbuja proporcional a N de salarios válidos (Q11A/B). Regla N >= 30 cumplida en todos los puntos. Líneas punteadas muestran referencia estratégica.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "02_matriz_volumen_vs_salario_q11.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def fig_03_mapa_calor_tecnologias(R: dict) -> Path:
    """Visual 3 (P1): Mapa de calor comparativo por mercado (Curso 6, pág. 5)."""
    rows = []
    for tipo in ["Lenguaje", "Base de datos", "Cloud"]:
        for item in R["pregunta_1_top5_gob_cruce"][tipo]:
            rows.append(
                {
                    "Tech": f"{item['tecnologia']} ({tipo[:3]})",
                    "GOB Total\n(N=679)": item["pct_demanda_gob_total"],
                    "GOB Chile\nLocal (401)": item["pct_gob_chile_local"],
                    "GOB Remoto\nGlobal (278)": item["pct_gob_remoto"],
                    "SO Chile\n(N=133)": item["pct_adopcion_chile"],
                    "SO LatAm\n(N=3.074)": item["pct_adopcion_latam"],
                }
            )
    df = pd.DataFrame(rows).set_index("Tech")

    fig, ax = plt.subplots(figsize=(10.8, 7.0), dpi=300)
    im = ax.imshow(df.values, cmap="YlGnBu", aspect="auto", vmin=0, vmax=70)

    ax.set_xticks(np.arange(df.shape[1]))
    ax.set_xticklabels(df.columns, fontsize=9, fontweight="bold", color=NAVY)
    ax.set_yticks(np.arange(df.shape[0]))
    ax.set_yticklabels(df.index, fontsize=8.8, color=GRAY_DARK)

    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            val = df.values[i, j]
            txt_color = "white" if val >= 36 else GRAY_DARK
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color=txt_color, fontsize=8.3, fontweight="bold")

    ax.axhline(4.5, color="white", linewidth=2.5)
    ax.axhline(9.5, color="white", linewidth=2.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.03)
    cbar.set_label("% de presencia", fontsize=8.8, color=GRAY_DARK)

    fig.suptitle(
        "El mercado Remoto Global tracciona JS (33,5%) y AWS (34,9%), mientras Chile Local prioriza SQL (34,9%)",
        fontsize=11.0,
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


def fig_04_bandas_experiencia(R: dict) -> Path:
    """Visual 4 (P2): Bandas p25–p75 y mediana por experiencia con control N >= 30 (Curso 6, pág. 5)."""
    gob_map = {r["segmento"]: r for r in R["pregunta_2_gob_seniority"]}
    so_map = {r["segmento"]: r for r in R["pregunta_2_so_exp"]}

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), dpi=300)

    # Panel A: Get on Board
    ax = axes[0]
    gob_order = [("Junior", False), ("Semi-Senior", True), ("Senior", True)]
    for idx, (seg, valid) in enumerate(gob_order):
        r = gob_map[seg]
        c_bar = BLUE if valid else GRAY_LIGHT
        c_dot = ORANGE if valid else GRAY_MID
        ax.barh(idx, r["p75_usd"] - r["p25_usd"], left=r["p25_usd"], height=0.45, color=c_bar, alpha=0.35 if valid else 0.7, edgecolor=c_bar, linewidth=1.3, zorder=3)
        ax.scatter([r["mediana_usd"]], [idx], color=c_dot, s=90, zorder=5)
        tag = f"N={r['n']}" if valid else f"N={r['n']} (<30 explor.)"
        ax.text(r["p75_usd"] + 85, idx, f"Med: ${int(r['mediana_usd']):,}\n({tag})".replace(",", "."), va="center", fontsize=8.3, color=NAVY if valid else GRAY_MID, fontweight="bold")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Junior *", "Semi-Senior", "Senior"], fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 5300)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.set_title("A. Ofertas Get on Board 2026 (+42,2% de Semi-Senior a Senior)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Salario Mensual USD (Barra = p25–p75 | Punto = Mediana)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Stack Overflow LatAm
    ax2 = axes[1]
    so_order = ["0-1 años (<2)", "2-4 años", "5-9 años", "10+ años"]
    for idx, seg in enumerate(so_order):
        r = so_map[seg]
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

    cl_med = R["pregunta_2_so_chile_agregado"][0]["mediana_usd"]
    ax2.axvline(cl_med, color=ORANGE, linestyle="--", linewidth=1.5, zorder=4)
    ax2.text(cl_med + 120, 1.48, f"Mediana Chile SO\n${cl_med:,.0f} (N=46)".replace(",", "."), color=ORANGE, fontsize=8.3, fontweight="bold", zorder=6, bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.92))
    ax2.set_yticks(range(4))
    ax2.set_yticklabels(so_order, fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax2.set_xlim(0, 8000)
    ax2.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax2.set_title("B. Stack Overflow LatAm 2024 (+566,6% de <2 a 10+ años)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("Salario Mensual USD (Barra = p25–p75 | Punto = Mediana)", fontsize=8.8)
    estilizar_ejes(ax2, "x")

    fig.suptitle(
        "El salto a Senior en Chile (+42,2%) y a 10+ años en LatAm (+566,6%) ensancha fuertemente la banda p25–p75",
        fontsize=11.6,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "*Junior GOB (N=17 < 30) es exploratorio; Lead (N=7) y Trainee (N=1) excluidos de inferencia (Curso 4). Bandas muestran cuartiles p25–p75 y mediana.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "04_bandas_salariales_experiencia_p2.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def fig_05_modalidades_y_causalidad(R: dict) -> Path:
    """Visual 5 (P3 + Q12): Modalidades vs INE ESI 2025 + Composición Seniority (Correlación != Causalidad)."""
    gob_m = {r["segmento"]: r for r in R["pregunta_3_gob_modalidad"]}
    so_m = {r["segmento"]: r for r in R["pregunta_3_so_modalidad"]}
    comp = {r["modalidad_grupo"]: r for r in R["q12_gob_modalidad_composicion"]}
    ine_usd = R["ine_referencia"]["mediana_usd_ref"]

    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.8), dpi=300)

    # Panel A: Modalidades vs INE
    ax = axes[0]
    items = [
        ("SO LatAm: Presencial (N=200)", so_m["Presencial"]["mediana_usd"], GRAY_MID, "1,63x INE"),
        ("SO LatAm: Híbrido (N=310)", so_m["Híbrido"]["mediana_usd"], TEAL, "2,88x INE (+76,3%)"),
        ("SO LatAm: Remoto (N=831)", so_m["Remoto"]["mediana_usd"], BLUE, "3,99x INE (+144,1%)"),
        ("GOB: Presencial (N=34)", gob_m["Presencial"]["mediana_usd"], GRAY_MID, "3,21x INE"),
        ("GOB: Híbrido (N=103)", gob_m["Híbrido"]["mediana_usd"], TEAL, "3,28x INE (+2,2%)"),
        ("GOB: Remoto Total (N=53)", gob_m["Remoto Total"]["mediana_usd"], BLUE, "3,71x INE (+15,6%)"),
        ("GOB: Remoto Local (N=45)", gob_m["Remoto Local"]["mediana_usd"], ORANGE, "5,35x INE (+66,7%)"),
    ]
    y = np.arange(len(items))
    vals = [x[1] for x in items]
    cols = [x[2] for x in items]
    ax.barh(y, vals, color=cols, height=0.60, zorder=3)
    ax.axvline(ine_usd, color="#991B1B", linestyle="--", linewidth=1.6, zorder=4)
    ax.text(ine_usd + 60, 6.72, f"INE ESI 2025: ${ine_usd:.0f} USD ($680k CLP)", color="#991B1B", fontsize=8.0, fontweight="bold")
    for idx, (_, v, _, tag) in enumerate(items):
        ax.text(v + 70, idx, f"${v:,.0f}  |  {tag}".replace(",", "."), va="center", fontsize=8.0, fontweight="bold", color=GRAY_DARK)
    ax.axhline(2.5, color=GRAY_LIGHT, linewidth=1.2, linestyle="-")
    ax.set_yticks(y)
    ax.set_yticklabels([x[0] for x in items], fontsize=8.4, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 5700)
    ax.set_ylim(-0.6, 7.2)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.set_title("A. Mediana Mensual USD vs. Línea Base INE ESI 2025", fontsize=9.8, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Mediana Salarial Mensual (USD)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Barras apiladas 100% — Composición Seniority
    ax2 = axes[1]
    mods = ["Presencial", "Híbrido", "Remoto Total", "Remoto Local"]
    sen = np.array([comp[m]["pct_senior"] + comp[m]["pct_lead"] for m in mods])
    semi = np.array([comp[m]["pct_semi_senior"] for m in mods])
    jr = np.array([100.0 - s - sm for s, sm in zip(sen, semi)])

    y2 = np.arange(len(mods))
    ax2.barh(y2, sen, color=NAVY, height=0.54, label="Senior + Lead", zorder=3)
    ax2.barh(y2, semi, left=sen, color=BLUE, height=0.54, label="Semi-Senior", zorder=3)
    ax2.barh(y2, jr, left=sen + semi, color=GRAY_LIGHT, height=0.54, label="Junior / Trainee", zorder=3)

    for i in range(len(mods)):
        ax2.text(sen[i] / 2, i, f"{sen[i]:.1f}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        ax2.text(sen[i] + semi[i] / 2, i, f"{semi[i]:.1f}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        alc = comp[mods[i]]["pct_alcance_remoto_global"]
        lbl_alc = "100% Remoto Global/LatAm" if alc == 100 else "100% Chile Local"
        ax2.text(101.5, i, lbl_alc, va="center", fontsize=7.8, color=ORANGE if alc == 100 else GRAY_MID, fontweight="bold")

    ax2.set_yticks(y2)
    ax2.set_yticklabels(mods, fontsize=9, fontweight="bold", color=GRAY_DARK)
    ax2.set_xlim(0, 146)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.set_title("B. Composición Seniority (Correlación ≠ Causalidad)", fontsize=9.8, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("% Composición de Seniority y Alcance (Get on Board)", fontsize=8.8)
    ax2.legend(loc="lower center", bbox_to_anchor=(0.38, -0.22), ncol=3, frameon=False, fontsize=8.2)
    estilizar_ejes(ax2, "x")

    fig.suptitle(
        "El formato Remoto Local paga 5,35x la mediana nacional INE porque el 68,9% exige perfil Senior/Lead internacional",
        fontsize=11.4,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Dólar Observado BCCh al 2026-11-10 = $969,80 CLP/USD. ESI 2025 INE ($680.000 CLP netos/mes). Panel B demuestra sesgo de composición (Curso 6, Correlación != Causalidad).")
    plt.tight_layout(rect=[0, 0.05, 1, 0.91])
    out = VIZ_DIR / "05_modalidades_vs_ine_y_causalidad_p3_q12.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def fig_06_latam_y_tamano_empresa(R: dict) -> Path:
    """Visual 6 (P4A + Países): Barras horizontales Países LatAm N>=30 y Barras verticales desde $0 OrgSize SO (Curso 6)."""
    paises = pd.DataFrame(R["so_latam_paises_n30"]).iloc[::-1].reset_index(drop=True)
    org = pd.DataFrame(R["pregunta_4_so_org_detalle"])
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
        "Just me - I am a freelancer, sole proprietor, etc.": "Freelancer\n(1)",
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

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.5), dpi=300)

    # Panel A: 7 Países LatAm N >= 30
    ax = axes[0]
    cols_p = [ORANGE if p == "Chile" else (NAVY if p == "Uruguay" else BLUE) for p in paises["pais"]]
    ax.barh(range(len(paises)), paises["mediana_usd"], color=cols_p, height=0.6, zorder=3)
    for i, r in paises.iterrows():
        ax.text(r["mediana_usd"] + 120, i, f"${r['mediana_usd']:,.0f} (N={r['n']})".replace(",", "."), va="center", fontsize=8.3, fontweight="bold", color=ORANGE if r["pais"] == "Chile" else GRAY_DARK)
    ax.set_yticks(range(len(paises)))
    ax.set_yticklabels(paises["pais"], fontsize=9.2, fontweight="bold", color=GRAY_DARK)
    ax.set_xlim(0, 8200)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.set_title("A. Los 7 países LatAm con N ≥ 30 (Chile es 2° regional)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax.set_xlabel("Mediana Salarial Mensual USD (SO 2024)", fontsize=8.8)
    estilizar_ejes(ax, "x")

    # Panel B: Barras verticales desde $0 por tamaño granular OrgSize (todos N >= 60; no cortar eje Y • Curso 6)
    ax2 = axes[1]
    x = np.arange(len(org))
    cols_o = [ORANGE if s == "500 to 999 employees" else BLUE for s in org["segmento"]]
    ax2.bar(x, org["mediana_usd"], width=0.62, color=cols_o, zorder=3)
    for i, r in org.iterrows():
        ax2.text(
            i,
            r["mediana_usd"] + 75,
            f"${int(round(r['mediana_usd'])):,}\n(N={r['n']})".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
            color=ORANGE if "500" in r["segmento"] else GRAY_DARK,
        )
    ax2.set_xticks(x)
    ax2.set_xticklabels([short_org[s] for s in org["segmento"]], fontsize=7.9, color=GRAY_DARK, fontweight="bold")
    ax2.set_ylim(0, 4250)
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax2.set_title("B. Mediana por Tamaño de Empresa en LatAm (desde $0 USD)", fontsize=10, fontweight="bold", color=NAVY, loc="left")
    ax2.set_xlabel("Dotación de Empleados (Stack Overflow LatAm 2024)", fontsize=8.8)
    ax2.set_ylabel("Mediana Mensual USD", fontsize=8.8)
    estilizar_ejes(ax2, "y")

    fig.suptitle(
        "Chile ($3.064 USD) es 2° en LatAm y las empresas medianas-grandes (500–999) lideran la compensación regional",
        fontsize=11.6,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    pie_fuente(fig, "Fuente: Stack Overflow Survey 2024 LatAm (19 países). Solo se muestran países con N >= 30 salarios válidos; en Panel B todos los tramos tienen N >= 60.")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    out = VIZ_DIR / "06_paises_latam_y_tamano_empresa_p4.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def fig_07_evolucion_dss_2020_2024(R: dict) -> Path:
    """Visual 7 (P4B): Líneas múltiples 2020–2024 en Data Science Salaries (Curso 6, pág. 2)."""
    dss_clean = pd.read_csv(BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed" / "DataScienceSalaries_2020_2024_20261111_v01_clean.csv")
    piv = dss_clean.groupby(["work_year", "tamano_es"])["salario_mensual_usd"].median().unstack()
    tot_y = pd.DataFrame(R["pregunta_4_dss_anual"]).set_index("segmento")["mediana_usd"]

    fig, ax = plt.subplots(figsize=(10.8, 5.4), dpi=300)
    years = [2020, 2021, 2022, 2023, 2024]

    ax.plot(years, tot_y.loc[years], marker="o", linewidth=3.0, color=NAVY, label="Mediana Global Total (N=6.599)", zorder=5)
    ax.plot(years, piv.loc[years, "Mediana (Medium)"], marker="s", linewidth=2.0, linestyle="--", color=BLUE, label="Empresas Medianas (N=5.860)", zorder=4)
    ax.plot(years, piv.loc[years, "Grande (Large)"], marker="^", linewidth=2.0, linestyle="-.", color=TEAL, label="Empresas Grandes (N=569)", zorder=4)
    ax.plot(years, piv.loc[years, "Pequeña (Small)"], marker="d", linewidth=2.0, linestyle=":", color=ORANGE, label="Empresas Pequeñas (N=170)", zorder=4)

    offsets_y = {2020: -780, 2022: -900, 2023: 540, 2024: -850}
    for yr in years:
        val = float(tot_y.loc[yr])
        if yr == 2021:
            ax.annotate(
                f"${val:,.0f}".replace(",", "."),
                xy=(2021, val),
                xytext=(2020.92, 9500),
                ha="center",
                fontsize=8.8,
                fontweight="bold",
                color=NAVY,
                zorder=6,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.0, shrinkA=2, shrinkB=5),
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.9),
            )
        else:
            ax.text(
                yr,
                val + offsets_y[yr],
                f"${val:,.0f}".replace(",", "."),
                ha="center",
                fontsize=8.8,
                fontweight="bold",
                color=NAVY,
                zorder=6,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.85),
            )
    small_2023 = float(piv.loc[2023, "Pequeña (Small)"])
    ax.text(2023.06, small_2023 - 550, "2024: Small N=0", fontsize=7.6, style="italic", color=ORANGE, fontweight="bold")

    ax.set_xticks(years)
    ax.set_ylim(0, 14800)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.set_ylabel("Mediana Salarial Mensual (USD)", fontsize=9.5, color=GRAY_DARK)
    ax.set_xlabel("Año de Referencia (Serie Internacional Separada)", fontsize=9.5, color=GRAY_DARK)
    estilizar_ejes(ax, "y")

    fig.suptitle(
        "El benchmark global Data Science saltó +79,1% entre 2020 y 2023 ($11.917) y se estabilizó en 2024 ($11.500)",
        fontsize=11.3,
        fontweight="bold",
        color=NAVY,
        x=0.02,
        ha="left",
        y=0.97,
    )
    ax.legend(loc="lower right", frameon=False, fontsize=8.8)
    pie_fuente(
        fig,
        "Fuente: Data Science Salaries 2020–2024 (ai-jobs.net, CC0 1.0, N=6.599; predominio EE.UU.; máx. 4 líneas, Curso 6).\n"
        "Nota N>=30: Pequeñas 2024 tiene N=0; subceldas año×tamaño con N<30 (Med 2020 N=17, Peq 2020 N=24, Gr 2024 N=12) son exploratorias.",
    )
    plt.tight_layout(rect=[0, 0.06, 1, 0.92])
    out = VIZ_DIR / "07_evolucion_dss_2020_2024_p4.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def exportar_excel_tableau() -> Path:
    """Genera el paquete limpio multi-hoja para cargar directamente en Tableau Public."""
    xlsx_path = SHARE_DIR / "Datos_Consolidados_Tableau_Public.xlsx"
    nota = pd.DataFrame(
        {
            "Regla_de_Uso_en_Tableau_Public": [
                "1. Nunca promediar ni sumar juntas filas de poblaciones distintas (Get on Board 2026, Stack Overflow 2024, DSS 2020-2024 e INE ESI 2025).",
                "2. ¿Qué es N y N >= 30 (Curso 4, Teorema del Límite Central)? N es el conteo exacto de observaciones válidas en un grupo; 30 es el tamaño mínimo muestral estable para representar a la población al 95% de confianza con menor margen de error.",
                "3. Derivadas de N: (a) N total de universo vs. N salarios válidos (ej. GOB N=679 ofertas vs. N=235 con sueldo válido); (b) N < 30 / cumple_n30=False = exploratorio sin inferencia (ej. Junior N=17, 12 países LatAm); (c) N = 0 = sin datos (Small 2024); (d) Cotas observadas (N>=38, N>=335, N>=34, N>=60) = mínimo real resultante tras filtrar N>=30.",
                "4. Usar las hojas P1_Tecnologias, P2_Experiencia, P3_Modalidad_INE, P4_Tamano_DSS, SO_Paises_LatAm_N30, Q11_Tech_vs_Salario, Q12_Modalidad_Seniority y Q13_Categorias_GOB como fuentes independientes o tablas complementarias.",
                "5. Tipo de cambio referencial oficial: Dólar Observado BCCh al 2026-11-10 = $969,80 CLP/USD.",
            ]
        }
    )
    mapa_csv = BASE_DIR / "descargas" / "Matriz_TLC_19_Paises_LatAm.csv"
    if not mapa_csv.exists():
        mapa_csv = BASE_DIR / "03_Fase_Procesar_Process" / "datos_limpios_processed" / "Matriz_TLC_19_Paises_LatAm.csv"

    sheets = {
        "LEEME_Poblaciones": nota,
        "P1_Tecnologias": pd.read_csv(RES_DIR / "resumen_p1_tecnologias_gob_vs_so.csv"),
        "P2_Experiencia": pd.read_csv(RES_DIR / "resumen_p2_salarios_experiencia.csv"),
        "P3_Modalidad_INE": pd.read_csv(RES_DIR / "resumen_p3_salarios_modalidad_vs_ine.csv"),
        "P4_Tamano_DSS": pd.read_csv(RES_DIR / "resumen_p4_tamano_empresa_y_dss_temporal.csv"),
        "SO_Paises_LatAm_N30": pd.read_csv(RES_DIR / "resumen_paises_so_latam_n30.csv"),
        "Q11_Tech_vs_Salario": pd.read_csv(RES_DIR / "resumen_q11_tecnologia_vs_salario.csv"),
        "Q12_Modalidad_Seniority": pd.read_csv(RES_DIR / "resumen_q12_modalidad_composicion_seniority.csv"),
        "Q13_Categorias_GOB": pd.read_csv(RES_DIR / "resumen_q13_gob_categorias.csv"),
        "Mapa_LatAm_19_Paises": pd.read_csv(mapa_csv),
    }
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, dframe in sheets.items():
            dframe.to_excel(writer, sheet_name=name[:31], index=False)

    descargas_xlsx = BASE_DIR / "descargas" / "Datos_Consolidados_Tableau_Public.xlsx"
    if descargas_xlsx.parent.exists():
        shutil.copyfile(xlsx_path, descargas_xlsx)

    return xlsx_path


def render_deck_ejecutivo_pdf(viz_paths: list[Path]) -> Path:
    """Genera la Presentación Ejecutiva 16:9 (~30 min) siguiendo la estructura exacta del Curso 6 Mód. 4."""
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
        ax.text(3.2, 92.2, kicker.upper(), fontsize=9.5, fontweight="bold", color=ORANGE)
        ax.text(3.2, 87.2, title, fontsize=17.0, fontweight="bold", color=NAVY)
        ax.plot([3.2, 96.8], [85.0, 85.0], color=GRAY_LIGHT, linewidth=1.2)
        ax.text(96.8, 2.0, f"Diapositiva {page_num} / 12  •  Manuel Yáñez Orellana  •  2026-11-11", ha="right", fontsize=8.2, color=GRAY_MID)

    def embed_img(fig, img_path: Path, rect=(0.03, 0.06, 0.94, 0.77)):
        iax = fig.add_axes(rect)
        iax.imshow(plt.imread(img_path))
        iax.axis("off")

    with PdfPages(pdf_path) as pdf:
        # Slide 1: Portada
        f, ax = new_slide(NAVY)
        ax.add_patch(FancyBboxPatch((4, 18), 1.0, 62, boxstyle="square,pad=0", facecolor=AMBER, edgecolor="none"))
        ax.text(7.5, 67, "ESTUDIO DE CASO 3 (PISTA B)  •  GOOGLE DATA ANALYTICS", fontsize=11.5, fontweight="bold", color=AMBER)
        ax.text(7.5, 52, "Mercado Laboral y Salarios en Tecnología:\nChile y Latinoamérica (2024–2026)", fontsize=27, fontweight="bold", color="white", linespacing=1.25)
        ax.text(7.5, 39, "Brecha de Habilidades, Bandas Salariales por Experiencia, Modalidad y Tamaño de Empresa", fontsize=14, color="#E2E8F0")
        ax.text(7.5, 25, "Presentado por: Manuel Yáñez Orellana   |   Patrocinador: Consultora RRHH Tech & Academia Digital (Chile)\nFecha: 11 de noviembre de 2026   |   Exposición Ejecutiva: 30 minutos", fontsize=11, color="#CBD5E1", linespacing=1.5)
        pdf.savefig(f); plt.close(f)

        # Slide 2: Agenda
        f, ax = new_slide()
        header(ax, "Hoja de Ruta • Curso 6 (Módulo 4)", "Agenda de la Sesión Ejecutiva (30 minutos)", 2)
        agenda = [
            ("01", "4 min", "Introducciones y Propósito", "Contexto del cliente (Academia Digital y Consultora RRHH Tech en Chile)."),
            ("02", "5 min", "Proyecto, Hipótesis y Métricas", "4 fuentes independientes (72.797 crudos), regla N >= 30 y meta >= 20%."),
            ("03", "10 min", "Datos, Hallazgos y Visuales Clave", "Top 5 tech, prima Cloud, bandas p25–p75, paradoja remota y serie DSS."),
            ("04", "3 min", "Recomendaciones Estratégicas", "Priorización curricular, ajuste de bandas salariales y atracción remota."),
            ("05", "3 min", "Pasos Prácticos (Qué / Quién / Cuándo)", "Plan de implementación a 30–90 días e indicadores de seguimiento."),
            ("06", "5 min", "Preguntas, Limitaciones y Q&A", "Bruto/líquido, brecha cambiaria, N < 30 y Correlación != Causalidad."),
        ]
        for i, (num, dur, tit, desc) in enumerate(agenda):
            y = 73 - i * 11.2
            ax.add_patch(FancyBboxPatch((4, y - 3.2), 92, 9.0, boxstyle="round,pad=0.4", facecolor=BG_PANEL, edgecolor=GRAY_LIGHT, linewidth=0.8))
            ax.text(6.5, y + 1.2, num, fontsize=14, fontweight="bold", color=BLUE)
            ax.text(12.5, y + 1.2, dur, fontsize=11, fontweight="bold", color=ORANGE)
            ax.text(21.5, y + 1.2, tit, fontsize=12, fontweight="bold", color=NAVY)
            ax.text(21.5, y - 1.5, desc, fontsize=9.8, color=GRAY_DARK)
        pdf.savefig(f); plt.close(f)

        # Slide 3: Propósito, Hipótesis y Métricas
        f, ax = new_slide()
        header(ax, "Fase 1: Preguntar (Ask)", "Tarea Empresarial, Hipótesis Inicial y Métricas de Éxito", 3)
        cards = [
            ("TAREA EMPRESARIAL", "Cuantificar demanda tech vigente en Get on Board (01-ene a 10-nov-2026 GMT-3), adopción en Stack Overflow 2024 (Chile y 19 países LatAm), serie DSS 2020–2024 y línea base INE ESI 2025 para orientar mallas curriculares y calibrar bandas salariales.", NAVY),
            ("HIPÓTESIS INICIAL", "El lenguaje #1 en volumen domina la empleabilidad de entrada, pero las especializaciones Cloud y los roles remotos con exigencia Senior explican las mayores brechas salariales frente al mercado presencial local.", BLUE),
            ("MÉTRICAS Y REGLAS", "• Meta #1: Tecnologías >= 20% presencia.\n• Meta #2: Umbral N >= 30 (confianza 95%).\n• Meta #3: Mediana USD y cuartiles p25–p75 (sin fusionar poblaciones).\n• Referencia BCCh 2026-11-10: $969,80 CLP/USD.", TEAL),
        ]
        for idx, (ctit, cbody, col) in enumerate(cards):
            x = 4 + idx * 31.5
            ax.add_patch(FancyBboxPatch((x, 42), 29.5, 38, boxstyle="round,pad=0.6", facecolor=BG_PANEL, edgecolor=col, linewidth=1.6))
            ax.text(x + 1.8, 75, ctit, fontsize=11.5, fontweight="bold", color=col)
            wrapped_lines = "\n".join(textwrap.fill(line, 36) for line in cbody.split("\n"))
            ax.text(x + 1.8, 70, wrapped_lines, fontsize=9.6, color=GRAY_DARK, va="top", linespacing=1.42)

        kpis = [("72.797 -> 10.354", "Crudos auditados -> Limpios clave"), ("679 / 235", "Ofertas GOB Chile/Remoto / Salarios válidos"), ("3.074 / 1.341", "LatAm SO 19 países / Salarios válidos"), ("$680.000 CLP", "Mediana Nacional INE ESI 2025 ($701 USD)")]
        for idx, (kval, klbl) in enumerate(kpis):
            x = 4 + idx * 23.5
            ax.add_patch(FancyBboxPatch((x, 14.0), 21.5, 20.5, boxstyle="round,pad=0.5", facecolor=NAVY, edgecolor="none"))
            ax.text(x + 10.75, 26.0, kval, ha="center", fontsize=15, fontweight="bold", color=AMBER)
            ax.text(x + 10.75, 18.2, textwrap.fill(klbl, 24), ha="center", va="center", fontsize=9.2, color="white")

        ax.add_patch(FancyBboxPatch((4, 4.0), 92, 7.6, boxstyle="round,pad=0.4", facecolor="#F1F5F9", edgecolor=NAVY, linewidth=1.1))
        ax.text(
            5.6,
            9.6,
            "GLOSARIO N (Curso 4, Mód. 1 • CLT):  N = conteo de observaciones válidas (N universo total vs. N salarios válidos).  N >= 30 = umbral mínimo estable (95% confianza).",
            fontsize=8.3,
            fontweight="bold",
            color=NAVY,
        )
        ax.text(
            5.6,
            6.1,
            "Derivadas:  N < 30 (cumple_n30=False) = submuestra solo exploratoria (ej. Junior N=17, 12 países LatAm);  N = 0 = sin registros (Small 2024);  N >= 38 / >= 335 / >= 34 = mínimo real tras filtrar N >= 30.",
            fontsize=8.1,
            color=GRAY_DARK,
        )
        pdf.savefig(f); plt.close(f)

        # Slides 4..10: Los 7 visuales corregidos
        slide_specs = [
            ("Pregunta 1 • Demanda vs. Adopción Real", "Visual 1: Top 5 Tecnologías y Brecha Formativa en Nube", 4, viz_paths[0]),
            ("Profundización Q11 • Matriz Volumen vs. Salario", "Visual 2: SQL Abre Puertas (32,8%), Cloud Eleva Salarios (+23% a +32%)", 5, viz_paths[1]),
            ("Pregunta 1 • Mapa de Intensidad por Mercado", "Visual 3: Mapa de Calor — Chile Local vs. Remoto Global vs. LatAm", 6, viz_paths[2]),
            ("Pregunta 2 • Bandas Salariales por Experiencia", "Visual 4: Progresión p25–p75 y Control Estricto N >= 30", 7, viz_paths[3]),
            ("Pregunta 3 + Q12 • Modalidad vs. INE ESI 2025", "Visual 5: Paradoja Remoto Local (5,35x INE) y Correlación ≠ Causalidad", 8, viz_paths[4]),
            ("Pregunta 4A • Chile en LatAm y Tamaño de Empresa", "Visual 6: Chile es 2° Regional ($3.064) y 500–999 Lidera por Tamaño", 9, viz_paths[5]),
            ("Pregunta 4B • Serie Histórica Internacional DSS", "Visual 7: Salto +79,1% (2020–2023) y Estabilización en 2024 ($11.500)", 10, viz_paths[6]),
        ]
        for kick, tit, pg, vpath in slide_specs:
            f, ax = new_slide()
            header(ax, kick, tit, pg)
            embed_img(f, vpath)
            pdf.savefig(f); plt.close(f)

        # Slide 11: Recomendaciones con ajuste limpio de líneas (sin desbordes)
        f, ax = new_slide()
        header(ax, "Conclusiones y Acciones (Avance a Fase 6)", "Recomendaciones Prioritarias y Plan de Acción (Qué / Quién / Cuándo)", 11)
        recs = [
            (
                "1. CURRÍCULO EN 2 NIVELES\n(Academia Digital • 30–60 días)",
                [
                    "• Núcleo Empleabilidad (Meses 1–2): SQL (32,8%) + Python (28,4%) + JavaScript (27,4%) + PostgreSQL.",
                    "• Track Salarial Cloud (Mes 3+): AWS (30,0%, $2.850 GOB) y Azure (20,8% demanda vs. 15,0% uso actual en Chile) + TypeScript.",
                ],
                NAVY,
            ),
            (
                "2. CALIBRACIÓN DE BANDAS RRHH\n(Consultora RRHH • Inmediato)",
                [
                    "• Bandas Chile GOB (N>=30): Semi-Senior p25–p75 $1.850–$2.600 USD (Med $2.250); Senior $2.300–$4.000 USD (Med $3.200, +42,2%).",
                    "• Presión internacional: Remoto Global/LatAm paga +45,6% sobre Chile Local ($3.275 vs $2.250) y hasta $3.750 en Remoto Local Senior.",
                ],
                TEAL,
            ),
            (
                "3. TRANSPARENCIA SALARIAL\n(RRHH + Analítica • Trimestral)",
                [
                    "• Declarar sueldo bruto/líquido explícito en vacantes (solo 34,9% nominal / 34,6% válido hoy).",
                    "• Levantar >= 30 ofertas Junior antes de fijar bandas entry-level automáticas.",
                    "• No indexar salarios locales al benchmark EE.UU. DSS ($11.500 USD).",
                ],
                ORANGE,
            ),
        ]
        for idx, (rtit, bullets, col) in enumerate(recs):
            x = 4 + idx * 31.5
            ax.add_patch(FancyBboxPatch((x, 14), 29.5, 65, boxstyle="round,pad=0.6", facecolor=BG_PANEL, edgecolor=col, linewidth=1.6))
            ax.text(x + 1.8, 73.5, rtit, fontsize=10.8, fontweight="bold", color=col, linespacing=1.35)
            y_cursor = 62.5
            for b in bullets:
                wrapped = textwrap.fill(b, 35)
                ax.text(x + 1.8, y_cursor, wrapped, fontsize=9.4, color=GRAY_DARK, va="top", linespacing=1.42)
                y_cursor -= (wrapped.count("\n") + 1) * 4.2 + 3.0
        pdf.savefig(f); plt.close(f)

        # Slide 12: Advertencias y Apéndice Técnico
        f, ax = new_slide()
        header(ax, "Apéndice Técnico y Q&A • Curso 6 (Módulo 4)", "Limitaciones de Datos, Control de Sesgos y Reproducibilidad", 12)
        notes = [
            ("Bruto vs. Líquido y Tasa Cambiaria", "Get on Board no etiqueta sueldo bruto/líquido; Stack Overflow 2024 usó tasas de cambio 2024 vs. BCCh 2026-11-10 ($969,80 CLP/USD), mientras INE ESI 2025 es ingreso líquido neto nacional."),
            ("Cobertura Temporal y Autoselección", "API pública de Get on Board solo entrega avisos abiertos vigentes al corte 2026-11-10 (GMT-3) y 34,9% declara sueldo (235 válidos tras anular $100 y $300 <$500 USD)."),
            ("Correlación ≠ Causalidad y Regla N >= 30", "El +66,7% de Remoto Local se explica por composición (100% alcance remoto internacional y 68,9% Senior/Lead). Junior (N=17), Lead (N=7) y ML/AI (N=21) quedan como exploratorios."),
            ("Reproducibilidad 100% Auditada", "Datos crudos inmutables (21,05 MiB) -> Python ETL (3,20 MiB limpios, 6 tipos de validación, Changelog 7 campos) -> SQLite Q01–Q13 (sin duplicación en JOIN 1:N) -> Tableau Public & Deck."),
        ]
        for idx, (ntit, nbody) in enumerate(notes):
            row = idx // 2
            col_i = idx % 2
            x = 4 + col_i * 47
            y = 48 - row * 32
            ax.add_patch(FancyBboxPatch((x, y), 44.5, 27, boxstyle="round,pad=0.5", facecolor=BG_PANEL, edgecolor=GRAY_LIGHT, linewidth=1.2))
            ax.text(x + 1.8, y + 21.5, ntit, fontsize=11.5, fontweight="bold", color=NAVY)
            ax.text(x + 1.8, y + 17.5, textwrap.fill(nbody, 56), fontsize=9.5, color=GRAY_DARK, va="top", linespacing=1.45)
        pdf.savefig(f); plt.close(f)

    return pdf_path


def main() -> None:
    with open(RES_DIR / "resumen_fase4_completo.json", "r", encoding="utf-8") as f:
        R = json.load(f)

    viz_paths = [
        fig_01_demanda_vs_adopcion(R),
        fig_02_matriz_volumen_vs_salario(R),
        fig_03_mapa_calor_tecnologias(R),
        fig_04_bandas_experiencia(R),
        fig_05_modalidades_y_causalidad(R),
        fig_06_latam_y_tamano_empresa(R),
        fig_07_evolucion_dss_2020_2024(R),
    ]
    xlsx_path = exportar_excel_tableau()
    pdf_path = render_deck_ejecutivo_pdf(viz_paths)

    summary = {
        "visualizaciones_png": [{"file": p.name, "bytes": p.stat().st_size} for p in viz_paths],
        "excel_tableau": {"file": xlsx_path.name, "bytes": xlsx_path.stat().st_size},
        "presentacion_pdf": {"file": pdf_path.name, "bytes": pdf_path.stat().st_size},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
