import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(
    page_title="Executive Sales Dashboard 2026",
    page_icon="💼",
    layout="wide"
)

# 2. Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid #1e293b; }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #131d31, #0c1322);
        border: 1px solid #334155;
        border-top: 1px solid #475569;
        border-left: 1px solid #475569;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 12px 28px -5px rgba(0, 0, 0, 0.85);
    }
    
    div[data-testid="stMetric"] label { color: #94a3b8 !important; font-weight: 700 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #00f2fe !important; font-weight: 800 !important; }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"] {
        background: linear-gradient(145deg, #0f172a, #090e1a) !important;
        border: 1px solid #2d3d54 !important;
        border-top: 1px solid #475569 !important;
        border-left: 1px solid #475569 !important;
        border-radius: 20px !important;
        padding: 22px !important;
    }

    h1 { color: #f8fafc; font-weight: 800; }
    h3 { color: #38bdf8; font-size: 1.25rem !important; font-weight: 700; margin-bottom: 15px; }
    hr { border-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# 3. Cargar datos con parseo estricto de fechas
@st.cache_data
def cargar_datos():
    hojas_excel = pd.read_excel("ventas_ficticias_Q1_2026.xlsx", sheet_name=None)
    
    dfs = []
    for nombre_hoja, df_hoja in hojas_excel.items():
        if df_hoja.empty:
            continue
            
        df_hoja = df_hoja.copy()
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        df_hoja['Mes'] = str(nombre_hoja).strip().capitalize()
        dfs.append(df_hoja)
        
    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    
    renombres = {
        'Monto en dólares': 'Monto',
        'monto en dólares': 'Monto',
        'Categoría': 'Categoria',
        'categoría': 'Categoria',
        'concepto': 'Concepto'
    }
    df.rename(columns=renombres, inplace=True)
    
    if 'Concepto' in df.columns:
        df = df[df['Concepto'].astype(str).str.strip().str.lower() != 'total']
        
    df = df.dropna(subset=['Monto'])
    
    # Conversión robusta de la columna Fecha a datetime
    def parsear_fecha(val):
        if pd.isna(val):
            return None
        val_str = str(val).strip()
        if '31/04/' in val_str or '31-04-' in val_str or '2026-04-31' in val_str:
            val_str = val_str.replace('31/04/', '30/04/').replace('31-04-', '30-04-').replace('2026-04-31', '2026-04-30')
        return val_str

    df['Fecha_Limpia'] = df['Fecha'].apply(parsear_fecha)
    # Parsear a datetime aceptando día/mes/año o año-mes-día
    df['Fecha_DT'] = pd.to_datetime(df['Fecha_Limpia'], errors='coerce', dayfirst=True)
    
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        df = df[df['Categoria'].str.lower() != 'nan']
        
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# --- DEFINICIÓN DE OPCIONES ---
MESES_ORDEN = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]
meses_disponibles = [m for m in MESES_ORDEN if m in df['Mes'].unique()]

fecha_min_data = df['Fecha_DT'].min().date() if not df.empty else pd.to_datetime("2026-01-01").date()
fecha_max_data = df['Fecha_DT'].max().date() if not df.empty else pd.to_datetime("2026-12-31").date()

# --- INICIALIZAR SESSION STATE ---
if 'filtro_fechas' not in st.session_state:
    st.session_state.filtro_fechas = (fecha_min_data, fecha_max_data)

if 'filtro_meses' not in st.session_state:
    st.session_state.filtro_meses = []

# --- CALLBACKS DE EXCLUSIÓN MUTUA ---
def al_cambiar_fecha():
    st.session_state.filtro_meses = []

def al_cambiar_meses():
    st.session_state.filtro_fechas = (fecha_min_data, fecha_max_data)

# 4. BARRA LATERAL
st.sidebar.title("🎛️ Panel de Control")

rango_fechas = st.sidebar.date_input(
    "📅 Rango de Fechas:",
    key='filtro_fechas',
    min_value=fecha_min_data,
    max_value=fecha_max_data,
    on_change=al_cambiar_fecha
)

meses_seleccionados = st.sidebar.multiselect(
    "📆 Seleccionar Mes(es):",
    options=meses_disponibles,
    key='filtro_meses',
    on_change=al_cambiar_meses
)

categorias_disponibles = sorted([c for c in df['Categoria'].unique() if pd.notna(c) and str(c).lower() != 'nan'])
categorias_seleccionadas = st.sidebar.multiselect(
    "🏷️ Seleccionar Categoría(s):",
    options=categorias_disponibles,
    default=categorias_disponibles
)

# 5. LÓGICA DE FILTRADO ESTRICTA
df_filtrado = df.copy()

# A) Si seleccionó meses explícitamente:
if meses_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_seleccionados)]
# B) Si no hay meses seleccionados, aplicar ESTRICTAMENTE el filtro por Fecha
elif isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    f_inicio, f_fin = rango_fechas
    # Comparación estricta de objetos date
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_DT'].dt.date >= f_inicio) & 
        (df_filtrado['Fecha_DT'].dt.date <= f_fin)
    ]

# C) Filtrar Categorías
if categorias_seleccionadas:
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

st.markdown("<br>", unsafe_allow_html=True)

# 7. VISUALIZACIÓN DE TENDENCIA POR MES
color_fondo_grafica = "#1e2d42"
COLORES_MESES = {'Enero': '#00f2fe', 'Febrero': '#ff007f', 'Marzo': '#ffbe0b', 'Abril': '#00f5d4'}

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para el rango o combinación de filtros seleccionada.")
else:
    with st.container(border=True):
        st.subheader("📈 Tendencia de Ventas por Mes")
        
        # Agrupar únicamente los datos que sobrevivieron al filtro
        ventas_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
        
        # Filtrar la lista de meses para que SOLO incluya los meses presentes tras el filtrado
        meses_filtrados = [m for m in MESES_ORDEN if m in ventas_mes['Mes'].unique()]
        
        ventas_mes['Mes'] = pd.Categorical(ventas_mes['Mes'], categories=meses_filtrados, ordered=True)
        ventas_mes = ventas_mes.sort_values('Mes').dropna()

        fig_linea = go.Figure()

        fig_linea.add_trace(go.Scatter(
            x=ventas_mes['Mes'],
            y=ventas_mes['Monto'],
            mode='lines+markers+text',
            text=[f"<b>{m}</b><br>${v:,.0f}" for m, v in zip(ventas_mes['Mes'], ventas_mes['Monto'])],
            textposition="top center",
            textfont=dict(color="#ffffff", size=13),
            line=dict(color="#00f2fe", width=4, shape='spline'),
            marker=dict(
                size=12,
                color=[COLORES_MESES.get(m, '#00f2fe') for m in ventas_mes['Mes']],
                line=dict(color='#ffffff', width=2)
            ),
            hovertemplate="<b>%{x}</b><br>Ventas Totales: $%{-y:,.2f}<extra></extra>"
        ))

        fig_linea.update_layout(
            paper_bgcolor=color_fondo_grafica,
            plot_bgcolor=color_fondo_grafica,
            font=dict(color="#f8fafc", family="sans-serif"),
            xaxis=dict(
                title="",
                type='category', # Asegura que Plotly no rellene los meses ausentes
                showgrid=False,
                linecolor='#475569',
                tickfont=dict(size=14, color="#f8fafc")
            ),
            yaxis=dict(
                title="Ventas ($)",
                showgrid=True,
                gridcolor='#334155',
                linecolor='#475569'
            ),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_linea, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detalle en tabla
    with st.expander("📄 Detalle de Registro de Operaciones"):
        st.dataframe(df_filtrado, use_container_width=True)