import streamlit as st
from streamlit_gsheets import GSheetsConnection
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Sistema de Auditoría Gastronómica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS PREMIUM INSTITUCIONAL
# =========================================================

st.markdown("""
<style>

/* ===== FONDO GENERAL ===== */

.stApp {
    background-color: #F5F7FA;
}

/* ===== HEADER ===== */

.main-header {
    background: linear-gradient(90deg,#1A4B84,#D8A7B1);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.10);
}

.main-title {
    color: white;
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 5px;
}

.main-subtitle {
    color: rgba(255,255,255,0.85);
    font-size: 15px;
}

/* ===== SIDEBAR ===== */

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #EAEAEA;
}

/* ===== KPI CARDS ===== */

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #1A4B84;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.12);
}

/* ===== TEXTOS ===== */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ===== EXPANDERS ===== */

.streamlit-expanderHeader {
    background-color: white;
    border-radius: 10px;
    padding: 10px;
}

/* ===== TABLAS ===== */

.ag-theme-streamlit {
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* ===== BADGES ===== */

.badge-ok {
    background-color: #E8F5E9;
    color: #2E7D32;
    padding: 6px 10px;
    border-radius: 8px;
    font-weight: 600;
}

/* ===== KPI VALUE ===== */

[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 800;
    color: #1A1A1A;
}

[data-testid="stMetricLabel"] {
    font-size: 15px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN SIMPLE PROFESIONAL
# =========================================================

with st.sidebar:

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg",
        width=90
    )

    st.markdown("## Acceso Institucional")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if usuario != "admin" or password != "1234":
        st.warning("Ingrese credenciales válidas")
        st.stop()

    st.success("Acceso autorizado")

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="main-header">
    <div class="main-title">
        ⚖️ Sistema de Auditoría Gastronómica
    </div>
    <div class="main-subtitle">
        Casa Rosada · Presidencia de la Nación Argentina
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MENÚ SUPERIOR
# =========================================================

selected = option_menu(
    menu_title=None,
    options=[
        "Dashboard Ejecutivo",
        "Auditoría",
        "Trazabilidad",
        "Análisis"
    ],
    icons=[
        "speedometer2",
        "shield-check",
        "search",
        "graph-up"
    ],
    orientation="horizontal",
)

# =========================================================
# CARGA DE DATOS
# =========================================================

url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, ttl="10m")

# =========================================================
# LIMPIEZA
# =========================================================

df['Marca temporal'] = pd.to_datetime(
    df['Marca temporal'],
    errors='coerce'
)

df = df.dropna(subset=['Marca temporal'])

df = df[
    ~df['Principal/minutas']
    .astype(str)
    .str.contains('NO SOLICITA', case=False, na=False)
]

# =========================================================
# SIDEBAR FILTROS
# =========================================================

with st.sidebar:

    st.markdown("---")

    st.markdown("## Filtros")

    fecha_min = df['Marca temporal'].min().date()
    fecha_max = df['Marca temporal'].max().date()

    rango = st.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max)
    )

    sectores = st.multiselect(
        "Sector",
        options=sorted(df['Sector'].dropna().unique())
    )

    platos = st.multiselect(
        "Platos",
        options=sorted(df['Principal/minutas'].dropna().unique())
    )

# =========================================================
# FILTROS
# =========================================================

df_f = df.copy()

if len(rango) == 2:
    df_f = df_f[
        (df_f['Marca temporal'].dt.date >= rango[0]) &
        (df_f['Marca temporal'].dt.date <= rango[1])
    ]

if sectores:
    df_f = df_f[df_f['Sector'].isin(sectores)]

if platos:
    df_f = df_f[df_f['Principal/minutas'].isin(platos)]

# =========================================================
# BUSCADOR GLOBAL
# =========================================================

st.markdown("### 🔎 Buscador Inteligente")

busqueda = st.text_input(
    "",
    placeholder="Buscar funcionario, sector, cargo o plato..."
)

if busqueda:

    mask = df_f.astype(str).apply(
        lambda row: row.str.contains(
            busqueda,
            case=False,
            na=False
        ).any(),
        axis=1
    )

    df_f = df_f[mask]

# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Pedidos Totales",
            f"{len(df_f):,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    variedad = df_f['Principal/minutas'].nunique()

    st.metric(
        "Variedad de Platos",
        variedad
    )

    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    top_plato = (
        df_f['Principal/minutas']
        .mode()[0]
        if not df_f.empty else "-"
    )

    st.metric(
        "Plato Más Solicitado",
        top_plato
    )

    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    promedio = round(
        len(df_f) / max(1, (rango[1] - rango[0]).days),
        1
    )

    st.metric(
        "Promedio Diario",
        promedio
    )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# GRÁFICOS
# =========================================================

col1, col2 = st.columns(2)

# =========================================================
# PIE CHART
# =========================================================

with col1:

    st.markdown("### 📊 Distribución por Sector")

    fig_pie = px.pie(
        df_f,
        names='Sector',
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    fig_pie.update_layout(
        height=430,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )

    evento = st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# =========================================================
# EVOLUCIÓN TEMPORAL
# =========================================================

with col2:

    st.markdown("### 📈 Evolución de Consumo")

    serie = (
        df_f.groupby(df_f['Marca temporal'].dt.date)
        .size()
        .reset_index(name='Pedidos')
    )

    fig_line = px.line(
        serie,
        x='Marca temporal',
        y='Pedidos',
        markers=True
    )

    fig_line.update_traces(
        line=dict(width=4)
    )

    fig_line.update_layout(
        height=430,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

# =========================================================
# TOP PLATOS
# =========================================================

st.markdown("### 🏆 Ranking de Platos")

ranking = (
    df_f['Principal/minutas']
    .value_counts()
    .head(10)
    .reset_index()
)

ranking.columns = ['Plato', 'Cantidad']

fig_bar = px.bar(
    ranking,
    x='Cantidad',
    y='Plato',
    orientation='h',
    text='Cantidad',
    color='Cantidad',
    color_continuous_scale='Blues'
)

fig_bar.update_layout(
    height=500,
    yaxis=dict(categoryorder='total ascending'),
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# =========================================================
# HEATMAP DE CONSUMO
# =========================================================

st.markdown("### 🔥 Heatmap de Consumo")

df_heat = (
    df_f.groupby([
        df_f['Marca temporal'].dt.day_name(),
        'Sector'
    ])
    .size()
    .reset_index(name='Cantidad')
)

fig_heat = px.density_heatmap(
    df_heat,
    x='Marca temporal',
    y='Sector',
    z='Cantidad',
    color_continuous_scale='Blues'
)

fig_heat.update_layout(
    height=500
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)

# =========================================================
# ALERTAS DE AUDITORÍA
# =========================================================

st.markdown("### 🚨 Alertas de Auditoría")

conteo = (
    df_f['Principal/minutas']
    .value_counts()
)

if not conteo.empty:

    plato_excesivo = conteo.idxmax()
    cantidad = conteo.max()

    if cantidad > 20:

        st.error(
            f"Consumo elevado detectado: "
            f"{plato_excesivo} ({cantidad} pedidos)"
        )

# =========================================================
# TABLA PROFESIONAL
# =========================================================

st.markdown("### 📋 Trazabilidad Completa")

gb = GridOptionsBuilder.from_dataframe(df_f)

gb.configure_pagination(paginationAutoPageSize=True)

gb.configure_default_column(
    groupable=True,
    value=True,
    enableRowGroup=True,
    editable=False,
    sortable=True,
    filter=True,
    resizable=True
)

gb.configure_selection("single")

gridOptions = gb.build()

AgGrid(
    df_f,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=450
)

# =========================================================
# ANÁLISIS AVANZADO
# =========================================================

with st.expander("📊 Análisis Ejecutivo"):

    colA, colB = st.columns(2)

    with colA:

        top_sector = (
            df_f['Sector']
            .value_counts()
            .idxmax()
        )

        st.info(
            f"Sector con mayor demanda: {top_sector}"
        )

    with colB:

        funcionario_top = (
            df_f.iloc[0]['Nombre y Apellido']
            if 'Nombre y Apellido' in df_f.columns
            else "No disponible"
        )

        st.success(
            f"Último registro auditado: {funcionario_top}"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Sistema Institucional · Auditoría Gastronómica · Casa Rosada"
)
