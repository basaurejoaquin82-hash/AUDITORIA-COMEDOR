import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Ejecutivo)
st.set_page_config(
    page_title="Reporte de Auditoría - Casa Rosada",
    page_icon="🇦🇷",
    layout="wide"
)

# Diseño estético con CSS (Colores: Azul noche, Dorado y Blanco)
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px; 
        border-top: 5px solid #1a2a6c; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .date-header {
        background-color: #1a2a6c;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        font-size: 20px;
        font-weight: bold;
    }
    h1, h2 { color: #1a2a6c; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
st.sidebar.markdown("### 🔒 Acceso Seguro")
password = st.sidebar.text_input("Contraseña Institucional", type="password")

if password == "1234":
    url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, ttl="600")
        
        # Limpieza inicial
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
        df = df.dropna(subset=['Marca temporal'])
        
        # Filtrado de "NO SOLICITA" (Limpieza total)
        df = df[~df['Principal/minutas'].str.contains('NO SOLICITA', na=False, case=False)]
        df = df[~df['Tostados / Medialunas / Chipa / Cuadraditos Dulces'].str.contains('NO SOLICITA', na=False, case=False)]

        # --- FILTRO DE FECHAS EN SIDEBAR ---
        st.sidebar.markdown("---")
        min_f, max_f = df['Marca temporal'].min().date(), df['Marca temporal'].max().date()
        
        st.sidebar.subheader("📅 Rango de Análisis")
        rango = st.sidebar.date_input("Seleccione período:", value=(min_f, max_f), min_value=min_f, max_value=max_f)

        if len(rango) == 2:
            inicio, fin = rango
            df_f = df[(df['Marca temporal'].dt.date >= inicio) & (df['Marca temporal'].dt.date <= fin)]
            
            # --- HEADER DE FECHAS PROLIJO ---
            st.markdown(f"""<div class="date-header">📊 REPORTE DE CONSUMO: {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')}</div>""", unsafe_allow_html=True)
            
            # --- DASHBOARD ---
            tab1, tab2, tab3 = st.tabs(["📈 Resumen Ejecutivo", "👥 Detalle por Funcionario", "📋 Auditoría de Datos"])

            with tab1:
                # Métricas Principales en Tarjetas
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Pedidos Totales", f"{len(df_f)}", help="Total de raciones despachadas")
                m2.metric("Plato Principal", f"{df_f['Principal/minutas'].mode()[0] if not df_f.empty else 'N/A'}")
                m3.metric("Infusiones/Dulces", f"{df_f['Tostados / Medialunas / Chipa / Cuadraditos Dulces'].mode()[0] if not df_f.empty else 'N/A'}")
                m4.metric("Sector Mayoritario", f"{df_f['Sector'].mode()[0] if not df_f.empty else 'N/A'}")

                st.markdown("### 📊 Tendencias de Consumo")
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.write("**Top 10 Platos Principales**")
                    st.bar_chart(df_f['Principal/minutas'].value_counts().head(10), color="#1a2a6c")
                
                with col_right:
                    st.write("**Consumo por Sector**")
                    st.bar_chart(df_f['Sector'].value_counts(), color="#D4AF37")

                st.markdown("---")
                st.write("**Despacho de Mozos y Personal de Cocina**")
                st.dataframe(df_f[['Mozo/a', 'Personal de despacho cocina']].value_counts().reset_index(name='Cantidad'), use_container_width=True)

            with tab2:
                st.subheader("🔍 Trazabilidad Individual")
                nombre = st.text_input("Ingrese nombre o apellido del funcionario:")
                if nombre:
                    res = df_f[df_f['Funcionario'].str.contains(nombre, case=False, na=False)]
                    st.dataframe(res[['Marca temporal', 'Funcionario', 'Sector', 'Principal/minutas', 'Guarnición']], use_container_width=True)

            with tab3:
                st.subheader("📋 Base de Datos de Auditoría")
                st.write(f"Se visualizan {len(df_f)} registros procesados.")
                st.dataframe(df_f, use_container_width=True)

    except Exception as e:
        st.error(f"Error en la estructura de datos: {e}")

else:
    st.info("🇦🇷 Sistema de Auditoría Interna - Inicie sesión para continuar.")
