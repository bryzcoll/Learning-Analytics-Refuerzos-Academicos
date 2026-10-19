"""Construye el notebook autónomo de la Fase 4 a partir del generador versionado."""

from pathlib import Path

import nbformat as nbf


BASE = Path(__file__).resolve().parent
generador = (BASE / "generar_datos_sinteticos.py").read_text(encoding="utf-8")
generador = generador.split('if __name__ == "__main__":')[0].rstrip()

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
    "colab": {"name": "Fase_4_Prueba_de_Concepto.ipynb", "provenance": []},
}

nb.cells = [
    nbf.v4.new_markdown_cell("""# Fase 4 · Prueba de concepto de Learning Analytics

**Herramienta:** Sistema de Analítica para la Planificación de Refuerzos Académicos.  
**Actor y decisión:** el ayudante de cátedra elige los temas y ejercicios de la próxima sesión semanal de refuerzo.  
**Pregunta descriptiva:** ¿qué contenidos presentan mayores dificultades según los ejercicios y las necesidades expresadas por los estudiantes?

Este notebook implementa el indicador central definido en *Fase 1 y Fase 2.pdf*. Usa **datos enteramente sintéticos**; ningún registro representa a estudiantes o cursos reales de la Universidad de Cuenca. Se ejecuta de arriba abajo en Google Colab con «Ejecutar todo», sin archivos externos. El código de generación también se entrega como `generar_datos_sinteticos.py`.

La visualización Plotly reproduce los elementos principales del [wireframe de priorización](../docs/03_diseno_herramienta.pdf): ranking por tema, Dₒ, Dₚ, Pᵣ y cobertura. La variante de Fase 4 usa las cifras calculadas aquí. Los planes y el seguimiento interactivos se demuestran aparte en `app.py`; este notebook verifica el indicador central."""),
    nbf.v4.new_markdown_cell("""## 1. Entorno y datos

La ventana de análisis es **del 9 al 15 de octubre de 2026**, antes de la sesión del 16 de octubre. Se simulan un curso, cinco temas y 64 estudiantes con códigos seudónimos. Las tablas tienen esta granularidad:

| Tabla | Unidad de cada fila | Uso |
|---|---|---|
| `temas` | tema de un curso | nombres para mostrar |
| `resultados` | estudiante–actividad–pregunta–intento | dificultad observada |
| `encuestas` | estudiante–tema–respuesta | dificultad percibida |

El generador usa semilla fija. Las probabilidades de acierto y de respuesta son parámetros de simulación, no estimaciones de la UCuenca. Se añade a propósito un tema sin encuesta, un segundo intento, duplicados, datos fuera de período y valores inválidos para verificar las reglas del diccionario."""),
    nbf.v4.new_code_cell("""import importlib.util
import subprocess
import sys

if importlib.util.find_spec("plotly") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "plotly>=5.18,<7"])

from IPython.display import display
import plotly.graph_objects as go
from plotly.subplots import make_subplots"""),
    nbf.v4.new_markdown_cell("""### Script documentado de generación sintética

La siguiente celda contiene íntegro el generador necesario para ejecutar el notebook en Colab sin subir archivos adicionales. La versión `.py` incluida en el entregable permite regenerar las tres tablas CSV por separado."""),
    nbf.v4.new_code_cell(generador),
    nbf.v4.new_code_cell("""datos_dir = Path("datos")
datos_dir.mkdir(exist_ok=True)
tablas_generadas = dict(zip(("temas", "resultados", "encuestas"), generar_datos()))
for nombre, tabla in tablas_generadas.items():
    tabla.to_csv(datos_dir / f"{nombre}.csv", index=False)

temas = pd.read_csv(datos_dir / "temas.csv")
resultados_brutos = pd.read_csv(datos_dir / "resultados.csv")
encuestas_brutas = pd.read_csv(datos_dir / "encuestas.csv")

print(f"Semilla: {SEMILLA} | Ventana: {INICIO} a {FIN}")
print(f"Cursos: {resultados_brutos['curso_id'].nunique()} | Estudiantes simulados: 64 | Temas: {len(temas)}")
print(f"Resultados por intento: {len(resultados_brutos)} | Respuestas de encuesta: {len(encuestas_brutas)}")
print("Tablas CSV generadas y cargadas desde:", datos_dir)
print("Los identificadores de curso y asignatura son ficticios.")
display(temas)
display(resultados_brutos.head(3))
display(encuestas_brutas.head(3))"""),
    nbf.v4.new_markdown_cell("""## 2. Reglas de limpieza

Se usan solo registros del mismo curso y de la ventana de siete días. Para resultados, se exige estudiante, curso, actividad, pregunta, tema, fecha y puntajes válidos. Los duplicados exactos se eliminan; si un mismo intento tiene valores contradictorios, se excluye ese intento. Después se toma el **primer intento válido** de cada estudiante por actividad y pregunta. Para encuestas se conserva la **última respuesta válida** de cada estudiante por tema; «No he trabajado este tema» y respuestas fuera de 1 a 5 se excluyen. La ausencia de datos nunca se transforma en cero.

El orden de filtros y el número de filas retiradas se muestran para que el tratamiento sea auditable."""),
    nbf.v4.new_code_cell("""inicio = pd.Timestamp(INICIO)
fin = pd.Timestamp(FIN)
calidad = []

def filtrar(tabla, nombre, motivo, mascara_valida):
    retiradas = int((~mascara_valida).sum())
    calidad.append({"tabla": nombre, "regla": motivo, "filas_retiradas": retiradas})
    return tabla.loc[mascara_valida].copy()

r = resultados_brutos.copy()
r["fecha_intento"] = pd.to_datetime(r["fecha_intento"], errors="coerce")
for col in ["puntaje_obtenido", "puntaje_maximo", "numero_intento"]:
    r[col] = pd.to_numeric(r[col], errors="coerce")

r = filtrar(r, "resultados", "fecha dentro del período", r["fecha_intento"].between(inicio, fin))
ids_r = ["asignatura_id", "curso_id", "estudiante_id", "actividad_id", "pregunta_id", "tema_id"]
r = filtrar(r, "resultados", "identificadores presentes", r[ids_r].notna().all(axis=1))
r = filtrar(r, "resultados", "puntajes entre 0 y máximo positivo",
            r["puntaje_maximo"].gt(0) & r["puntaje_obtenido"].ge(0)
            & r["puntaje_obtenido"].le(r["puntaje_maximo"]))
r = filtrar(r, "resultados", "número de intento entero positivo",
            r["numero_intento"].ge(1) & r["numero_intento"].mod(1).eq(0))
r = filtrar(r, "resultados", "duplicados exactos", ~r.duplicated())

clave_intento = ["curso_id", "estudiante_id", "actividad_id", "pregunta_id", "numero_intento"]
r = filtrar(r, "resultados", "intentos contradictorios", ~r.duplicated(clave_intento, keep=False))
assert r.groupby(["curso_id", "actividad_id", "pregunta_id"])["tema_id"].nunique().max() == 1, "Una pregunta aparece en varios temas"

clave_pregunta = ["curso_id", "estudiante_id", "actividad_id", "pregunta_id"]
r = r.sort_values(["numero_intento", "fecha_intento"], kind="stable")
r = filtrar(r, "resultados", "intentos posteriores al primero válido", ~r.duplicated(clave_pregunta))
r["dificultad_respuesta"] = (1 - r["puntaje_obtenido"] / r["puntaje_maximo"]) * 100

e = encuestas_brutas.copy()
e["fecha_encuesta"] = pd.to_datetime(e["fecha_encuesta"], errors="coerce")
e["dificultad_num"] = pd.to_numeric(e["dificultad_percibida"], errors="coerce")
e = filtrar(e, "encuestas", "fecha dentro del período", e["fecha_encuesta"].between(inicio, fin))
e = filtrar(e, "encuestas", "identificadores presentes", e[["curso_id", "estudiante_id", "tema_id"]].notna().all(axis=1))
e = filtrar(e, "encuestas", "escala válida de 1 a 5 (incluye 'No he trabajado' como excluido)",
            e["dificultad_num"].between(1, 5) & e["dificultad_num"].mod(1).eq(0))
e = filtrar(e, "encuestas", "duplicados exactos", ~e.duplicated())
clave_encuesta = ["curso_id", "estudiante_id", "tema_id"]
e = e.sort_values("fecha_encuesta", kind="stable")
e = filtrar(e, "encuestas", "respuestas anteriores a la última válida", ~e.duplicated(clave_encuesta, keep="last"))

display(pd.DataFrame(calidad))
print(f"Resultados seleccionados: {len(r)} | Encuestas seleccionadas: {len(e)}")"""),
    nbf.v4.new_markdown_cell(r"""## 3. Indicadores por curso y tema

Se respetan las fórmulas acordadas en la Fase 2:

\(D_o = 100\,\operatorname{promedio}_i(1 - P_i/P_{max,i})\), dando **igual peso a cada respuesta válida**.  
\(D_p = 100\,\#(respuestas\ 4\ o\ 5)/\#(respuestas\ válidas)\), una respuesta por estudiante y tema.  
\(P_r = 0.5D_o + 0.5D_p\), solamente si ambos existen.

El índice ordena temas para apoyar la planificación. No representa probabilidad de fracaso, diagnóstico individual ni tiempo de clase recomendado. Junto a cada valor se muestran los tamaños de ambas fuentes, porque sus participantes pueden diferir."""),
    nbf.v4.new_code_cell("""observada = (r.groupby(["curso_id", "tema_id"], as_index=False)
    .agg(dificultad_observada=("dificultad_respuesta", "mean"),
         n_estudiantes_academicos=("estudiante_id", "nunique"),
         n_respuestas_evaluadas=("pregunta_id", "size"),
         n_preguntas_distintas=("pregunta_id", "nunique")))

e["dificultad_alta"] = e["dificultad_num"].isin([4, 5]).astype(int)
percibida = (e.groupby(["curso_id", "tema_id"], as_index=False)
    .agg(dificultad_percibida_pct=("dificultad_alta", lambda x: x.mean() * 100),
         n_estudiantes_encuesta=("estudiante_id", "nunique")))

catalogo = temas.assign(curso_id=CURSO_ID)
resumen = (catalogo.merge(observada, on=["curso_id", "tema_id"], how="left")
    .merge(percibida, on=["curso_id", "tema_id"], how="left"))
ambos = resumen[["dificultad_observada", "dificultad_percibida_pct"]].notna().all(axis=1)
resumen["prioridad_refuerzo"] = (
    0.5 * resumen["dificultad_observada"]
    + 0.5 * resumen["dificultad_percibida_pct"]
)
resumen["estado"] = np.where(ambos, "Calculable", "Información incompleta")
resumen = resumen.sort_values("prioridad_refuerzo", ascending=False, na_position="last").reset_index(drop=True)

assert resumen["prioridad_refuerzo"].dropna().between(0, 100).all()
assert resumen.loc[resumen["estado"].eq("Información incompleta"), "prioridad_refuerzo"].isna().all()
assert resumen.loc[resumen["tema_id"].eq("T05"), "prioridad_refuerzo"].isna().all()
assert r.duplicated(clave_pregunta).sum() == 0
assert e.duplicated(clave_encuesta).sum() == 0

display(resumen.round(2))
print("Tema con mayor prioridad calculable:", resumen.loc[resumen["prioridad_refuerzo"].first_valid_index(), "tema"])
print("Prioridades incompletas:", int(resumen["prioridad_refuerzo"].isna().sum()))"""),
    nbf.v4.new_markdown_cell("""## 4. Vista tipo tablero para el ayudante

Propuesta funcional para una pantalla de planificación: **ranking de prioridad**, comparación de sus dos componentes y **tabla con cobertura**. La fila «Información incompleta» permanece visible y no recibe un valor inventado. El ayudante revisaría los primeros temas junto con los tamaños de muestra y elegiría contenidos y ejercicios para la próxima sesión. El tablero no impone un umbral ni toma la decisión por él.

Esta composición corresponde a la primera pantalla del wireframe de Fase 3. El HTML generado permite abrir el tablero sin ejecutar Python. La aplicación Streamlit del repositorio demuestra la acción de planificar y registrar seguimiento."""),
    nbf.v4.new_code_cell("""def formato_pct(valor):
    return "Sin datos" if pd.isna(valor) else f"{valor:.1f}%"

orden = resumen["tema"].tolist()
prioridad = resumen.dropna(subset=["prioridad_refuerzo"])
fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "table", "colspan": 2}, None]],
    subplot_titles=("Prioridad de refuerzo por tema", "Componentes del indicador", "Cobertura y resultados"),
    row_heights=[0.56, 0.44], vertical_spacing=0.14,
)
fig.add_trace(go.Bar(
    x=prioridad["prioridad_refuerzo"], y=prioridad["tema"], orientation="h",
    name="Prioridad", marker_color="#315caa",
    text=prioridad["prioridad_refuerzo"].map(lambda x: f"{x:.1f}"), textposition="outside",
    hovertemplate="%{y}<br>Prioridad: %{x:.1f}/100<extra></extra>",
), row=1, col=1)
for columna, etiqueta, color in [
    ("dificultad_observada", "Observada", "#d97732"),
    ("dificultad_percibida_pct", "Percibida", "#49998b"),
]:
    fig.add_trace(go.Bar(
        x=resumen[columna], y=resumen["tema"], orientation="h",
        name=etiqueta, marker_color=color,
        hovertemplate=f"%{{y}}<br>{etiqueta}: %{{x:.1f}}%<extra></extra>",
    ), row=1, col=2)

columnas_tabla = [
    ("Tema", resumen["tema"].tolist()),
    ("Do", [formato_pct(x) for x in resumen["dificultad_observada"]]),
    ("Dp", [formato_pct(x) for x in resumen["dificultad_percibida_pct"]]),
    ("Pr", [formato_pct(x) for x in resumen["prioridad_refuerzo"]]),
    ("Est. acad.", ["—" if pd.isna(x) else str(int(x)) for x in resumen["n_estudiantes_academicos"]]),
    ("Respuestas", ["—" if pd.isna(x) else str(int(x)) for x in resumen["n_respuestas_evaluadas"]]),
    ("Preguntas", ["—" if pd.isna(x) else str(int(x)) for x in resumen["n_preguntas_distintas"]]),
    ("Encuestas", ["—" if pd.isna(x) else str(int(x)) for x in resumen["n_estudiantes_encuesta"]]),
    ("Estado", resumen["estado"].tolist()),
]
fig.add_trace(go.Table(
    columnwidth=[210, 65, 65, 65, 75, 90, 80, 80, 145],
    header=dict(values=[c[0] for c in columnas_tabla], fill_color="#e8eef8", align="left", font=dict(size=12)),
    cells=dict(values=[c[1] for c in columnas_tabla], fill_color="white", align="left", height=30, font=dict(size=11)),
), row=2, col=1)
fig.update_layout(
    title=f"Planificación del refuerzo · {CURSO_ID} · {INICIO} a {FIN}",
    width=1450, height=850, barmode="group", template="plotly_white",
    legend=dict(orientation="h", y=1.05, x=0.63), margin=dict(l=90, r=45, t=105, b=45),
)
fig.update_xaxes(range=[0, 108], title_text="Puntos / 100", row=1, col=1)
fig.update_xaxes(range=[0, 100], title_text="Porcentaje", row=1, col=2)
fig.update_yaxes(autorange="reversed", row=1, col=1)
fig.update_yaxes(autorange="reversed", row=1, col=2)
fig.show()
fig.write_html("tablero_prueba_concepto.html", include_plotlyjs=True, full_html=True)
print("Tablero guardado en tablero_prueba_concepto.html")"""),
    nbf.v4.new_markdown_cell("""## 5. Lo que este prototipo no puede decir todavía

1. **Validez técnica.** Que el índice sea calculable no demuestra que mida necesidades reales de refuerzo. Hay que contrastarlo con resultados posteriores o juicio docente, evaluar la ponderación 50/50 y revisar si las preguntas de los temas son comparables.
2. **Impacto pedagógico.** Los datos sintéticos no demuestran que planificar con este tablero mejore comprensión, asistencia o notas. El plan de validación del grupo propone una comparación con grupos y períodos adecuados; no se ha ejecutado y se conserva fuera de este repositorio.
3. **Usabilidad y adopción.** No se ha probado si ayudantes y docentes entienden el índice, las coberturas ni la etiqueta «Información incompleta». Hacen falta pruebas con usuarios.
4. **Representatividad y sesgos.** Una encuesta voluntaria puede atraer más a quienes tienen dificultades; quienes faltan en resultados o encuestas pueden diferir. Las dos fuentes no contienen necesariamente a los mismos estudiantes.
5. **Privacidad y operación.** Con datos reales habría que autorizar acceso, seudonimizar, limitar las vistas por rol y evitar desgloses de grupos pequeños. No se ha implementado la conexión con eVirtual. La aplicación de demostración registra acciones solo en la sesión del navegador.

**Modelo predictivo:** no aplica en esta fase porque la pregunta y el indicador de las Fases 1 y 2 son descriptivos. No se generan predicciones individuales.

**Uso de IA generativa:** se utilizó OpenAI Codex para redactar y programar este prototipo. La ejecución reproducible y las comprobaciones de rangos, duplicados y datos faltantes se verifican con las celdas anteriores. La [declaración completa](../docs/07_uso_ia.pdf) requiere revisión final del grupo."""),
]

salida = BASE / "Fase_4_Prueba_de_Concepto.ipynb"
nbf.write(nb, salida)
print(salida)
