# Fase 4 · Prueba de concepto

El [notebook autónomo](Fase_4_Prueba_de_Concepto.ipynb) demuestra que Dₒ, Dₚ y Pᵣ se pueden calcular con datos sintéticos. Incluye generación y carga de tres tablas, limpieza auditable, cálculo, tablero Plotly y sección «Lo que este prototipo no puede decir todavía». No requiere descargar un dataset ni usar datos reales de UCuenca.

## Archivos

| Archivo | Función |
|---|---|
| `Fase_4_Prueba_de_Concepto.ipynb` | Entregable principal, autónomo para Google Colab. |
| `generar_datos_sinteticos.py` | Generador documentado con semilla `20261016`; su código está incluido en el notebook. |
| `datos/*.csv` | Catálogo de temas, resultados por intento y encuestas ficticias. |
| `tablero_prueba_concepto.html` | Resultado Plotly interactivo que puede abrirse sin Python. |
| `construir_notebook.py` | Fuente que reconstruye el notebook si se modifican sus reglas o explicación. |

## Ejecutar

**En Colab:** cargar solo el `.ipynb` y pulsar **Entorno de ejecución → Ejecutar todo**. La primera celda instala Plotly si es necesario; el generador interno escribe los CSV en el entorno temporal.

**En local:** desde la raíz del repositorio:

```bash
python -m pip install -r fase4/requirements.txt
cd fase4
jupyter lab Fase_4_Prueba_de_Concepto.ipynb
```

Ejecutar todas las celdas en orden. El notebook escribe `datos/` y `tablero_prueba_concepto.html` relativos al directorio de trabajo. Para reconstruir el archivo antes de ejecutarlo: `python fase4/construir_notebook.py` desde la raíz.

## Datos y resultados esperados

La ventana fija es **9–15 de octubre de 2026**, un curso, cinco temas y 64 estudiantes ficticios. Los CSV contienen 911 resultados brutos por intento y 185 respuestas brutas de encuesta. Tras la limpieza quedan **810 primeras respuestas válidas** y **180 últimas encuestas válidas**. Probabilidad condicional ocupa el primer lugar con Pᵣ ≈ 62,64; Regresión lineal conserva Dₒ, pero su Pᵣ queda ausente porque no se generaron encuestas de ese tema.

- Dₒ = promedio de `100 × (1 − puntaje_obtenido/puntaje_maximo)` sobre primeras respuestas válidas.
- Dₚ = porcentaje de últimas encuestas válidas con valor 4 o 5.
- Pᵣ = `0,5Dₒ + 0,5Dₚ` únicamente cuando existen ambos componentes.

El tablero Plotly muestra ranking, componentes y cobertura, como la [pantalla de priorización](../docs/03_diseno_herramienta.pdf). La [app](../app.py) permite demostrar el paso siguiente: planificar 120 minutos y registrar ejecución. Son datos **sintéticos**: las cifras no describen a la Universidad de Cuenca.
