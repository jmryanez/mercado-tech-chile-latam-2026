# CHANGELOG — Portafolio Google Data Analytics (Caso Práctico 3 • Pista B)

Este archivo registra cronológicamente (de la versión más reciente a la más antigua) los cambios realizados en los datos, scripts y entregables del estudio **"Mercado Laboral y Salarios en Tecnología (Chile y LatAm)"**, siguiendo las prácticas recomendadas del **Curso 4 (Módulo 4: Registros de cambios)**.

---

## Versión 1.5.1 (`2026-11-15`) — Resolución Exhaustiva de Hallazgos de la Segunda Ronda Red-Team

### Corregido
- **Consistencia Documental Muestras Pre vs. Post-Limpieza**:
  - Explicitación de la distinción muestral en `01_Declaracion_Tarea_Empresarial.docx`, `02_Descripcion_Fuentes_y_ROCCC.docx` y `DIARIO_DE_DATOS_BITACORA.docx`: `Semi-Senior=97` y `Junior=17` salarios válidos post-limpieza (tras la anulación determinista de 2 casos $<$500 USD de las 18 ofertas Junior y 98 Semi-Senior iniciales).
- **Matriz de Calidad y Validación de Integridad**:
  - Actualización de `descargas/Matriz_Validacion_Integridad_Calidad.csv` y visor web de Validación: población formal de `3.074 SO LatAm / 679 GOB`, exclusión exacta de `2 vacantes GOB (<$500) / 67 respuestas SO (<$1k o >$500k)` y resultado de `235 salarios válidos GOB / 1.341 salarios válidos SO`.
  - Corrección de atribución curricular: las 6 validaciones formales se referencian al **Curso 5** en `README.md` y `CHANGELOG.md`.
- **Sincronización Total de Datasets Raíz y Descargas**:
  - Sobreescritura del archivo `explorador_datasets.json` en la raíz del repositorio con los datos consolidados y auditados de `descargas/Explorador_Datasets_Consolidados.json`.
  - Homologación de comas decimales en `error_est` (`±20,2%`, `±22,6%`, etc.) y ajuste de paridad de Chile a `$3.063,54 USD` y `$2.971.022 CLP` en `Matriz_TLC_19_Paises_LatAm.csv`.
  - Corrección aritmética de IQR en tramo Director (`19.167 - 11.333 = 7.834 USD`) en `Bandas_Salariales_y_Saltos_Seniority.csv`.
- **Cuaderno Kaggle y SQL Relacional**:
  - Corrección textual en Celda Markdown 7 de `kaggle_notebook_portafolio.ipynb` y `descargas/kaggle_notebook_portafolio.ipynb`: transición Semi-Senior a Senior expresada como `de $2.250 USD a $3.200 USD ($2.182.050 a $3.103.360 CLP)`.
  - Dinamismo en consulta `Q03` de `04_consultas_analisis.sql`, reemplazando el divisor cableado `679.0` por `(SELECT COUNT(DISTINCT job_id) FROM vacantes)`.
- **Frontend Web & Accesibilidad (WCAG 2.1 AA)**:
  - Corrección de cifras en Visualización 7 (`$138.000 USD anuales (~$11.500 USD/mes)`), texto de salarios (`$3.275 USD vs. $2.250 USD`) y armonización de primas en `index.html`.
  - Soporte de ordenamiento numérico en columnas con porcentajes (`sortTlcTable` y `sortSalTable` con `parseSortValue`).
  - Incorporación de prefijo UTF-8 BOM (`\uFEFF`) en funciones de exportación CSV para compatibilidad nativa con Microsoft Excel en Windows.
  - Implementación de navegación accesible por teclado (WCAG 2.1.1): atributos `tabindex="0"`, `role="button"`, etiquetas `aria-label` y listeners `keydown` (`Enter` / `Espacio`) en los 29 encabezados ordenables, las 6 tarjetas interactivas de fase y los 7 contenedores de ampliación modal.
  - Protección de seguridad inversa añadiendo `rel="noopener noreferrer"` en todos los enlaces externos con `target="_blank"`.

---

## Versión 1.5.0 (`2026-11-15`) — Resolución Exhaustiva de Hallazgos de la Auditoría Red-Team Multi-Agente

