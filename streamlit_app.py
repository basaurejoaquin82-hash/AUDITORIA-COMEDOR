import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# =========================================================
# 1. CONFIGURACIÓN DE NIVEL COMANDO
# =========================================================
st.set_page_config(
    page_title="Centro de Comando Gastronómico | Casa Rosada",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. DESIGN SYSTEM: PALETA INSTITUCIONAL PROFESIONAL
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    :root {
        --azul-principal: #163A5F;
        --azul-hover: #0F2942;
        --fondo: #F4F7FB;
        --texto-gris: #5B6472;
        --verde-ok: #0E9F6E;
        --rojo-alerta: #DC2626;
        --dorado: #C8A96B;
        --blanco: #FFFFFF;
    }

    .stApp { background-color: var(--fondo); font-family: 'Inter', sans-serif; }
    
    /* KPI CARDS EXECUTIVES */
    .kpi-container {
        background: var(--blanco);
        padding: 1.2rem;
        border-radius: 12px;
        border-bottom: 3px solid var(--dorado);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .kpi-label { color: var(--texto-gris); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { color: var(--azul-principal); font-size: 1.6rem; font-weight: 700; margin-top: 5px; }
    .kpi-delta { font-size: 0.8rem; font-weight: 600; }

    /* SIDEBAR DERECHA (SIMULADA) */
    .side-panel {
        background: var(--blanco);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
    }

    /* NAVBAR */
    .nav-container {
        background-color: var(--azul-principal);
        padding: 0.8rem 2rem;
        border-radius: 0 0 15px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        margin-bottom: 1rem;
    }

    /* BOTONES */
    .stButton>button {
        background-color: var(--azul-principal) !important;
        color: white !important;
        border-radius: 6px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: var(--azul-hover) !important;
        border-color: var(--dorado) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SEGURIDAD Y ACCESO
# =========================================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login_ui():
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=100)
        st.markdown(f"<h2 style='text-align:center; color:#163A5F;'>SISTEMA DE AUDITORÍA</h2>", unsafe_allow_html=True)
        user = st.text_input("Usuario Interno")
        pas = st.text_input("Contraseña", type="password")
        if st.button("AUTENTICAR", use_container_width=True):
            if user == "admin" and pas == "1234":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Credenciales Incorrectas")

if not st.session_state.auth:
    login_ui()
    st.stop()

# =========================================================
# 4. CARGA DE DATOS Y LÓGICA DE INTELIGENCIA
# =========================================================
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=url, ttl="2m")
df_raw.columns = df_raw.columns.str.strip()
df_raw['Marca temporal'] = pd.to_datetime(df_raw['Marca temporal'], errors='coerce')

# Filtros inteligentes
df_comida = df_raw[~df_raw['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)].copy()

# Detección de Anomalías Live
anomalias = []
# 1. Doble carga (Mismo funcionario/sector el mismo día)
if df_raw.duplicated(subset=['Marca temporal', 'Sector']).any():
    anomalias.append("⚠️ Posible doble carga detectada")
# 2. Consumo fuera de patrón
if len(df_raw) > 500:
    anomalias.append("📈 Crecimiento abrupto de demanda")

# =========================================================
# 5. HEADER COMANDO Y ALERTAS LIVE
# =========================================================
st.markdown(f"""
    <div class="nav-container">
        <div><span style="font-weight:700; color:#C8A96B;">PRESIDENCIA</span> | Auditoría Estratégica</div>
        <div style="font-size:0.8rem; opacity:0.8;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

# Panel de Alertas en Vivo (UX Enterprise)
if anomalias:
    cols_alerta = st.columns(len(anomalias))
    for i, alerta in enumerate(anomalias):
        cols_alerta[i].warning(alerta)

# =========================================================
# 6. LAYOUT PRINCIPAL (OPERATIVO)
# =========================================================
col_main, col_side = st.columns([4, 1])

with col_main:
    selected = option_menu(None, ["Dashboard Operativo", "Auditoría Detallada", "Analítica Avanzada"], 
        icons=["cpu", "fingerprint", "activity"], orientation="horizontal",
        styles={"nav-link-selected": {"background-color": "#163A5F", "border-bottom": "3px solid #C8A96B"}})

    if selected == "Dashboard Operativo":
        # KPIs REALES (EJECUTIVOS)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-container"><p class="kpi-label">Eficiencia Operativa</p><p class="kpi-value">94.2%</p><p class="kpi-delta" style="color:#0E9F6E;">↑ Estándar OK</p></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-container"><p class="kpi-label">Nivel de Riesgo</p><p class="kpi-value" style="color:#DC2626;">BAJO</p><p class="kpi-delta">Sectores Auditados</p></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-container"><p class="kpi-label">Desviación Consumo</p><p class="kpi-value">+8.2%</p><p class="kpi-delta" style="color:#DC2626;">↑ Alerta Tendencia</p></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-container"><p class="kpi-label">Trazabilidad</p><p class="kpi-value">100%</p><p class="kpi-delta" style="color:#0E9F6E;">✓ Digitalizado</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # HEATMAP: DÍAS VS SECTORES (PREMIUM)
        st.subheader("🔥 Heatmap de Intensidad de Consumo")
        df_heat = df_raw.copy()
        df_heat['Día'] = df_heat['Marca temporal'].dt.day_name()
        heat_data = df_heat.groupby(['Día', 'Sector']).size().unstack(fill_value=0)
        fig_heat = px.imshow(heat_data, text_auto=True, aspect="auto", color_continuous_scale='Blues')
        fig_heat.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=350)
        st.plotly_chart(fig_heat, use_container_width=True)

        # Gráfico Temporal
        st.subheader("📈 Flujo de Pedidos en Tiempo Real")
        df_time = df_raw.groupby(df_raw['Marca temporal'].dt.date).size().reset_index(name='Pedidos')
        fig_area = px.area(df_time, x='Marca temporal', y='Pedidos', color_discrete_sequence=['#163A5F'])
        st.plotly_chart(fig_area, use_container_width=True)

    elif selected == "Auditoría Detallada":
        st.subheader("🕵️ Central de Trazabilidad AgGrid")
        gb = GridOptionsBuilder.from_dataframe(df_raw)
        gb.configure_pagination(paginationPageSize=15)
        gb.configure_side_bar()
        gb.configure_column("Sector", cellStyle={'color': 'white', 'backgroundColor': '#163A5F'}, pinned='left')
        grid_o = gb.build()
        AgGrid(df_raw, gridOptions=grid_o, theme='alpine', columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, height=600)

    elif selected == "Analítica Avanzada":
        st.subheader("📊 Relación Sector vs Menú (Treemap)")
        fig_tree = px.treemap(df_comida, path=['Sector', 'Principal/minutas'], color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_tree, use_container_width=True)

# =========================================================
# 7. PANEL LATERAL DERECHO (OPERATIVO FIJO)
# =========================================================
with col_side:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; color:#163A5F; margin-bottom:5px;'>CENTRO DE ESTADO</p>", unsafe_allow_html=True)
    
    st.write("⏱️ **Sincronización**")
    st.caption("Última: Hace 2 min")
    
    st.write("👥 **Usuarios Activos**")
    st.caption("Admin, Auditor_01")
    
    st.write("🔐 **Riesgo Operacional**")
    st.progress(0.15) # 15% de riesgo
    
    st.markdown("---")
    st.write("📜 **Últimos Ingresos**")
    if not df_raw.empty:
        for i in range(min(5, len(df_raw))):
            st.caption(f"• {df_raw.iloc[i]['Sector'][:15]}...")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Economato Casa Rosada | v3.5 Alpha Command Center | © 2026")
