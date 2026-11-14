-- =============================================================================
-- FASE 4: ANALIZAR (ANALYZE) — CONSULTAS SQL RELACIONALES (SQLite / Curso 5)
-- Estudio de Caso 3 (Pista B): Mercado Laboral y Salarios Tech (Chile y LatAm)
-- Técnicas aplicadas del Curso 5:
--   CREATE TEMP TABLE, LEFT JOIN, INNER JOIN, COUNT(DISTINCT ...), CASE WHEN,
--   COALESCE, HAVING (control muestral N >= 30 y >= 20% presencia), GROUP BY,
--   ORDER BY y control explícito contra duplicación de filas en uniones 1:N.
-- Nota: Poblaciones distintas se analizan por separado (sin fusionar filas).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- PASO PREVIO: Tablas temporales de denominadores globales (CREATE TEMP TABLE)
-- -----------------------------------------------------------------------------
-- [SQL_SETUP]
CREATE TEMP TABLE tmp_denominadores AS
SELECT
    'GetOnBoard_2026' AS fuente,
    COUNT(DISTINCT job_id) AS n_total,
    COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) AS n_salario_valido
FROM vacantes
UNION ALL
SELECT
    'StackOverflow_LatAm_2024' AS fuente,
    COUNT(DISTINCT ResponseId) AS n_total,
    COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN ResponseId END) AS n_salario_valido
FROM so_encuestados
UNION ALL
SELECT
    'StackOverflow_Chile_2024' AS fuente,
    COUNT(DISTINCT CASE WHEN es_chile = 1 THEN ResponseId END) AS n_total,
    COUNT(DISTINCT CASE WHEN es_chile = 1 AND salario_valido_flag = 1 THEN ResponseId END) AS n_salario_valido
FROM so_encuestados;

-- -----------------------------------------------------------------------------
-- Q01 (Control de Integridad sin Duplicación 1:N con LEFT JOIN + COALESCE)
-- Verifica que el denominador completo (679 GOB y 3.074 SO LatAm) no se pierda
-- ni se multiplique al unir las tablas largas de tecnologías.
-- -----------------------------------------------------------------------------
-- [QUERY: q01_control_integridad_left_join]
SELECT
    'Get on Board 2026 (Chile/Remoto)' AS poblacion,
    COUNT(DISTINCT v.job_id) AS registros_unicos,
    COUNT(h.tecnologia) AS filas_expandidas_1aN,
    COUNT(DISTINCT CASE WHEN h.tecnologia IS NULL THEN v.job_id END) AS registros_sin_tecnologia_coalesce,
    ROUND(AVG(CASE WHEN v.salario_valido_flag = 1 THEN v.salario_mensual_usd END), 2) AS media_con_duplicacion_join_1aN
FROM vacantes AS v
LEFT JOIN vacante_habilidades AS h
    ON v.job_id = h.job_id
UNION ALL
SELECT
    'Stack Overflow 2024 (LatAm 19)' AS poblacion,
    COUNT(DISTINCT s.ResponseId) AS registros_unicos,
    COUNT(t.tecnologia) AS filas_expandidas_1aN,
    COUNT(DISTINCT CASE WHEN COALESCE(t.tecnologia, 'SIN_TECNOLOGIA') = 'SIN_TECNOLOGIA' THEN s.ResponseId END) AS registros_sin_tecnologia_coalesce,
    ROUND(AVG(CASE WHEN s.salario_valido_flag = 1 THEN s.salario_mensual_usd END), 2) AS media_con_duplicacion_join_1aN
FROM so_encuestados AS s
LEFT JOIN so_tecnologias AS t
    ON s.ResponseId = t.ResponseId;

