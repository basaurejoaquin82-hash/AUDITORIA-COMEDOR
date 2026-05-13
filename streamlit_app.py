import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ESTÉTICA DE LA PÁGINA
st.set_page_config(
    page_title="Sistema de Auditoría - Economato Casa Rosada",
    page_icon="⚖️",
    layout="wide"
)

# Estilo CSS personalizado para un look institucional
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1a2a6c; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE REGISTRO / LOGIN (Simulado)
st.sidebar.title("🔐 Acceso Institucional")
user_role = st.sidebar.selectbox("Rol de Usuario", ["Invitado", "Auditor", "Cocinero", "Depósito"])
password = st.sidebar.text_input("Contraseña", type="password")

if password == "1234": # Aquí pondrías tu clave real
    st.sidebar.success(f"Sesión iniciada como: {user_role}")
    
    # 3. CARGA DE DATOS
    url = "https://docs.google.com/spreadsheets/d/13yrtrXfH_k-lJbTDMFXVAPb1KUbZqRWUKDgHXH79wvw/edit#gid=803817362"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url)

        st.title("⚖️ Panel de Auditoría y Control de Suministros")
        
        # Pestañas con diseño organizado
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Trazabilidad", "📦 Auditoría Stock", "📜 Logs"])

        with tab1:
            st.subheader("Resumen de Consumo Actual")
            col1, col2, col3 = st.columns(3)
            
            total_pedidos = len(df)
            plato_top = df['¿Que desea pedir?'].mode()[0]
            
            col1.metric("Total Platos Servidos", total_pedidos)
            col2.metric("Plato más solicitado", plato_top)
            col3.metric("Estado del Sistema", "Activo")
            
            st.markdown("---")
            conteo = df['¿Que desea pedir?'].value_counts()
            st.bar_chart(conteo, color="#1a2a6c")

        with tab2:
            st.subheader("Búsqueda de Funcionarios y Eventos")
            nombre = st.text_input("Buscar por Nombre y Apellido:")
            if nombre:
                busqueda = df[df['Nombre y Apellido'].str.contains(nombre, case=False, na=False)]
                st.dataframe(busqueda, use_container_width=True)

        with tab3:
            if user_role in ["Auditor", "Depósito"]:
                st.subheader("Contraste de Materia Prima")
                # Aquí es donde harías la lógica de: Platos * Gramos = Salida de Depósito
                st.warning("⚠️ Discrepancia detectada: Carne Vacuna (-12%)")
                st.write("Cruce entre Pedidos Realizados vs. Vales de Salida del Depósito.")
            else:
                st.error("No tienes permisos para ver esta sección.")

        with tab4:
            st.subheader("Registro de Actividad (Audit Logs)")
            st.caption("Registro automático de modificaciones y consultas")
            # Simulamos un log de auditoría
            log_data = {
                "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                "Usuario": [user_role],
                "Acción": ["Consulta de reporte de consumo"]
            }
            st.table(pd.DataFrame(log_data))

    except Exception as e:
        st.error(f"Error de conexión: {e}")

else:
    st.warning("Por favor, ingrese la contraseña en la barra lateral para ver los datos.")
    st.info("Nota: Para la prueba usa '1234'")
