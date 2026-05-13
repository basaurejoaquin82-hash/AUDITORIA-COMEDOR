import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Sistema de Auditoría Gastronómica",
    page_icon="⚖️",
    layout="wide"
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
    background-color: white;
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
}

/* MÉTRICAS */

[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 800;
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
}

/* FUENTE */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
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
# MENÚ SUPERIOR
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
    orientation="horizontal"
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

    st.error(f"Error conectando Google Sheets: {e}")
    st.stop()

# =========================================================
# LIMPIEZA DE DATOS
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
# FILTROS SIDEBAR
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

# =========================================================
# FILTRADO
# =========================================================

df_f = df.copy()

if len(rango) == 2:

    df_f = df_f[
        (df_f['Marca temporal'].dt.date >= rango[0]) &
        (df_f['Marca temporal'].dt.date <= rango[1])
    ]

if sectores and 'Sector' in df_f.columns:

    df_f = df_f[df_f['Sector'].isin(sectores)]

# =========================================================
# BUSCADOR GLOBAL
# =========================================================

st.markdown("### 🔎 Buscador Inteligente")

busqueda = st.text_input(
    "",
    placeholder="Buscar funcionario, sector o plato..."
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

    top_plato = (
        df_f['Principal/minutas'].mode()[0]
        if not df_f.empty and 'Principal/minutas' in df_f.columns
        else "-"
    )

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

# PIE CHART

with col1:

    st.markdown("### 📊 Distribución por Sector")

    if 'Sector' in df_f.columns:

        fig_pie = px.pie(
            df_f,
            names='Sector',
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )

        fig_pie.update_layout(height=420)

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

# LINE CHART

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

    fig_line.update_traces(
        line=dict(width=4)
    )

    fig_line.update_layout(height=420)

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

# =========================================================
# RANKING
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

        top = conteo.idxmax()
        cantidad = conteo.max()

        if cantidad > 20:

            st.error(
                f"Consumo elevado detectado: "
                f"{top} ({cantidad} pedidos)"
            )

        else:

            st.success(
                "No se detectaron anomalías críticas"
            )

# =========================================================
# TABLA
# =========================================================

st.markdown("### 📋 Trazabilidad Completa")

st.dataframe(
    df_f,
    use_container_width=True,
    height=500
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Sistema Institucional · Auditoría Gastronómica · Casa Rosada"
)