-- -----------------------------------------------------------------------------
-- Q02 (Pregunta 1 — Demanda en Get on Board vs Adopción Chile y LatAm en SO)
-- Tablas temporales pre-agregadas con COUNT(DISTINCT) + LEFT JOIN / INNER JOIN
-- para comparar tecnologías sin duplicar filas al unir ni mezclar poblaciones.
-- -----------------------------------------------------------------------------
-- [SQL_SETUP]
CREATE TEMP TABLE tmp_gob_tech AS
SELECT
    COALESCE(h.tipo_tecnologia, 'Sin mención taxonómica') AS tipo_tecnologia,
    COALESCE(h.tecnologia, 'Sin mención taxonómica') AS tecnologia,
    COUNT(DISTINCT v.job_id) AS n_ofertas,
    ROUND(
        100.0 * COUNT(DISTINCT v.job_id) /
        (SELECT COUNT(DISTINCT job_id) FROM vacantes),
        2
    ) AS pct_demanda_gob_total,
    COUNT(DISTINCT CASE WHEN v.alcance_geo = 'Chile Local' THEN v.job_id END) AS n_gob_chile_local,
    COUNT(DISTINCT CASE WHEN v.alcance_geo = 'Remoto Global/LatAm' THEN v.job_id END) AS n_gob_remoto
FROM vacantes AS v
LEFT JOIN vacante_habilidades AS h
    ON v.job_id = h.job_id
GROUP BY 1, 2;

-- [SQL_SETUP]
CREATE TEMP TABLE tmp_so_tech AS
SELECT
    COALESCE(t.tipo_tecnologia, 'Sin mención taxonómica') AS tipo_tecnologia,
    COALESCE(t.tecnologia, 'Sin mención taxonómica') AS tecnologia,
    COUNT(DISTINCT s.ResponseId) AS n_latam,
    ROUND(
        100.0 * COUNT(DISTINCT s.ResponseId) /
        (SELECT COUNT(DISTINCT ResponseId) FROM so_encuestados),
        2
    ) AS pct_adopcion_latam,
    COUNT(DISTINCT CASE WHEN s.es_chile = 1 THEN s.ResponseId END) AS n_chile,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN s.es_chile = 1 THEN s.ResponseId END) /
        (SELECT COUNT(DISTINCT ResponseId) FROM so_encuestados WHERE es_chile = 1),
        2
    ) AS pct_adopcion_chile
FROM so_encuestados AS s
LEFT JOIN so_tecnologias AS t
    ON s.ResponseId = t.ResponseId
GROUP BY 1, 2;

-- [QUERY: q02_tecnologias_cruce_demanda_vs_adopcion]
SELECT
    g.tipo_tecnologia,
    g.tecnologia,
    g.n_ofertas AS gob_n_ofertas,
    g.pct_demanda_gob_total,
    g.n_gob_chile_local,
    g.n_gob_remoto,
    s.n_chile AS so_n_chile,
    s.pct_adopcion_chile,
    s.n_latam AS so_n_latam,
    s.pct_adopcion_latam,
    CASE
        WHEN g.pct_demanda_gob_total >= 20.0 AND s.pct_adopcion_latam >= 20.0 THEN 'Cumple Meta >=20% en Demanda y Adopción'
        WHEN g.pct_demanda_gob_total >= 20.0 THEN 'Cumple Meta >=20% en Demanda GOB'
        WHEN s.pct_adopcion_latam >= 20.0 THEN 'Cumple Meta >=20% en Adopción SO'
        ELSE 'Bajo 20% (Nicho / Especialidad)'
    END AS estado_objetivo_metrico_1
FROM tmp_gob_tech AS g
INNER JOIN tmp_so_tech AS s
    ON g.tipo_tecnologia = s.tipo_tecnologia
   AND g.tecnologia = s.tecnologia
WHERE g.tecnologia <> 'Sin mención taxonómica'
ORDER BY g.tipo_tecnologia, g.n_ofertas DESC;

