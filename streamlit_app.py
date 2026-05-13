import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Intentar cargar el menú opcional
try:
    from streamlit_option_menu import option_menu
    menu_disponible = True
except ImportError:
    menu_disponible = False

# CONFIGURACIÓN
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# CSS: Blanco, Azul y Letras Negras
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    html, body, [class*="st-"], p, h1, h2, h3, label { color: #000000 !important; }
    .card { background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #1A4B84; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ACCESO
with st.sidebar:
    st.title("🔐 Acceso")
    pw = st.text_input("Contraseña", type="password")
    if pw != "1234":
        st.info("Esperando autenticación...")
        st.stop()

# MENÚ SUPERIOR
if menu_disponible:
    selected = option_menu(None, ["Dashboard", "Trazabilidad"], icons=["speedometer2", "search"], orientation="horizontal")
else:
    selected = st.radio("Navegación", ["Dashboard", "Trazabilidad"], horizontal=True)

# CARGA DE DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    # Limpieza prolija
    df.columns = df.columns.str.strip()
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    
    if selected == "Dashboard":
        st.title("📊 Resumen de Gestión")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Total Pedidos", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            if 'Sector' in df.columns:
                fig = px.pie(df, names='Sector', color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error técnico en los datos: {e}")
