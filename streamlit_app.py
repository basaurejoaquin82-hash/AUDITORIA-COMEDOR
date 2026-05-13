import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN ESTÉTICA
st.set_page_config(
    page_title="Auditoría Economato - Casa Rosada",
    page_icon="⚖️",
    layout="wide"
)

# Estilo profesional e institucional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    h1 { color: #1a2a6c; font-family: 'Helvetica', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN DE ACCESO
st.sidebar.title("🔐 Acceso Institucional")
user_role = st.sidebar.selectbox("Rol de Usuario", ["Auditor", "Depósito", "Cocina"])
password = st.sidebar.text_input("Contraseña", type="password")

if password == "1234":
    # 3. CONEXIÓN A TU NUEVA PLANILLA
    url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Cargamos los datos ignorando filas vacías
        df = conn.read(spreadsheet=url, ttl="1m")
        df = df.dropna(how='all')

        st.title("⚖️ Panel de Control y Auditoría de Suministros")
        st.caption(f"Visualizando datos del sector: {user_role}")

        # Pestañas de gestión
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Consumo General", "👥 Trazabilidad Funcionarios", "📦 Auditoría Materia Prima", "📜 Registro de Logs"])

        with tab1:
            st.subheader("Análisis de Pedidos (Platos y Minutas)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Pedidos Registrados", len(df))
            with col2:
                # Calculamos el plato más pedido de la columna D (Principal/minutas)
                plato_top = df['Principal/minutas'].mode()[0] if not df['Principal/minutas'].empty else "Sin datos"
                st.metric("Plato más solicitado", plato_top)
            with col3:
                # Calculamos el sector con más demanda de la columna B (Sector)
                sector_top = df['Sector'].mode()[0] if not df['Sector'].empty else "Sin datos"
                st.metric("Sector con mayor consumo", sector_top)

            st.markdown("---")
            
            # Gráfico de consumo por tipo de plato
            st.write("**Distribución de Platos Principales y Minutas:**")
            conteo_platos = df['Principal/minutas'].value_counts()
            st.bar_chart(conteo_platos, color="#1a2a6c")

            # Gráfico de desayunos/meriendas (Columna E)
            st.write("**Distribución de Tostados, Medialunas y Dulces:**")
            conteo_desayunos = df['Tostados / Medialunas / Chipa / Cuadraditos Dulces'].value_counts()
            st.bar_chart(conteo_desayunos, color="#c7a17a")

        with tab2:
            st.subheader("Buscador de Consumo por Funcionario")
            # Usamos la columna C (Funcionario)
            query = st.text_input("Ingrese apellido o nombre del funcionario:")
            if query:
                busqueda = df[df['Funcionario'].str.contains(query, case=False, na=False)]
                st.dataframe(busqueda[['Marca temporal', 'Sector', 'Funcionario', 'Principal/minutas', 'Postres']], use_container_width=True)

        with tab3:
            st.subheader("Control de Materia Prima vs. Despacho")
            st.info("Este panel calcula la materia prima teórica basada en los pedidos realizados.")
            
            # Ejemplo de lógica de auditoría para la columna F (Cantidad tostados/medialunas)
            total_unidades = df['Cantidad solo tostados y medialunas'].sum()
            st.metric("Total Unidades de Panadería Despachadas", f"{int(total_unidades)} u.")
            
            st.write("---")
            st.write("**Detalle de despacho por Mozo/a (Columna J):**")
            mozos = df['Mozo/a'].value_counts()
            st.table(mozos)

        with tab4:
            st.subheader("Logs de Auditoría Interna")
            # Registro de quién entró a mirar los datos
            log_entry = pd.DataFrame([{
                "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Usuario": user_role,
                "Acción": "Consulta de Dashboard General"
            }])
            st.table(log_entry)

    except Exception as e:
        st.error(f"Error al procesar las columnas: {e}")
        st.info("Asegúrate de que los nombres de las columnas en el Excel coincidan exactamente con el código.")

else:
    if password:
        st.sidebar.error("Contraseña incorrecta")
    st.warning("Ingrese la contraseña institucional para visualizar los reportes de auditoría.")
