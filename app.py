"""Demostración Streamlit del flujo priorizar → planificar → seguir.

Ejecutar con ``streamlit run app.py``. Usa exclusivamente datos sintéticos.
"""

from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analitica import cargar_demo


st.set_page_config(page_title="Panel de refuerzo · Demo", page_icon="📘", layout="wide")


@st.cache_data(show_spinner=False)
def datos_demo() -> dict:
    return cargar_demo()


datos = datos_demo()
resumen = datos["resumen"]
n_estudiantes = len(set(datos["resultados_validos"]["estudiante_id"]) | set(datos["encuestas_validas"]["estudiante_id"]))
por_id = {fila.tema_id: fila for fila in resumen.itertuples(index=False)}
ids = resumen["tema_id"].tolist()
if "selected_topics" not in st.session_state:
    st.session_state.selected_topics = resumen.loc[resumen["prioridad_refuerzo"].notna(), "tema_id"].head(3).tolist()


def porcentaje(valor: float) -> str:
    return "—" if pd.isna(valor) else f"{valor:.1f}%".replace(".", ",")


def entero(valor: float) -> str:
    return "—" if pd.isna(valor) else str(int(valor))


def etiqueta_tema(tema_id: str) -> str:
    return por_id[tema_id].tema


def panel_tema(tema_id: str) -> None:
    fila = por_id[tema_id]
    st.subheader(fila.tema)
    st.caption(f"Estado: {fila.estado} · Período {datos['inicio']} a {datos['fin']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Dificultad observada · Dₒ", porcentaje(fila.dificultad_observada))
    m2.metric("Dificultad percibida · Dₚ", porcentaje(fila.dificultad_percibida_pct))
    m3.metric("Prioridad · Pᵣ", porcentaje(fila.prioridad_refuerzo) if pd.notna(fila.prioridad_refuerzo) else "No calculada")
    st.info(
        f"Cobertura: {entero(fila.n_estudiantes_academicos)} estudiantes con resultados, "
        f"{entero(fila.n_respuestas_evaluadas)} respuestas, "
        f"{entero(fila.n_preguntas_distintas)} preguntas y "
        f"{entero(fila.n_estudiantes_encuesta)} encuestas válidas."
    )
    if pd.isna(fila.prioridad_refuerzo):
        st.warning("Falta una fuente: el tema requiere revisión y justificación humana; la prioridad no se reemplaza por cero.")
    elif fila.dificultad_percibida_pct > fila.dificultad_observada:
        st.caption("La dificultad percibida supera la observada. Conviene preguntar por las dudas antes de elegir ejercicios.")
    else:
        st.caption("Revisa la muestra y las preguntas antes de decidir ejercicios y tiempo.")


st.title("Planificación de refuerzo académico")
st.caption("Prueba de concepto · datos sintéticos, no reales · Ayudante de cátedra · un curso y una ventana de siete días")
st.markdown(
    """<style>
    div[data-testid="stMetric"] {background:white;border:1px solid #d5e0ec;border-radius:12px;padding:15px;}
    div[data-testid="stVerticalBlockBorderWrapper"] {background:white;border-radius:12px;}
    </style>""",
    unsafe_allow_html=True,
)

tab_priorizar, tab_plan, tab_seguimiento = st.tabs(
    ["1 · Priorización", "2 · Plan de 120 minutos", "3 · Seguimiento"]
)

