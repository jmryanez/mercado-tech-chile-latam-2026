#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/ejecutar_todo.py
Orquestador maestro y reproducible del pipeline completo de datos del portafolio.
Ejecuta la secuencia integral desde la limpieza hasta la generación de todos los artefactos derivados.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLANTILLAS = ROOT / "scripts" / "plantillas"


def restaurar_plantillas_si_es_necesario() -> None:
    """Restaura archivos base desde scripts/plantillas si fueron desvinculados en un entorno de validación."""
    if not PLANTILLAS.exists():
        return

    archivos_base = [
        "01_Fase_Preguntar_Ask/01_Declaracion_Tarea_Empresarial.docx",
        "01_Fase_Preguntar_Ask/01_Alcance_del_Trabajo_SOW.docx",
        "02_Fase_Preparar_Prepare/02_Descripcion_Fuentes_y_ROCCC.docx",
        "03_Fase_Procesar_Process/03_Documentacion_Limpieza_y_Changelog.docx",
        "04_Fase_Analizar_Analyze/04_Resumen_Analisis_SQL_y_Python.docx",
        "05_Fase_Compartir_Share/05_Diseno_Visual_Tableau_y_Presentacion.docx",
        "06_Fase_Actuar_Act/06_Plan_de_Accion_y_Conclusiones_Finales.docx",
        "DIARIO_DE_DATOS_BITACORA.docx",
        "index.html",
        "README.md",
    ]

    for rel in archivos_base:
        destino = ROOT / rel
        origen = PLANTILLAS / rel
        if not destino.exists() and origen.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)


def ejecutar_paso(cmd: list[str], descripcion: str) -> None:
    """Ejecuta un comando del pipeline verificando su código de salida."""
    print(f"\n[PIPELINE] >>> {descripcion}...")
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Falló: {descripcion} (Código {res.returncode})")
        print("--- STDERR ---")
        print(res.stderr[-1000:])
        print("--- STDOUT ---")
        print(res.stdout[-1000:])
        sys.exit(res.returncode)
    print(f"[OK] {descripcion} completado exitosamente.")


def main() -> None:
    print("=====================================================================")
    print("INICIANDO EJECUCIÓN MAESTRA DEL PIPELINE (PORTAFOLIO v1.13.9)")
    print("=====================================================================")

    # Paso 0: Restauración de plantillas base si fueron eliminadas
    restaurar_plantillas_si_es_necesario()

    # Paso 1: Procesar (Limpieza y validación de fuentes crudas)
    ejecutar_paso(
        [sys.executable, "03_Fase_Procesar_Process/scripts/03_limpieza_y_validacion.py"],
        "Paso 1: Fase Procesar (03_limpieza_y_validacion.py)",
    )

    # Paso 2: Analizar (Análisis estadístico, SQL y cálculo de derivadas)
    ejecutar_paso(
        [sys.executable, "04_Fase_Analizar_Analyze/scripts/04_analisis_estadistico_python.py"],
        "Paso 2: Fase Analizar (04_analisis_estadistico_python.py)",
    )

    # Paso 3: Descargas y explorador consolidado
    ejecutar_paso(
        [sys.executable, "scripts/generar_descargas.py"],
        "Paso 3: Generación de Descargas y Explorador (scripts/generar_descargas.py)",
    )

    # Paso 4: Compartir (Visualizaciones PNG, Excel y Deck PDF)
    ejecutar_paso(
        [sys.executable, "05_Fase_Compartir_Share/scripts/05_generar_visualizaciones_y_deck.py"],
        "Paso 4: Fase Compartir (05_generar_visualizaciones_y_deck.py)",
    )

    # Paso 5: Actuar (Cuaderno reproducible Jupyter/Kaggle ejecutado)
    ejecutar_paso(
        [sys.executable, "scripts/generar_y_ejecutar_cuaderno.py"],
        "Paso 5: Cuaderno Jupyter/Kaggle (scripts/generar_y_ejecutar_cuaderno.py)",
    )

    # Paso 6: Actualización y sincronización de documentos .docx
    ejecutar_paso(
        [sys.executable, "scripts/actualizar_documentos_docx.py"],
        "Paso 6: Sincronización de Documentos .docx (scripts/actualizar_documentos_docx.py)",
    )

    # Paso 7: Actualización del sitio interactivo index.html
    ejecutar_paso(
        [sys.executable, "scripts/actualizar_index_html.py"],
        "Paso 7: Actualización de index.html (scripts/actualizar_index_html.py)",
    )

    # Paso 8: Actualización de la documentación README.md
    ejecutar_paso(
        [sys.executable, "scripts/actualizar_readme.py"],
        "Paso 8: Actualización de README.md (scripts/actualizar_readme.py)",
    )

    print("\n=====================================================================")
    print("PIPELINE MAESTRO COMPLETADO EXITOSAMENTE CON CÓDIGO 0")
    print("=====================================================================")


if __name__ == "__main__":
    main()
