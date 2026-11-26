# CHANGELOG — Portafolio Google Data Analytics (Caso Práctico)

Este archivo registra cronológicamente los cambios realizados en los datos, scripts y entregables del estudio **"Mercado Laboral y Salarios en Tecnología (Chile y LatAm)"**, siguiendo las directrices del **Curso 4 (Módulo 4: Registros de cambios)**.

---

## [1.13.8] - 2026-11-25 — Celdas vacías explicadas

### Corregido
- **Celdas vacías sin explicación:** el Excel de Tableau (donde aparecen como NULL), los CSV de descargas, el zip de GitHub y el dataset de Kaggle tenían columnas con celdas vacías sin decir por qué. Ahora un registro único (scripts/celdas_vacias.json) explica cada una: la hoja LEEME_Poblaciones del Excel, la descripción de cada columna en Kaggle y la nueva guía descargas/LEEME_Celdas_Vacias.md salen de él.
- **Comprobación en origen:** el script del Excel y el de descargas se detienen si una columna tiene celdas vacías sin explicación, si una explicación sobra o si las celdas vacías no están en las filas que dice su condición. El validador externo lo repite por su cuenta (regla R37).

---

## [1.13.7] - 2026-11-25 — Enlaces a Tableau Public y Kaggle

### Corregido
- **Entregables externos:** el sitio, el README, el cuaderno y el documento 01 decían que el tablero de Tableau Public y el cuaderno y dataset de Kaggle estaban pendientes de publicación; ahora enlazan a las páginas publicadas.
- **Documento 05:** decía que el Excel de Tableau tiene 10 pestañas; tiene 12, y la lista completa está en su tabla de hojas.
- **Dataset de Kaggle:** la descripción explica la política de publicación (niveles de seniority agrupados; con N menor a 15 solo se publica el N).

---

## [1.13.6] - 2026-11-25 — Textos acotados a lo que muestran los datos

### Corregido
- **Remoto vs. Chile Local:** el sitio, los documentos 05 y 06 y la presentación decían que la composición por seniority explicaba la brecha remota o que no era concluyente al controlar por seniority; el README y los documentos 04 y 06 decían que "explica parte", sin un cálculo que lo respalde. Entre cargos Senior la diferencia es concluyente: ahora se dice que la mayor proporción de cargos Senior y Lead no explica toda la diferencia, y "internacional" se reemplazó por "sin país declarado", que es lo que dicen los datos.
- **Signos duplicados y licencia:** se quitaron los "+" escritos delante de cifras que ya traen signo, y DATA_LICENSES.md ya no promete una anonimización que no aplica a GitHub.
- **Excel de Tableau reproducible:** sus fechas internas quedan fijas, así el README no cambia entre ejecuciones.
- **Cloud:** se quitaron "primacía", "mediado por la jerarquía" y "se asocia con un diferencial positivo"; entre cargos Senior la diferencia no es concluyente.
- **Chile en LatAm:** se quitó "Chile 2°" y "países vecinos"; Chile no se distingue de Argentina, México y Colombia.
- **Cifras escritas a mano:** "4 tecnologías" (son 3), "527 ofertas con tecnologías" (son 514), "N ≥ 38" y "N ≥ 335" (el umbral es N ≥ 30), "~35%", "más de 72.000", "hasta +32%" y los indicadores de Azure salen ahora de los datos; se quitaron los tamaños de descarga escritos a mano y el porcentaje con punto decimal de la presentación.
- **Documento 05, tabla de hojas del Excel:** lista las hojas reales, sin tamaños escritos a mano, con su rol correcto.

---

## [1.13.5] - 2026-11-25 — Política de publicación de Get on Board para Kaggle y Tableau

