import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="Sistema de Auditoría Gastronómica",
    page_icon="⚖️",
    layout="wide"
)

# 2. CSS PREMIUM (Letras Negras y Estilo)
st.markdown("""
<style>
.stApp { background-color: #F5F7FA; }
.main-header {
    background: linear-gradient(90deg,#1A4B84,#D8A7B1);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.10);
}
.main-title { color: white; font-size: 34px; font-weight: 700; }
.main-subtitle { color: rgba(255,255,255,0.85); font-size: 15px; }
[data-testid="stMetricValue"] { color: #000000 !important; font-size: 30px; font-weight: 800; }
[data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 600; }
h1, h2, h3, p, span { color: #000000 !important; }
.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #1A4B84;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# 3. LOGIN EN SIDEBAR
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=90)
    st.markdown("## Acceso Institucional")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if usuario != "admin" or password != "1234":
        st.warning("Ingrese credenciales válidas")
        st.stop()
    st.success("Acceso autorizado")

# 4. HEADER
st.markdown("""
<div class="main-header">
    <div class="main-title">⚖️ Sistema de Auditoría Gastronómica</div>
    <div class="main-subtitle">Casa Rosada · Presidencia de la Nación Argentina</div>
</div>
""", unsafe_allow_html=True)

# 5. MENÚ SUPERIOR
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Auditoría", "Trazabilidad", "Análisis"],
    icons=["speedometer2", "shield-check", "search", "graph-up"],
    orientation="horizontal"
)

# 6. CONEXIÓN Y DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="10m")
    
    # Limpieza
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    if 'Principal/minutas' in df.columns:
        df = df[~df['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)]

    # Filtros
    with st.sidebar:
        st.markdown("---")
        st.markdown("## Filtros")
        f_min, f_max = df['Marca temporal'].min().date(), df['Marca temporal'].max().date()
        rango = st.date_input("Rango de fechas", value=(f_min, f_max))
        sectores = st.multiselect("Sector", sorted(df['Sector'].dropna().unique()) if 'Sector' in df.columns else [])

    # Filtrado lógico
    df_f = df.copy()
    if len(rango) == 2:
        df_f = df_f[(df_f['Marca temporal'].dt.date >= rango[0]) & (df_f['Marca temporal'].dt.date <= rango[1])]
    if sectores:
        df_f = df_f[df_f['Sector'].isin(sectores)]

    # DASHBOARD PRINCIPAL
    if selected == "Dashboard":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Pedidos Totales", f"{len(df_f):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            variedad = df_f['Principal/minutas'].nunique() if 'Principal/minutas' in df_f.columns else 0
            st.metric("Variedad Platos", variedad)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            top = df_f['Principal/minutas'].mode()[0] if not df_f.empty else "-"
            st.metric("Top Plato", top)
            st.markdown('</div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            dias = max(1, (rango[1] - rango[0]).days)
            st.metric("Promedio Diario", round(len(df_f)/dias, 1))
            st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Distribución por Sector")
            fig_pie = px.pie(df_f, names='Sector', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.markdown("### 📈 Evolución")
            serie = df_f.groupby(df_f['Marca temporal'].dt.date).size().reset_index(name='Pedidos')
            st.line_chart(serie.set_index('Marca temporal'))

    else:
        st.info(f"Sección {selected} en desarrollo o visualizando datos filtrados:")
        st.dataframe(df_f, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
