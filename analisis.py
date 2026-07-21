import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Executive Sales Dashboard 2026",
    page_icon="💼",
    layout="wide"
)

# 2. Inyección de CSS para Fondo Contrastado y Tarjetas Flotantes
st.markdown("""
    <style>
    /* Fondo general del Dashboard */
    .stApp {
        background-color: #0b0e14;
        color: #e0e6ed;
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #121721;
        border-right: 1px solid #1f2937;
    }
    
    /* Tarjetas de Métricas (KPIs) */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #182030, #111622);
        border: 1px solid #2d3748;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 30px -5px rgba(0, 0, 0, 0.7), 
                    0 0 15px rgba(56, 189, 248, 0.2);
        border-color: #38bdf8;
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Contenedores de Gráficos (Efecto Tarjeta Contrastada) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"] {
        background-color: #151c28 !important;
        border: 1px solid #2a3547 !important;
        border-radius: 16px !important;
        padding: 15px !important;
        box-shadow: 0 12px 28px -5px rgba(0, 0, 0, 0.65), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
    }

    h1 { color: #f8fafc; font-weight: 800; letter-spacing: -0.5px; }
    h3 { color: #38bdf8; font-size: 1.15rem !important; font-weight: 700; margin-bottom: 15px; }
    hr { border-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# 3. Cargar datos detectando dinámicamente cualquier pestaña
@st.cache_data
def cargar_datos():
    hojas_excel = pd.read_excel("ventas_ficticias_Q1_2026.xlsx", sheet_name=None)
    
    dfs = []
    for nombre_hoja, df_hoja in hojas_excel.items():
        if df_hoja.empty:
            continue
            
        df_hoja = df_hoja.copy()
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        
        # Asignar el mes basándose en el nombre de la pestaña
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
    
    def corregir_fecha(val):
        if pd.isna(val):
            return val
        val_str = str(val).strip()
        if '31/04/' in val_str or '31-04-' in val_str or '2026-04-31' in val_str:
            val_str = val_str.replace('31/04/', '30/04/').replace('31-04-', '30-04-').replace('2026-04-31', '2026-04-30')
        return val_str

    df['Fecha_Texto'] = df['Fecha'].apply(corregir_fecha)
    df['Fecha'] = pd.to_datetime(df['Fecha_Texto'], dayfirst=True, errors='coerce')
    
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].astype(str).str.strip()
        df = df[df['Categoria'].str.lower() != 'nan']
        
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo Excel: {e}")
    st.stop()

# 4. BARRA LATERAL
st.sidebar.title("🎛️ Panel de Control")

MESES_CALENDARIO = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

meses_detectados = df['Mes'].unique() if not df.empty else []
meses_disponibles = [m for m in MESES_CALENDARIO if m in meses_detectados]

for m in meses_detectados:
    if m not in meses_disponibles:
        meses_disponibles.append(m)

categorias_disponibles = sorted([c for c in df['Categoria'].unique() if pd.notna(c) and str(c).lower() != 'nan']) if not df.empty else []

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

st.markdown("<br>", unsafe_allow_html=True)

# 7. GRÁFICOS
color_fondo_grafica = "#182232"

paleta_barras = ['#38bdf8', '#818cf8', '#a78bfa', '#f472b6', '#34d399', '#fbbf24']
paleta_pie = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa']

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
else:
    # --- FILA 1: Ventas por Mes y Proporción por Categoría ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        with st.container(border=True):
            st.subheader("📊 Rendimiento de Ventas por Mes")
            if 'Mes' in df_filtrado.columns:
                ventas_por_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
                ventas_por_mes['Mes'] = pd.Categorical(ventas_por_mes['Mes'], categories=meses_disponibles, ordered=True)
                ventas_por_mes = ventas_por_mes.sort_values('Mes').dropna(subset=['Mes'])
                
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
                    marker_line_color='#ffffff',
                    marker_line_width=1.5,
                    opacity=0.95
                )
                fig_barras.update_layout(
                    showlegend=False,
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#e2e8f0", family="sans-serif"),
                    xaxis=dict(showgrid=False, linecolor='#334155'),
                    yaxis=dict(showgrid=True, gridcolor='#263346', linecolor='#334155'),
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_barras, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.subheader("🏷️ Distribución por Categoría")
            if 'Categoria' in df_filtrado.columns:
                fig_pie = px.pie(
                    df_filtrado,
                    names='Categoria',
                    values='Monto',
                    hole=0.55,
                    color_discrete_sequence=paleta_pie,
                    template="plotly_dark"
                )
                fig_pie.update_traces(
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#151c28', width=3))
                )
                fig_pie.update_layout(
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#e2e8f0", family="sans-serif"),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FILA 2: Ranking de Categorías & Top 10 Conceptos ---
    col_cat, col_conc = st.columns(2)

    with col_cat:
        with st.container(border=True):
            st.subheader("📂 Top Categorías más Vendidas")
            if 'Categoria' in df_filtrado.columns:
                top_categorias = (
                    df_filtrado.groupby('Categoria')['Monto']
                    .sum()
                    .nlargest(10)
                    .reset_index()
                )
                
                fig_cat = px.bar(
                    top_categorias,
                    x='Categoria',
                    y='Monto',
                    color='Monto',
                    text_auto='.3s',
                    labels={'Monto': 'Ventas ($)', 'Categoria': 'Categoría'},
                    color_continuous_scale='Tealgrn',
                    template="plotly_dark"
                )
                fig_cat.update_traces(
                    textposition='outside',
                    marker_line_color='#ffffff',
                    marker_line_width=1.2,
                    opacity=0.95
                )
                fig_cat.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#e2e8f0", family="sans-serif"),
                    xaxis=dict(showgrid=False, linecolor='#334155'),
                    yaxis=dict(showgrid=True, gridcolor='#263346', linecolor='#334155'),
                    margin=dict(l=20, r=20, t=30, b=30)
                )
                st.plotly_chart(fig_cat, use_container_width=True)

    with col_conc:
        with st.container(border=True):
            st.subheader("🏆 Top 10 Conceptos más Vendidos")
            if 'Concepto' in df_filtrado.columns:
                top10_conceptos = (
                    df_filtrado.groupby('Concepto')['Monto']
                    .sum()
                    .nlargest(10)
                    .reset_index()
                )
                
                fig_top10 = px.bar(
                    top10_conceptos,
                    x='Concepto',
                    y='Monto',
                    color='Monto',
                    text_auto='.3s',
                    labels={'Monto': 'Ventas ($)', 'Concepto': 'Concepto / Producto'},
                    color_continuous_scale='Blues',
                    template="plotly_dark"
                )
                fig_top10.update_traces(
                    textposition='outside',
                    marker_line_color='#ffffff',
                    marker_line_width=1.2,
                    opacity=0.95
                )
                fig_top10.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#e2e8f0", family="sans-serif"),
                    xaxis=dict(showgrid=False, linecolor='#334155', tickangle=-25),
                    yaxis=dict(showgrid=True, gridcolor='#263346', linecolor='#334155'),
                    margin=dict(l=20, r=20, t=30, b=30)
                )
                st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabla de detalle
    with st.expander("📄 Detalle de Registro de Operaciones"):
        st.dataframe(df_filtrado, use_container_width=True)