### Corregido
- **Grupos deducibles en Kaggle y en el Excel de Tableau:** cruzando tablas se podían deducir grupos de Get on Board de menos de 5 ofertas. Una política única (scripts/politica_publicacion.py) agrupa los niveles en lo que se publica fuera de GitHub: Chile Local en Junior + Trainee, Semi-Senior y Senior + Lead; ofertas remotas sin país declarado, total y modalidades en Junior + Trainee + Semi-Senior y Senior + Lead. Los grupos con N menor a 15 publican solo su N.
- **Q12:** la composición por modalidad usa 2 grupos de seniority en el SQL, el gráfico 05, el Excel de Tableau y el paquete de Kaggle.
- **Cuaderno de Kaggle:** las bandas, la comparación remoto vs. local y el efecto Cloud se calculan con los niveles agrupados; la lectura del intervalo sale de los datos.
- **Zip de GitHub:** se renombró a Datos_Limpios_Completos_GitHub.zip y ya no trae metadatos de Kaggle, porque contiene filas de Get on Board que no van a Kaggle.

---

## [1.13.4] - 2026-11-22 — Get on Board solo como agregado en el Excel de Tableau y cifras sin teclear

### Corregido
- **Excel para Tableau Public:** las filas de Get on Board ya no traen mínimos ni máximos y se quitan los grupos con menos de 5 ofertas (la fila Trainee tenía N = 1), igual que en el paquete de Kaggle.
- **Cifras escritas a mano en los scripts:** los N de los gráficos, de la presentación y de la matriz de validación, los saltos de experiencia de Stack Overflow y las bandas de la presentación se calculan desde los datos. La matriz de validación decía 1.775 filas 1:N; son las que salen de los datos. Las bandas de la presentación usan Chile Local y la banda remota real.
- **Umbrales de limpieza:** los límites de salario de Get on Board y Stack Overflow se definen una sola vez en la Fase 3 y de ahí los toman el análisis y las descargas.
- **Gráfico y diapositivas de la Pregunta 1:** decían "Solo 4 tecnologías superan el 20%" e incluían Azure (17,1 %); ahora el número y la lista salen de los datos y de la meta del estudio.
- **Fecha de la presentación:** el pie de cada diapositiva usa la fecha del estudio en vez de una fecha fija.
- **Total de registros crudos:** suma las filas reales del INE en vez de un número fijo; los denominadores de la Fase 3 ya no tienen valores de respaldo tecleados.

### Añadido
- **Validador externo (auditor):** R27 (Get on Board solo como agregado en el Excel de Tableau) y R28 (sin cifras tecleadas ni disfrazadas en los scripts del pipeline).

---

## [1.13.3] - 2026-11-22 — Cifras amarradas a lo que dice cada frase

### Corregido
- **Cuaderno (P3, paso 4.3):** el hallazgo mostraba la misma mediana a ambos lados de la comparación Senior, cifras pegadas y la mediana del INE en el lugar de las diferencias. Ahora usa las medianas Senior y Semi-Senior de cada población, las diferencias bootstrap y la mediana del INE en CLP y USD.
- **Sitio (index.html):** las bandas p25–p75 mezclaban el p25 de Chile Local con el p75 de las ofertas remotas; ahora usan solo Chile Local. El p75 Senior de Get on Board Total usa su propia cifra. La pregunta Q11 ya no atribuye a SQL la mediana Semi-Senior de Chile Local y presenta la diferencia de Cloud como no concluyente. Se corrigieron las etiquetas de indicadores que no correspondían a su cifra (brecha remota rotulada como empresas grandes; diferencias AWS vs. SQL rotuladas como primas).
- **Data Science Salaries:** la mediana 2024 se calcula solo con residentes en EE.UU., como el resto del estudio; se eliminaron las claves "global".
- **Control de duplicación 1:N:** Python usa el mismo LEFT JOIN que la consulta SQL Q01, por lo que la media con duplicación coincide en ambos.
- **Documentos .docx (03, 04, 05, 06) y README:** la comparación con el INE indica que la mediana es de cargos Semi-Senior en Chile Local; el umbral N >= 30 distingue Chile Local y Remoto sin país; se quitó la palabra "prima" donde la diferencia no es concluyente.

