import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO GERENCIAL DARK
# ---------------------------------------------------------
st.set_page_config(
    page_title="Executive Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Inyección de CSS estilo Reporte Gerencial / High-Tech Executive
st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #1e2d42;
    }
    
    /* Estilo de Tarjetas de KPI */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f172a, #1e293b);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: #00f2fe;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00f2fe !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    
    /* Contenedores de Gráficas */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"] {
        background: linear-gradient(145deg, #0b0f19, #131c2e) !important;
        border: 1px solid #1e2d42 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.7) !important;
    }
    
    h1 { color: #f8fafc; font-weight: 800; }
    h3 { color: #38bdf8; font-size: 1.15rem !important; font-weight: 700; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARGA Y PROCESAMIENTO DE DATOS
# ---------------------------------------------------------
@st.cache_data
def cargar_datos():
    archivo_excel = "ventas por provedor.xlsx"
    df = pd.read_excel(archivo_excel, sheet_name=0)
    
    # Limpieza de nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Mapeo y conversión de tipos
    df['Fecha de contabilización'] = pd.to_datetime(df['Fecha de contabilización'], errors='coerce')
    df['VENTAS'] = pd.to_numeric(df['VENTAS'], errors='coerce').fillna(0)
    df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)
    
    # Crear columnas de tiempo
    df['Año'] = df['Fecha de contabilización'].dt.year
    df['Trimestre'] = 'Q' + df['Fecha de contabilización'].dt.quarter.astype(str)
    df['Mes_Num'] = df['Fecha de contabilización'].dt.month
    
    meses_nombre = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df['Mes_Nombre'] = df['Mes_Num'].map(meses_nombre)
    
    return df

try:
    df_raw = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al leer 'ventas por provedor.xlsx': {e}")
    st.stop()

# ---------------------------------------------------------
# 3. FILTROS INTERACTIVOS (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("🎛️ Filtros Ejecutivos")

# Filtro 1: Rango de Fecha de Contabilización
fecha_min = df_raw['Fecha de contabilización'].min().date()
fecha_max = df_raw['Fecha de contabilización'].max().date()

rango_fechas = st.sidebar.date_input(
    "📅 Rango de Fecha de Contabilización:",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtro 2: Proveedor
proveedores_lista = sorted(df_raw['Nombre proveedor'].dropna().unique().tolist())
prov_sel = st.sidebar.multiselect(
    "🏭 Nombre de Proveedor:",
    options=proveedores_lista,
    default=[]
)

# Filtro 3: Cliente
clientes_lista = sorted(df_raw['CLIENTE'].dropna().unique().tolist())
cli_sel = st.sidebar.multiselect(
    "🏢 Nombre de Cliente:",
    options=clientes_lista,
    default=[]
)

# Aplicar Filtros
df = df_raw.copy()

if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    f_inicio, f_fin = rango_fechas
    df = df[(df['Fecha de contabilización'].dt.date >= f_inicio) & 
            (df['Fecha de contabilización'].dt.date <= f_fin)]

if prov_sel:
    df = df[df['Nombre proveedor'].isin(prov_sel)]

if cli_sel:
    df = df[df['CLIENTE'].isin(cli_sel)]

# ---------------------------------------------------------
# 4. HEADER Y KPIS GERENCIALES
# ---------------------------------------------------------
st.title("📊 Reporte Gerencial de Ventas")
st.markdown("---")

total_ventas = df['VENTAS'].sum()
q1_ventas = df[df['Trimestre'] == 'Q1']['VENTAS'].sum()
q2_ventas = df[df['Trimestre'] == 'Q2']['VENTAS'].sum()
q3_ventas = df[df['Trimestre'] == 'Q3']['VENTAS'].sum()
q4_ventas = df[df['Trimestre'] == 'Q4']['VENTAS'].sum()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("💰 Ventas Totales", f"${total_ventas:,.2f}")
kpi2.metric("🌱 Q1 (Ene-Mar)", f"${q1_ventas:,.2f}")
kpi3.metric("☀️ Q2 (Abr-Jun)", f"${q2_ventas:,.2f}")
kpi4.metric("🍂 Q3 (Jul-Sep)", f"${q3_ventas:,.2f}")
kpi5.metric("❄️ Q4 (Oct-Dic)", f"${q4_ventas:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Colors palette para gráficos gerenciales
FONDO_GRAFICA = "#131c2e"
TEXTO_COLOR = "#f8fafc"

if df.empty:
    st.warning("⚠️ No se encontraron registros para los filtros seleccionados.")
else:
    # ---------------------------------------------------------
    # 5. FILA 1: VENTAS POR MES Y DONUT TOP 10 PRODUCTOS
    # ---------------------------------------------------------
    col_mes, col_pie = st.columns([1.2, 0.8])

    with col_mes:
        with st.container(border=True):
            st.subheader("📈 Ventas Totales por Mes")
            
            meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            df_mes = df.groupby(['Mes_Num', 'Mes_Nombre'])['VENTAS'].sum().reset_index()
            df_mes = df_mes.sort_values('Mes_Num')

            fig_mes = go.Figure()
            fig_mes.add_trace(go.Bar(
                x=df_mes['Mes_Nombre'],
                y=df_mes['VENTAS'],
                text=[f"${v/1000:,.0f}k" for v in df_mes['VENTAS']],
                textposition='outside',
                marker=dict(color=df_mes['VENTAS'], colorscale='Viridis'),
                hovertemplate="<b>%{x}</b><br>Ventas: $%{-y:,.2f}<extra></extra>"
            ))

            fig_mes.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR),
                xaxis=dict(showgrid=False, linecolor='#334155'),
                yaxis=dict(showgrid=True, gridcolor='#1e293b', title="Monto ($)"),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_mes, use_container_width=True)

    with col_pie:
        with st.container(border=True):
            st.subheader("🌐 Top 10 Productos (Dona 3D)")
            top10_prod = df.groupby('PRODUCTO')['VENTAS'].sum().nlargest(10).reset_index()

            fig_donut = go.Figure(data=[go.Pie(
                labels=top10_prod['PRODUCTO'],
                values=top10_prod['VENTAS'],
                hole=0.45,
                pull=[0.05] * len(top10_prod),
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Ventas: $%{-value:,.2f}<br>Porcentaje: %{percent}<extra></extra>",
                marker=dict(colors=px.colors.qualitative.Bold)
            )])

            fig_donut.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR),
                showlegend=False,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 6. FILA 2: TOP 20 CLIENTES Y TOP 20 PROVEEDORES
    # ---------------------------------------------------------
    col_cli, col_prov = st.columns(2)

    with col_cli:
        with st.container(border=True):
            st.subheader("🏢 Top 20 Clientes con Mayor Compra")
            top20_cli = df.groupby('CLIENTE')['VENTAS'].sum().nlargest(20).reset_index().sort_values('VENTAS', ascending=True)

            fig_cli = px.bar(
                top20_cli,
                x='VENTAS',
                y='CLIENTE',
                orientation='h',
                color='VENTAS',
                color_continuous_scale='Blues',
                text=[f"${v/1000:,.0f}k" for v in top20_cli['VENTAS']]
            )
            fig_cli.update_traces(textposition='outside')
            fig_cli.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR, size=11),
                xaxis=dict(showgrid=True, gridcolor='#1e293b', title=""),
                yaxis=dict(title=""),
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=30, b=10)
            )
            st.plotly_chart(fig_cli, use_container_width=True)

    with col_prov:
        with st.container(border=True):
            st.subheader("🏭 Top 20 Proveedores con Mayor Venta")
            top20_prov = df.groupby('Nombre proveedor')['VENTAS'].sum().nlargest(20).reset_index().sort_values('VENTAS', ascending=True)

            fig_prov = px.bar(
                top20_prov,
                x='VENTAS',
                y='Nombre proveedor',
                orientation='h',
                color='VENTAS',
                color_continuous_scale='Tealgrn',
                text=[f"${v/1000:,.0f}k" for v in top20_prov['VENTAS']]
            )
            fig_prov.update_traces(textposition='outside')
            fig_prov.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR, size=11),
                xaxis=dict(showgrid=True, gridcolor='#1e293b', title=""),
                yaxis=dict(title=""),
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=30, b=10)
            )
            st.plotly_chart(fig_prov, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 7. FILA 3: TOP 20 PRODUCTOS Y TOP 10 GRUPOS
    # ---------------------------------------------------------
    col_p20, col_grp = st.columns([1.1, 0.9])

    with col_p20:
        with st.container(border=True):
            st.subheader("📦 Top 20 Productos más Vendidos")
            top20_prod = df.groupby('PRODUCTO')['VENTAS'].sum().nlargest(20).reset_index().sort_values('VENTAS', ascending=True)

            fig_p20 = px.bar(
                top20_prod,
                x='VENTAS',
                y='PRODUCTO',
                orientation='h',
                color='VENTAS',
                color_continuous_scale='Purples',
                text=[f"${v/1000:,.0f}k" for v in top20_prod['VENTAS']]
            )
            fig_p20.update_traces(textposition='outside')
            fig_p20.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR, size=10),
                xaxis=dict(showgrid=True, gridcolor='#1e293b', title=""),
                yaxis=dict(title=""),
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=30, b=10)
            )
            st.plotly_chart(fig_p20, use_container_width=True)

    with col_grp:
        with st.container(border=True):
            st.subheader("🏷️ Top 10 Grupos de Productos")
            top10_grp = df.groupby('grupos de productos')['VENTAS'].sum().nlargest(10).reset_index().sort_values('VENTAS', ascending=True)

            fig_grp = px.bar(
                top10_grp,
                x='VENTAS',
                y='grupos de productos',
                orientation='h',
                color='VENTAS',
                color_continuous_scale='Plasma',
                text=[f"${v/1000:,.0f}k" for v in top10_grp['VENTAS']]
            )
            fig_grp.update_traces(textposition='outside')
            fig_grp.update_layout(
                paper_bgcolor=FONDO_GRAFICA,
                plot_bgcolor=FONDO_GRAFICA,
                font=dict(color=TEXTO_COLOR, size=11),
                xaxis=dict(showgrid=True, gridcolor='#1e293b', title=""),
                yaxis=dict(title=""),
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=30, b=10)
            )
            st.plotly_chart(fig_grp, use_container_width=True)

    # ---------------------------------------------------------
    # 8. DETALLE EN TABLA EXPANDIBLE
    # ---------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📄 Ver Registro Completo de Operaciones Filtradas"):
        st.dataframe(
            df[['Fecha de contabilización', 'CLIENTE', 'Nombre proveedor', 'PRODUCTO', 'grupos de productos', 'CANTIDAD', 'VENTAS']],
            use_container_width=True
        )