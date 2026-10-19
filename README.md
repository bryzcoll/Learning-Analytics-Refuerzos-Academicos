# Sistema de Analítica para la Planificación de Refuerzos Académicos

**Integrantes:** [Nombre y apellido 1] · [Nombre y apellido 2] · [Nombre y apellido 3, si aplica]

**Asignatura/grupo:** [Completar antes de entregar]

Propuesta de Learning Analytics para la Universidad de Cuenca. **Actor:** ayudante de cátedra. **Decisión:** seleccionar temas, ejercicios y minutos de la próxima sesión semanal de refuerzo. **Nivel:** descriptivo, orientado a la enseñanza. La demostración usa exclusivamente datos sintéticos y no contiene información de estudiantes reales.

## Entregables versionados y acceso rápido

| Entregable de la rúbrica | Archivo |
|---|---|
| Matriz de dos casos | [Análisis de FlipMyLearning y OnTask (PDF)](docs/00_analisis_casos.pdf) |
| Canvas de nueve bloques | Sección siguiente de este README |
| Contexto y evidencia del problema | [Evidencia y límites (PDF)](docs/01_evidencia_problema.pdf) |
| Diccionario, fórmulas y ética | [Diccionario de datos (PDF)](docs/02_diccionario_datos.pdf) |
| Wireframes, anotaciones, flujo y arquitectura | [Diseño de la herramienta (PDF)](docs/03_diseno_herramienta.pdf) y [seis vistas exportadas](docs/wireframes/) |
| Prueba de concepto ejecutable | [Notebook](fase4/Fase_4_Prueba_de_Concepto.ipynb), [datos sintéticos](fase4/datos/) y [guía](fase4/README.md) |
| Declaración de IA | [Uso y verificación (PDF)](docs/07_uso_ia.pdf) |

El plan de validación, el pitch y los documentos internos de revisión se conservan **solo en local** por decisión del grupo; no se versionan en este repositorio. Los PDF de la consigna, las fases y los wireframes originales están en [`docs/referencias/`](docs/referencias/). Los diseños editables están en [Figma](https://www.figma.com/design/QHtLMqwRSsuo9FO7KPO2dE); las imágenes del repositorio permiten revisar la entrega sin entrar a Figma.

## Canvas de diseño (nueve bloques; máximo dos páginas)

| Bloque | Respuesta |
|---|---|
| **1. Actor y decisión** | El ayudante de cátedra decide semanalmente qué temas y ejercicios abordar y cómo distribuir aproximadamente 120 minutos. Hoy usa preguntas de los estudiantes, temas vistos y su observación. La herramienta agrega evidencia de ejercicios y encuestas; la decisión final sigue siendo humana. |
| **2. Problema educativo** | Según la experiencia del grupo, algunas asignaturas de Programación I–III, Cálculo y Física tienen ayudantías según el período; en cursos conocidos estiman **20–30 inscritos por asignatura**, no asistentes ni afectados. La propuesta inicial describe que preguntas expresadas pueden omitir dificultades observables en ejercicios. Son observaciones preliminares sin conteo institucional; falta medir cuántos estudiantes presentan esa brecha y [se propone cómo hacerlo](docs/01_evidencia_problema.pdf). |
| **3. Pregunta analítica** | «¿Qué contenidos de un curso presentan mayores dificultades en los últimos siete días según los resultados de ejercicios y las necesidades expresadas por los estudiantes?». Nivel **descriptivo**; tipo **enseñanza**; unidad **curso–tema–período**. |
| **4. Datos e indicadores** | Fuentes previstas: ejercicios o evaluaciones formativas de eVirtual/registro docente y encuesta voluntaria 1–5 por tema. Variables clave: curso, tema, estudiante seudonimizado, pregunta, primer intento válido, puntaje obtenido/máximo y última encuesta válida. Dificultad observada Dₒ = promedio de `100 × (1 − obtenido/máximo)`; percibida Dₚ = porcentaje de respuestas 4–5; prioridad Pᵣ = `0,5Dₒ + 0,5Dₚ`, solo si ambos existen. Mostrar tamaños de muestra y exclusiones. [Diccionario](docs/02_diccionario_datos.pdf). |
| **5. Intervención** | El ayudante revisa el ranking y la cobertura, abre el detalle, justifica temas, asigna estrategia y minutos, guarda el plan y registra asistencia, tiempo real y observaciones. Si no se actúa, la sesión continúa con la planificación habitual; no se marca al estudiante ni se genera una alerta individual. |
| **6. Ética y privacidad** | Puntajes, intentos, respuestas y asistencia son datos personales vinculables al estudiante. Seudonimizar antes del cálculo, separar la llave de reidentificación y mostrar al ayudante solo agregados por tema; el docente accedería según permiso institucional. Encuesta voluntaria e informada; registros reales requieren autorización y base de tratamiento. No mostrar grupos pequeños. Quienes trabajan o acceden en otros horarios pueden quedar subrepresentados: ausencia no equivale a cero ni a desinterés. |
| **7. Prueba de concepto** | [Notebook autónomo para Colab](fase4/Fase_4_Prueba_de_Concepto.ipynb) con semilla fija: 64 estudiantes ficticios, un curso, cinco temas, limpieza, Dₒ/Dₚ/Pᵣ, calidad y tablero Plotly. [Aplicación Streamlit](app.py) para demostrar la secuencia de tres pantallas. No se infiere impacto educativo a partir de datos simulados. |
| **8. Validación** | Hipótesis: planificar con tablero mejora la ganancia pre–post frente a la planificación habitual. Comparar métodos por curso–semana. Técnica: auditar cálculo y contrastar prioridad con evaluación posterior y juicio docente (ρ de Spearman ≥ 0,30 y acuerdo ≥ 70 % como metas). Pedagógica: diferencia de ganancia ≥ 5 puntos porcentuales. Usabilidad: ≥ 80 % de tareas críticas sin ayuda y mediana SUS ≥ 70. Estos son criterios provisionales, no resultados. |
| **9. Preguntas para estadística** | ¿Cuántas sesiones y estudiantes se necesitan? ¿Qué prueba compara la ganancia entre grupos? ¿Cómo manejar dependencia entre temas y estudiantes? ¿Qué incertidumbre tienen Dₒ y Dₚ con muestras pequeñas? ¿Cómo estimar sesgo de no respuesta? ¿Qué cambio mínimo es relevante? |

## Uso de IA generativa

Los entregables originales de las Fases 0, 1 y 2, incluida la matriz de casos, fueron aportados por el grupo; **no se generaron con IA**. OpenAI Codex se usó después para revisar la entrega y desarrollar la prueba de concepto. Mediante la integración MCP de Figma se reconstruyeron wireframes y diagramas a partir de los PDF originales. El alcance y las verificaciones se detallan en la [declaración de IA](docs/07_uso_ia.pdf).

## Ejecución local y despliegue posterior

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Para verificar el notebook por separado, ver [instrucciones de Fase 4](fase4/README.md). El despliegue queda a cargo del grupo; esta carpeta no contiene secretos ni depende de un servicio externo. La aplicación guarda plan y seguimiento **solo en la sesión del navegador**: es una demostración, no un sistema institucional persistente.

Si se publica como aplicación Streamlit, usar **esta carpeta como raíz**, `app.py` como archivo principal y `requirements.txt` como dependencias. No se necesitan variables de entorno. La instalación y la app se probaron localmente con Python 3.13; tras el despliegue conviene abrir las tres pestañas y comprobar que se guardan plan y seguimiento de demostración.
