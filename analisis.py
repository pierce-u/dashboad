import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas 2026",
    page_icon="📊",
    layout="wide"
)

# 2. Función para cargar datos con caché
@st.cache_data
def cargar_datos():
    # Cargar el archivo Excel
    df = pd.read_excel("ventas_ficticias_Q1_2026.xlsx")
    
    # Asegurar conversión a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Mapeo manual de meses en español (evita problemas de idioma/locale)
    meses_map = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    # Crear columna de Mes normalizada
    df['Mes'] = df['Fecha'].dt.month.map(meses_map)
    
    # Limpiar posibles espacios en texto
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        
    return df

# Cargar el DataFrame
try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# 3. BARRA LATERAL (Panel de Control)
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("Filtra los datos para actualizar las métricas y gráficos al instante.")

# Obtener opciones únicas disponibles en el Excel
meses_disponibles = list(df['Mes'].unique())
categorias_disponibles = list(df['Categoria'].unique()) if 'Categoria' in df.columns else []

# Filtro de Mes
meses_seleccionados = st.sidebar.multiselect(
    "📅 Seleccionar Mes(es):",
    options=meses_disponibles,
    default=meses_disponibles
)

# Filtro de Categoría
if categorias_disponibles:
    categorias_seleccionadas = st.sidebar.multiselect(
        "🏷️ Seleccionar Categoría(s):",
        options=categorias_disponibles,
        default=categorias_disponibles
    )
else:
    categorias_seleccionadas = []

# 4. APLICAR FILTROS
df_filtrado = df.copy()

if meses_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_seleccionados)]

if categorias_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias_seleccionadas)]

# 5. HEADER Y MÉTRICAS PRINCIPALES
st.title("📈 Dashboard de Ventas 2026")
st.markdown("---")

col1, col2, col3 = st.columns(3)

total_ventas = df_filtrado['Monto'].sum() if not df_filtrado.empty else 0
total_ordenes = len(df_filtrado)
ticket_promedio = df_filtrado['Monto'].mean() if not df_filtrado.empty else 0

col1.metric("💰 Ventas Totales", f"${total_ventas:,.2f}")
col2.metric("📦 Total Transacciones", f"{total_ordenes}")
col3.metric("🎯 Ticket Promedio", f"${ticket_promedio:,.2f}")

st.markdown("---")

# 6. GRÁFICOS
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados. Si seleccionaste **Abril**, verifica que tu archivo Excel contenga fechas pertenecientes a ese mes.")
else:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Evolución de Ventas por Mes")
        ventas_por_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
        
        # Ordenar los meses cronológicamente
        orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        ventas_por_mes['Mes'] = pd.Categorical(ventas_por_mes['Mes'], categories=orden_meses, ordered=True)
        ventas_por_mes = ventas_por_mes.sort_values('Mes')
        
        fig_linea = px.line(
            ventas_por_mes,
            x='Mes',
            y='Monto',
            markers=True,
            labels={'Monto': 'Monto ($ USD)', 'Mes': 'Mes'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_linea, use_container_width=True)

    with col_right:
        st.subheader("🏷️ Participación por Categoría")
        fig_pie = px.pie(
            df_filtrado,
            names='Categoria',
            values='Monto',
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Tabla de datos
    with st.expander("📄 Ver detalle de los datos filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)