import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. ESTILO: AZUL, BLANCO Y LETRAS NEGRAS (Sin fallos)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    
    /* Forzar negro en todos los textos */
    html, body, [class*="st-"], p, h1, h2, h3, span, label { 
        color: #000000 !important; 
    }
    
    /* Tarjetas Blancas Estilo Ejecutivo */
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-top: 5px solid #1A4B84; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
    }

    /* Estilo de las métricas */
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCESO (SIDEBAR)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=80)
    st.markdown("### Acceso Institucional")
    pw = st.text_input("Contraseña", type="password")
    if pw != "1234":
        st.info("Esperando autenticación...")
        st.stop()

# 4. TÍTULO PRINCIPAL
st.title("⚖️ Auditoría Gastronómica - Casa Rosada")

# 5. CONEXIÓN A DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    # Limpieza prolija de columnas y datos
    df.columns = df.columns.str.strip()
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    
    # Filtro de "NO SOLICITA"
    if 'Principal/minutas' in df.columns:
        df = df[~df['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)]

    # --- PESTAÑAS (TABS) NATIVAS (No requieren librerías extra) ---
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Consumo", "🔍 Trazabilidad", "📅 Filtros Temporales"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="card"><h4>Pedidos Totales</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2:
            top = df['Principal/minutas'].mode()[0] if not df.empty else "N/A"
            st.markdown(f'<div class="card"><h4>Plato Estrella</h4><h4>{top}</h4></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card"><h4>Sectores</h4><h2>{df["Sector"].nunique() if "Sector" in df.columns else 0}</h2></div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if 'Sector' in df.columns:
                fig = px.pie(df, names='Sector', title="Consumo por Sector", color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            serie = df.groupby(df['Marca temporal'].dt.date).size().reset_index(name='Cant')
            fig2 = px.line(serie, x='Marca temporal', y='Cant', title="Evolución de Pedidos")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        busqueda = st.text_input("Buscar por funcionario o sector:")
        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            st.dataframe(df[mask], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.info("Filtros avanzados de fecha en desarrollo.")
        st.date_input("Seleccionar rango para reporte:")
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error técnico: {e}")

except Exception as e:
    st.error(f"Error técnico: {e}")
