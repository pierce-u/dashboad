import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(
    page_title="Executive Sales Dashboard 2026",
    page_icon="💼",
    layout="wide"
)

# 2. Inyección de CSS para Fondo Contrastado, Tarjetas Flotantes y Títulos Neón
st.markdown("""
    <style>
    /* Fondo general del Dashboard */
    .stApp {
        background-color: #080b10;
        color: #f1f5f9;
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Tarjetas de Métricas (KPIs) con relieve luminoso */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #131b2e, #0d1322);
        border: 1px solid #2d3854;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.7), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 32px -5px rgba(0, 0, 0, 0.8), 
                    0 0 20px rgba(0, 242, 254, 0.25);
        border-color: #00f2fe;
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00f2fe !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
    }
    
    /* Contenedores de Gráficos (Tarjetas Neón Contrastadas) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"] {
        background-color: #111827 !important;
        border: 1px solid #1f293d !important;
        border-radius: 18px !important;
        padding: 18px !important;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.7), 
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
    df['Dia'] = df['Fecha'].dt.day
    
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

# 7. PALETAS Y MAPAS DE COLORES NÉON / EJECUTIVOS
color_fondo_grafica = "#151e2e"

COLORES_MESES = {
    'Enero': '#00f2fe',      # Cian Neón
    'Febrero': '#ff007f',    # Magenta Eléctrico
    'Marzo': '#ffbe0b',      # Oro Neón
    'Abril': '#00f5d4',      # Verde Menta
    'Mayo': '#8338ec',      # Púrpura
    'Junio': '#3a86ff',     # Azul Eléctrico
    'Julio': '#ff006e',     # Rosa Neón
    'Agosto': '#fb5607',    # Naranja Neón
    'Septiembre': '#7000ff',# Violeta
    'Octubre': '#38bdf8',   # Celeste
    'Noviembre': '#f472b6', # Rosa Pastel
    'Diciembre': '#a78bfa'  # Lavanda
}

COLORES_CATEGORIAS = {
    'Servicios': '#00f2fe',
    'Electrónica': '#ff007f',
    'Mobiliario': '#ffbe0b',
    'Software': '#00f5d4',
    'Accesorios': '#8338ec'
}

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
else:
    # --- FILA 1: GRAFICA LINEAL 3D (TENDENCIA POR MES CON COLOR Y NOMBRE EN SERIE) ---
    with st.container(border=True):
        st.subheader("📈 Tendencia Lineal 3D de Ventas Diarias por Mes")
        
        fig_linea_3d = go.Figure()
        
        # Filtrar meses ordenados presentes en el dataframe
        meses_en_datos = [m for m in meses_disponibles if m in df_filtrado['Mes'].unique()]
        
        for idx_m, mes in enumerate(meses_en_datos):
            df_m = df_filtrado[df_filtrado['Mes'] == mes]
            if df_m.empty:
                continue
                
            # Agrupar por día para obtener la tendencia temporal
            df_dia = df_m.groupby('Dia')['Monto'].sum().reset_index().sort_values('Dia')
            
            color_mes = COLORES_MESES.get(mes, '#00f2fe')
            
            # Crear arreglo de textos para colocar el nombre del mes flotando en el último día
            textos = [''] * len(df_dia)
            if len(textos) > 0:
                textos[-1] = f"<b> {mes}</b>"
            
            fig_linea_3d.add_trace(go.Scatter3d(
                x=df_dia['Dia'],
                y=[idx_m] * len(df_dia),  # Posición fija en eje Y para dar la profundidad del mes
                z=df_dia['Monto'],
                mode='lines+markers+text',
                name=f"Mes: {mes}",
                text=textos,
                textposition="top right",
                textfont=dict(color=color_mes, size=14),
                line=dict(color=color_mes, width=6),
                marker=dict(size=5, color=color_mes, symbol='circle'),
                hovertemplate=f"<b>Mes: {mes}</b><br>Día: %{{x}}<br>Ventas: $%{{z:,.2f}}<extra></extra>"
            ))
            
        fig_linea_3d.update_layout(
            paper_bgcolor=color_fondo_grafica,
            plot_bgcolor=color_fondo_grafica,
            font=dict(color="#f1f5f9", family="sans-serif"),
            scene=dict(
                xaxis=dict(title='Día del Mes', backgroundcolor="#0f172a", gridcolor="#23324a", showbackground=True),
                yaxis=dict(
                    title='Secuencia de Mes',
                    tickvals=list(range(len(meses_en_datos))),
                    ticktext=meses_en_datos,
                    backgroundcolor="#0f172a",
                    gridcolor="#23324a",
                    showbackground=True
                ),
                zaxis=dict(title='Ventas ($)', backgroundcolor="#0f172a", gridcolor="#23324a", showbackground=True),
                camera=dict(
                    eye=dict(x=-1.6, y=-1.6, z=0.8) # Ángulo tridimensional óptimo
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.95,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=10, r=10, t=30, b=20)
        )
        
        st.plotly_chart(fig_linea_3d, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FILA 2: Ranking Categorías 3D & Top 10 Conceptos (Horizontal) ---
    col_cat, col_conc = st.columns(2)

    with col_cat:
        with st.container(border=True):
            st.subheader("🌐 Ranking 3D de Categorías más Vendidas")
            if 'Categoria' in df_filtrado.columns:
                top_cat = df_filtrado.groupby('Categoria')['Monto'].sum().reset_index().sort_values('Monto', ascending=False)
                colores_lista = [COLORES_CATEGORIAS.get(c, '#00f2fe') for c in top_cat['Categoria']]
                
                fig_3d = go.Figure(data=[go.Pie(
                    labels=top_cat['Categoria'],
                    values=top_cat['Monto'],
                    pull=[0.1, 0.05, 0.05, 0.05, 0.05],
                    marker=dict(
                        colors=colores_lista,
                        line=dict(color='#080b10', width=3)
                    ),
                    textinfo='label+value',
                    texttemplate='%{label}<br><b>$%{value:,.0f}</b>',
                    hoverinfo='label+percent+value',
                    textfont=dict(size=13, color='#ffffff'),
                    opacity=0.95
                )])
                
                fig_3d.update_layout(
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#f1f5f9", family="sans-serif"),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=20, r=20, t=30, b=40)
                )
                st.plotly_chart(fig_3d, use_container_width=True)

    with col_conc:
        with st.container(border=True):
            st.subheader("🏆 Top 10 Conceptos más Vendidos")
            if 'Concepto' in df_filtrado.columns:
                top10_conceptos = (
                    df_filtrado.groupby('Concepto')['Monto']
                    .sum()
                    .nlargest(10)
                    .reset_index()
                    .sort_values('Monto', ascending=True)
                )
                
                fig_top10 = px.bar(
                    top10_conceptos,
                    y='Concepto',
                    x='Monto',
                    color='Monto',
                    orientation='h',
                    text_auto='.3s',
                    labels={'Monto': 'Ventas ($)', 'Concepto': 'Concepto'},
                    color_continuous_scale=['#f107a3', '#7000ff', '#38bdf8'],
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
                    font=dict(color="#f1f5f9", family="sans-serif", size=12),
                    xaxis=dict(showgrid=True, gridcolor='#23324a', linecolor='#334155'),
                    yaxis=dict(showgrid=False, linecolor='#334155'),
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabla de detalle
    with st.expander("📄 Detalle de Registro de Operaciones"):
        st.dataframe(df_filtrado, use_container_width=True)