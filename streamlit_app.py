import streamlit as st
from streamlit_gsheets import GSheetsConnection
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
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
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FA;
}

/* HEADER */

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
}

.main-subtitle {
    color: rgba(255,255,255,0.85);
    font-size: 15px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #EAEAEA;
}

/* CARDS */

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #1A4B84;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,0.10);
}

/* TEXTO */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* MÉTRICAS */

[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 800;
    color: #111111;
}

[data-testid="stMetricLabel"] {
    font-size: 15px;
    font-weight: 600;
}

/* BOTONES */

.stButton>button {
    border-radius: 10px;
    border: none;
    background-color: #1A4B84;
    color: white;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN
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
# MENU SUPERIOR
# =========================================================

selected = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
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
# CONEXIÓN GOOGLE SHEETS
# =========================================================

url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:

    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        spreadsheet=url,
        ttl="10m"
    )

except Exception as e:

    st.error(f"Error cargando Google Sheets: {e}")
    st.stop()

# =========================================================
# LIMPIEZA
# =========================================================

df['Marca temporal'] = pd.to_datetime(
    df['Marca temporal'],
    errors='coerce'
)

df = df.dropna(subset=['Marca temporal'])

if 'Principal/minutas' in df.columns:

    df = df[
        ~df['Principal/minutas']
        .astype(str)
        .str.contains(
            'NO SOLICITA',
            case=False,
            na=False
        )
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
        sorted(df['Sector'].dropna().unique())
        if 'Sector' in df.columns else []
    )

    platos = st.multiselect(
        "Platos",
        sorted(df['Principal/minutas'].dropna().unique())
        if 'Principal/minutas' in df.columns else []
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

if sectores and 'Sector' in df_f.columns:

    df_f = df_f[df_f['Sector'].isin(sectores)]

if platos and 'Principal/minutas' in df_f.columns:

    df_f = df_f[df_f['Principal/minutas'].isin(platos)]

# =========================================================
# BUSCADOR
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
# KPIs
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    st.metric(
        "Pedidos Totales",
        f"{len(df_f):,}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

with c2:

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    variedad = (
        df_f['Principal/minutas'].nunique()
        if 'Principal/minutas' in df_f.columns
        else 0
    )

    st.metric(
        "Variedad de Platos",
        variedad
    )

    st.markdown('</div>', unsafe_allow_html=True)

with c3:

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    if not df_f.empty and 'Principal/minutas' in df_f.columns:

        top_plato = df_f['Principal/minutas'].mode()[0]

    else:

        top_plato = "-"

    st.metric(
        "Plato Más Solicitado",
        top_plato
    )

    st.markdown('</div>', unsafe_allow_html=True)

with c4:

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    dias = max(1, (rango[1] - rango[0]).days)

    promedio = round(len(df_f) / dias, 1)

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

    if 'Sector' in df_f.columns:

        fig_pie = px.pie(
            df_f,
            names='Sector',
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )

        fig_pie.update_layout(
            height=430,
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

# =========================================================
# EVOLUCIÓN
# =========================================================

with col2:

    st.markdown("### 📈 Evolución Temporal")

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

    fig_line.update_traces(line=dict(width=4))

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

if 'Principal/minutas' in df_f.columns:

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
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(categoryorder='total ascending')
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# =========================================================
# ALERTAS
# =========================================================

st.markdown("### 🚨 Alertas de Auditoría")

if 'Principal/minutas' in df_f.columns:

    conteo = df_f['Principal/minutas'].value_counts()

    if not conteo.empty:

        plato_top = conteo.idxmax()
        cantidad = conteo.max()

        if cantidad > 20:

            st.error(
                f"Consumo elevado detectado: "
                f"{plato_top} ({cantidad} pedidos)"
            )

        else:

            st.success(
                "No se detectaron anomalías críticas"
            )

# =========================================================
# TABLA PROFESIONAL
# =========================================================

st.markdown("### 📋 Trazabilidad Completa")

gb = GridOptionsBuilder.from_dataframe(df_f)

gb.configure_pagination(
    paginationAutoPageSize=True
)

gb.configure_default_column(
    sortable=True,
    filter=True,
    resizable=True
)

gridOptions = gb.build()

AgGrid(
    df_f,
    gridOptions=gridOptions,
    fit_columns_on_grid_load=True,
    height=500,
    theme="streamlit"
)

# =========================================================
# ANALÍTICA AVANZADA
# =========================================================

with st.expander("📊 Análisis Ejecutivo"):

    colA, colB = st.columns(2)

    with colA:

        if 'Sector' in df_f.columns and not df_f.empty:

            sector_top = (
                df_f['Sector']
                .value_counts()
                .idxmax()
            )

            st.info(
                f"Sector con mayor demanda: {sector_top}"
            )

    with colB:

        if 'Marca temporal' in df_f.columns:

            ultimo = (
                df_f['Marca temporal']
                .max()
            )

            st.success(
                f"Última actualización: {ultimo}"
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Sistema Institucional · Auditoría Gastronómica · Casa Rosada"
)
