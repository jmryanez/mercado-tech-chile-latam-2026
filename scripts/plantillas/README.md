# Mercado Laboral y Salarios en Tecnología en Chile y Latinoamérica (2024–2026)

*Caso de estudio con cliente y partes interesadas simulados (ejercicio académico)*

🌐 **Sitio Web Oficial (GitHub Pages):** [https://jmryanez.github.io/mercado-tech-chile-latam-2026/](https://jmryanez.github.io/mercado-tech-chile-latam-2026/)  
📁 **Repositorio en GitHub:** [https://github.com/jmryanez/mercado-tech-chile-latam-2026](https://github.com/jmryanez/mercado-tech-chile-latam-2026)  
👤 **Autor:** Manuel Yáñez Orellana • **Rótulo profesional:** Analista de Datos  
🎓 **Credencial:** Certificado Profesional de Análisis de Datos de Google (Google Data Analytics Professional Certificate), Google / Coursera, noviembre 2026 • [https://www.credly.com/users/manuel-yanez](https://www.credly.com/users/manuel-yanez)  
🏢 **Patrocinadores simulados:** Consultora de Recursos Humanos Tech & Academia de Formación Digital (Chile)  
📊 **Estado de entregables externos:**  
- Tablero en Tableau Public: [Mercado Tech Chile y LatAm 2024-2026](https://public.tableau.com/app/profile/manuel.y.ez/viz/MercadoTechChileyLatAm2024-2026/1_Brechadehabilidadesysalarios)  
- Cuaderno y dataset en Kaggle: [cuaderno](https://www.kaggle.com/code/manuelyanezorellana/mercado-tech-chile-y-latam-2024-2026-analisis) y [dataset agregado](https://www.kaggle.com/datasets/manuelyanezorellana/mercado-tech-chile-y-latam-2024-2026)  

---

## Síntesis Ejecutiva

Este proyecto investiga qué tecnologías concentran la demanda laboral vigente aplicable a Chile (**Get on Board API v0**, corte 2026-11-10 GMT-3, N = {{gob_total_ofertas.val}} ofertas / N = {{gob_salarios_validos_total.val}} salarios válidos) frente a la adopción técnica declarada en Chile y Latinoamérica (**Stack Overflow Developer Survey 2024**, 19 países, N = {{so_latam_encuestados_total.val}} encuestados / N = {{so_latam_salarios_validos.val}} salarios válidos; Chile N = {{so_chile_encuestados.val}} / N = {{so_chile_salarios_validos.val}} salarios), contextualizadas contra la serie internacional **Data Science Salaries 2020–2024** (N = {{dss_total_registros.val}} registros en total; N = {{dss_eeuu_total.val}} residentes en EE.UU.) y la línea base nacional chilena **INE ESI 2025** ({{ine_esi_mediana_clp.str}}/mes mediana = {{ine_esi_mediana_usd.str}} al Dólar Observado BCCh de {{dolar_observado_bcch.str}} CLP/USD al 2026-11-10; media {{ine_media_clp.str}} CLP = {{ine_media_usd.str}}).

Las 4 poblaciones se analizan **de forma estrictamente separada** (sin promediar ni fusionar registros entre encuestas y bolsas de empleo) y bajo control de tamaño muestral **N >= 30** (**Curso 4, Módulo 1**).

---

## Conclusiones Estratégicas del Negocio (Fase 6 • Actuar)

### 1. Demanda vs. Adopción Tecnológica (P1)
3 tecnologías superan el 20% de las ofertas en Get on Board: SQL ({{gob_demanda_sql_pct.str}}, N={{gob_demanda_sql_n.val}}), AWS ({{gob_demanda_aws_pct.str}}, N={{gob_demanda_aws_n.val}}) y Python ({{gob_demanda_python_pct.str}}, N={{gob_demanda_python_n.val}}). En plataformas Cloud, solo AWS supera el umbral del 20%, mientras que Google Cloud ({{gob_demanda_gcp_pct.str}}, N={{gob_demanda_gcp_n.val}}) y Microsoft Azure ({{gob_demanda_azure_pct.str}}, N={{gob_demanda_azure_n.val}}) se sitúan por debajo del umbral estratégico. La diferencia entre la demanda de Azure ({{gob_demanda_azure_pct.str}}) y su adopción en Chile ({{so_chile_adopcion_azure_pct.str}}, {{tech_azure_moe_chile.str}}) está dentro del margen de error muestral.

![Demanda vs Adopción Top 3](05_Fase_Compartir_Share/visualizaciones/01_demanda_vs_adopcion_top5_p1.png)

### 2. Progresión Salarial y Bandas de Seniority (P2)
En Chile Local (Get on Board 2026), la mediana salarial es {{gob_cl_semi_senior_mediana.str}} USD en Semi-Senior (N={{gob_cl_semi_senior_n.val}}, p25 {{gob_cl_semi_senior_p25.str}}, p75 {{gob_cl_semi_senior_p75.str}}) y {{gob_cl_senior_mediana.str}} USD en Senior (N={{gob_cl_senior_n.val}}, p25 {{gob_cl_senior_p25.str}}, p75 {{gob_cl_senior_p75.str}}), representando un salto de {{gob_cl_salto_semi_senior_pct.str}} en mediana. Si se considera el conjunto total de Get on Board (Chile + remotas sin país declarado), la mediana Semi-Senior es {{gob_total_semi_senior_mediana.str}} (N={{gob_total_semi_senior_mediana.n}}) y Senior {{gob_total_senior_mediana.str}} (N={{gob_total_senior_mediana.n}}), con un salto de {{gob_total_salto_semi_senior_pct.str}}. En Stack Overflow Chile agregado (N={{so_chile_salarios_validos.val}}), la mediana es {{so_chile_mediana.str}} USD ({{so_chile_pesos_ref.str}}).

![Bandas Salariales por Seniority](05_Fase_Compartir_Share/visualizaciones/04_bandas_salariales_experiencia_p2.png)

### 3. Modalidad Laboral, Alcance y Comparación INE (P3)
La mayor proporción de cargos Senior y Lead en remoto no explica toda la diferencia: entre cargos Senior, las ofertas remotas sin país declarado tienen mediana {{gob_senior_remoto_mediana.str}} frente a {{gob_senior_local_mediana.str}} en Chile Local (diferencia concluyente: {{ic_senior_remoto_vs_local_diff.str}} USD, IC 95% bootstrap [{{ic_senior_remoto_vs_local_ci95_inf.str}}, {{ic_senior_remoto_vs_local_ci95_sup.str}}]); entre Semi-Senior la remota es menor ({{gob_semi_remoto_mediana.str}} vs {{gob_semi_local_mediana.str}}, diferencia no concluyente: {{ic_semi_remoto_vs_local_diff.str}}, IC 95% [{{ic_semi_remoto_vs_local_ci95_inf.str}}, {{ic_semi_remoto_vs_local_ci95_sup.str}}]). Modalidad y alcance no se pueden separar con estos datos, y no se sabe si las ofertas remotas admiten residentes en Chile. Frente a la mediana nacional del INE ESI 2025 ({{ine_esi_mediana_clp.str}} / {{ine_esi_mediana_usd.str}}), los cargos Semi-Senior en Chile Local ({{gob_cl_semi_senior_mediana.str}} USD mediana) representan {{ratio_cl_semi_vs_ine_mediana.str}} la mediana del INE ({{salto_cl_semi_vs_ine_pct.str}}).

![Modalidades vs INE y Causalidad](05_Fase_Compartir_Share/visualizaciones/05_modalidades_vs_ine_y_causalidad_p3_q12.png)

### 4. Posicionamiento Regional y Serie Temporal (P4)
En Latinoamérica (Stack Overflow 2024, N ≥ 30), Uruguay registra la mayor mediana muestral ({{so_uruguay_mediana.str}} USD, N={{so_uruguay_n.val}}). Chile ({{so_chile_mediana.str}} USD, N={{so_chile_salarios_validos.val}}) se sitúa en un grupo estadísticamente no diferenciable frente a Argentina ({{so_argentina_mediana.str}} USD, N={{so_argentina_n.val}}), México ({{so_mexico_mediana.str}} USD, N={{so_mexico_n.val}}) y Colombia ({{so_colombia_mediana.str}} USD, N={{so_colombia_n.val}}) (todos los intervalos de confianza bootstrap del 95% de las diferencias con Chile incluyen el 0). Brasil registra {{so_brasil_mediana.str}} USD (N={{so_brasil_n.val}}) y Venezuela {{so_venezuela_mediana.str}} USD (N={{so_venezuela_n.val}}). En Data Science Salaries (residentes en EE.UU.), la mediana pasó de {{dss_eeuu_2020_mediana.str}} USD en 2020 (N={{dss_eeuu_2020_mediana.n}} < 30) a {{dss_eeuu_2023_mediana.str}} USD en 2023 (N={{dss_eeuu_2023_mediana.n}}) y {{dss_eeuu_2024_mediana.str}} USD en 2024 (N={{dss_eeuu_2024_mediana.n}}).

![Posicionamiento Regional LatAm](05_Fase_Compartir_Share/visualizaciones/06_paises_latam_y_tamano_empresa_p4.png)
![Evolución Temporal DSS EE.UU.](05_Fase_Compartir_Share/visualizaciones/07_evolucion_dss_2020_2024_p4.png)

### 5. Matriz Volumen vs. Compensación y Efecto Cloud (Q11)
Al cruzar volumen de demanda con salarios en Senior de Get on Board, las vacantes que solicitan plataformas Cloud presentan una mediana de {{gob_senior_cloud_mediana.str}} USD (N={{gob_senior_cloud_n.val}}) frente a {{gob_senior_sin_cloud_mediana.str}} USD (N={{gob_senior_sin_cloud_n.val}}) en vacantes sin Cloud (diferencia observada de {{gob_senior_cloud_diff.str}} USD). No obstante, los intervalos de confianza bootstrap del 95% incluyen el 0, por lo que la diferencia no resulta concluyente al controlar por seniority.

![Matriz Volumen vs Salario](05_Fase_Compartir_Share/visualizaciones/02_matriz_volumen_vs_salario_q11.png)

---

## Tabla de Recomendaciones Estratégicas (Fase 6 • Actuar)

A partir de los hallazgos con representatividad estadística, se establece la siguiente matriz de implementación Qué / Quién / Cuándo / KPI:

| # | Qué hay que hacer (Acción concreta) | Quién debería hacerlo | Cuándo (Plazo) | Indicador Clave de Rendimiento (KPI) |
|---|---|---|---|---|
| **1** | Alinear currículo formativo a las 3 tecnologías líderes (SQL, AWS, Python) con electivos en cloud computing. | Academia de formación digital | Trimestre 1 (Q1) | Porcentaje de cobertura de tecnologías top en sílabos (meta: ≥ 80% sobre las 3 tecnologías ≥ 20%). |
| **2** | Calibrar bandas salariales diferenciando explícitamente entre vacantes de Chile Local y Remoto sin país declarado. | Consultora de RRHH tech | Trimestre 1 (Q1) | Tasa de ofertas con salario publicado clasificadas por alcance local vs remoto (meta: 100%). |
| **3** | Diseñar rutas de transición y nivelación técnica de Semi-Senior a Senior con foco en diseño de sistemas y arquitectura cloud. | Academia y Consultora en conjunto | Trimestre 2 (Q2) | Brecha porcentual observada entre tramos Semi-Senior y Senior ({{gob_cl_salto_semi_senior_pct.str}} en Chile Local). |

---

## Estructura del Repositorio

```text
{{tree}}
```

---

## Cómo Reproducir este Proyecto

### Requisitos Previos
- Python 3.10 o superior
- Git

### Instrucciones Paso a Paso
```bash
# 1. Clonar el repositorio
git clone https://github.com/jmryanez/mercado-tech-chile-latam-2026.git
cd mercado-tech-chile-latam-2026

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el orquestador maestro reproducible
python3 scripts/ejecutar_todo.py
```