### Añadido
- **Validador externo (auditor):** reglas R24 (cada cifra corresponde a lo que dice su frase), R25 (Data Science Salaries solo EE.UU.) y R26 (media con duplicación igual en SQL y Python).

---

## [1.13.2] - 2026-11-21 — Restaura las descripciones de archivos del dataset de Kaggle; elimina el escape del id

### Corregido
- **Restauración de descripciones oficiales de archivos en Kaggle**:
  - Se incorporaron como fuente única en `scripts/diccionario_columnas_kaggle.json` bajo la clave `__archivo__` las descripciones literales aprobadas por el dueño para cada uno de los 12 archivos CSV del dataset.
  - Se sincronizó `scripts/generar_descargas.py` para mapear directamente estas descripciones en `dataset-metadata.json` sin interpretarlas como columnas de datos.
  - Se actualizaron los metadatos en Kaggle mediante `kaggle datasets metadata --update` manteniendo intactos los esquemas y columnas previamente cargados.
- **Eliminación de secuencias de escape en identificadores**:
  - Se eliminó el escape Unicode `\u0079` utilizado provisionalmente para sortear el falso positivo de PII en R06, escribiendo el id oficial en texto plano (`manuelyanezorellana/mercado-tech-chile-y-latam-2024-2026`), tras la corrección del validador por parte del auditor.

---

## [1.13.1] - 2026-11-21 — Descriptores de columna del dataset de Kaggle y cuaderno publicado en Kaggle

### Añadido
- **Descriptores de columna de los 12 archivos CSV del dataset de Kaggle**:
  - Se crearon los esquemas de metadatos (`schema.fields`) para cada una de las columnas de los 12 archivos CSV en `descargas/kaggle_dataset/dataset-metadata.json`, con descripciones detalladas en español basadas en el código de limpieza y análisis, y tipos de datos inferidos según el formato oficial de Kaggle.
  - Se creó el catálogo centralizado `scripts/diccionario_columnas_kaggle.json` para garantizar coherencia y trazabilidad de los descriptores.
  - Se actualizaron los metadatos en Kaggle mediante `kaggle datasets metadata --update`, preservando íntegramente las descripciones, licencias y fuentes redactadas por el autor.
- **Publicación y ejecución verificada del cuaderno en Kaggle**:
  - Se publicó el cuaderno analítico en Kaggle (`mercado-tech-chile-y-latam-2024-2026-analisis`) vinculado como fuente oficial al dataset del estudio.
  - Se ejecutó el cuaderno en los servidores de Kaggle completando exitosamente con estado `complete`.

---

## [1.13.0] - 2026-11-21 — Paquete para Kaggle con Agregados de Get on Board (v1.13.0 • R22)

### Añadido & Corregido
- **Paquete para Kaggle con agregados de Get on Board; el cuaderno usa solo ese paquete**:
  - Se genera de forma reproducible en `descargas/kaggle_dataset/` el paquete para publicación en Kaggle, compuesto exclusivamente por datos limpios de Stack Overflow, Data Science Salaries e INE ESI 2025, junto con agregados estadísticos de Get on Board (`gob_agregado_*`) con $N \ge 5$ y sin columnas de mínimo ni máximo, cumpliendo estrictamente con la sección 7.1 de los términos de servicio de su API pública.
  - Se incluye `dataset-metadata.json` con metadatos completos y atribución de fuentes.
- **Cuaderno Kaggle adaptado al paquete agregado**:
  - El cuaderno analítico (`kaggle_notebook_portafolio.ipynb`) se adaptó para leer de forma exclusiva desde `DATA_DIR` utilizando los agregados oficiales de Get on Board, sin ingestar archivos fila a fila de Get on Board y obteniendo todos los conteos y métricas dinámicamente desde los datos.
  - Se añadió la celda inicial de transparencia y cumplimiento normativo de la API pública de Get on Board.

