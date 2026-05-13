import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. CSS PARA ESTÉTICA AZUL/BLANCO Y LETRAS NEGRAS
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    /* Forzar negro en todo el texto */
    html, body, [class*="st-"], p, h1, h2, h3, span, label { color: #000000 !important; }
    
    /* Tarjetas Blancas con borde azul */
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-top: 5px solid #1A4B84; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
    }
    /* Estilo para los botones del menú nativo */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: 1px solid #1A4B84;
        color: #1A4B84;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=80)
    st.markdown("### Acceso Institucional")
    pw = st.text_input("Contraseña", type="password")
    if pw != "1234":
        st.info("Esperando autenticación...")
        st.stop()
    st.success("Acceso Autorizado")

# 4. NAVEGACIÓN (Usando el componente nativo de Streamlit)
st.markdown("### 🧭 Navegación")
selected = st.radio("", ["📊 Dashboard de Consumo", "🔍 Trazabilidad y Búsqueda"], horizontal=True)

# 5. CARGA DE DATOS
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    # Limpieza prolija
    df.columns = df.columns.str.strip()
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    
    # Filtro de "NO SOLICITA"
    if 'Principal/minutas' in df.columns:
        df = df[~df['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)]

    if selected == "📊 Dashboard de Consumo":
        st.title("Panel de Gestión Gastronómica")
        
        # Fila de Métricas
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="card"><h4>Pedidos Totales</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2:
            top = df['Principal/minutas'].mode()[0] if not df.empty else "N/A"
            st.markdown(f'<div class="card"><h4>Plato Estrella</h4><h4>{top}</h4></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card"><h4>Sectores Activos</h4><h2>{df["Sector"].nunique() if "Sector" in df.columns else 0}</h2></div>', unsafe_allow_html=True)

        # Gráficos
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

    else:
        st.title("🔍 Trazabilidad Completa")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        busqueda = st.text_input("Buscar por funcionario, mozo o sector:")
        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            st.dataframe(df[mask], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
