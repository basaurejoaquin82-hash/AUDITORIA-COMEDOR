import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría Gastronómica CR", layout="wide")

# 2. ESTILO CSS: AZUL, BLANCO Y TEXTO NEGRO
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    html, body, [class*="st-"], p, h1, h2, h3, h4 { color: #000000 !important; }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        border-top: 5px solid #1A4B84;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCESO
with st.sidebar:
    st.title("🔵 Gestión CR")
    # CAMBIA TU CONTRASEÑA AQUÍ:
    password = st.text_input("Contraseña", type="password")
    if password != "1234":
        st.warning("Ingrese clave para continuar.")
        st.stop()
    st.success("Acceso Autorizado")

# 4. CONEXIÓN Y DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="600")

    # Limpieza de datos
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    df = df[~df['Principal/minutas'].str.contains('NO SOLICITA', na=False, case=False)]

    # Filtro de fecha
    min_f, max_f = df['Marca temporal'].min().date(), df['Marca temporal'].max().date()
    rango = st.sidebar.date_input("Rango de Auditoría", value=(min_f, max_f))

    if len(rango) == 2:
        df_f = df[(df['Marca temporal'].dt.date >= rango[0]) & (df['Marca temporal'].dt.date <= rango[1])]
    else:
        df_f = df

    # 5. INTERFAZ DASHBOARD
    st.title("⚖️ Panel de Auditoría y Control Gastronómico")
    
    # --- FILA 1: MÉTRICAS EXTENDIDAS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Pedidos", len(df_f))
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        variedad = df_f['Principal/minutas'].nunique()
        st.metric("Variedad de Platos", variedad)
        st.markdown('</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        top_p = df_f['Principal/minutas'].mode()[0] if not df_f.empty else "N/A"
        st.metric("Plato más solicitado", top_p)
        st.markdown('</div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        promedio = round(len(df_f) / (max(1, (rango[1]-rango[0]).days)), 1) if len(rango)==2 else 0
        st.metric("Promedio Diario", f"{promedio}")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- FILA 2: GRÁFICOS AVANZADOS ---
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Distribución por Sector")
        # Gráfico de Torta usando Plotly para que sea interactivo
        fig_pie = px.pie(df_f, names='Sector', color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 Evolución de Pedidos")
        # Gráfico de línea temporal
        df_time = df_f.groupby(df_f['Marca temporal'].dt.date).size().reset_index(name='Pedidos')
        st.line_chart(df_time.set_index('Marca temporal'), color="#1A4B84")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- FILA 3: RANKING ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏆 Top 10 Platos más consumidos")
    st.bar_chart(df_f['Principal/minutas'].value_counts().head(10), color="#1A4B84")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- TABLA DE DATOS ---
    with st.expander("🔍 Ver Detalle de Trazabilidad"):
        st.dataframe(df_f, use_container_width=True)

except Exception as e:
    st.error(f"Error en los datos: {e}")