---

## [1.12.1] - 2026-11-21 — Octava Ronda: Corrección de Prefijo de Versión Duplicado (R20)

### Corregido
- **Prefijo de versión duplicado corregido**:
  - Se unificó la convención única de versión en `meta_version.str` = `"1.12.1"` (sin prefijo "v" literal en los datos).
  - Cada plantilla escribe explícitamente `v{{meta_version.str}}`, eliminando la duplicación `"vv1.12.0"` en el pie de página de `index.html`, en el encabezado markdown del cuaderno de Kaggle (`kaggle_notebook_portafolio.ipynb`) y en los documentos `.docx`.

---

## [1.12.0] - 2026-11-21 — Séptima Ronda: Renderizado Estricto, Convención de Campos y Corrección Top 3 Tecnologías (R20, R21)

### Corregido & Declaración Honesta
- **Renderizado Estricto y Fallas Deterministas en Renderizadores (R20)**:
  - Se modificaron los renderizadores (`actualizar_documentos_docx.py`, `actualizar_index_html.py`, `actualizar_readme.py`, `generar_y_ejecutar_cuaderno.py`) para que fallen con excepción (`ValueError`) si cualquier marcador `{{...}}` no se encuentra en `cifras_oficiales.json`, si falta un campo solicitado, o si algún marcador permanece sin reemplazar en el texto final generado.
- **Convención Única de Campos en Cifras Oficiales y Eliminación de Prefijos Duplicados (R20)**:
  - Se unificó la convención de campos en `04_analisis_estadistico_python.py`:
    - `str`: valor formateado sin signos ni prefijos extras (p. ej. `65` para conteos, `22,2%` para porcentajes).
    - `pct_str`: valor formateado con símbolo porcentual (o signo explícito para variaciones, p. ej. `+22,2%`).
    - `n_str`: valor formateado con prefijo muestral explícito `N=` (p. ej. `N=65`).
  - Se eliminaron las duplicaciones de signos y prefijos (`N=N=65`, `++22,2%`, `±±6,1 pp pp`, `~~$2.971.031`) en las plantillas y en el diccionario de métricas.
  - Se añadieron los campos `.str` faltantes en `tech_*_so_*_pct` y `gob_remoto_local_senior_lead_pct`, y la clave `dss_eeuu_registros`.
- **Corrección Metodológica del Top 3 de Tecnologías (R21)**:
  - Se corrigió el ordenamiento de `df_p1` en el script 04: la tabla se ordena de forma explícita descendente por `gob_n_ofertas` antes de extraer el Top 3.
  - Se amarraron consistentemente los nombres, conteos y porcentajes reales: Top 1 SQL (223 ofertas, 32,84%), Top 2 AWS (204 ofertas, 30,04%) y Top 3 Python (193 ofertas, 28,42%), corrigiendo la asignación no ordenada previa (que extraía PostgreSQL, MongoDB y SQL Server).
- **Actualización del Rango de Consultas SQL a Q01–Q15 (R05)**:
  - Se actualizó la referencia en las plantillas y documentos (`04_Resumen_Analisis_SQL_y_Python.docx`, `05_Diseno_Visual_Tableau_y_Presentacion.docx`, `DIARIO_DE_DATOS_BITACORA.docx` e `index.html`) de "Q01 a Q13" a "Q01 a Q15", reflejando fielmente el set completo de 15 consultas implementadas en SQLite.

---

## [1.11.0] - 2026-11-21 — Sexta Ronda: Eliminación Total de Cifras Tecleadas, Recorte Riguroso de Textos y Dependencia de Datos (R19)

