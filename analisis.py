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

# 2. Inyección de CSS para Fondo de Alto Contraste
st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #f8fafc;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid #1e293b;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f172a, #131d33);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.8), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 32px -5px rgba(0, 0, 0, 0.9), 
                    0 0 20px rgba(0, 242, 254, 0.3);
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
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"] {
        background-color: #0f172a !important;
        border: 1px solid #283548 !important;
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.8), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
    }

    h1 { color: #f8fafc; font-weight: 800; letter-spacing: -0.5px; }
    h3 { color: #38bdf8; font-size: 1.2rem !important; font-weight: 700; margin-bottom: 15px; }
    hr { border-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# 3. Cargar datos
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

# 7. PALETAS
color_fondo_grafica = "#1e293b"

COLORES_MESES = {
    'Enero': '#00f2fe',
    'Febrero': '#ff007f',
    'Marzo': '#ffbe0b',
    'Abril': '#00f5d4'
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
    # --- FILA 1: GRAFICA LINEAL TENDENCIA POR MES ---
    with st.container(border=True):
        st.subheader("📈 Tendencia de Ventas por Mes")
        
        ventas_mes = df_filtrado.groupby('Mes')['Monto'].sum().reset_index()
        ventas_mes['Mes'] = pd.Categorical(ventas_mes['Mes'], categories=meses_disponibles, ordered=True)
        ventas_mes = ventas_mes.sort_values('Mes').dropna(subset=['Mes'])
        
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

    # --- FILA 2: Ranking Categorías 3D & Treemap de Conceptos ---
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
                    pull=[0.08, 0.04, 0.04, 0.04, 0.04],
                    marker=dict(
                        colors=colores_lista,
                        line=dict(color='#0f172a', width=3)
                    ),
                    textinfo='label+value',
                    texttemplate='%{label}<br><b>$%{value:,.0f}</b>',
                    hoverinfo='label+percent+value',
                    textfont=dict(size=13, color='#ffffff'),
                    opacity=0.98
                )])
                
                fig_3d.update_layout(
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#f8fafc", family="sans-serif"),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color="#cbd5e1")
                    ),
                    margin=dict(l=20, r=20, t=30, b=40)
                )
                st.plotly_chart(fig_3d, use_container_width=True)

    with col_conc:
        with st.container(border=True):
            st.subheader("🧩 Mapa Proporcional de Conceptos (Treemap)")
            if 'Concepto' in df_filtrado.columns:
                top10_conceptos = (
                    df_filtrado.groupby(['Categoria', 'Concepto'])['Monto']
                    .sum()
                    .reset_index()
                )
                
                fig_treemap = px.treemap(
                    top10_conceptos,
                    path=['Categoria', 'Concepto'],
                    values='Monto',
                    color='Monto',
                    color_continuous_scale=['#8338ec', '#7000ff', '#f107a3', '#00f2fe']
                )
                
                fig_treemap.update_traces(
                    texttemplate='<b>%{label}</b><br>$%{value:,.0f}',
                    marker=dict(cornerradius=6, pad=dict(t=25, l=4, r=4, b=4))
                )
                
                fig_treemap.update_layout(
                    paper_bgcolor=color_fondo_grafica,
                    plot_bgcolor=color_fondo_grafica,
                    font=dict(color="#f8fafc", family="sans-serif", size=13),
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=20, b=10)
                )
                st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabla de detalle
    with st.expander("📄 Detalle de Registro de Operaciones"):
        st.dataframe(df_filtrado, use_container_width=True)