import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Intentar importar el menú, si falla, usamos botones normales
try:
    from streamlit_option_menu import option_menu
    has_menu = True
except:
    has_menu = False

st.set_page_config(page_title="Auditoría CR", layout="wide")

# CSS Simple y Letras Negras
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    html, body, [class*="st-"], p, h1, h2, h3, label { color: #000000 !important; }
    .card { background: white; padding: 20px; border-radius: 15px; border-top: 5px solid #1A4B84; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# LOGIN
with st.sidebar:
    st.title("🔐 Acceso")
    pw = st.text_input("Contraseña", type="password")
    if pw != "1234":
        st.info("Ingrese contraseña")
        st.stop()

# MENÚ
if has_menu:
    selected = option_menu(None, ["Dashboard", "Trazabilidad"], icons=["speedometer2", "search"], orientation="horizontal")
else:
    selected = st.radio("Navegación", ["Dashboard", "Trazabilidad"], horizontal=True)

# DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    df.columns = df.columns.str.strip()
    
    if selected == "Dashboard":
        st.title("📊 Resumen de Auditoría")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Total Pedidos", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            if 'Sector' in df.columns:
                fig = px.pie(df, names='Sector', title="Consumo por Sector")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("📋 Detalle de Registros")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
