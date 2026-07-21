import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Executive Sales Dashboard 2026",
    page_icon="💼",
    layout="wide"
)

# 2. Inyección de CSS para diseño Ejecutivo / Corporativo
st.markdown("""
    <style>
    /* Fondo principal de la app */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    
    /* Estilo para la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Estilos para las tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* Personalización de títulos */
    h1 {
        color: #f0f6fc;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h3 {
        color: #c9d1d9;
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    
    /* Línea divisora */
    hr {
        border-color: #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Cargar datos corrigiendo fechas e integrando pestañas
@st.cache_data
def cargar_datos():
    hojas_excel = pd.read_excel("ventas_ficticias_Q1_2026.xlsx", sheet_name=None)
    df = pd.concat(hojas_excel.values(), ignore_index=True)
    df.columns = df.columns.astype(str).str.strip()
    
    renombres = {
        'Monto en dólares': 'Monto',
        'monto en dólares': 'Monto',
        'Categoría': 'Categoria',
        'categoría': 'Categoria'
    }
    df.rename(columns=renombres, inplace=True)
    
    if 'Concepto' in df.columns:
        df = df[df['Concepto'].astype(str).str.strip().str.lower() != 'total']
        
    df = df.dropna(subset=['Monto'])
    
    def corregir_fecha(val):
        if pd.isna(val):
            return val
        val_str = str(val).strip()
        if '31/04/' in val_str or '31-04-' in val_str or '2026-04-31' in val_str:
            val_str = val_str.replace('31/04/', '30/04/').replace('31-04-', '30-04-').replace('2026-04-31', '2026-04-30')
        return val_str

    df['Fecha_Texto'] = df['Fecha'].apply(corregir_fecha)
    df['Fecha'] = pd.to_datetime(df['Fecha_Texto'], dayfirst=True, errors='coerce')
    
    meses_map = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df['Mes'] = df['Fecha'].dt.month.map(meses_map)
    
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        df = df[df['Categoria'].str.lower() != 'nan']
        
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# 4. BARRA LATERAL (Panel de Control)
st.sidebar.title("🎛️ Panel de Control")

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

# 5. APLICAR FILTROS
df_filtrado = df.copy()

if meses_seleccionados and 'Mes' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_seleccionados)]

if categorias_seleccionadas and 'Categoria' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias_seleccionadas)]

# 6. HEADER Y MÉTRICAS
st.title("💼 Dashboard de Ventas Ejecutivas 2026")
st.markdown("---")

col1, col2, col3 = st.columns(3)

total_ventas = df_filtrado['Monto'].sum() if not df_filtrado.empty else 0
total_ordenes = len(df_filtrado)
ticket_promedio = df_filtrado['Monto'].mean() if not df_filtrado.empty else 0

col1.metric("💰 Ventas Totales", f"${total_ventas:,.2f}")
col2.metric("📦 Transacciones", f"{total_ordenes}")
col3.metric("🎯 Ticket Promedio", f"${ticket_promedio:,.2f}")

st.markdown("---")

# 7. GRÁFICOS CON PALETA EJECUTIVA
# Paletas de color elegantes
paleta_barras = ['#1f77b4', '#38bdf8', '#818cf8', '#a78bfa']
paleta_pie = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa']

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
else:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Rendimiento de Ventas por Mes")
        if 'Mes' in df_filtrado.columns:
            ventas_por_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
            ventas_por_mes['Mes'] = pd.Categorical(ventas_por_mes['Mes'], categories=orden_meses, ordered=True)
            ventas_por_mes = ventas_por_mes.sort_values('Mes')
            
            fig_barras = px.bar(
                ventas_por_mes,
                x='Mes',
                y='Monto',
                color='Mes',
                text_auto='.3s',
                labels={'Monto': 'Ventas ($)', 'Mes': 'Mes'},
                color_discrete_sequence=paleta_barras,
                template="plotly_dark"
            )
            fig_barras.update_traces(
                textposition='outside',
                marker_line_color='#30363d',
                marker_line_width=1.5
            )
            fig_barras.update_layout(
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#c9d1d9"),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig_barras, use_container_width=True)

    with col_right:
        st.subheader("🏷️ Distribución por Categoría")
        if 'Categoria' in df_filtrado.columns:
            fig_pie = px.pie(
                df_filtrado,
                names='Categoria',
                values='Monto',
                hole=0.5,
                color_discrete_sequence=paleta_pie,
                template="plotly_dark"
            )
            fig_pie.update_traces(
                textinfo='percent+label',
                marker=dict(line=dict(color='#161b22', width=2))
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#c9d1d9"),
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Tabla de detalle con diseño
    with st.expander("📄 Detalle de Registro de Operaciones"):
        st.dataframe(df_filtrado, use_container_width=True)