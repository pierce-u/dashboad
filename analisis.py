import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas 2026",
    page_icon="📊",
    layout="wide"
)

# 2. Cargar datos con limpieza estricta de nulos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("ventas_ficticias_Q1_2026.xlsx")
    
    # Limpiar espacios en blanco al inicio o final de los encabezados
    df.columns = df.columns.astype(str).str.strip()
    
    # Renombrar columnas clave
    renombres = {
        'Monto en dólares': 'Monto',
        'monto en dólares': 'Monto',
        'Categoría': 'Categoria',
        'categoría': 'Categoria'
    }
    df.rename(columns=renombres, inplace=True)
    
    # Eliminar filas donde la fecha o el monto sean nulos/vacíos
    df = df.dropna(subset=['Fecha', 'Monto'])
    
    # Procesar Fecha y Mes
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha']) # Eliminar fechas no válidas
    
    meses_map = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df['Mes'] = df['Fecha'].dt.month.map(meses_map)
    
    # Limpiar Categoría (si está vacía, asignar 'Sin Categoría' o eliminar)
    if 'Categoria' in df.columns:
        df = df.dropna(subset=['Categoria'])
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        df = df[df['Categoria'].str.lower() != 'nan'] # Filtrar texto 'nan'
        
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# 3. BARRA LATERAL (Panel de Control)
st.sidebar.title("🎛️ Panel de Control")

# Filtrar listas para excluir cualquier nulo residual
meses_disponibles = [m for m in df['Mes'].unique() if pd.notna(m) and str(m).lower() != 'nan']
categorias_disponibles = [c for c in df['Categoria'].unique() if pd.notna(c) and str(c).lower() != 'nan']

meses_seleccionados = st.sidebar.multiselect(
    "📅 Seleccionar Mes(es):",
    options=meses_disponibles,
    default=meses_disponibles
)

categorias_seleccionadas = st.sidebar.multiselect(
    "🏷️ Seleccionar Categoría(s):",
    options=categorias_disponibles,
    default=categorias_disponibles
)

# 4. APLICAR FILTROS
df_filtrado = df.copy()

if meses_seleccionados and 'Mes' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_seleccionados)]

if categorias_seleccionadas and 'Categoria' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias_seleccionadas)]

# 5. HEADER Y MÉTRICAS
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
    st.warning("⚠️ No hay datos válidos para los filtros seleccionados.")
else:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Evolución de Ventas por Mes")
        if 'Mes' in df_filtrado.columns:
            ventas_por_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
            orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            ventas_por_mes['Mes'] = pd.Categorical(ventas_por_mes['Mes'], categories=orden_meses, ordered=True)
            ventas_por_mes = ventas_por_mes.sort_values('Mes')
            
            fig_linea = px.line(
                ventas_por_mes,
                x='Mes',
                y='Monto',
                markers=True,
                template="plotly_dark"
            )
            st.plotly_chart(fig_linea, use_container_width=True)

    with col_right:
        st.subheader("🏷️ Participación por Categoría")
        if 'Categoria' in df_filtrado.columns:
            fig_pie = px.pie(
                df_filtrado,
                names='Categoria',
                values='Monto',
                hole=0.4,
                template="plotly_dark"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with st.expander("📄 Ver detalle de los datos filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)