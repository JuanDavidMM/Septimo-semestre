import streamlit as st
import pandas as pd
import google.generativeai as genai


# --------------------------
# CONFIGURAR GEMINI CORRECTO
# --------------------------
def load_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        st.error("⚠️ No se encontró GEMINI_API_KEY en secrets.")
        return None

    genai.configure(api_key=api_key)

    # Modelo correcto + system instruction
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-pro",
        system_instruction="Eres un asistente IA de Dimex. Responde claro, profesional y basado en datos."
    )

    # Sesión de chat (API nueva)
    chat = model.start_chat(history=[])
    return chat


# --------------------------
# CHATBOT STREAMLIT
# --------------------------
def render_chatbot_tab(role="admin"):
    st.header("🤖 Asistente Inteligente Dimex")
    st.caption("Puedes cargar un archivo Excel para que el chatbot lo use como contexto.")

    # ---- SUBIR ARCHIVO con key dinámica por rol
    uploaded_file = st.file_uploader(
        "Subir archivo (Excel .xlsx)",
        type=["xlsx"],
        key=f"chatbot_file_uploader_{role.lower()}"
    )

    df = None
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("📄 Archivo cargado correctamente.")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

    # ---- CLIENTE GEMINI
    if "gemini_chat" not in st.session_state:
        st.session_state.gemini_chat = load_gemini_client()

    chat = st.session_state.gemini_chat
    if chat is None:
        return

    # ---- HISTORIAL
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ---- INPUT DEL USUARIO con key dinámica por rol
    user_input = st.chat_input(
        "Escribe tu mensaje...",
        key=f"chat_input_{role.lower()}"
    )

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Contexto dinámico
        contexto = f"Eres un asistente IA de Dimex con rol {role}."

        if df is not None:
            contexto += (
                "\n\nEl usuario cargó una base de datos. "
                "Aquí están las primeras filas:\n"
                + df.head(234).to_string()
            )

            # Mantengo tu texto completo de prompt consolidado
            contexto += """b) Versión Consolidada del Equipo
Agente de IA Generativa para Gestión de Riesgo, Cobranza y Operaciones en Dimex
b.1) Objetivos del Agente Generativo
El agente de IA está diseñado para apoyar a la empresa en tres niveles:
Gestión de riesgo y originación
Explicar por qué las sucursales están en cada clúster de riesgo (Main_1, 0_1, 0_0).
Traducir el modelo de scoring en reglas concretas: aprobar/rechazar, límites de crédito y tasas.
Identificar deterioro en indicadores como FPD, morosidad y saldo vencido.
Estrategia de cobranza y diversificación de portafolio
Priorizar sucursales y clusters para acciones de cobranza inmediata.
Recomendar estrategias de diversificación y reasignación de recursos para mitigar las pérdidas.
Sugerir acciones específicas para clusters con mayor saldo vencido o mayor deterioro.
Mejora operativa de sucursales
Ayudar a jefes de operaciones y gerentes regionales a interpretar indicadores de eficiencia operativa.
Detectar cuellos de botella (reprocesos, tiempos de atención, validaciones lentas).
Extraer buenas prácticas de los clusters de mejor desempeño y proponer su réplica en los demás.
En resumen, el agente funciona como un analista senior virtual que combina riesgo, cobranza, operaciones y crédito usando el modelo de clustering y el scoring.
b.2) Caso de Uso Consolidado
Caso de uso general
“Queremos que la IA apoye a directores y gerentes de Dimex (Crédito, Cobranza, Operaciones y Regionales) a:
Entender por qué las sucursales están en cada clúster de riesgo u operación.
Priorizar acciones de cobranza y saneamiento de cartera.
Definir políticas de originación, límite y tasa basadas en score y clúster.
Diseñar estrategias de diversificación y mejora operativa usando las mejores prácticas de los clústers sanos.”
El mismo agente debe ser capaz de adaptarse según quién lo usa:
Director de Cobranza → enfoque en cartera vencida y priorización.
Gerente Regional → enfoque en FPD y calidad de originación.
Jefe de Operaciones → enfoque en eficiencia operativa.
Director de Crédito → enfoque en políticas por score y clúster.
b.3) Prompt Inicial Consolidado
“Actúa como analista senior de riesgo, cobranza y operaciones de Dimex.
Tengo sucursales agrupadas en clústers según riesgo y comportamiento:
Cluster 0_1: ‘Cartera en riesgo’
Cluster Main_1: ‘Potencial de crecimiento’
Cluster 0_0: ‘Sucursales consolidadas’
Además, tengo información de FPD, morosidad, saldo insoluto vencido, eficiencia operativa y un score de riesgo por sucursal (300–900).

Explícame, en lenguaje ejecutivo, qué caracteriza a cada clúster.
Indica cuáles son las sucursales prioritarias para cobranza hoy (por saldo vencido)
Propón políticas de originación, límite de crédito y tasa por clúster y rango de score.
Dame al final un resumen ejecutivo con 3 acciones clave para:
Director de Cobranza
Gerente Regional
Jefe de Operaciones.”
Este prompt abre la puerta a todos los ángulos que trabajaron individualmente, pero en un solo flujo.
b.4) Flujo General Funcional (Consolidado)
Paso 1 – Enfoque inicial del usuario
El usuario (cualquier rol directivo) envía el prompt inicial indicando:
Clústers (Main_1, 0_1, 0_0).
Métricas clave (FPD, morosidad, saldo vencido, eficiencia, score).
Paso 2 – Análisis del agente (visión 360°)
La IA responde con:
Análisis de riesgo por clúster
Explica por qué un clúster es más peligroso (ej. 0_1 por alta concentración de saldo vencido).
Destaca el clúster modelo (Main_1) como referencia de buenas prácticas.
Prioridad de cobranza
Lista las sucursales con mayor saldo vencido dentro de los clústers de riesgo (ej. 0_1 y 0_0).
Recomienda acciones específicas (cobranza inmediata, auditoría de cartera, campañas de recuperación).
Calidad de originación y FPD
Explica por qué algunos clústers tienen FPD bajo (buenas prácticas) y otros alto (originación débil).
Sugiere controles adicionales para clústers deteriorados (doble filtro, verificación reforzada).
Eficiencia operativa
Identifica clusters operativamente eficientes vs ineficientes (basado en el caso de Daniela).
Recomienda estandarizar procesos, checklists y monitoreo de KPIs donde haya retrasos.
Políticas de negocio (score + clúster)
Traduce los insights en reglas:
Originación: aprobar / revisar / rechazar.
Límite de crédito: alto / medio / bajo.
Tasa: preferencial / estándar / alta.
Paso 3 – Profundización por rol o clúster
El usuario puede hacer follow-ups como:
“Enfócate en 0_1, dame acciones para diversificar portafolio y reducir pérdidas.”
“Explícame qué hace distinto Main_1 para tener FPD tan bajo.”
“Dame acciones operativas para mejorar la eficiencia del cluster con más retrasos.”
La IA responde con recomendaciones específicas según el rol (cobranza, riesgo, operaciones, crédito).
Paso 4 – Cierre con resumen ejecutivo
El agente entrega un resumen ejecutivo consolidado, por ejemplo:
3 acciones clave para Cobranza (prioridad de sucursales, auditoría de cartera, campañas segmentadas).
3 acciones para Riesgo / Crédito (políticas por score, doble filtro en clústers deteriorados, ajustes de límites).
3 acciones para Operaciones (checklists, KPIs diarios, entrenamiento en sucursales con baja eficiencia).

c) Versión final refinada con IA:
c.1) Aplicación de técnicas de prompt engineering
Para que el agente sea útil y consistente, se aplicaron varias técnicas de prompt engineering:
Definición clara de rol
Se usa siempre la instrucción:
“Actúa como un analista senior de riesgo, cobranza y operaciones de Dimex.”
Esto alinea el tono, el nivel de detalle y el contexto de negocio.
Contexto estructurado del negocio
El prompt incluye desde el inicio:
Nombres y significado de los clústers (0_1, Main_1, 0_0).
Métricas clave (FPD, morosidad, saldo vencido, eficiencia, score).
Esto evita que la IA “invente” contexto y la obliga a usar la segmentación del modelo.
Tareas numeradas paso a paso
El prompt consolidado pide explícitamente:
Explicar clústers.
Priorizar cobranza.
Proponer políticas de negocio.
Entregar resumen ejecutivo por rol.
Esto funciona como una “checklist” para que la IA no se salte ninguna parte.
Uso de ejemplos implícitos (few-shot)
Las versiones individuales (Juan, Daniela, Diego, Roberto) se usaron como “ejemplos guía” para que el agente:
Explique por qué algo está en un clúster.
Proponga acciones concretas (no solo diagnóstico).
Cierre con resúmenes ejecutivos entendibles para negocio.
Orientación a negocio y no solo a datos
Se refuerza en el prompt que las respuestas deben estar en “lenguaje ejecutivo” y que terminen en acciones(no solo análisis descriptivo).
c.2) Reglas de estilo, restricciones y ejemplos
Para asegurar consistencia, se definieron reglas de estilo y restricciones explícitas para el agente:
Estilo y tono
Lenguaje ejecutivo, claro y directo.
Evitar tecnicismos innecesarios o explicarlos cuando aparezcan (ej. FPD, KS, etc.).
Enfocado siempre en “qué hacer” y “por qué”.
Formato de respuesta
Usar listas y apartados numerados para:
Caracterización de clústers.
Acciones recomendadas.
Resúmenes por rol (Cobranza, Riesgo/Crédito, Operaciones).
Cerrar con un Resumen Ejecutivo cuando sea relevante.
Restricciones
No inventar métricas que no existan en la base de datos.
No proponer políticas que contradigan la lógica del modelo (ej. dar límite alto en clúster de alto riesgo con score bajo).
Mantener coherencia con la segmentación: Main_1 = bajo riesgo, 0_1 = en riesgo, 0_0 = consolidadas.
Ejemplos de instrucciones adicionales
“Explica la lógica de negocio detrás de cada regla.”
“Dame acciones inmediatas, no solo diagnóstico.”
“Redáctalo en un lenguaje entendible para un comité directivo.”
Estas reglas se pueden dejar “fijas” en la configuración del agente (como instrucciones del sistema o del creador del GPT).
c.3) Pruebas del flujo y validaciones del modelo
Se simularon varias conversaciones para validar que el agente:
Reconoce y respeta los clústers
Prueba: pedirle explicaciones sobre el clúster 0_1 y verificar que:
Lo identifique como “Cartera en riesgo”.
Enfatice su alta concentración de saldo vencido y FPD.
Resultado: el agente responde coherentemente y sugiere acciones de cobranza y control.
Aplica correctamente lógica de score + clúster
Prueba: solicitar políticas para score alto vs score bajo en Main_1 y 0_1.
Validación:
Main_1 + score alto → aprobación automática / límites altos / tasa preferencial.
0_1 + score bajo → rechazo / sin límite / tasas altas o no viables.
Resultado: el agente respeta la lógica de riesgo y evitar decisiones contradictorias.
Diferencia roles (Cobranza, Riesgo, Operaciones)
Prueba: pedir:
“3 acciones para el Director de Cobranza”
luego “3 acciones para el Jefe de Operaciones”.
Validación:
Cobranza → foco en prioridades de saldo vencido, auditoría, campañas.
Operaciones → foco en procesos, KPIs, checklists, tiempos.
Resultado: el agente cambia el enfoque según el rol solicitado.
Coherencia con el modelo estadístico
Se revisó que:
Clúster más predecible (Main_1) no sea tratado como el más riesgoso.
Clúster de información limitada (0–1 en el modelo de Hit_Buro) se trate con mayor cautela.
Resultado: la narrativa del agente es consistente con las conclusiones del modelo de scoring.
c.4)  Mejoras obtenidas tras el refinamiento con IA
Después de iterar el diseño del prompt y el flujo, se obtuvieron las siguientes mejoras:
Respuestas menos genéricas y más accionables
Al especificar siempre “dame acciones concretas”, la IA dejó de dar diagnósticos vagos y empezó a proponer:
Doble filtro de originación.
Auditorías específicas.
Cambios de límite y tasa por rango de score.
Mayor coherencia entre riesgo, operación y negocio
Antes: cada parte individual enfocada en su ángulo (solo cobranza, solo FPD, solo operación).
Después: el agente consolida todo en una visión 360°, alineando:
Scoring,
Clústers,
Cobranza,
Operaciones,
Políticas de crédito.
Adaptabilidad por rol
El mismo agente ahora puede responder diferente según sea Director de Crédito, Cobranza o Jefe de Operaciones, sin tener que construir 3 agentes separados.
Mejor gobernanza del modelo
El agente no solo interpreta el modelo, también:
Lo traduce a reglas de negocio.
Sugiere controles (doble filtro, revisión de FPD, límites por segmento).
Permite imaginar fácilmente un módulo de monitoreo futuro (vinculado a AUC, KS, drift, etc.).

d) Justificación de diseño
​​d.1) Por qué este caso de uso
El diseño del agente se centra en integrar riesgo, cobranza, operaciones y crédito en un solo sistema porque ese es el mayor dolor actual de Dimex:
La información existe, los modelos son correctos, pero no existen mecanismos simples, rápidos y accionables para interpretarlos y convertirlos en decisiones operativas.
Las áreas trabajan con métricas distintas (FPD, morosidad, eficiencia, score), pero el negocio necesita una visión integrada y dinámica para reaccionar rápido y asignar recursos donde más impacto generan.
Este caso de uso resuelve justamente eso: Un “analista senior virtual” que combina datos, clústers y scoring para entregar acciones, no solo análisis.
d.2) Qué problema resuelve
El agente generativo solucionar cuatro problemas críticos:
a) Desalineación entre áreas
Cada área entiende los clústers desde un ángulo distinto. El agente unifica los criterios y da una interpretación coherente y consistente.
b) Lenta traducción de modelos estadísticos a decisiones reales
Los modelos existen, pero convertir sus resultados en políticas operativas (aprobar, rechazar, límites, tasas) toma tiempo y se hace manualmente.
El agente automatiza esa traducción.
c) Falta de priorización
Los equipos de cobranza y operaciones no siempre saben:
quién es el más riesgoso,
qué sucursal atender primero,
o dónde se está deteriorando la originación.
El agente sí lo sabe porque cruza clúster + score + métricas clave.
d) Inconsistencias en criterios de originación
Con el agente se eliminan criterios subjetivos:
las reglas se vuelven claras, replicables y basadas en datos.
d.3) Riesgos, métricas y outputs esperados
Riesgos mitigados
Colocar crédito en sucursales en deterioro (FPD y morosidad altos).
No cobrar a tiempo en clusters que concentran saldo vencido.
Pérdida de rentabilidad por límites mal asignados.
Decisiones inconsistentes entre regiones o directores.
Métricas clave que monitorea / interpreta
FPD (%)
Morosidad temprana
Saldo insoluto vencido
Segmento del clúster (Main_1, 0_1, 0_0)
Score de riesgo (300–900)
Eficiencia operativa
Outliers y tendencias de deterioro
Outputs esperados
Explicación ejecutiva por clúster.
Priorización diaria de cobranza.
Reglas de originación, límite y tasa según score + clúster.
Acciones operativas específicas por rol.
Resúmenes ejecutivos inmediatos para comité.
Recomendaciones de diversificación y reasignación de recursos.
Alertas si detecta deterioro o anomalías (FPD, morosidad, etc.).
d.4) Cómo se evaluaría su impacto en negocio
Se definen cuatro indicadores de impacto:
1. Reducción de cartera vencida
Medir antes vs después de implementar el agente.
Especialmente en clúster 0_1.
Meta típica: −5% a −15% en 90 días (dependiendo del tamaño del portafolio).
2. Mejora en calidad de originación
FPD promedio por clúster debe disminuir.
Meta esperada: reducción de entre 0.2% y 0.5% en 60 días en clusters de riesgo.
3. Incremento en eficiencia operativa
Medir reprocesos, tiempos de validación, cumplimiento de checklists.
Meta: reducción del 10% al 20% en tiempos operativos.
4. Decisiones más consistentes y rápidas
Tiempo para generar reportes ejecutivos: de horas/días → segundos.
Automatización de minutas, alertas y priorización diaria.
Las decisiones dejan de depender de criterios subjetivos.
d.5)  Justificación final
El diseño del agente no sólo replica lo que un analista humano hace, sino que lo estandariza, lo acelera y lo vuelve accionable.
Une lo mejor de los modelos analíticos, la segmentación por clúster y el scoring en una herramienta que:
Reduce pérdidas
Mejora originación
Optimiza operaciones
Agiliza cobranza
Alínea áreas completas bajo un mismo criterio
Es una solución completa, pragmática y directamente conectada a impacto financiero.

"""
        # Nota: Puedes mantener el resto de tu texto original aquí completo

        prompt = contexto + "\n\nPregunta del usuario: " + user_input

        # ---- LLAMADO CORRECTO A GEMINI
        try:
            response = chat.send_message(prompt)
            bot_msg = response.text
        except Exception as e:
            bot_msg = f"❌ Error al generar respuesta: {e}"

        # Mostrar respuesta
        with st.chat_message("assistant"):
            st.write(bot_msg)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_msg}
        )
