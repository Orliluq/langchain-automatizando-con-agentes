import streamlit as st
import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from herramientas import crear_herramientas

# Inicia la aplicación
st.set_page_config(
    page_title="Asistente de Análisis de Datos con IA",
    layout="centered"
)

st.title("🤖📊 Asistente Inteligente de Análisis de Datos")

# Descripción de la herramienta
st.info("""
🚀 Este asistente utiliza un agente de IA creado con LangChain para ayudarte a explorar, analizar y visualizar datos de forma interactiva.

📂 Carga un archivo CSV y podrás:

📄 **Generar reportes automáticos**

• 📋 Reporte de información general
• 📈 Reporte de estadísticas descriptivas
• 🧹 Identificación de valores nulos
• 🔍 Detección de registros duplicados
• 💡 Recomendaciones de análisis

🔎 **Realizar preguntas sobre tus datos**

• ¿Cuál es el promedio de ventas?
• ¿Cuántos clientes existen por región?
• ¿Cuál es el producto más vendido?

📊 **Crear gráficos automáticamente**

Describe lo que quieres visualizar y la IA generará el análisis correspondiente.

🎯 Ideal para analistas, científicos de datos, estudiantes y equipos de negocio.
""")

# Upload de CSV
st.markdown("## 📂 Carga tu archivo CSV")
archivo_cargado = st.file_uploader(
    "📁 Selecciona un archivo CSV",
    type="csv",
    label_visibility="collapsed"
)

if archivo_cargado:
    df = pd.read_csv(archivo_cargado)
    st.success("✅ Archivo cargado exitosamente")
    st.markdown("### 👀 Vista previa de los datos")
    st.dataframe(df.head())

    st.info(
        f"📊 Dataset con **{df.shape[0]} filas** y **{df.shape[1]} columnas**"
    )

    # LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama3-70b-8192",
        temperature=0
    )

    # Herramientas
    tools = crear_herramientas(df)

    # Prompt react
    df_head = df.head().to_markdown()

    prompt_react_es = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={"df_head": df_head},
        template="""
            Eres un asistente que responde en castellano.

            Tienes acceso a un dataframe pandas llamado `df`.
            Aquí están las primeras filas del DataFrame, obtenidas usando `df.head().to_markdown()`:
            
            {df_head}

            Responde a las siguientes preguntas de la mejor manera posible.
            Para este fin, tienes acceso a las siguientes herramientas:

            {tools}

            Usa el siguiente formato:

            Question: La pregunta de entrada que debes responder
            Thought: Debes siempre pensar en lo que debes hacer
            Action: La acción que será ejecutada, debe ser una de las [{tool_names}]
            Action Input: La entrada para la acción
            Observation: El resultado de la acción
            ... (este Thought/Action/Action Input/Observation puede repetirse N veces)
            Thought: Ahora sé la respuesta final
            Final Answer: La respuesta final para la pregunta de entrada inicial.

            Comienza!

            Question: {input}
            Thought: {agent_scratchpad}
        """
        )

    
    # Agente
    agente = create_react_agent(llm=llm, tools=tools, prompt=prompt_react_es)
    orquestador = AgentExecutor(agent=agente,
                                tools=tools,
                                verbose=True,
                                handle_parsing_errors=True)

    # ACCIONES RÁPIDAS
    st.markdown("---")
    st.markdown("## ⚡ Acciones rápidas con IA")

    # Reporte de Informaciones Generales
    if st.button(
        "📄📋 Generar Reporte General",
        key="boton_reporte_general"
    ):
        with st.spinner("🤖 Analizando dataset..."):
            respuesta = orquestador.invoke({"input": "Quero um relatório com informações sobre os dados"})
            st.session_state['reporte_general'] = respuesta["output"]

    # Exhibe el reporte con botón de descarga
    if 'reporte_general' in st.session_state:
        with st.expander("📄 Resultado: Reporte General"):
            st.markdown(st.session_state['reporte_general'])

            st.download_button(
                label="📥 Descargar Reporte General",
                data=st.session_state['reporte_general'],
                file_name="reporte_general.md",
                mime="text/markdown"
            )

    # Reporte de estadísticas descriptivas
    if st.button(
        "📈📊 Generar Reporte Estadístico",
        key="boton_reporte_estadisticas"
    ):
        with st.spinner("📊 Calculando estadísticas..."):
            respuesta = orquestador.invoke({"input": "Quiero un Reporte de estadísticas descriptivas"})
            st.session_state['reporte_estadisticas'] = respuesta["output"]

    # Exhibe el reporte almacenado con opción de descarga
    if 'reporte_estadisticas' in st.session_state:
        with st.expander("📈 Resultado: Estadísticas Descriptivas"):
            st.markdown(st.session_state['reporte_estadisticas'])

        st.download_button(
            label="📥 Descargar Reporte Estadístico",
            data=st.session_state['reporte_estadisticas'],
            file_name="reporte_estadisticas_descritivas.md",
            mime="text/markdown"
        )
   
    # PERGUNTA SOBRE LOS DATOS
    st.markdown("---")
    st.markdown("## 🔎💬 Pregunta a tus datos")
    pregunta_sobre_datos = st.text_input(
    "❓ Escribe tu pregunta",
    key="pregunta_sobre_datos"
    )
    if st.button(
    "🚀 Obtener respuesta",
    key="responder_pregunta_datos"
    ):
        with st.spinner("🧠 Pensando sobre los datos..."):
            respuesta = orquestador.invoke({"input": pregunta_sobre_datos})
            st.markdown((respuesta["output"]))


    # GENERACIÓN DE GRÁFICOS
    st.markdown("---")
    st.markdown("## 📊🎨 Crear visualizaciones")

    pregunta_grafico = st.text_input(
    "📈 ¿Qué deseas visualizar?",
    key="pregunta_grafico"
    )
    if st.button(
    "🎨 Generar gráfico",
    key="generar_grafico"
    ):
        with st.spinner("📊 Construyendo visualización..."):
            orquestador.invoke({"input": pregunta_grafico})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Filas", df.shape[0])

    with col2:
        st.metric("📊 Columnas", df.shape[1])

    with col3:
        st.metric("🧩 Valores nulos", int(df.isnull().sum().sum()))