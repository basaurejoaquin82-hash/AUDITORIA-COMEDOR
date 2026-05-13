import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría CR - Gestión Azul", layout="wide")

# 2. ESTILO CSS: PALETA AZUL, BLANCO Y NEGRO
st.markdown("""
    <style>
    /* Fondo general gris muy claro */
    .stApp { background-color: #F0F2F5; }
    
    /* Forzar color NEGRO en todos los textos y números */
    html, body, [class*="st-"], .stMarkdown, p, h1, h2, h3, h4 {
        color: #000000 !important;
    }

    /* Tarjetas Blancas con borde azul superior */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        border-top: 5px solid #1A4B84; /* Azul Institucional */
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Métricas: Números en Negro */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-weight: 500 !important;
    }

    /* Estilo del Sidebar (Azul Suave) */
    [data-testid="stSidebar"] {
        background-color: #E6EEF8;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCESO EN SIDEBAR
with st.sidebar:
    st.title("🔵 COMANDAS SIN CARGO")
    st.caption("Gestión de Comedor")
    password = st.text_input("Contraseña", type="password")
    if password != "91218":
        st.warning("Ingrese la clave para visualizar el reporte.")
        st.stop()
    st.success("Conexión Establecida")

# 4. CONEXIÓN A DATOS
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
    rango = st.sidebar.date_input("Rango de Fechas", value=(min_f, max_f))

    if len(rango) == 2:
        df_f = df[(df['Marca temporal'].dt.date >= rango[0]) & (df['Marca temporal'].dt.date <= rango[1])]
    else:
        df_f = df

    # 5. INTERFAZ DASHBOARD
    st.title("Sistema de Auditoría Gastronómica")
    st.info(f"Mostrando datos del período: {rango}")
    
    # KPIs en Tarjetas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Pedidos", len(df_f))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        top_p = df_f['Principal/minutas'].mode()[0] if not df_f.empty else "N/A"
        st.metric("Plato Destacado", top_p)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sector = df_f['Sector'].mode()[0] if not df_f.empty else "N/A"
        st.metric("Sector con más pedidos", sector)
        st.markdown('</div>', unsafe_allow_html=True)

    # Gráficos y Tablas
    tab1, tab2 = st.tabs(["📊 Gráficos de Consumo", "🔍 Trazabilidad"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Distribución de Platos")
        # Gráfico en azul institucional
        st.bar_chart(df_f['Principal/minutas'].value_counts().head(10), color="#1A4B84")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        nombre = st.text_input("Filtrar por Funcionario:")
        if nombre:
            res = df_f[df_f['Funcionario'].str.contains(nombre, case=False, na=False)]
            st.dataframe(res, use_container_width=True)
        else:
            st.dataframe(df_f, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error en la carga de datos: {e}")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Verifica que la planilla de Google Sheets tenga permisos de lectura para 'Cualquier persona con el enlace'.")
