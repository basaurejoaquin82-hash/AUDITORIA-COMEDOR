import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE MARCA Y ESTILO
st.set_page_config(page_title="Gestión Gastronómica - Casa Rosada", layout="wide")

# CSS personalizado para replicar la imagen
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #FDF2F2; }
    
    /* Sidebar personalizado */
    [data-testid="stSidebar"] { background-color: #FCE4E4; border-right: 1px solid #E5E5E5; }
    
    /* Tarjetas (Cards) */
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        margin-bottom: 20px;
    }
    
    /* Títulos y textos */
    h1, h2, h3 { color: #5D1224; font-family: 'Inter', sans-serif; }
    .status-badge {
        background-color: #FEF3C7; color: #92400E;
        padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;
    }
    .critical-badge {
        color: #B91C1C; font-weight: bold; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR (Navegación Institucional)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/1200px-Flag_of_Argentina.svg.png", width=50)
    st.markdown("### **Casa Rosada**")
    st.caption("Comedor Institucional")
    st.markdown("---")
    st.button("📊 Dashboard", use_container_width=True)
    st.button("📅 Planificación", use_container_width=True)
    st.button("📖 Recetas", use_container_width=True)
    st.button("🍽️ Salad Bar", use_container_width=True)
    st.button("⚙️ Configuración", use_container_width=True)

# 3. CUERPO PRINCIPAL
st.markdown("## Sistema de Planificación Gastronómica")
st.caption("Dashboard Principal - Gestión y control del flujo gastronómico nacional")

# Fila 1: Tarjetas de Resumen (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="main-card">
        <p style='color: #6B7280; font-size: 14px;'>MENÚ DEL DÍA <span class="status-badge">ACTIVO</span></p>
        <h3 style='margin: 0;'>Pollo al verdeo con puré rústico</h3>
        <p style='font-size: 12px; color: #92400E;'>⭐ Recomendación del Chef</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="main-card">
        <p style='color: #6B7280; font-size: 14px;'>TICKETS HOY <span style='color: #059669;'>↗ +12%</span></p>
        <h2 style='margin: 0;'>1,248</h2>
        <p style='font-size: 12px; color: #6B7280;'>Meta diaria: 1,500</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="main-card">
        <p style='color: #6B7280; font-size: 14px;'>PRODUCCIÓN EST.</p>
        <h2 style='margin: 0;'>850 kg</h2>
        <div style='background-color: #E5E7EB; height: 8px; border-radius: 4px;'>
            <div style='background-color: #5D1224; width: 65%; height: 100%; border-radius: 4px;'></div>
        </div>
        <p style='font-size: 12px; color: #6B7280; margin-top: 5px;'>En progreso</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="main-card">
        <p style='color: #6B7280; font-size: 14px;'>ALERTAS DE STOCK <span class="critical-badge">CRÍTICO</span></p>
        <h2 style='margin: 0; color: #B91C1C;'>04</h2>
        <p style='font-size: 12px; color: #6B7280;'>Insumos por debajo del mínimo</p>
    </div>
    """, unsafe_allow_html=True)

# Fila 2: Gráficos y Popularidad
c_left, c_right = st.columns([2, 1])

with c_left:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### Consumo Semanal de Insumos")
    # Simulamos el gráfico de la imagen
    chart_data = pd.DataFrame({
        'Día': ['LUN', 'MAR', 'MIE', 'JUE', 'VIE'],
        'Consumo': [40, 50, 30, 70, 55]
    })
    st.bar_chart(chart_data.set_index('Día'), color="#D6B6B6")
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### Popularidad Menús")
    
    # Simulación de barras de progreso
    def progress_bar(label, value, color):
        st.write(f"{label} **{value}%**")
        st.progress(value / 100)

    progress_bar("Tradicional", 45, "#5D1224")
    progress_bar("Vegetariano", 30, "#D4AF37")
    progress_bar("Saludable (Fit)", 15, "#5D1224")
    progress_bar("Celiacos / Otros", 10, "#5D1224")
    st.markdown('</div>', unsafe_allow_html=True)

# Botón flotante de "Añadir" (Estético)
st.markdown("""
    <div style='position: fixed; bottom: 20px; right: 20px; background-color: #5D1224; color: white; width: 50px; height: 50px; border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); cursor: pointer;'>
    +
    </div>
    """, unsafe_allow_html=True)