-- -----------------------------------------------------------------------------
-- Q03 (Pregunta 1 — Filtro Objetivo Métrico #1 con HAVING >= 20% en Demanda)
-- -----------------------------------------------------------------------------
-- [QUERY: q03_gob_tecnologias_meta_20pct_having]
SELECT
    h.tipo_tecnologia,
    h.tecnologia,
    COUNT(DISTINCT v.job_id) AS n_ofertas,
    ROUND(100.0 * COUNT(DISTINCT v.job_id) / 679.0, 2) AS pct_demanda_gob
FROM vacantes AS v
INNER JOIN vacante_habilidades AS h
    ON v.job_id = h.job_id
GROUP BY h.tipo_tecnologia, h.tecnologia
HAVING (100.0 * COUNT(DISTINCT v.job_id) / 679.0) >= 20.0
ORDER BY pct_demanda_gob DESC;

-- -----------------------------------------------------------------------------
-- Q04 (Pregunta 2 — Compensación y Regla N >= 30 por Nivel de Experiencia GOB)
-- Usa CASE WHEN para clasificar grupos válidos vs exploratorios/insuficientes.
-- -----------------------------------------------------------------------------
-- [QUERY: q04_gob_salarios_por_seniority]
SELECT
    seniority_nivel,
    COUNT(DISTINCT job_id) AS total_ofertas_publicadas,
    COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) AS n_salarios_validos,
    ROUND(AVG(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_usd END), 2) AS media_mensual_usd,
    MIN(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_usd END) AS min_mensual_usd,
    MAX(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_usd END) AS max_mensual_usd,
    CASE
        WHEN COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) >= 30
            THEN 'Válido N >= 30 (Inferencia)'
        WHEN COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) >= 15
            THEN 'Exploratorio N < 30 (Limitación muestral)'
        ELSE 'Excluido de inferencia (N < 15)'
    END AS estado_regla_n30
FROM vacantes
GROUP BY seniority_nivel
ORDER BY n_salarios_validos DESC;

-- -----------------------------------------------------------------------------
-- Q05 (Pregunta 2 — Experiencia Profesional en Stack Overflow LatAm con HAVING N >= 30)
-- -----------------------------------------------------------------------------
-- [QUERY: q05_so_latam_salarios_por_experiencia]
SELECT
    tramo_experiencia,
    COUNT(DISTINCT ResponseId) AS n_encuestados_con_salario,
    ROUND(AVG(salario_mensual_usd), 2) AS media_mensual_usd,
    ROUND(AVG(salario_mensual_clp_ref), 0) AS media_mensual_clp_ref,
    MIN(salario_mensual_usd) AS min_mensual_usd,
    MAX(salario_mensual_usd) AS max_mensual_usd
FROM so_encuestados
WHERE salario_valido_flag = 1
  AND tramo_experiencia <> 'Sin dato'
GROUP BY tramo_experiencia
HAVING COUNT(DISTINCT ResponseId) >= 30
ORDER BY
    CASE tramo_experiencia
        WHEN '0-1 años (<2)' THEN 1
        WHEN '2-4 años' THEN 2
        WHEN '5-9 años' THEN 3
        WHEN '10+ años' THEN 4
        ELSE 5
    END;

-- -----------------------------------------------------------------------------
-- Q06 (Pregunta 3 — Modalidad Laboral en Get on Board + Alcance Geográfico + INE)
-- -----------------------------------------------------------------------------
-- [QUERY: q06_gob_salarios_por_modalidad_y_alcance]
SELECT
    v.modalidad_grupo,
    COUNT(DISTINCT v.job_id) AS n_salarios_validos,
    ROUND(AVG(v.salario_mensual_usd), 2) AS media_mensual_usd,
    ROUND(AVG(v.salario_mensual_clp_ref), 0) AS media_mensual_clp_ref,
    ROUND(
        AVG(v.salario_mensual_clp_ref) /
        (SELECT monto_clp_mensual FROM ine_esi_2025 WHERE indicador LIKE '%Mediano%'),
        2
    ) AS ratio_media_vs_mediana_ine_2025,
    COUNT(DISTINCT CASE WHEN v.alcance_geo = 'Chile Local' THEN v.job_id END) AS n_chile_local,
    COUNT(DISTINCT CASE WHEN v.alcance_geo = 'Remoto Global/LatAm' THEN v.job_id END) AS n_remoto_global
FROM vacantes AS v
WHERE v.salario_valido_flag = 1
GROUP BY v.modalidad_grupo
HAVING COUNT(DISTINCT v.job_id) >= 30
ORDER BY media_mensual_usd DESC;

