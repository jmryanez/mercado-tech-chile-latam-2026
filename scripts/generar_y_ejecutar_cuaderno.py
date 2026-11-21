#!/usr/bin/env python3
"""Generador y ejecutor de cuaderno Jupyter reproducible desde plantillas JSON y celdas de código."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient

BASE_DIR = Path(__file__).resolve().parent.parent
PLANTILLA_PATH = BASE_DIR / "scripts" / "plantillas" / "cuaderno_plantillas.json"
CIFRAS_PATH = BASE_DIR / "04_Fase_Analizar_Analyze" / "resumenes" / "cifras_oficiales.json"
NOTEBOOK_PATH = BASE_DIR / "06_Fase_Actuar_Act" / "kaggle_notebook_portafolio.ipynb"
DESCARGAS_PATH = BASE_DIR / "descargas" / "kaggle_notebook_portafolio.ipynb"

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


# Celdas de código reproducibles del cuaderno analítico
CODE_CELLS = {
    1: """from pathlib import Path
import glob
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configuración visual adaptada al estándar de accesibilidad del Curso 6
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.autolayout'] = True

# Detección determinista de rutas según el entorno (Kaggle o local)
LOCAL_DATA = Path("03_Fase_Procesar_Process/datos_limpios_processed")
KAGGLE_CANDIDATES = glob.glob("/kaggle/input/**/GetOnBoard_Vacantes_*.csv", recursive=True)

if KAGGLE_CANDIDATES:
    DATA_DIR = Path(KAGGLE_CANDIDATES[0]).parent
    print(f"Ambiente Kaggle detectado. Directorio de datos: {DATA_DIR}")
elif LOCAL_DATA.exists():
    DATA_DIR = LOCAL_DATA
    print(f"Ambiente local detectado. Directorio de datos: {DATA_DIR}")
else:
    DATA_DIR = Path(".")
    print(f"Directorio de datos por defecto: {DATA_DIR}")""",

    2: """# Ingesta de las 4 poblaciones validadas (Fase 2: Preparar • Cursos 3 y 4)
gob_vac = pd.read_csv(DATA_DIR / "GetOnBoard_Vacantes_2026_20261111_v01_clean.csv")
gob_hab = pd.read_csv(DATA_DIR / "GetOnBoard_Habilidades_2026_20261111_v01_clean.csv")
so_lat  = pd.read_csv(DATA_DIR / "StackOverflow_LatAm_2024_20261111_v01_clean.csv")
so_tec  = pd.read_csv(DATA_DIR / "StackOverflow_Tecnologias_2024_20261111_v01_clean.csv")
dss     = pd.read_csv(DATA_DIR / "DataScienceSalaries_2020_2024_20261111_v01_clean.csv")
ine     = pd.read_csv(DATA_DIR / "INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv")

print(f"Get on Board Vacantes: {len(gob_vac):,} filas | Habilidades: {len(gob_hab):,} filas")
print(f"Stack Overflow LatAm:  {len(so_lat):,} filas | Tecnologías: {len(so_tec):,} filas")
print(f"Data Science Salaries: {len(dss):,} filas")
mediana_ine = int(ine[ine['indicador'] == 'Ingreso Mediano Nacional Ocupados']['monto_clp_mensual'].iloc[0])
mediana_ine_usd = round(mediana_ine / 969.8, 2)
print(f"INE ESI 2025 Nacional = {mediana_ine:,} CLP ({mediana_ine_usd:,} USD aprox.)")""",

    4: """conn = sqlite3.connect(":memory:")
gob_vac.to_sql("vacantes", conn, index=False)
gob_hab.to_sql("vacante_habilidades", conn, index=False)
so_lat.to_sql("so_encuestados", conn, index=False)
so_tec.to_sql("so_tecnologias", conn, index=False)
dss.to_sql("dss", conn, index=False)
ine.to_sql("ine", conn, index=False)