### Corregido (Hallazgos Críticos)
- **Portabilidad Absoluta y Privacidad (0% PII)**:
  - Eliminación de rutas absolutas locales en `03_limpieza_y_validacion.py`, `04_analisis_estadistico_python.py` y `05_generar_visualizaciones_y_deck.py`, reemplazándolas por resolución relativa `Path(__file__).resolve().parent.parent.parent`.
  - Verificación estricta de 0% PII en todo el árbol del repositorio y purga de cachés de compilación.
- **Reproducibilidad en Tableau Public**:
  - Inclusión determinista de la 10ª hoja `Mapa_LatAm_19_Paises` en la función `exportar_excel_tableau()` y sincronización automática hacia `descargas/Datos_Consolidados_Tableau_Public.xlsx`.
  - Actualización de `05_Diseno_Visual_Tableau_y_Presentacion.docx` a 10 hojas de trabajo y adición de fila explicativa en Tabla 4.
- **Portabilidad de Cuaderno Kaggle & Pack de Datos Limpios**:
  - Refinamiento de la lógica de autodetección en Celda 1 de `kaggle_notebook_portafolio.ipynb` mediante comprobación de archivos requeridos.
  - Creación y publicación del archivo descargable `descargas/Datos_Limpios_Completos_Kaggle.zip` con los 6 datasets limpios para ejecución con un clic.
- **Consistencia Muestral y Cuantitativa (TLC & Métricas)**:
  - Reevaluación de la matriz `Matriz_TLC_19_Paises_LatAm.csv`: la bandera `cumple_n30` ahora evalúa estrictamente el tamaño de salarios válidos ($N_{sal} \ge 30$). Solo 7 países cumplen el criterio para inferencia no paramétrica, mientras que 12 países se clasifican con rigor metodológico como *Muestra Exploratoria (N < 30)*.
  - Corrección de valores salariales en `Bandas_Salariales_y_Saltos_Seniority.csv` y `Explorador_Datasets_Consolidados.json`: Chile Local ($N=137$, Mediana=$2.250 USD) y Remoto Global ($N=98$, Mediana=$3.275 USD, salto $+45,6\%$).
  - Rectificación de cifras en tarjetas de datos en `index.html`: GOB con 1.877 habilidades, SO con 3.074 desarrolladores, DSS con 6.599 registros históricos (corrigiendo la errata de 67.575 a 6.599), e INE ESI con 2 Indicadores Oficiales (Mediana y Media Nacional).
  - Precisión de métricas en textos: sesgo por duplicación cartesiana 1:N ajustado a `+$38,30 USD` ($2.920,43 vs $2.882,13 real), y variable confusora en Remoto Local ajustada a `68,9%` Senior/Lead (31 de 45 ofertas con salario).

### Añadido (Accesibilidad y UX Frontend)
- **Menú de Navegación Móvil Táctil**: Habilitación de desplazamiento táctil horizontal continuo (`overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch;`) en dispositivos de pantalla reducida ($\le 960$px), eliminando la ocultación no accesible.
- **Prevención de Solapamiento de Encabezado Fijo**: Configuración global de `scroll-padding-top: 85px` en `html` y `scroll-margin-top: 85px` en todas las secciones y pie de página.
- **Accesibilidad y Contraste WCAG 2.1 AA**:
  - Calibración del token `--text-muted` a `#94A3B8` (ratio de contraste 6.9:1).
  - Inclusión de atributos `aria-label` descriptivos en todos los controles de búsqueda, filtros desplegables y selector de tamaño de página del Explorador.
  - Atributos `aria-sort` e indicadores visuales de flecha (▲/▼) en encabezados ordenables de tablas.
  - Atributos `aria-label` y `aria-current="page"` en la paginación interactiva de vacantes.
  - Diálogo modal accesible (`role="dialog"`, `aria-modal="true"`, `aria-label`, y texto alternativo dinámico para ampliación de visualizaciones).
- **Galería Completa de 7 Visualizaciones en `#patrones`**:
  - Incorporación interactiva de la **Visualización 03** (*Mapa de Calor de Tecnologías por Segmento de Mercado*) y la **Visualización 07** (*Evolución Salarial Tech Global y Tamaño de Empresa DSS 2020–2024*).

---

## Versión 1.4.1 (`2026-11-15`) — Sincronización y Ajustes de Despliegue para Kaggle y Tableau Public

