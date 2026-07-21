import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas 2026",
    page_icon="📊",
    layout="wide"
)

# 2. Cargar datos leyendo TODAS las pestañas del Excel
@st.cache_data
def cargar_datos():
    # Cargar todas las hojas del libro de Excel en un diccionario
    hojas_excel = pd.read_excel("ventas_ficticias_Q1_2026.xlsx", sheet_name=None)
    
    # Unir todas las pestañas (Enero, Febrero, Marzo, Abril) en un solo DataFrame
    df = pd.concat(hojas_excel.values(), ignore_index=True)
    
    # Limpiar espacios en los encabezados
    df.columns = df.columns.astype(str).str.strip()
    
    # Renombrar columnas clave
    renombres = {
        'Monto en dólares': 'Monto',
        'monto en dólares': 'Monto',
        'Categoría': 'Categoria',
        'categoría': 'Categoria'
    }
    df.rename(columns=renombres, inplace=True)
    
    # Excluir filas resumen/totales y registros vacíos
    if 'Concepto' in df.columns:
        df = df[df['Concepto'].astype(str).str.strip().str.lower() != 'total']
        
    df = df.dropna(subset=['Fecha', 'Monto'])
    
    # Convertir Fecha asegurando formato correcto
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha']) # Eliminar fechas inválidas
    
    # Mapear mes en español
    meses_map = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df['Mes'] = df['Fecha'].dt.month.map(meses_map)
    
    # Limpiar Categoría
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        df = df[df['Categoria'].str.lower() != 'nan']
        
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# 3. BARRA LATERAL (Panel de Control)
st.sidebar.title("🎛️ Panel de Control")

# Ordenar los meses en secuencia natural
orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_en_datos = [m for m in df['Mes'].unique() if pd.notna(m)]
meses_disponibles = [m for m in orden_meses if m in meses_en_datos]

categorias_disponibles = sorted([c for c in df['Categoria'].unique() if pd.notna(c) and str(c).lower() != 'nan'])

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
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
else:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Evolución de Ventas por Mes")
        if 'Mes' in df_filtrado.columns:
            ventas_por_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
            ventas_por_mes['Mes'] = pd.Categorical(ventas_por_mes['Mes'], categories=orden_meses, ordered=True)
            ventas_por_mes = ventas_por_mes.sort_values('Mes')
            
            # Gráfico de barras con un color por mes (color='Mes')
            fig_barras = px.bar(
                ventas_por_mes,
                x='Mes',
                y='Monto',
                color='Mes',
                text_auto='.2s', # Muestra el monto formateado sobre cada barra
                labels={'Monto': 'Monto ($ USD)', 'Mes': 'Mes'},
                template="plotly_dark"
            )
            fig_barras.update_traces(textposition='outside')
            fig_barras.update_layout(showlegend=False) # Ocultar leyenda para mayor limpieza
            
            st.plotly_chart(fig_barras, use_container_width=True)

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