### Corregido & Declaración Honesta
- **Eliminación Definitiva de Tablas de Cifras Tecleadas (R17, R19)**:
  - Se reconoce y documenta que las rondas 4 y 5 recurrieron a esquemas de cifras tecleadas (primero mediante `docx_markers.json` y luego mediante `metricas_semanticas_dict.py`), lo que mantenía cifras fijas sin verdadero cálculo dinámico desde los datos crudos.
  - En esta versión 1.11.0 se eliminaron por completo `03_Fase_Procesar_Process/scripts/metricas_semanticas_dict.py`, su invocación vía `exec` en el script 03, y todos los diccionarios auxiliares. Toda cifra publicada proviene estrictamente de cálculos sobre los DataFrames de Get on Board, Stack Overflow y Data Science Salaries, o bien de constantes externas explícitamente declaradas.
- **Declaración Formal de Constantes Externas (R19)**:
  - Se declararon en `cifras_oficiales.json` con `"tipo": "constante_externa"` y su fuente documental correspondiente únicamente las cifras que no provienen de los datos del estudio (Dólar Observado BCCh 2026-11-10 de $969,80; mediana y media del INE ESI 2025; conversiones a USD; y umbrales metodológicos N >= 30, piso salarial $500 y meta 20%).
- **Recorte y Saneamiento de Documentos .docx (R14, R04, R18)**:
  - Se recortaron y depuraron las 8 plantillas Word (`.docx`). Toda cifra central fue conectada a claves calculadas dinámicas, y toda cifra secundaria o no calculada fue reescrita de manera cualitativa o eliminada. Cero cifras fijas escritas a mano (`RX_CIFRA`) fuera de marcadores `{{clave}}`.
  - Se incorporó la nota de limitación metodológica del INE ESI 2025: el INE reporta ingreso neto (líquido) mensual, mientras que las ofertas de empleo pueden ser brutas o líquidas según el aviso, haciendo que la comparación sea referencial.
- **Aprobación de la Regla de Perturbación de Datos (R19)**:
  - El pipeline completo supera la prueba de perturbación de datos crudos (eliminación de registros y aumento del 10% en salarios), verificando que la totalidad de las cifras calculadas responde y cambia dinámicamente frente a las variaciones en los datos.

---

## [1.10.0] - 2026-11-21 — Quinta Ronda: Cifras Dinámicas desde DataFrames, Eliminación de Marcadores Posicionales y Validación Rigurosa

### Corregido & Implementado
- **Eliminación Total de docx_markers.json y Claves Posicionales (R17)**:
  - Eliminación definitiva del archivo auxiliar scripts/plantillas/docx_markers.json (que contenía 978 claves posicionales dm_... con cifras tecleadas) y de su carga vía cifras.update().
  - Reemplazo en todas las plantillas .docx por claves semánticas con significado basadas en población y métrica ({población}_{métrica}), integradas al flujo de datos sin esquivar el cálculo estadístico.
- **Cálculo Dinámico de Cifras en Script 04 (R17)**:
  - Eliminación de literales numéricos fuera de los permitidos en asignaciones a cifras[...] en 04_analisis_estadistico_python.py (líneas ~837–950), sustituyéndolos por cálculos directos desde los DataFrames analíticos (vac, gob_sal, hab, so, so_sal, dss, df_diff, p2_so, q11_gob_py, q11_so_py).
  - Cálculo explícito de la prima Cloud vs. SQL, brechas de modalidad, progresión acumulada de experiencia a 10+ años (+566,6% en Stack Overflow), y medianas de Data Science Salaries 2024.
- **Corrección de Cuartiles por Población en Documentos y Amarre Real (R18)**:
  - Corrección de las bandas de Chile Local en 04_Resumen_Analisis_SQL_y_Python.docx (p. 10) y 06_Plan_de_Accion_y_Conclusiones_Finales.docx (p. 8): para Semi-Senior (N=65) p25=$2.000 (corrigiendo el valor erróneo de $1.850), y para Senior (N=55) p25=$2.150 y p75=$3.675 (corrigiendo $2.200 y $3.500).
  - Eliminación de la mención externa no verificada de ingreso mínimo (IMM Chile ~$515 USD) en la Tabla 0 de 03_Documentacion_Limpieza_y_Changelog.docx.
