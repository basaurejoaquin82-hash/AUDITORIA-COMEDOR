import streamlit as st
from streamlit_gsheets import GSheetsConnection
try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("Falta la librería 'streamlit-option-menu'. Verificá tu requirements.txt")
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. CSS PARA VISIBILIDAD TOTAL
st.markdown("""
<style>
    .stApp { background-color: #F5F7FA; }
    html, body, [class*="st-"], p, h1, h2, h3, span, label { color: #000000 !important; }
    .main-header {
        background: linear-gradient(90deg,#1A4B84,#D8A7B1);
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 6px solid #1A4B84; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 3. LOGIN SIMPLIFICADO
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=80)
    st.title("Acceso")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if user != "admin" or pw != "1234":
        st.info("Esperando credenciales...")
        st.stop()

# 4. HEADER INSTITUCIONAL
st.markdown("""<div class="main-header"><h1 style="color:white !important; margin:0;">⚖️ Auditoría Gastronómica</h1><p style="color:white !important; margin:0;">Casa Rosada · Presidencia de la Nación</p></div>""", unsafe_allow_html=True)

# 5. MENÚ
selected = option_menu(None, ["Dashboard", "Trazabilidad", "Análisis"], 
    icons=["speedometer2", "search", "graph-up"], orientation="horizontal")

# 6. DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    # Limpieza de columnas y filas
    df.columns = df.columns.str.strip()
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    
    # Filtro dinámico de "NO SOLICITA"
    col_menu = 'Principal/minutas'
    if col_menu in df.columns:
        df = df[~df[col_menu].astype(str).str.contains('NO SOLICITA', case=False, na=False)]

    # Filtros laterales
    with st.sidebar:
        st.markdown("---")
        f_min, f_max = df['Marca temporal'].min().date(), df['Marca temporal'].max().date()
        rango = st.date_input("Fecha", value=(f_min, f_max))
    
    # Lógica de filtrado
    df_f = df.copy()
    if len(rango) == 2:
        df_f = df_f[(df_f['Marca temporal'].dt.date >= rango[0]) & (df_f['Marca temporal'].dt.date <= rango[1])]

    if selected == "Dashboard":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Pedidos", len(df_f))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            val = df_f[col_menu].mode()[0] if col_menu in df_f.columns and not df_f.empty else "N/A"
            st.metric("Top Plato", val)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Sectores", df['Sector'].nunique() if 'Sector' in df.columns else 0)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### Visualización de Datos")
        col_a, col_b = st.columns(2)
        with col_a:
            if 'Sector' in df_f.columns:
                fig = px.pie(df_f, names='Sector', title="Pedidos por Sector")
                st.plotly_chart(fig, use_container_width=True)
        with col_b:
            serie = df_f.groupby(df_f['Marca temporal'].dt.date).size().reset_index(name='Cant')
            fig2 = px.line(serie, x='Marca temporal', y='Cant', title="Evolución Diaria")
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.dataframe(df_f, use_container_width=True)

except Exception as e:
    st.error(f"Error detectado: {e}")
