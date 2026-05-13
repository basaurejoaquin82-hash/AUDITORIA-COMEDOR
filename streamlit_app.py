import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y MARCA
st.set_page_config(page_title="Auditoría Gastronómica - Casa Rosada", layout="wide")

# CSS PERSONALIZADO (Estética de Tarjetas + Letras Negras)
st.markdown("""
    <style>
    /* Fondo general rosado suave */
    .stApp { background-color: #FDF2F2; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #FCE4E4; border-right: 1px solid #E5E5E5; }
    
    /* Forzar color NEGRO en todos los textos */
    h1, h2, h3, h4, p, span, li, label, div { 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif; 
    }

    /* Tarjetas Blancas (Cards) */
    .main-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        margin-bottom: 20px;
    }

    /* Ajuste para métricas de Streamlit */
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    
    /* Tabs (Pestañas) */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - CONTROL DE ACCESO Y FILTROS
with st.sidebar:
    st.markdown("### **Panel de Control**")
    password = st.sidebar.text_input("Contraseña Institucional", type="password")
    
    if password == "1234":
        st.success("Acceso Autorizado")
    else:
        st.warning("Ingrese clave para operar")
        st.stop()

# 3. CARGA Y LIMPIEZA DE DATOS (Solo si la clave es correcta)
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="600")
    
    # Limpieza de "NO SOLICITA" y Fechas
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    df = df[~df['Principal/minutas'].str.contains('NO SOLICITA', na=False, case=False)]
    
    # Selector de fechas en Sidebar
    st.sidebar.markdown("---")
    min_f, max_f = df['Marca temporal'].min().date(), df['Marca temporal'].max().date()
    rango = st.sidebar.date_input("Rango de Auditoría", value=(min_f, max_f))

    if len(rango) == 2:
        inicio, fin = rango
        df_f = df[(df['Marca temporal'].dt.date >= inicio) & (df['Marca temporal'].dt.date <= fin)]
    else:
        df_f = df

    # 4. CUERPO PRINCIPAL - DISEÑO DE TARJETAS
    st.markdown(f"## Auditoría de Consumo | {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")
    st.caption("Dirección de Administración - Casa Rosada")

    # Fila de KPIs (Tarjetas superiores)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""<div class="main-card"><p style='font-size: 14px;'>PEDIDOS REALES</p><h2 style='margin: 0;'>{len(df_f)}</h2><p style='font-size: 12px;'>Registros procesados</p></div>""", unsafe_allow_html=True)

    with col2:
        top_p = df_f['Principal/minutas'].mode()[0] if not df_f.empty else "N/A"
        st.markdown(f"""<div class="main-card"><p style='font-size: 14px;'>PLATO ESTRELLA</p><h3 style='margin: 0;'>{top_p}</h3><p style='font-size: 12px; color: #5D1224;'>Más solicitado</p></div>""", unsafe_allow_html=True)

    with col3:
        sector = df_f['Sector'].mode()[0] if not df_f.empty else "N/A"
        st.markdown(f"""<div class="main-card"><p style='font-size: 14px;'>MAYOR DEMANDA</p><h2 style='margin: 0;'>{sector}</h2><p style='font-size: 12px;'>Sector activo</p></div>""", unsafe_allow_html=True)

    with col4:
        # Ejemplo de alerta estética
        st.markdown(f"""<div class="main-card" style="border-left: 5px solid #5D1224;"><p style='font-size: 14px;'>ESTADO SISTEMA</p><h2 style='margin: 0;'>ACTIVO</h2><p style='font-size: 12px; color: green;'>Sincronizado</p></div>""", unsafe_allow_html=True)

    # Tabs para organización
    tab_graficos, tab_trazabilidad, tab_datos = st.tabs(["📊 Análisis Visual", "🔍 Trazabilidad", "📋 Base Completa"])

    with tab_graficos:
        c_left, c_right = st.columns([2, 1])
        with c_left:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("### Top Consumo por Plato")
            st.bar_chart(df_f['Principal/minutas'].value_counts().head(10), color="#5D1224")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c_right:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("### Consumo por Sector")
            st.bar_chart(df_f['Sector'].value_counts(), color="#D4AF37")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_trazabilidad:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        nombre = st.text_input("Buscar Funcionario:")
        if nombre:
            res = df_f[df_f['Funcionario'].str.contains(nombre, case=False, na=False)]
            st.dataframe(res[['Marca temporal', 'Funcionario', 'Sector', 'Principal/minutas']], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_datos:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.dataframe(df_f, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Verifica que la planilla de Google Sheets tenga permisos de lectura para 'Cualquier persona con el enlace'.")