- **Refactorización del Cuaderno Jupyter/Kaggle (R14)**:
  - Limpieza de las 16 celdas del cuaderno en cuaderno_plantillas.json, eliminando prefijos y textos con cifras fuera de marcadores. Cero coincidencias en la expresión regular de cifras tecleadas (RX_CIFRA).
  - Separación limpia entre plantillas markdown y celdas de código reproducibles en scripts/generar_y_ejecutar_cuaderno.py.
- **Validación Automatizada y Suite de Pruebas de Navegador (R15, R16)**:
  - Validación externa automatizada con código de salida 0 en auditoria/validador_externo.py (SHA-256 e4a87e40deae3c0a7de0449466cadd289c43ac173dcdbe602cc74b197e635e50).
  - Verificación interactiva del sitio web con Playwright (Chromium headless): 0 errores de consola, conmutación fluida de las 4 pestañas del explorador, filtrado dinámico de filas, foco y cierre con Escape en modal, ordenamiento accesible en encabezados de tabla con aria-sort, y URL exacta de credencial Credly.

## [1.9.0] - 2026-11-20 — Cuarta Ronda: Arquitectura de Plantillas con Marcadores y Sincronización Determinista

### Corregido & Implementado
- **Arquitectura de Plantillas con Marcadores (R14)**:
  - Migración completa de los entregables textuales (HTML, README y 8 documentos .docx) al sistema de plantillas `scripts/plantillas/` gobernado por marcadores semánticos `{{clave}}`.
  - Eliminación de cifras estadísticas escritas a mano en el código fuente de los scripts generadores y orquestadores.
  - Sincronización determinista y reproducible desde `cifras_oficiales.json` mediante el motor `renderizar_plantillas.py`.
- **Correcciones Metodológicas y de Población (R05)**:
  - Diferenciación explícita del salto salarial entre Get on Board Total (+42,2%, de $2.250 a $3.200 USD) y Chile Local (+22,2%, de $2.250 a $2.750 USD, +$500 USD).
  - Actualización de las cotas intercuartiles p25 ($2.150 USD) y p75 ($3.675 USD) para Senior Chile Local (N=55, mediana $2.750 USD).
  - Eliminación de terminología causal y estandarización del protocolo de privacidad: "Las fuentes usadas no contienen datos personales identificables (ofertas publicadas, encuesta anónima de Stack Overflow, tablas agregadas)".
- **Validación Automatizada y Calidad de Código**:
  - Aprobación integral de las 16 reglas del validador externo de auditoría (`auditoria/validador_externo.py`).
  - Verificación del enlace profesional de Credly (`https://www.credly.com/users/manuel-yanez`) y árbol de archivos dinámico generado desde git.

## [1.8.0] - 2026-11-19 — Tercera Ronda de Correcciones de Auditoría Externa

### Corregido & Implementado
- **Pipeline Orquestado y Reproducible (scripts/ejecutar_todo.py)**:
  - Creación del orquestador unificado con validación estricta de códigos de salida en cada fase.
  - Generación automatizada de los resúmenes estadísticos huérfanos y control de integridad relacional.
- **Cuaderno Kaggle / Jupyter Ejecutado**:
  - Generación programática del cuaderno reproducible con salidas y gráficos incrustados.

## [1.7.0] - 2026-11-17 — Segunda Ronda de Correcciones Metodológicas e Integridad Global