-- -----------------------------------------------------------------------------
-- Q07 (Pregunta 3 — Modalidad Laboral en Stack Overflow LatAm vs Línea Base INE)
-- -----------------------------------------------------------------------------
-- [QUERY: q07_so_latam_salarios_por_modalidad]
SELECT
    modalidad_grupo,
    COUNT(DISTINCT ResponseId) AS n_salarios_validos,
    ROUND(AVG(salario_mensual_usd), 2) AS media_mensual_usd,
    ROUND(AVG(salario_mensual_clp_ref), 0) AS media_mensual_clp_ref,
    ROUND(
        AVG(salario_mensual_clp_ref) /
        (SELECT monto_clp_mensual FROM ine_esi_2025 WHERE indicador LIKE '%Mediano%'),
        2
    ) AS ratio_media_vs_mediana_ine_2025
FROM so_encuestados
WHERE salario_valido_flag = 1
  AND modalidad_grupo <> 'Sin dato'
GROUP BY modalidad_grupo
HAVING COUNT(DISTINCT ResponseId) >= 30
ORDER BY media_mensual_usd DESC;

-- -----------------------------------------------------------------------------
-- Q08 (Pregunta 4 — Tamaño de Empresa en Stack Overflow LatAm con HAVING N >= 30)
-- -----------------------------------------------------------------------------
-- [QUERY: q08_so_latam_salarios_por_tamano_empresa]
SELECT
    org_size_grupo,
    COUNT(DISTINCT ResponseId) AS n_salarios_validos,
    ROUND(AVG(salario_mensual_usd), 2) AS media_mensual_usd,
    ROUND(AVG(salario_mensual_clp_ref), 0) AS media_mensual_clp_ref,
    MIN(salario_mensual_usd) AS min_mensual_usd,
    MAX(salario_mensual_usd) AS max_mensual_usd
FROM so_encuestados
WHERE salario_valido_flag = 1
  AND org_size_grupo <> 'Sin dato / NS-NR'
GROUP BY org_size_grupo
HAVING COUNT(DISTINCT ResponseId) >= 30
ORDER BY
    CASE org_size_grupo
        WHEN 'Pequeña (1-99)' THEN 1
        WHEN 'Mediana (100-999)' THEN 2
        WHEN 'Grande (1.000+)' THEN 3
        ELSE 4
    END;

-- -----------------------------------------------------------------------------
-- Q09 (Pregunta 4 — Serie Histórica Data Science Salaries 2020–2024 por Año y Tamaño)
-- -----------------------------------------------------------------------------
-- [QUERY: q09_dss_evolucion_2020_2024_y_tamano]
SELECT
    work_year,
    tamano_es,
    COUNT(*) AS n_registros,
    ROUND(AVG(salario_mensual_usd), 2) AS media_mensual_usd,
    MIN(salario_mensual_usd) AS min_mensual_usd,
    MAX(salario_mensual_usd) AS max_mensual_usd
FROM dss_salarios
GROUP BY work_year, tamano_es
HAVING COUNT(*) >= 10
ORDER BY work_year ASC,
    CASE tamano_es
        WHEN 'Pequeña (Small)' THEN 1
        WHEN 'Mediana (Medium)' THEN 2
        WHEN 'Grande (Large)' THEN 3
    END;

-- -----------------------------------------------------------------------------
-- Q10 (Resumen Agregado País Chile vs LatAm en Stack Overflow 2024)
-- -----------------------------------------------------------------------------
-- [QUERY: q10_so_chile_vs_resto_latam]
SELECT
    subregion,
    COUNT(DISTINCT ResponseId) AS n_total_encuestados,
    COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN ResponseId END) AS n_salarios_validos,
    ROUND(AVG(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_usd END), 2) AS media_mensual_usd,
    ROUND(AVG(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_clp_ref END), 0) AS media_mensual_clp_ref
FROM so_encuestados
GROUP BY subregion
HAVING COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN ResponseId END) >= 30
ORDER BY media_mensual_usd DESC;

-- -----------------------------------------------------------------------------
-- Q11A (Matriz Demanda vs Compensación por Tecnología en Get on Board, N >= 30)
-- Nota: No existe duplicación de filas dentro de cada (tipo_tecnologia, tecnologia) porque
-- vacante_habilidades está deduplicada por (job_id, tipo_tecnologia, tecnologia).
-- -----------------------------------------------------------------------------
-- [QUERY: q11a_gob_tecnologia_vs_salario]
SELECT
    h.tipo_tecnologia,
    h.tecnologia,
    COUNT(DISTINCT v.job_id) AS n_ofertas_con_salario_valido,
    ROUND(AVG(v.salario_mensual_usd), 2) AS media_mensual_usd,
    MIN(v.salario_mensual_usd) AS min_mensual_usd,
    MAX(v.salario_mensual_usd) AS max_mensual_usd