q_integridad = \"\"\"
SELECT 
    'Get on Board 2026' AS poblacion,
    COUNT(DISTINCT v.job_id) AS total_vacantes_unicas,
    COUNT(h.job_id) AS filas_expandidas_1_n,
    ROUND(AVG(v.salario_mensual_usd), 2) AS media_correcta_sin_duplicacion,
    ROUND(AVG(v_dup.salario_mensual_usd), 2) AS media_naive_con_duplicacion
FROM vacantes v
LEFT JOIN vacante_habilidades h ON v.job_id = h.job_id
LEFT JOIN (
    SELECT v2.job_id, v2.salario_mensual_usd 
    FROM vacantes v2 
    JOIN vacante_habilidades h2 ON v2.job_id = h2.job_id
) v_dup ON 1=1
WHERE v.salario_valido_flag = 1
GROUP BY 1;
\"\"\"
df_int = pd.read_sql(q_integridad, conn)
display(df_int)""",

    6: """q_p1 = \"\"\"
SELECT 
    h.tecnologia,
    COUNT(DISTINCT h.job_id) AS ofertas_gob,
    ROUND(COUNT(DISTINCT h.job_id) * 100.0 / {{gob_total_scope.val}}, 2) AS pct_demanda_gob,
    COALESCE(t_so.pct_adopcion_chile, 0) AS pct_so_chile
FROM vacante_habilidades h
LEFT JOIN (
    SELECT 
        tecnologia,
        ROUND(COUNT(DISTINCT ResponseId) * 100.0 / {{so_chile_total.val}}, 2) AS pct_adopcion_chile
    FROM so_tecnologias
    WHERE pais = 'Chile'
    GROUP BY tecnologia
) t_so ON h.tecnologia = t_so.tecnologia
WHERE h.tecnologia IN ('SQL', 'AWS', 'Python', 'Microsoft Azure', 'Google Cloud', 'JavaScript')
GROUP BY h.tecnologia
ORDER BY pct_demanda_gob DESC;
\"\"\"
df_p1 = pd.read_sql(q_p1, conn)

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(df_p1))
width = 0.35

rects1 = ax.bar(x - width/2, df_p1['pct_demanda_gob'], width, label='Demanda Get on Board 2026 (N={{gob_total_scope.val}})', color='#1B365D')
rects2 = ax.bar(x + width/2, df_p1['pct_so_chile'], width, label='Uso en Chile Stack Overflow 2024 (N={{so_chile_total.val}})', color='#D97706')

ax.set_ylabel('% de Presencia / Adopción')
ax.set_title('Top Tecnologías: Demanda en Vacantes vs. Adopción Real (Chile)')
ax.set_xticks(x)
ax.set_xticklabels(df_p1['tecnologia'])
ax.legend()
ax.axhline(20.0, color='#DC2626', linestyle='--', linewidth=1.5, label='Umbral Mínimo de Presencia (20%)')

for r in rects1:
    h = r.get_height()
    ax.annotate(f'{h:.1f}%', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                textcoords="offset points", ha='center', fontsize=9, color='#1B365D', fontweight='bold')
for r in rects2:
    h = r.get_height()
    ax.annotate(f'{h:.1f}%', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                textcoords="offset points", ha='center', fontsize=9, color='#D97706', fontweight='bold')

ax.set_ylim(0, 70)
plt.show()""",

    8: """gob_sal = gob_vac[gob_vac['salario_valido_flag'] == True].copy()

def resumen_bandas(df):
    return df.groupby('seniority_nivel')['salario_mensual_usd'].agg(
        n='count',
        p25=lambda s: s.quantile(0.25),
        mediana='median',
        p75=lambda s: s.quantile(0.75)
    ).reset_index()

bandas_cl = resumen_bandas(gob_sal[gob_sal['alcance_geo'] == 'Chile Local'])
bandas_rem = resumen_bandas(gob_sal[gob_sal['alcance_geo'] == 'Remoto sin país declarado'])

