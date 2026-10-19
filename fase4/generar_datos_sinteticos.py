"""Datos ficticios y reproducibles para la prueba de concepto de refuerzos.

No contiene información de estudiantes ni cursos reales de la UCuenca.
La semilla fija permite repetir exactamente las cifras del notebook.
"""

from pathlib import Path

import numpy as np
import pandas as pd


SEMILLA = 20261016
CURSO_ID = "CURSO_DEMO_01"
ASIGNATURA_ID = "ASIGNATURA_DEMO"
INICIO = "2026-10-09"
FIN = "2026-10-15"


def generar_datos(semilla=SEMILLA):
    """Devuelve catálogo de temas, resultados por intento y encuestas por respuesta.

    Simula 64 estudiantes seudónimos, un curso y una ventana de siete días.
    Los puntajes son aciertos de 10; la probabilidad de acierto varía por tema.
    Se agregan duplicados, intentos posteriores y algunos errores para probar
    las reglas de limpieza. T05 no tiene encuesta: sirve para comprobar que la
    prioridad queda ausente cuando falta uno de sus dos componentes.
    """
    rng = np.random.default_rng(semilla)
    temas = pd.DataFrame(
        [
            ("T01", "Probabilidad condicional", 0.46, [0.03, 0.07, 0.18, 0.34, 0.38]),
            ("T02", "Distribuciones", 0.67, [0.12, 0.19, 0.28, 0.26, 0.15]),
            ("T03", "Intervalos de confianza", 0.75, [0.18, 0.27, 0.31, 0.16, 0.08]),
            ("T04", "Pruebas de hipótesis", 0.53, [0.05, 0.10, 0.20, 0.35, 0.30]),
            ("T05", "Regresión lineal", 0.63, None),
        ],
        columns=["tema_id", "tema", "prob_acierto_simulada", "prob_encuesta_simulada"],
    )
    estudiantes = [f"E{i:03d}" for i in range(1, 65)]
    dias = pd.date_range(INICIO, FIN, freq="D")
    resultados = []
    encuestas = []

    for tema in temas.itertuples(index=False):
        for estudiante in estudiantes:
            if rng.random() < 0.84:
                actividad = f"ACT_{tema.tema_id}"
                for numero_pregunta in range(1, 4):
                    fecha = rng.choice(dias)
                    base = dict(
                        asignatura_id=ASIGNATURA_ID,
                        curso_id=CURSO_ID,
                        estudiante_id=estudiante,
                        actividad_id=actividad,
                        tipo_actividad="ejercicio",
                        pregunta_id=f"{tema.tema_id}_P{numero_pregunta}",
                        tema_id=tema.tema_id,
                        puntaje_maximo=10,
                    )
                    resultados.append(
                        {**base, "numero_intento": 1, "fecha_intento": str(pd.Timestamp(fecha).date()),
                         "puntaje_obtenido": int(rng.binomial(10, tema.prob_acierto_simulada))}
                    )
                    if rng.random() < 0.12:
                        resultados.append(
                            {**base, "numero_intento": 2, "fecha_intento": str(dias[-1].date()),
                             "puntaje_obtenido": int(rng.binomial(10, min(0.95, tema.prob_acierto_simulada + 0.15)))}
                        )
            if tema.prob_encuesta_simulada is not None and rng.random() < 0.72:
                valor = int(rng.choice(np.arange(1, 6), p=tema.prob_encuesta_simulada))
                encuestas.append(
                    {"curso_id": CURSO_ID, "estudiante_id": estudiante, "tema_id": tema.tema_id,
                     "fecha_encuesta": str(pd.Timestamp(rng.choice(dias)).date()), "dificultad_percibida": str(valor)}
                )

    # Casos controlados para verificar la limpieza, sin alterar el diseño del indicador.
    resultados.extend([resultados[0].copy(), resultados[1].copy()])
    resultados.append({**resultados[2], "puntaje_obtenido": 12})
    resultados.append({**resultados[3], "estudiante_id": None})
    resultados.append({**resultados[4], "fecha_intento": "2026-10-08"})
    encuestas.append(encuestas[0].copy())
    encuestas.append({**encuestas[1], "dificultad_percibida": "6"})
    encuestas.append({**encuestas[2], "fecha_encuesta": "2026-10-08"})
    encuestas.append({**encuestas[3], "dificultad_percibida": "No he trabajado este tema"})
    encuestas[4]["fecha_encuesta"] = "2026-10-12"
    encuestas.append({**encuestas[4], "fecha_encuesta": FIN, "dificultad_percibida": "5"})

    return temas.drop(columns=["prob_acierto_simulada", "prob_encuesta_simulada"]), pd.DataFrame(resultados), pd.DataFrame(encuestas)


if __name__ == "__main__":
    salida = Path(__file__).resolve().parent / "datos"
    salida.mkdir(parents=True, exist_ok=True)
    tablas = dict(zip(("temas", "resultados", "encuestas"), generar_datos()))
    for nombre, tabla in tablas.items():
        tabla.to_csv(salida / f"{nombre}.csv", index=False)
        print(f"{nombre}: {len(tabla)} filas -> {salida / f'{nombre}.csv'}")