with tab_priorizar:
    st.subheader("Contexto del análisis")
    c1, c2, c3 = st.columns(3)
    c1.text_input("Asignatura", value="ASIGNATURA_DEMO", disabled=True)
    c2.text_input("Curso", value=datos["curso_id"], disabled=True)
    c3.text_input("Período analizado", value=f"{datos['inicio']} a {datos['fin']}", disabled=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Temas analizados", len(resumen))
    k2.metric("Estudiantes ficticios", n_estudiantes)
    k3.metric("Respuestas válidas", len(datos["resultados_validos"]))
    k4.metric("Encuestas válidas", len(datos["encuestas_validas"]))
    k5.metric("Filas excluidas", int(datos["calidad"]["filas_retiradas"].sum()))

    izquierda, derecha = st.columns([2.1, 1], gap="large")
    with izquierda:
        st.subheader("Temas que requieren refuerzo")
        st.caption("Ordenados por Pᵣ = 0,5 Dₒ + 0,5 Dₚ. Umbrales 70 / 40 provisionales.")
        tabla = pd.DataFrame(
            {
                "Tema": resumen["tema"],
                "Dₒ": resumen["dificultad_observada"].map(porcentaje),
                "Dₚ": resumen["dificultad_percibida_pct"].map(porcentaje),
                "Prioridad": resumen["prioridad_refuerzo"].map(lambda x: porcentaje(x) if pd.notna(x) else "No calculada"),
                "Cobertura A/E": [f"{entero(a)} / {entero(e)}" for a, e in zip(resumen["n_estudiantes_academicos"], resumen["n_estudiantes_encuesta"])],
                "Estado": resumen["estado"],
            }
        )
        st.dataframe(tabla, hide_index=True, width="stretch")
        grafo = resumen.dropna(subset=["prioridad_refuerzo"]).iloc[::-1]
        figura = go.Figure(go.Bar(
            x=grafo["prioridad_refuerzo"], y=grafo["tema"], orientation="h",
            marker_color=["#B7343C" if x >= 70 else "#B67508" if x >= 40 else "#178059" for x in grafo["prioridad_refuerzo"]],
            text=[f"{x:.1f}%" for x in grafo["prioridad_refuerzo"]], textposition="outside",
        ))
        figura.update_layout(height=280, margin=dict(l=10, r=50, t=10, b=20), xaxis_range=[0, 105],
                             xaxis_title="Prioridad de refuerzo", plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(figura, width="stretch")
        with st.expander("Ver limpieza y exclusiones por regla"):
            st.dataframe(datos["calidad"], hide_index=True, width="stretch")
    with derecha:
        tema_actual = st.selectbox("Abrir detalle del tema", ids, format_func=etiqueta_tema)
        panel_tema(tema_actual)
        if st.button("Agregar este tema al plan", width="stretch"):
            if tema_actual not in st.session_state.selected_topics:
                st.session_state.selected_topics.append(tema_actual)
            st.success("Tema agregado. Abre la pestaña «Plan de 120 minutos».")

    st.warning(
        "Interpretación responsable: datos ficticios. «Sin datos» no significa dificultad cero. "
        "La ponderación 50/50 y los umbrales 70/40 requieren validación; el panel no clasifica estudiantes."
    )

with tab_plan:
    st.subheader("Plan de la próxima sesión")
    st.caption("El ayudante elige temas, estrategia y minutos. La prioridad orienta, pero no asigna tiempo automáticamente.")
    seleccion = st.multiselect("Temas seleccionados", ids, key="selected_topics", format_func=etiqueta_tema)
    valores_plan = []
    with st.form("form_plan"):
        for i, tema_id in enumerate(seleccion):
            fila = por_id[tema_id]
            st.markdown(f"#### {fila.tema} · {fila.estado}")
            st.caption(f"Dₒ {porcentaje(fila.dificultad_observada)} · Dₚ {porcentaje(fila.dificultad_percibida_pct)} · Pᵣ {porcentaje(fila.prioridad_refuerzo)} · cobertura A/E {entero(fila.n_estudiantes_academicos)}/{entero(fila.n_estudiantes_encuesta)}")
            a, b = st.columns([1, 2])
            default_minutos = [50, 40, 30][i] if i < 3 else 0
            minutos = a.number_input("Minutos", min_value=0, max_value=120, step=5, value=default_minutos, key=f"min_{tema_id}")
            estrategia = b.text_input("Estrategia y ejercicios", value="Ejercicios guiados y práctica" if i == 0 else "Resolución colaborativa", key=f"estrategia_{tema_id}")
            justificacion = st.text_area("Justificación pedagógica", value="Prioridad y cobertura revisadas; ajustaré según las dudas del grupo.", key=f"justificacion_{tema_id}", height=70)
            valores_plan.append({
                "tema_id": tema_id, "tema": fila.tema, "minutos_planificados": int(minutos),
                "accion_pedagogica": estrategia.strip(), "justificacion": justificacion.strip(),
                "dificultad_observada": None if pd.isna(fila.dificultad_observada) else float(fila.dificultad_observada),
                "dificultad_percibida_pct": None if pd.isna(fila.dificultad_percibida_pct) else float(fila.dificultad_percibida_pct),
                "prioridad_refuerzo": None if pd.isna(fila.prioridad_refuerzo) else float(fila.prioridad_refuerzo),
                "n_estudiantes_academicos": None if pd.isna(fila.n_estudiantes_academicos) else int(fila.n_estudiantes_academicos),
                "n_estudiantes_encuesta": None if pd.isna(fila.n_estudiantes_encuesta) else int(fila.n_estudiantes_encuesta),
            })
        guardar = st.form_submit_button("Guardar planificación", width="stretch")
    total = sum(fila["minutos_planificados"] for fila in valores_plan)
    st.progress(min(total / 120, 1.0), text=f"{total} / 120 minutos asignados")
    if guardar:
        if not seleccion:
            st.error("Selecciona al menos un tema.")
        elif total != 120:
            st.error("La suma de minutos debe ser exactamente 120.")
        elif any(not fila["accion_pedagogica"] or not fila["justificacion"] for fila in valores_plan):
            st.error("Completa estrategia y justificación en cada tema.")
        else:
            st.session_state.plan = {
                "sesion_id": "DEMO-" + uuid4().hex[:8].upper(),
                "curso_id": datos["curso_id"], "periodo_inicio": datos["inicio"], "periodo_fin": datos["fin"],
                "fecha_guardado": datetime.now().isoformat(timespec="seconds"),
                "duracion_minutos": 120, "temas": valores_plan,
            }
            st.session_state.pop("seguimiento", None)
            st.success("Plan guardado en esta sesión. Continúa en «Seguimiento».")
    if "plan" in st.session_state:
        st.download_button("Descargar plan JSON de demostración", json.dumps(st.session_state.plan, ensure_ascii=False, indent=2),
                           file_name="plan_demo.json", mime="application/json")

with tab_seguimiento:
    st.subheader("Seguimiento de la sesión")
    if "plan" not in st.session_state:
        st.info("Guarda primero un plan de 120 minutos en la pestaña anterior.")
    else:
        plan = st.session_state.plan
        st.caption(f"Sesión {plan['sesion_id']} · curso {plan['curso_id']} · comparación de lo previsto con lo realizado")
        valores_seguimiento = []
        with st.form("form_seguimiento"):
            asistentes = st.number_input("Asistentes únicos (dato ficticio de demostración)", min_value=0, max_value=n_estudiantes, value=min(24, n_estudiantes))
            for tema in plan["temas"]:
                st.markdown(f"#### {tema['tema']}")
                a, b = st.columns([1, 3])
                a.metric("Minutos previstos", tema["minutos_planificados"])
                real = b.number_input("Minutos reales", min_value=0, max_value=240, value=tema["minutos_planificados"],
                                      key=f"real_{tema['tema_id']}")
                nota = st.text_input("Observación pedagógica (sin nombres)", key=f"nota_{tema['tema_id']}")
                valores_seguimiento.append({"tema_id": tema["tema_id"], "tema": tema["tema"],
                                            "minutos_planificados": tema["minutos_planificados"], "minutos_reales": int(real),
                                            "observaciones": nota.strip()})
            nota_general = st.text_area("Observación general (sin nombres)")
            guardar_seg = st.form_submit_button("Guardar seguimiento", width="stretch")
        total_real = sum(fila["minutos_reales"] for fila in valores_seguimiento)
        st.metric("Tiempo real registrado", f"{total_real} min", delta=f"{total_real - 120:+d} min frente al plan")
        if guardar_seg:
            st.session_state.seguimiento = {
                "sesion_id": plan["sesion_id"], "fecha_guardado": datetime.now().isoformat(timespec="seconds"),
                "asistentes_unicos": int(asistentes), "minutos_reales_totales": total_real,
                "observacion_general": nota_general.strip(), "temas": valores_seguimiento,
            }
            st.success("Seguimiento guardado en esta sesión. Las diferencias documentan la ejecución; no son una penalización.")
        if "seguimiento" in st.session_state:
            st.download_button("Descargar seguimiento JSON de demostración",
                               json.dumps(st.session_state.seguimiento, ensure_ascii=False, indent=2),
                               file_name="seguimiento_demo.json", mime="application/json")
        st.info("La asistencia voluntaria no mide interés. Este registro no demuestra mejora de aprendizaje; para ello se requiere el plan de validación.")

st.divider()
st.caption("Prototipo educativo local · datos generados con semilla fija · sin integración con eVirtual, autenticación ni persistencia institucional")
