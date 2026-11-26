# Celdas vacías en los datos publicados

Las celdas vacías no son datos perdidos: cada columna con celdas vacías tiene un motivo, explicado aquí. En Tableau aparecen como NULL. Este archivo se genera desde scripts/celdas_vacias.json, el mismo registro que usan la hoja LEEME_Poblaciones del Excel de Tableau y las descripciones de columnas del dataset de Kaggle.

## Archivos CSV (carpeta descargas, zip de GitHub y dataset de Kaggle)

### Matriz_TLC_19_Paises_LatAm.csv

- `ic95_mediana_inf_usd`: Vacío en los países con menos de 30 salarios válidos (exploratorios): no se calcula intervalo de confianza.
- `ic95_mediana_sup_usd`: Vacío en los países con menos de 30 salarios válidos (exploratorios): no se calcula intervalo de confianza.

### StackOverflow_LatAm_2024_20261111_v01_clean.csv

- `years_code_pro_num`: Vacío cuando la encuesta no trae años de experiencia profesional (YearsCodePro sin respuesta).
- `salary_yearly_usd_raw`: Vacío cuando la encuesta no trae la remuneración anual convertida a USD (ConvertedCompYearly): la persona no la declaró o Stack Overflow no la convirtió.
- `salary_yearly_usd_clean`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_usd`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_clp_ref`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `motivo_exclusion_salario`: Vacío cuando el salario es válido o la remuneración no viene convertida a USD en la encuesta: solo se llena cuando un salario se anuló.

### gob_agregado_bandas_chile_local.csv

- `media_usd`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `mediana_usd`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `p25_usd`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `p75_usd`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `amplitud_p25_p75_usd`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `mediana_clp_ref`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.
- `media_clp_ref`: Vacío en el grupo con menos de 15 ofertas con sueldo válido: de ese grupo solo se publica el N.

### gob_agregado_modalidad_vs_ine.csv

- `nota`: Vacío en las filas de Stack Overflow, porque la nota se refiere solo a Get on Board.

### StackOverflow_LatAm_19_Paises_2024.csv

- `years_code_pro_num`: Vacío cuando la encuesta no trae años de experiencia profesional (YearsCodePro sin respuesta).
- `salary_yearly_usd_raw`: Vacío cuando la encuesta no trae la remuneración anual convertida a USD (ConvertedCompYearly): la persona no la declaró o Stack Overflow no la convirtió.
- `salary_yearly_usd_clean`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_usd`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_clp_ref`: Vacío cuando no hay salario válido: la remuneración no viene convertida a USD en la encuesta o se anuló (el motivo está en motivo_exclusion_salario).
- `motivo_exclusion_salario`: Vacío cuando el salario es válido o la remuneración no viene convertida a USD en la encuesta: solo se llena cuando un salario se anuló.

### Bandas_Salariales_y_Saltos_Seniority.csv

- `ic95_mediana_inf_usd`: Vacío en los grupos con menos de 5 salarios válidos: con tan pocos datos no se calcula intervalo de confianza.
- `ic95_mediana_sup_usd`: Vacío en los grupos con menos de 5 salarios válidos: con tan pocos datos no se calcula intervalo de confianza.

### GetOnBoard_Vacantes_Auditadas_679.csv

- `sal_usd`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló en la limpieza.
- `sal_clp`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló en la limpieza.

### GetOnBoard_Vacantes_2026_20261111_v01_clean.csv

- `min_salary_usd_raw`: Vacío cuando la oferta no publica sueldo.
- `max_salary_usd_raw`: Vacío cuando la oferta no publica sueldo.
- `min_salary_usd_clean`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló (el motivo está en motivo_exclusion_salario).
- `max_salary_usd_clean`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_usd`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló (el motivo está en motivo_exclusion_salario).
- `salario_mensual_clp_ref`: Vacío cuando la oferta no tiene sueldo válido: no lo publica o se anuló (el motivo está en motivo_exclusion_salario).
- `motivo_exclusion_salario`: Vacío cuando el sueldo es válido o no se publica: solo se llena cuando un sueldo publicado se anuló.

## Excel de Tableau Public (Datos_Consolidados_Tableau_Public.xlsx)

### Hoja P1_Tecnologias_Largo

- `moe_pp`: Vacía en las filas de Get on Board: es un conteo de las ofertas de Get on Board en el alcance del estudio al corte, no una muestra de encuesta, así que no lleva margen de error muestral.

### Hoja P2_Experiencia

- `seniority_nivel`: Vacía en las filas de Stack Overflow y Data Science Salaries. Cada fuente guarda su experiencia en su propia columna: Get on Board en seniority_nivel, Stack Overflow en tramo_experiencia y Data Science Salaries en experiencia_es.
- `tramo_experiencia`: Vacía en las filas de Get on Board y Data Science Salaries, porque solo Stack Overflow usa tramos de años de experiencia.
- `experiencia_es`: Vacía en las filas de Get on Board y Stack Overflow, porque solo Data Science Salaries usa estos niveles.
- `min_usd`: Vacía en las filas de Get on Board: no se publican mínimos para no exponer ofertas individuales.
- `max_usd`: Vacía en las filas de Get on Board: no se publican máximos para no exponer ofertas individuales.

### Hoja Q11_Tech_vs_Salario

- `min_usd`: Vacía en las filas de Get on Board: no se publican mínimos para no exponer ofertas individuales.
- `max_usd`: Vacía en las filas de Get on Board: no se publican máximos para no exponer ofertas individuales.
- `gob_n_ofertas`: Vacía en las filas de Stack Overflow, porque es un dato de Get on Board.
- `pct_demanda_gob_total`: Vacía en las filas de Stack Overflow, porque es un dato de Get on Board.
- `so_n_latam`: Vacía en las filas de Get on Board, porque es un dato de Stack Overflow.
- `pct_adopcion_latam`: Vacía en las filas de Get on Board, porque es un dato de Stack Overflow.

### Hoja Q13_Categorias_GOB

- `media_usd`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `mediana_usd`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `p25_usd`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `p75_usd`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `amplitud_p25_p75_usd`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `mediana_clp_ref`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.
- `media_clp_ref`: Vacía en las categorías con menos de 15 ofertas con sueldo válido: de esos grupos solo se publica el N.

### Hoja Mapa_LatAm_19_Paises

- `ic95_mediana_inf_usd`: Vacía en los países con menos de 30 salarios válidos (exploratorios): no se calcula intervalo de confianza.
- `ic95_mediana_sup_usd`: Vacía en los países con menos de 30 salarios válidos (exploratorios): no se calcula intervalo de confianza.