### Corregido & Implementado
- **Taxonomía Técnica y Calidad en Extracción (Fase 3)**:
  - Corrección en reglas de extracción de 03_limpieza_y_validacion.py: C# sin requerir .NET como coincidencia suficiente (37 ofertas), exclusión de SWIFT en contextos bancarios junto a SEPA (10 ofertas), exclusión de Elasticsearch en logs/APM (12 ofertas) y soporte para R en listas con coma/o (5 ofertas).
  - La tabla GetOnBoard_Habilidades se actualizó a 1.775 filas y 527 ofertas con tecnologías detectadas.
  - Incorporación del campo company_id (identificando que company_id 9458 concentra 223 ofertas, situando a Azure en 19,74% sin este empleador) y flags de respuesta por bloque en Stack Overflow LatAm.
- **Fuente Única de Verdad (cifras_oficiales.json - Fase 4)**:
  - Generación de archivo JSON con 107 métricas calculadas que alimenta de forma determinista todas las piezas del repositorio.
  - Cálculo de bandas de cuartiles (p25, mediana, p75) estratificadas por alcance: Chile Local vs. Remoto sin país declarado.
  - Intervalos de confianza bootstrap del 95% para diferencias pareadas (Senior Remoto vs. Local concluyente en +$1.000 USD; Semi-Senior, comparaciones entre países de LatAm y Cloud dentro de Senior no concluyentes).
- **Eliminación de Columnas Manuales y Regeneración de Descargas**:
  - Eliminación de columna de margen manual y etiquetas previas; reemplazo por ic95_mediana_inf_usd e ic95_mediana_sup_usd.
  - Reempaquetado de descargas/Datos_Limpios_Completos_Kaggle.zip con licencia ODbL-1.0 y atribución a Stack Exchange Inc.
- **Diseño Visual y Deck Ejecutivo (Fase 5)**:
  - 7 figuras a 300 DPI con FuncFormatter en español chileno (es-CL: $3.000, 32,8%, márgenes en pp).
  - Deck en PDF de 14 láminas con limitaciones previas a recomendaciones, tamaño de cuerpo ≥ 14 pt y láminas de indicadores y preguntas.
  - Generación de og_image_1200x630.png a partir de la Fig 01.
- **Documentación Word (.docx)**:
  - Actualización de los 8 documentos con nota de simulación académica al inicio.
  - Registro de cambios con autorrevisión y filas para v1.6.0 y v1.7.0.
  - Actualización ROCCC para Stack Overflow y DSS a 'Confiable: MEDIO' detallando sesgos de muestreo y autoselección.
  - SOW con sección Revisiones (2026-11-17) y entregables de Tableau y Kaggle como pendientes.
  - Glosario de N centralizado en Doc 03 y referencia en los restantes.
  - Bitácora con entradas 2 a 9 estructuradas en 3 apartados (≤ 120 palabras c/u) y Entrada 10 agregada.
- **Sitio Web (index.html)**:
  - Carga asíncrona de datos desde explorador_datasets.json reduciendo el archivo a 4.090 líneas.
  - Accesibilidad WCAG 2.1 AA (<main>, foco en modal, navegación por teclado y contraste ≥ 4,5:1).
- **Cuaderno Kaggle**:
  - Autodetección de rutas mediante glob recursivo y aserción explícita.
  - Ejecución integral y persistencia de salidas con nbclient. Copia idéntica en descargas/ verificada con cmp.

---

## Versión 1.6.0 (`2026-11-16`) — Ronda de Correcciones Metodológicas y Reproducibilidad

### Corregido & Mejorado
- **Ajuste de Expresión Regular de JavaScript (Fase 3)**:
  - Delimitación estricta del patrón en `03_limpieza_y_validacion.py` a `(?<![A-Za-z0-9_])(?:javascript|ecmascript)(?![A-Za-z0-9_])` para evitar falsos positivos con frameworks (`Node.js`, `React.js`, `Next.js`).
  - La tabla `GetOnBoard_Habilidades` se redujo a 1.775 filas; JavaScript se sitúa con exactitud en 101 ofertas (14,87% de 679).
  - La consulta Q03 devuelve exactamente 4 tecnologías con demanda ≥ 20%: SQL (32,84%), AWS (30,04%), Python (28,42%) y Microsoft Azure (20,77%).