### Modificado
- **Cuaderno Interactivo de Kaggle ([`06_Fase_Actuar_Act/kaggle_notebook_portafolio.ipynb`](06_Fase_Actuar_Act/kaggle_notebook_portafolio.ipynb))**:
  - Eliminación absoluta de rutas locales del sistema y verificación de 0% PII.
  - Autodetección robusta de rutas multi-entorno (`/kaggle/input/`, rutas relativas y carpeta `descargas/`).
  - Incorporación del flujo analítico completo: consultas SQL en SQLite, respuestas empíricas a las 4 preguntas de negocio (P1 a P4) + Q11, visualizaciones con accesibilidad para daltonismo, matriz de implementación Qué/Quién/Cuándo (30, 60 y 90 días) y herramientas de carrera del Curso 9 (STAR, X-Y-Z y Elevator Pitch).
  - Réplica sincronizada en [`descargas/kaggle_notebook_portafolio.ipynb`](descargas/kaggle_notebook_portafolio.ipynb).
- **Libro de Trabajo para Tableau Public ([`05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx`](05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx))**:
  - Actualización de la hoja de gobernanza `LEEME_Poblaciones` con los enlaces oficiales al sitio web en GitHub Pages, repositorio en GitHub y estandarización de los 9 cursos oficiales.
  - Incorporación de la nueva hoja `Mapa_LatAm_19_Paises` con los 19 países de Latinoamérica, sus tamaños de muestra ($N_{total}$, $N_{sal}$), medianas, cuartiles $p25–p75$, error muestral y flag `cumple_n30` para la generación directa de mapas coropléticos.
  - Réplica sincronizada en [`descargas/Datos_Consolidados_Tableau_Public.xlsx`](descargas/Datos_Consolidados_Tableau_Public.xlsx).

---

## Versión 1.4.0 (`2026-11-15`) — Desglose Metodológico en Profundidad (6 Fases) y Descarga de Entregables Oficiales

### Añadido
- **Visor Metodológico en Profundidad (`#metodologia-deepdive`)**: Módulo interactivo con navegación por pestañas de las 6 fases (Preguntar, Preparar, Procesar, Analizar, Compartir y Actuar). Cada fase desglosa en cuadrículas estructuradas:
  - Tarea Empresarial y Enfoque Google.
  - Métodos, Técnicas y Herramientas Oficiales de los 9 Cursos.
  - Criterios de Rigor, Verificación, Integridad y Control de Sesgos.
  - Enlaces de descarga directa de cada entregable oficial y botones de navegación rápida a la sección correspondiente del sitio web.
- **Tarjetas Interactivas de Fase**: Cada una de las 6 tarjetas en `.phases-grid` ahora actúa como disparador interactivo con indicador visual (`active-phase`), desplegando y desplazando suavemente la vista hacia el visor técnico en profundidad.
- **Subsección de Entregables Oficiales por Fases (`.docx`) en el Centro de Descargas (`#descargas`)**: Incorporación de 7 tarjetas descargables correspondientes a los documentos oficiales de cada fase (SOW, Tarea Empresarial, Descripción ROCCC, Documentación de Limpieza/Changelog, Resumen SQL/Python, Guía de Diseño Visual y Plan de Acción/Empleabilidad).

### Corregido
- **Auditoría y Completitud Exhaustiva de las 18 Tarjetas Metodológicas**:
  - **Fase 3**: Corrección de enumeraciones incompletas: el *Checklist de Limpieza de 12 Puntos de Google* ahora lista explícitamente los 12 puntos del Curso 4 (antes mostraba solo 4), y el *Changelog Oficial de 7 Campos* desglosa los 7 campos de auditoría (antes mostraba solo 3).
  - **Fase 1**: Desglose íntegro de los 5 Porqués (Toyota/Google), las 7 secciones obligatorias del SOW y las 4 preguntas S.M.A.R.T. con criterios de equidad (Fairness).
  - **Fase 2**: Enumeración explícita de las 4 fuentes inmutables (72.797 filas), los 5 criterios del marco ROCCC y los 3 tipos de metadatos (descriptivos, estructurales y administrativos).
  - **Fase 4**: Mapeo completo de las 14 consultas SQL (Q01 a Q13) y control de clave foránea 1:N que evitó el sesgo de +$75 USD.
  - **Fase 5**: Detalle cronometrado de los 6 bloques de la presentación de 30 minutos (4+5+10+3+3+5 min) y los 3 estándares de Edward Tufte, accesibilidad para daltonismo y honestidad escalar.
  - **Fase 6**: Especificación completa de las 4 conclusiones, 3 recomendaciones con matriz Qué/Quién/Cuándo (30, 60 y 90 días) y las 3 herramientas de carrera del Curso 9 (STAR, X-Y-Z y Elevator Pitch).