FROM vacantes AS v
INNER JOIN vacante_habilidades AS h
    ON v.job_id = h.job_id
WHERE v.salario_valido_flag = 1
GROUP BY h.tipo_tecnologia, h.tecnologia
HAVING COUNT(DISTINCT v.job_id) >= 30
ORDER BY h.tipo_tecnologia, media_mensual_usd DESC;

-- -----------------------------------------------------------------------------
-- Q11B (Matriz Adopción vs Compensación por Tecnología en Stack Overflow LatAm, N >= 30)
-- -----------------------------------------------------------------------------
-- [QUERY: q11b_so_latam_tecnologia_vs_salario]
SELECT
    t.tipo_tecnologia,
    t.tecnologia,
    COUNT(DISTINCT s.ResponseId) AS n_encuestados_con_salario_valido,
    ROUND(AVG(s.salario_mensual_usd), 2) AS media_mensual_usd,
    MIN(s.salario_mensual_usd) AS min_mensual_usd,
    MAX(s.salario_mensual_usd) AS max_mensual_usd
FROM so_encuestados AS s
INNER JOIN so_tecnologias AS t
    ON s.ResponseId = t.ResponseId
WHERE s.salario_valido_flag = 1
GROUP BY t.tipo_tecnologia, t.tecnologia
HAVING COUNT(DISTINCT s.ResponseId) >= 30
ORDER BY t.tipo_tecnologia, media_mensual_usd DESC;

-- -----------------------------------------------------------------------------
-- Q12 (Correlación != Causalidad • Curso 6: Composición Seniority y Alcance por Modalidad GOB)
-- Explica la brecha de Remoto Local ($3.750 USD) frente a Presencial ($2.250 USD).
-- -----------------------------------------------------------------------------
-- [QUERY: q12_gob_modalidad_composicion_seniority]
SELECT
    modalidad_grupo,
    COUNT(DISTINCT job_id) AS n_salarios_validos,
    ROUND(AVG(salario_mensual_usd), 2) AS media_mensual_usd,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN seniority_nivel = 'Senior' THEN job_id END) / COUNT(DISTINCT job_id), 1) AS pct_senior,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN seniority_nivel = 'Semi-Senior' THEN job_id END) / COUNT(DISTINCT job_id), 1) AS pct_semi_senior,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN seniority_nivel IN ('Junior', 'Trainee') THEN job_id END) / COUNT(DISTINCT job_id), 1) AS pct_junior_trainee,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN seniority_nivel = 'Lead' THEN job_id END) / COUNT(DISTINCT job_id), 1) AS pct_lead,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN alcance_geo = 'Remoto Global/LatAm' THEN job_id END) / COUNT(DISTINCT job_id), 1) AS pct_alcance_remoto_global
FROM vacantes
WHERE salario_valido_flag = 1
GROUP BY modalidad_grupo
HAVING COUNT(DISTINCT job_id) >= 30
ORDER BY pct_senior DESC;

-- -----------------------------------------------------------------------------
-- Q13 (Categorías de Puesto Get on Board con Control N >= 30 • CASE WHEN)
-- -----------------------------------------------------------------------------
-- [QUERY: q13_gob_salarios_por_categoria]
SELECT
    categoria,
    COUNT(DISTINCT job_id) AS total_ofertas_publicadas,
    COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) AS n_salarios_validos,
    ROUND(AVG(CASE WHEN salario_valido_flag = 1 THEN salario_mensual_usd END), 2) AS media_mensual_usd,
    CASE
        WHEN COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) >= 30
            THEN 'Válido N >= 30 (Inferencia)'
        WHEN COUNT(DISTINCT CASE WHEN salario_valido_flag = 1 THEN job_id END) >= 15
            THEN 'Exploratorio N < 30 (Limitación muestral)'
        ELSE 'Excluido de inferencia (N < 15)'
    END AS estado_regla_n30
FROM vacantes
GROUP BY categoria
ORDER BY n_salarios_validos DESC;