fig, ax = plt.subplots(figsize=(9, 4.5))
niveles = ['Semi-Senior', 'Senior']
cl_plot = bandas_cl.set_index('seniority_nivel').reindex(niveles).reset_index()

y = np.arange(len(cl_plot))
ax.barh(y, cl_plot['p75'] - cl_plot['p25'], left=cl_plot['p25'], height=0.4, color='#93C5FD', label='Rango Intercuartil (p25–p75)')
ax.scatter(cl_plot['mediana'], y, color='#1B365D', s=100, zorder=5, label='Mediana (USD)')

for idx, row in cl_plot.iterrows():
    y_pos = y[idx]
    ax.text(row['mediana'], y_pos + 0.2, f"${row['mediana']:,.0f} (N={int(row['n'])})".replace(',', '.'),
            ha='center', fontweight='bold', color='#1B365D', fontsize=9)

ax.set_yticks(y)
ax.set_yticklabels(cl_plot['seniority_nivel'])
ax.set_xlabel('Salario Mensual (USD)')
ax.set_title('Bandas Salariales por Seniority: Chile Local (Get on Board 2026)')
ax.legend(loc='lower right')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}".replace(',', '.')))
plt.show()""",

    10: """comp_q12 = gob_sal.groupby(['modalidad_grupo', 'seniority_nivel']).size().unstack(fill_value=0)
print("=== COMPOSICIÓN MODALIDAD X SENIORITY (GOB) ===")
display(comp_q12)

med_cl_local = gob_sal[gob_sal['modalidad_grupo'] == 'Presencial']['salario_mensual_usd'].median()
med_hibrido  = gob_sal[gob_sal['modalidad_grupo'] == 'Híbrido']['salario_mensual_usd'].median()
med_rem_loc  = gob_sal[gob_sal['modalidad_grupo'] == 'Remoto Local']['salario_mensual_usd'].median()
med_ine_usd = 701.18

fig, ax = plt.subplots(figsize=(8, 4))
bar_data = pd.Series({
    'INE ESI 2025 (Nacional)': med_ine_usd,
    'Presencial (GOB)': med_cl_local,
    'Híbrido (GOB)': med_hibrido,
    'Remoto Local (GOB)': med_rem_loc
})

bars = ax.barh(bar_data.index, bar_data.values, color=['#9CA3AF', '#1B365D', '#0072B2', '#2563EB'], height=0.55)
for b in bars:
    w = b.get_width()
    ax.text(w + 50, b.get_y() + b.get_height()/2, f"${w:,.0f} USD".replace(',', '.'), va='center', fontweight='bold', fontsize=9)

ax.set_xlim(0, 4500)
ax.set_xlabel('Mediana Salarial Mensual (USD)')
ax.set_title('Mediana Salarial por Modalidad en Chile vs. Línea Base INE ESI 2025')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}".replace(',', '.')))
plt.show()""",

    12: """candidate_tlc = [
    DATA_DIR / "Matriz_TLC_19_Paises_LatAm.csv",
    Path("descargas/Matriz_TLC_19_Paises_LatAm.csv"),
    Path("../descargas/Matriz_TLC_19_Paises_LatAm.csv")
]
tlc_file = next((f for f in candidate_tlc if f.exists()), None)

if tlc_file:
    df_tlc = pd.read_csv(tlc_file)
    print(f"Cargando matriz TLC desde: {tlc_file}")
    display(df_tlc[['pais', 'n_sal', 'cumple_n30', 'med_usd', 'ic95_mediana_inf_usd', 'ic95_mediana_sup_usd']].head(10))
else:
    raise FileNotFoundError("Archivo Matriz_TLC_19_Paises_LatAm.csv no encontrado")

