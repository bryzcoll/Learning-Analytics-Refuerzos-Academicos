"""Cálculo reproducible de los indicadores del prototipo de refuerzos.

Este módulo procesa únicamente los datos sintéticos generados en ``fase4``.
La implementación sigue las reglas del diccionario y del notebook entregado.
"""

from __future__ import annotations

import pandas as pd

from fase4.generar_datos_sinteticos import CURSO_ID, FIN, INICIO, generar_datos


def calcular_indicadores(
    temas: pd.DataFrame,
    resultados_brutos: pd.DataFrame,
    encuestas_brutas: pd.DataFrame,
    curso_id: str = CURSO_ID,
    inicio: str = INICIO,
    fin: str = FIN,
) -> dict:
    """Limpia tablas y calcula Dₒ, Dₚ y Pᵣ por tema para un curso/ventana.

    Devuelve ``resumen``, tablas seleccionadas y un registro de exclusiones.
    Un componente ausente queda como NaN, nunca como cero.
    """
    desde, hasta = pd.Timestamp(inicio), pd.Timestamp(fin)
    if hasta < desde:
        raise ValueError("La fecha final debe ser posterior a la inicial")
    calidad: list[dict] = []

    def filtrar(tabla: pd.DataFrame, nombre: str, regla: str, mascara: pd.Series) -> pd.DataFrame:
        mascara = mascara.fillna(False)
        calidad.append({"tabla": nombre, "regla": regla, "filas_retiradas": int((~mascara).sum())})
        return tabla.loc[mascara].copy()

    r = resultados_brutos.copy()
    r["fecha_intento"] = pd.to_datetime(r["fecha_intento"], errors="coerce")
    for columna in ("puntaje_obtenido", "puntaje_maximo", "numero_intento"):
        r[columna] = pd.to_numeric(r[columna], errors="coerce")
    r = filtrar(r, "resultados", "curso y fecha dentro de ventana", r["curso_id"].eq(curso_id) & r["fecha_intento"].between(desde, hasta))
    ids_r = ["asignatura_id", "curso_id", "estudiante_id", "actividad_id", "pregunta_id", "tema_id"]
    r = filtrar(r, "resultados", "identificadores presentes", r[ids_r].notna().all(axis=1))
    r = filtrar(
        r, "resultados", "puntajes entre 0 y máximo positivo",
        r["puntaje_maximo"].gt(0) & r["puntaje_obtenido"].ge(0) & r["puntaje_obtenido"].le(r["puntaje_maximo"]),
    )
    r = filtrar(r, "resultados", "número de intento entero positivo", r["numero_intento"].ge(1) & r["numero_intento"].mod(1).eq(0))
    r = filtrar(r, "resultados", "duplicados exactos", ~r.duplicated())
    clave_intento = ["curso_id", "estudiante_id", "actividad_id", "pregunta_id", "numero_intento"]
    r = filtrar(r, "resultados", "intentos contradictorios", ~r.duplicated(clave_intento, keep=False))
    if not r.empty and r.groupby(["curso_id", "actividad_id", "pregunta_id"])["tema_id"].nunique().max() > 1:
        raise ValueError("Una pregunta figura en varios temas")
    clave_pregunta = ["curso_id", "estudiante_id", "actividad_id", "pregunta_id"]
    r = r.sort_values(["numero_intento", "fecha_intento"], kind="stable")
    r = filtrar(r, "resultados", "intentos posteriores al primero válido", ~r.duplicated(clave_pregunta))
    r["dificultad_respuesta"] = 100 * (1 - r["puntaje_obtenido"] / r["puntaje_maximo"])

    e = encuestas_brutas.copy()
    e["fecha_encuesta"] = pd.to_datetime(e["fecha_encuesta"], errors="coerce")
    e["dificultad_num"] = pd.to_numeric(e["dificultad_percibida"], errors="coerce")
    e = filtrar(e, "encuestas", "curso y fecha dentro de ventana", e["curso_id"].eq(curso_id) & e["fecha_encuesta"].between(desde, hasta))
    e = filtrar(e, "encuestas", "identificadores presentes", e[["curso_id", "estudiante_id", "tema_id"]].notna().all(axis=1))
    e = filtrar(e, "encuestas", "escala válida de 1 a 5", e["dificultad_num"].between(1, 5) & e["dificultad_num"].mod(1).eq(0))
    e = filtrar(e, "encuestas", "duplicados exactos", ~e.duplicated())
    clave_encuesta = ["curso_id", "estudiante_id", "tema_id"]
    e = e.sort_values("fecha_encuesta", kind="stable")
    e = filtrar(e, "encuestas", "respuestas anteriores a la última válida", ~e.duplicated(clave_encuesta, keep="last"))

    observada = (
        r.groupby(["curso_id", "tema_id"], as_index=False)
        .agg(
            dificultad_observada=("dificultad_respuesta", "mean"),
            n_estudiantes_academicos=("estudiante_id", "nunique"),
            n_respuestas_evaluadas=("pregunta_id", "size"),
            n_preguntas_distintas=("pregunta_id", "nunique"),
        )
    )
    e["dificultad_alta"] = e["dificultad_num"].isin([4, 5]).astype(int)
    percibida = (
        e.groupby(["curso_id", "tema_id"], as_index=False)
        .agg(
            dificultad_percibida_pct=("dificultad_alta", lambda valores: valores.mean() * 100),
            n_estudiantes_encuesta=("estudiante_id", "nunique"),
        )
    )
    catalogo = temas[["tema_id", "tema"]].assign(curso_id=curso_id)
    resumen = catalogo.merge(observada, on=["curso_id", "tema_id"], how="left").merge(percibida, on=["curso_id", "tema_id"], how="left")
    resumen["prioridad_refuerzo"] = 0.5 * resumen["dificultad_observada"] + 0.5 * resumen["dificultad_percibida_pct"]
    ambos = resumen[["dificultad_observada", "dificultad_percibida_pct"]].notna().all(axis=1)
    uno = resumen[["dificultad_observada", "dificultad_percibida_pct"]].notna().any(axis=1)

    def estado(fila) -> str:
        if not uno.iloc[fila.name]:
            return "Sin datos"
        if not ambos.iloc[fila.name]:
            return "Información incompleta"
        valor = fila["prioridad_refuerzo"]
        return "Alta" if valor >= 70 else "Media" if valor >= 40 else "Baja"

    resumen["estado"] = resumen.apply(estado, axis=1)
    resumen = resumen.sort_values("prioridad_refuerzo", ascending=False, na_position="last").reset_index(drop=True)
    for columna in ("dificultad_observada", "dificultad_percibida_pct", "prioridad_refuerzo"):
        if not resumen[columna].dropna().between(0, 100).all():
            raise AssertionError(f"{columna} fuera de rango")
    if not resumen.loc[resumen["estado"].eq("Información incompleta"), "prioridad_refuerzo"].isna().all():
        raise AssertionError("Prioridad calculada con un componente ausente")

    return {
        "resumen": resumen,
        "resultados_validos": r,
        "encuestas_validas": e,
        "calidad": pd.DataFrame(calidad),
        "curso_id": curso_id,
        "inicio": inicio,
        "fin": fin,
    }


def cargar_demo() -> dict:
    """Genera y calcula siempre el mismo ejemplo ficticio."""
    temas, resultados, encuestas = generar_datos()
    return calcular_indicadores(temas, resultados, encuestas)
