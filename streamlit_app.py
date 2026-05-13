import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN ESTÉTICA
st.set_page_config(
    page_title="Auditoría Economato - Casa Rosada",
    page_icon="⚖️",
    layout="wide"
)

# Estilo Institucional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    h1 { color: #1a2a6c; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
st.sidebar.title("🔐 Acceso Institucional")
user_role = st.sidebar.selectbox("Rol", ["Auditor", "Depósito", "Cocina"])
password = st.sidebar.text_input("Contraseña", type="password")

if password == "1234":
    url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, ttl="1m")
        
        # --- LIMPIEZA DE DATOS ---
        # 1. Convertimos la 'Marca temporal' a formato fecha real para poder filtrar
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
        df = df.dropna(subset=['Marca temporal'])
        
        # 2. BORRAMOS TODO LO QUE DIGA "NO SOLICITA"
        # Esto limpia tanto en platos principales como en desayunos
        df = df[df['Principal/minutas'] != 'NO SOLICITA']
        df = df[df['Tostados / Medialunas / Chipa / Cuadraditos Dulces'] != 'NO SOLICITA']

        # --- FILTRO DE TRAZABILIDAD TEMPORAL ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Rango de Auditoría")
        min_fecha = df['Marca temporal'].min().date()
        max_fecha = df['Marca temporal'].max().date()
        
        rango_fechas = st.sidebar.date_input(
            "Seleccioná el período:",
            value=(min_fecha, max_fecha),
            min_value=min_fecha,
            max_value=max_fecha
        )

        # Aplicar el filtro de fechas si se seleccionan ambas
        if len(rango_fechas) == 2:
            inicio, fin = rango_fechas
            mask = (df['Marca temporal'].dt.date >= inicio) & (df['Marca temporal'].dt.date <= fin)
            df_filtrado = df.loc[mask]
        else:
            df_filtrado = df

        st.title("⚖️ Panel de Control y Auditoría")
        st.caption(f"Mostrando información desde {rango_fechas[0]} hasta {rango_fechas[1] if len(rango_fechas)>1 else '...'}")

        tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Consumo", "🔍 Trazabilidad de Funcionarios", "📋 Datos Crudos"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pedidos Reales", len(df_filtrado))
            with col2:
                top_p = df_filtrado['Principal/minutas'].mode()[0] if not df_filtrado.empty else "N/A"
                st.metric("Plato Estrella", top_p)
            with col3:
                sector = df_filtrado['Sector'].mode()[0] if not df_filtrado.empty else "N/A"
                st.metric("Sector con más pedidos", sector)

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Consumo de Platos Principales**")
                st.bar_chart(df_filtrado['Principal/minutas'].value_counts(), color="#1a2a6c")
            with c2:
                st.write("**Consumo de Panadería/Dulces**")
                st.bar_chart(df_filtrado['Tostados / Medialunas / Chipa / Cuadraditos Dulces'].value_counts(), color="#c7a17a")

        with tab2:
            st.subheader("Buscador por Funcionario")
            nombre = st.text_input("Escribí el nombre del funcionario:")
            if nombre:
                res = df_filtrado[df_filtrado['Funcionario'].str.contains(nombre, case=False, na=False)]
                st.dataframe(res, use_container_width=True)

        with tab3:
            st.subheader("Listado Detallado")
            st.write("Esta tabla muestra los registros filtrados por el rango de fechas seleccionado.")
            st.dataframe(df_filtrado, use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un error al procesar los datos: {e}")

else:
    st.warning("Por favor, ingrese la contraseña para acceder al sistema.")