### Modificado
- **Pie de Página Oficial**: Armonización y estandarización del texto de cierre del portafolio: *«Cumplimiento estricto de las directrices metodológicas de los 9 cursos oficiales para la obtención de la Certificación Profesional de Google Data Analytics»*.
- **Consistencia de Cursos Oficiales**: Verificación de alineación del estándar de los 9 cursos (Cursos 1 al 8 de fundamentos y capstone + Curso 9 de empleabilidad, narrativa STAR, fórmula X-Y-Z y elevator pitch).

---

## Versión 1.3.0 (`2026-11-14`) — Publicación Web Interactiva, Explorador de Datos y Optimización UX

### Añadido
- **Sitio Web Oficial en GitHub Pages ([`index.html`](https://jmryanez.github.io/mercado-tech-chile-latam-2026/))**: Plataforma web moderna responsive construida con HTML5 semántico, paleta de colores de Google (`#1A73E8`, `#0072B2`, `#D55E00`), tipografía Inter/JetBrains Mono y diseño accesible para daltonismo.
- **Explorador Interactivo de Datos (`#explorador-datos`)**: Componente cliente con búsqueda en tiempo real, filtros por país/ámbito, paginación dinámica (10, 25, 50 registros) y exportación a CSV:
  - Pestaña 1: Auditoría de 72.797 registros crudos y tabla de **679 vacantes limpias de Get on Board 2026**.
  - Pestaña 2: **Matriz Teorema del Límite Central (TLC) de los 19 países de América Latina + Chile**, indicando cumplimiento de $N \ge 30$ e IQR.
  - Pestaña 3: **Estructura salarial, cuartiles ($p25–p75$) y salto de +42,2% al nivel Senior**.
  - Pestaña 4: **Matriz de Integridad Relacional 1:N y los 6 tipos formales de validación de datos (Curso 5)**.
- **Centro de Descargas Abiertas ([`descargas/`](descargas/))**: Generación de 6 datasets en formatos abiertos CSV y JSON para auditoría y reproducibilidad pública.
- **Marcador Activo en Tiempo Real (*Scrollspy*)**: Script con cálculo de posición por scroll que ilumina dinámicamente con una píldora azul la sección en la que se encuentra el usuario.
- **Bloques Explícitos de Pregunta y Respuesta**: Cada tarjeta de visualización en la sección *Patrones Descubiertos* ahora integra un contenedor estructurado `❓ Pregunta de Negocio (P1 a P4)` y `💡 Hallazgo & Respuesta Directa`.
- **Favicon Personalizado**: Avatar circular trazado con fondo transparente en resoluciones estándar (16x16, 32x32, 512x512 y Apple Touch Icon).

### Modificado
- **Barra de Navegación (Header)**: Rediseño a arquitectura de **isla flotante centrada** (*Floating Island Nav*) para eliminar la colisión de texto del subtítulo y evitar que los enlaces se partieran en dos líneas.
- **Subtítulo de Sección de Hallazgos**: Reescritura del texto introductorio enfocándolo en los descubrimientos de mercado en lugar de rúbricas técnicas de diseño gráfico.
- **Protección PII Absoluta**: Purgado total de datos de contacto personales en código fuente, metadatos y documentación (100% conforme a la directiva de ética y privacidad de Google).

---

## Versión 0.6.0 (`2026-11-11`) — Cierre Fase 6: Actuar (*Act* • Cursos 8 y 9)

### Añadido
- Entregable Oficial 6 [`06_Fase_Actuar_Act/06_Plan_de_Accion_y_Conclusiones_Finales.docx`](06_Fase_Actuar_Act/06_Plan_de_Accion_y_Conclusiones_Finales.docx) con conclusiones de alto nivel, glosario muestral `N >= 30` (Curso 4), `3` recomendaciones prioritarias con alternativas (`Pros y Contras`), matriz `Qué / Quién / Cuándo`, `4` líneas de exploración futura (**Curso 8**), guía para **GitHub / Kaggle / Tableau Public**, viñetas `X-Y-Z`, historia `STAR` y elevator pitch de `20 segundos` (**Curso 9**).
- Portada pública del repositorio [`README.md`](README.md) con hallazgos verificados, visualizaciones incrustadas (`300 DPI`), glosario `N >= 30`, estructura completa (Fases 1–6) e instrucciones de reproducibilidad.
- Cuaderno interactivo [`06_Fase_Actuar_Act/kaggle_notebook_portafolio.ipynb`](06_Fase_Actuar_Act/kaggle_notebook_portafolio.ipynb) en Python/Markdown listo para publicar en Kaggle.
- Archivo [`.gitignore`](.gitignore) excluyendo archivos temporales del sistema y carpeta personal `cv/` (protección PII antes de publicar en GitHub).

### Modificado
- Actualización final de [`DIARIO_DE_DATOS_BITACORA.docx`](DIARIO_DE_DATOS_BITACORA.docx) añadiendo la entrada de cierre **Fase 6: Actuar (`Cursos 8 y 9`)**.

---

## Versión 0.5.3 (`2026-11-11`) — Alineación Visual y Léxica Final con los 9 Cursos (Fases 1–5)

### Modificado
- **Visual 06 Panel B ([`06_paises_latam_y_tamano_empresa_p4.png`](05_Fase_Compartir_Share/visualizaciones/06_paises_latam_y_tamano_empresa_p4.png))**: Reemplazo de puntos conectados desde `$1.000` por **barras verticales desde `$0 USD`** para cumplir literalmente la regla del **Curso 6** (*no cortar el eje Y ni conectar categorías no temporales*, [Entregable Oficial de Diseño Visual](05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx)).
- **Lenguaje literal de los Cursos 5 y 6 en Fases 1, 2, 4, 5, SQL y Bitácora**: Reemplazo de anglicismos/términos externos (*"duplicación en uniones 1:N"* en vez de jerga inglesa de `JOIN`, *"continua y ascendente en cada tramo"* en la progresión salarial de Fase 4, y *"alta proporción datos-tinta"* en Checklist de Fase 5).

---

## Versión 0.5.2 (`2026-11-11`) — Homologación Léxica Literal con los 9 Cursos (Fases 1–5)

### Modificado
- **Alineación literal con Cursos 6 y 7** en código, resúmenes y documentación de Fases 1, 4 y 5 (Fases 2 y 3 ya cumplían al 100%):
  - Estandarización de las métricas de dispersión salarial a **"cuartiles (`p25–p75`)"** y **`amplitud_p25_p75_usd`** (derivados directamente de `describe()` y `quantile([0.25, 0.75])` enseñados en el **Curso 7**, y de cuartiles/percentiles del **Curso 6**).
  - Estandarización de la nomenclatura cromática a **"paleta apta para daltonismo (azul/naranja • Curso 6)"**.
- Regeneración completa de [`04_Fase_Analizar_Analyze/resumenes/`](04_Fase_Analizar_Analyze/resumenes/), [`05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx`](05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx), [`05_Fase_Compartir_Share/visualizaciones/04_bandas_salariales_experiencia_p2.png`](05_Fase_Compartir_Share/visualizaciones/04_bandas_salariales_experiencia_p2.png), [`05_Fase_Compartir_Share/05_Presentacion_Ejecutiva_30min.pdf`](05_Fase_Compartir_Share/05_Presentacion_Ejecutiva_30min.pdf) y los `.docx` de Fases 1, 4 y 5.

---

## Versión 0.5.1 (`2026-11-11`) — Glosario Transversal de `N`, Regla `N >= 30` y Derivadas (Fases 1–5 • Curso 4)

### Añadido
- Definición formal de **`N`** (conteo exacto de observaciones válidas), fundamentación oficial de **`N >= 30`** (**Curso 4, Módulo 1**: *Teorema del Límite Central*, `95%` de confianza, menor margen de error y significación estadística) y glosario unificado de sus derivadas (`N universo vs. N salarios válidos`, `N < 30` exploratorio / `cumple_n30=False`, `N = 0`, y cotas mínimas observadas `N >= 38`, `N >= 335`, `N >= 34`, `N >= 60`, `N >= 75`) incorporado transversalmente en:
  - **Fase 1**: [`01_Alcance_del_Trabajo_SOW.docx`](01_Fase_Preguntar_Ask/01_Alcance_del_Trabajo_SOW.docx) y [`01_Declaracion_Tarea_Empresarial.docx`](01_Fase_Preguntar_Ask/01_Declaracion_Tarea_Empresarial.docx).
  - **Fase 2**: [`02_Descripcion_Fuentes_y_ROCCC.docx`](02_Fase_Preparar_Prepare/02_Descripcion_Fuentes_y_ROCCC.docx).
  - **Fase 3**: [`03_Documentacion_Limpieza_y_Changelog.docx`](03_Fase_Procesar_Process/03_Documentacion_Limpieza_y_Changelog.docx) (`Sección 4.1`).
  - **Fase 4**: [`04_Resumen_Analisis_SQL_y_Python.docx`](04_Fase_Analizar_Analyze/04_Resumen_Analisis_SQL_y_Python.docx) (`Sección 9`).
  - **Fase 5**: [`05_Diseno_Visual_Tableau_y_Presentacion.docx`](05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx) (`Sección 1.3`), hoja `LEEME_Poblaciones` (`6x1`) de [`Datos_Consolidados_Tableau_Public.xlsx`](05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx) y barra metodológica en Diapositiva 3 de [`05_Presentacion_Ejecutiva_30min.pdf`](05_Fase_Compartir_Share/05_Presentacion_Ejecutiva_30min.pdf).

---

## Versión 0.5.0 (`2026-11-11`) — Fase 5: Compartir (*Share* • Cursos 6 y 8)

### Añadido
- Script reproducible de visualización y deck [`05_Fase_Compartir_Share/scripts/05_generar_visualizaciones_y_deck.py`](05_Fase_Compartir_Share/scripts/05_generar_visualizaciones_y_deck.py) (`matplotlib`, `seaborn`, `openpyxl`, `PdfPages`).
- Siete visualizaciones ejecutivas a `300 DPI` en [`05_Fase_Compartir_Share/visualizaciones/`](05_Fase_Compartir_Share/visualizaciones/) (`01_demanda_vs_adopcion_top5_p1.png` a `07_evolucion_dss_2020_2024_p4.png`) con paleta daltónica segura (azul/naranja • Curso 6), ejes de barras en `$0`/`0%`, máximo `4` líneas, etiquetado directo, separación estricta de las 4 poblaciones y umbral `N >= 30`.
- Paquete multi-hoja limpio para Tableau Public [`05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx`](05_Fase_Compartir_Share/Datos_Consolidados_Tableau_Public.xlsx) (`9` hojas independientes incluyendo `LEEME_Poblaciones` y `SO_Paises_LatAm_N30` para mapa coroplético).
- Presentación ejecutiva panorámica `16:9` de `12` diapositivas [`05_Fase_Compartir_Share/05_Presentacion_Ejecutiva_30min.pdf`](05_Fase_Compartir_Share/05_Presentacion_Ejecutiva_30min.pdf) estructurada bajo la agenda oficial de 30 minutos (`4+5+10+3+3+5`) del **Curso 6**.
- Entregable Oficial 5 [`05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx`](05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx) con Marcos de McCandless y Fung, textos alternativos (Alt-Text), guía de diseño en Tableau Public + Tabla Complementaria, Notas del Orador, Matriz de Objeciones (datos/análisis/hallazgos) y Rúbrica de Evaluación de Diapositivas + Checklist de 13 puntos.

### Modificado
- Actualización de [`DIARIO_DE_DATOS_BITACORA.docx`](DIARIO_DE_DATOS_BITACORA.docx) añadiendo `TABLA 5` (Fase 5: Compartir).
- Homologación en Diapositiva 11 del deck y Tabla 3 del Entregable 5 (`34,9% nominal / 34,6% válido`, `Argentina $2.958,34`, `México $2.632,54` y aviso exploratorio `Pequeñas 2024 N=0` / subceldas DSS `N < 30`).

### Correcciones
- Desactivación de `text.parse_math` en `matplotlib` para evitar interpretación LaTeX en signos `$`; fondo blanco (`bbox`) y reubicación de etiquetas en Visual 01 (`17.2%`), Visual 02 (`JavaScript` y `TypeScript` fuera de ejes punteados), Visual 04 (2 líneas para `Med: $560` y `Med: $1.305` sin cruce con `$3.064`) y Visual 07 (conector directo a `$6.886` en 2021 y nota `2024: Small N=0`).

---

## Versión 0.4.0 (`2026-11-11`) — Fase 4: Analizar (*Analyze*) Ampliada (`Q01–Q13`)

### Añadido
- Script SQL relacional [`04_Fase_Analizar_Analyze/sql/04_consultas_analisis.sql`](04_Fase_Analizar_Analyze/sql/04_consultas_analisis.sql) ejecutado en SQLite con `CREATE TEMP TABLE`, `LEFT JOIN`, `INNER JOIN`, `COUNT(DISTINCT ...)`, `CASE WHEN`, `COALESCE`, `HAVING` y salvaguarda sin duplicación en uniones 1:N (`14` consultas `Q01–Q13`).
- Script de cálculo descriptivo [`04_Fase_Analizar_Analyze/scripts/04_analisis_estadistico_python.py`](04_Fase_Analizar_Analyze/scripts/04_analisis_estadistico_python.py) (`pandas`, `numpy`, `groupby()`, `size()`, `agg()`, `describe()`, `quantile()`).
- Resúmenes analíticos exportados en [`04_Fase_Analizar_Analyze/resumenes/`](04_Fase_Analizar_Analyze/resumenes/) (incluyendo `resumen_q11_tecnologia_vs_salario.csv`, `resumen_q12_modalidad_composicion_seniority.csv`, `resumen_q13_gob_categorias.csv` y `resumen_fase4_completo.json`).
- Entregable Oficial 4 [`04_Fase_Analizar_Analyze/04_Resumen_Analisis_SQL_y_Python.docx`](04_Fase_Analizar_Analyze/04_Resumen_Analisis_SQL_y_Python.docx) incorporando la Matriz Volumen vs. Compensación (`Q11`), el contraste **Correlación ≠ Causalidad** en Modalidad × Seniority (`Q12`) y el desglose por categoría (`Q13`).

### Modificado
- Reubicación de `Stack Overflow Chile 2024 (Agregado)` al cierre de su bloque en la Tabla 2, precisión narrativa sobre los cinco motores de BD sobre `22%` en Stack Overflow (incluyendo `SQLite`) y estandarización decimal con coma en tablas.
- Actualización de [`DIARIO_DE_DATOS_BITACORA.docx`](DIARIO_DE_DATOS_BITACORA.docx) con la entrada completa de Fase 4 (`Q01–Q13`).

---

## Versión 0.3.0 (`2026-11-11`) — Cierre Fase 3: Procesar (*Process*) y Auditoría V2

### Añadido
- Script reproducible en Python [`03_Fase_Procesar_Process/scripts/03_limpieza_y_validacion.py`](03_Fase_Procesar_Process/scripts/03_limpieza_y_validacion.py) con `pandas`, `numpy` y `re` (Curso 7).
- Seis conjuntos de datos limpios y normalizados (Ancho + Largo) en [`03_Fase_Procesar_Process/datos_limpios_processed/`](03_Fase_Procesar_Process/datos_limpios_processed/) (`3.352.439` bytes totales):
  - `GetOnBoard_Vacantes_2026_20261111_v01_clean.csv` (`679` filas; `235` salarios válidos).
  - `GetOnBoard_Habilidades_2026_20261111_v01_clean.csv` (`1.877` filas; `528` ofertas con match).
  - `StackOverflow_LatAm_2024_20261111_v01_clean.csv` (`3.074` filas; `1.341` salarios válidos; `46` en Chile).
  - `StackOverflow_Tecnologias_2024_20261111_v01_clean.csv` (`31.759` filas; conserva `72` encuestados LatAm con `NA` para `LEFT JOIN`).
  - `DataScienceSalaries_2020_2024_20261111_v01_clean.csv` (`6.599` filas intactas con salario mensual USD y ref. CLP).
  - `INE_ESI_2025_ReferenciaNacional_20261111_v01_clean.csv` (`2` indicadores oficiales con tipo de cambio BCCh `2026-11-10 = $969,80`).
- Entregable Oficial 3 [`03_Fase_Procesar_Process/03_Documentacion_Limpieza_y_Changelog.docx`](03_Fase_Procesar_Process/03_Documentacion_Limpieza_y_Changelog.docx) con los 6 tipos de validación (Curso 5), checklist de 12 puntos + 3 pasos de objetivo (Curso 4), control `N >= 30` y tabla Changelog de 7 campos.

### Modificado
- Reclasificación de `Databricks` (`Cloud`) y `Oracle Cloud (OCI)` (`Cloud`), y separación de `PowerShell` vs. `Bash/Shell` en Get on Board para lograr paridad taxonómica 1:1 con `StackOverflow_Tecnologias`.
- Actualización cronológica de [`DIARIO_DE_DATOS_BITACORA.docx`](DIARIO_DE_DATOS_BITACORA.docx) con la entrada de Fase 3.

### Correcciones
- **Regex `.NET` (`C#`):** Corregido límite de palabra para recuperar `15` ofertas reales con `.NET` (total `C#` = `54`).
- **Regex `Go`:** Excluido `'Go / No-Go'`, `'Go-Live'`, `'Go Deep'` y `'Go-To'` (`Go` = `19` ofertas reales sin falsos positivos).
- **Filtro `Oracle` DB:** Excluidas `8` menciones no-BD (certificaciones `OCP`, `OCI`, `Middleware/OSB/WebLogic/SOA`, `Flexcube`, `ERP Oracle`), quedando `36` ofertas de Oracle Database.
- **Paridad `JavaScript`:** Restringido a mención explícita del lenguaje (`186` ofertas) sin inferencia por frameworks para evitar inflación artificial frente a Stack Overflow `LanguageHaveWorkedWith`.

---

## Versión 0.2.0 (`2026-11-11`) — Fase 2: Preparar (*Prepare*) y Actualización de Alcance

### Añadido
- Incorporación de 3 fuentes complementarias junto a Get on Board (`72.797` registros crudos inmutables, `21,05 MiB` / `22,07 MB` totales en `datos_crudos_raw/`): `StackOverflow_DeveloperSurvey_2024_20261111_v01_raw.csv.gz` (`65.437`), `DataScienceSalaries_2020_2024_20261110_v01_raw.csv` (`6.599`) e `INE_ESI_2025_ReferenciaNacional_20261110_v01_raw.csv` (`2`).
- Entregable Oficial 2 [`02_Fase_Preparar_Prepare/02_Descripcion_Fuentes_y_ROCCC.docx`](02_Fase_Preparar_Prepare/02_Descripcion_Fuentes_y_ROCCC.docx) con metadatos completos, auditoría ROCCC, 0% PII, seguridad, licencias y diseño Wide/Long + salvaguarda SQL sin duplicación en uniones 1:N.

### Modificado
- Actualización formal de [`01_Alcance_del_Trabajo_SOW.docx`](01_Fase_Preguntar_Ask/01_Alcance_del_Trabajo_SOW.docx) y [`01_Declaracion_Tarea_Empresarial.docx`](01_Fase_Preguntar_Ask/01_Declaracion_Tarea_Empresarial.docx) ampliando Get on Board a todo 2026 hasta el corte `2026-11-10` (`America/Santiago GMT-3`) y alineando el Objetivo Métrico #3 a `N >= 30`.

### Correcciones
- Renombrado de `GetOnBoard_OfertasTech_2026_20261110_v01_raw.json` con periodo `_2026_` explícito (Curso 3).
- Ajuste de conteos exactos en `02_Descripcion_Fuentes_y_ROCCC.docx` (`72` registros LatAm con `NA` tecnológico en los 19 países completos; `6` outliers bajos `$8–$63 USD/año` en Stack Overflow Chile; pesos exactos en `bytes` y `MiB`).

---

## Versión 0.1.0 (`2026-11-10`) — Fase 1: Preguntar (*Ask*) Inicial

### Añadido
- Estructura inicial de carpetas por las 6 fases del proceso de análisis de datos de Google en el portafolio.
- Documentos iniciales de Fase 1: `01_Alcance_del_Trabajo_SOW.docx`, `01_Declaracion_Tarea_Empresarial.docx` y apertura de `DIARIO_DE_DATOS_BITACORA.docx` con las 4 preguntas de reflexión del Curso 8.