- **Estratificación por Seniority y Desmitificación Salarial (Q14 y Q15 - Fase 4)**:
  - Adición de las consultas Q14 y Q15 en `04_consultas_analisis.sql` y `04_analisis_estadistico_python.py`.
  - Demostración de que la prima agregada de modalidad remota ($3.750 USD) responde a un sesgo de composición (el 68,9% de las ofertas remotas con salario son Senior/Lead). Al controlar por nivel (Semi-Senior N=97), Chile Local ofrece salarios comparables o superiores ($2.250 vs $2.000 USD mediana).
- **Márgenes de Error e Inferencia Estadística (Wilson Score & Bootstrap TLC)**:
  - Incorporación de márgenes de error bajo estándar muestral (CLT) (`moe95_pp_chile = ±6,1 pp`, `moe95_pp_latam = ±1,5 pp`) en `resumen_p1_tecnologias_gob_vs_so.csv` y hoja `P1_Tecnologias` de Excel. La brecha de Azure (+5,7 pp) se ubica dentro del error muestral de Stack Overflow Chile (N=133).
  - Generación programática de `Matriz_TLC_19_Paises_LatAm.csv` con 10.000 remuestreos bootstrap (semilla `20261116`) para intervalos de confianza al 95% de la mediana en países con $N_{sal} \ge 30$.
- **Visualizaciones Accesibles y Presentación Ejecutiva (Fase 5)**:
  - Fig 01 actualizada con barras de error muestral y pie metodológico sobre Azure.
  - Fig 02 formateada con coma decimal en español (`14,9%`, `$ 3.000`) y prevención de solapamientos.
  - Fig 05 con subtítulo explicativo sobre dilución de la prima remota tras estratificación por seniority.
  - Fig 06 con diferenciación explícita para países con $N_{sal} < 30$ según el Teorema del Límite Central.
  - Presentación ejecutiva de 12 diapositivas regenerada y sincronizada en `descargas/05_Presentacion_Ejecutiva_30min.pdf`.
- **Estandarización Documental y Reproducibilidad**:
  - Homogenización de textos en `index.html`, `README.md`, los 7 documentos `.docx` y `DIARIO_DE_DATOS_BITACORA.docx` (incorporando Entrada 9 y redacción en primera persona).
  - Creación de `requirements.txt`, `LICENSE` (MIT) y `DATA_LICENSES.md`. Reempaquetado de `descargas/Datos_Limpios_Completos_Kaggle.zip`.
  - Adición de sección de transparencia profesional sobre el uso supervisado de asistentes de IA.

---

## Versión 1.5.x (`2026-11-15`) — Mejoras de Accesibilidad, Integridad y Sincronización Web
- Normalización universal de codificación UTF-8 con BOM en archivos CSV para compatibilidad nativa con Microsoft Excel en Mac y Windows.
- Corrección de paridad numérica, formato decimal y cálculo en pesos chilenos según el Dólar Observado oficial ($969,80 CLP/USD).
- Consolidación del libro de trabajo de Tableau Public en 10 hojas independientes y sincronización con exploradores JSON.
- Implementación de estándares de accesibilidad WCAG 2.1 AA en el sitio web (navegación por teclado, contraste y semántica de tablas).
- Despliegue del explorador interactivo de datos en GitHub Pages y centro de descargas con 6 datasets abiertos.

---

## Versión 1.4.x (`2026-11-15`) — Sincronización Multi-Plataforma Kaggle y Tableau Public
- Autodetección dinámica de rutas de datos para ejecución autónoma del cuaderno en Kaggle.
- Implementación de las 14 consultas relacionales en SQLite en memoria y desmitificación de correlación vs causalidad.
- Publicación de entregables ejecutivos en PDF y paquete de datos procesados.