df_p4_plot = df_tlc[df_tlc['cumple_n30'] == True].sort_values('med_usd', ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(9, 5))
y_pos = np.arange(len(df_p4_plot))
xerr_inf = df_p4_plot['med_usd'] - df_p4_plot['ic95_mediana_inf_usd']
xerr_sup = df_p4_plot['ic95_mediana_sup_usd'] - df_p4_plot['med_usd']

colors_latam = ['#D97706' if p == 'Chile' else '#1B365D' for p in df_p4_plot['pais']]
ax.barh(y_pos, df_p4_plot['med_usd'], xerr=[xerr_inf, xerr_sup], capsize=4, color=colors_latam, height=0.55, 
        error_kw={'elinewidth': 1.5, 'ecolor': '#4B5563'})

for idx, row in df_p4_plot.iterrows():
    ax.text(row['ic95_mediana_sup_usd'] + 100, idx, f"${row['med_usd']:,.0f} (N={int(row['n_sal'])})".replace(',', '.'),
            va='center', fontsize=9, fontweight='bold', color='#1B365D')

ax.set_yticks(y_pos)
ax.set_yticklabels(df_p4_plot['pais'])
ax.set_xlabel('Mediana Salarial Mensual (USD)')
ax.set_title('Latinoamérica (N >= 30): Medianas e IC 95% Bootstrap de la Mediana')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}".replace(',', '.')))
ax.set_xlim(0, 7500)
plt.show()""",

    14: """candidate_ic = [
    Path("04_Fase_Analizar_Analyze/resumenes/resumen_ic_diferencias.csv"),
    Path("../04_Fase_Analizar_Analyze/resumenes/resumen_ic_diferencias.csv"),
    DATA_DIR / "resumen_ic_diferencias.csv"
]
ic_file = next((f for f in candidate_ic if f.exists()), None)

if ic_file:
    df_ic = pd.read_csv(ic_file)
    print("=== INTERVALOS DE CONFIANZA BOOTSTRAP DEL 95% PARA DIFERENCIAS DE MEDIANAS ===")
    display(df_ic[['comparacion', 'diferencia_observada_usd', 'ic95_inf_usd', 'ic95_sup_usd', 'concluyente']])
else:
    raise FileNotFoundError("Archivo resumen_ic_diferencias.csv no encontrado")"""
}


def build_notebook() -> nbformat.NotebookNode:
    nb = new_notebook()
    nb.metadata = {
        "language_info": {"name": "python", "version": "3.14.0"},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
    }
    with open(CIFRAS_PATH, "r", encoding="utf-8") as f:
        cifras = json.load(f)
    with open(PLANTILLA_PATH, "r", encoding="utf-8") as f:
        md_dict = json.load(f)

    cells = []
    for idx in range(16):
        if idx in CODE_CELLS:
            src = render_texto(CODE_CELLS[idx], cifras)
            cells.append(new_code_cell(src))
        else:
            raw_src = md_dict[idx]["source"] if isinstance(md_dict, list) else md_dict.get(f"cell_{idx}", md_dict.get(str(idx), ""))
            src = render_texto(raw_src, cifras)
            cells.append(new_markdown_cell(src))
    nb.cells = cells
    return nb


def main():
    print("Construyendo cuaderno Jupyter desde plantillas...")
    nb = build_notebook()

    print(f"Ejecutando cuaderno con NotebookClient en {BASE_DIR}...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute(cwd=BASE_DIR)

    print(f"Guardando cuaderno ejecutado en {NOTEBOOK_PATH}...")
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print(f"Copiando cuaderno ejecutado a {DESCARGAS_PATH}...")
    shutil.copyfile(NOTEBOOK_PATH, DESCARGAS_PATH)

    res = subprocess.run(["cmp", NOTEBOOK_PATH, DESCARGAS_PATH], capture_output=True, text=True)
    if res.returncode == 0:
        print("Verificación cmp exitosa: ambas copias del cuaderno son idénticas byte por byte.")
    else:
        print("ERROR: Las copias del cuaderno difieren:", res.stderr)
        exit(1)


if __name__ == "__main__":
    main()
