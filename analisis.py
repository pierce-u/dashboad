import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Ejecutivo | Ventas Q1 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ESTILOS CSS PERSONALIZADOS (TEMA OSCURO / DARK MODE)
st.markdown("""
    <style>
    /* Fondo Oscuro Principal */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    
    /* Fondo de la Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }
    
    /* Textos en la barra lateral */
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    /* Encabezado Principal */
    .title-container {
        background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    .title-container h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.2rem;
        color: #FFFFFF !important;
    }
    .title-container p {
        margin: 5px 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }

    /* Tarjetas KPI en modo oscuro */
    .kpi-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 0.88rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #38BDF8;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 8px;
    }

    /* Títulos de secciones */
    h2, h3, h4 {
        color: #F8FAFC !important;
    }
    </style>
""", unsafe_allow_html=True)

# BANNER PRINCIPAL
st.markdown("""
    <div class="title-container">
        <h1>📊 Dashboard Ejecutivo de Ventas</h1>
        <p>Análisis Consolidado de Rendimiento Trimestral — Q1 2026</p>
    </div>
""", unsafe_allow_html=True)

# 3. CARGA DE DATOS
archivo_excel = 'ventas_ficticias_Q1_2026.xlsx'

if not os.path.exists(archivo_excel):
    st.error(f"⚠️ No se encontró el archivo '{archivo_excel}' en el directorio actual.")
    st.stop()

@st.cache_data
def cargar_datos(ruta):
    xls = pd.ExcelFile(ruta)
    df_lista = []
    for nombre_pestana in xls.sheet_names:
        df_mes = pd.read_excel(ruta, sheet_name=nombre_pestana)
        df_mes['Mes'] = nombre_pestana
        df_lista.append(df_mes)
    df_historico = pd.concat(df_lista, ignore_index=True)
    return df_historico[df_historico['Concepto'] != 'Total'].copy()

df_limpio = cargar_datos(archivo_excel)

# 4. BARRA LATERAL (SIDEBAR) CON FILTROS
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1828/1828762.png", width=50)
st.sidebar.title("Panel de Control")
st.sidebar.markdown("Filtra los datos para actualizar las métricas y gráficos al instante.")
st.sidebar.markdown("---")

# Filtro de Mes
meses_disponibles = list(df_limpio['Mes'].unique())
meses_seleccionados = st.sidebar.multiselect(
    "🗓️ Seleccionar Mes(es):",
    options=meses_disponibles,
    default=meses_disponibles
)

# Filtro de Categoría
categorias_disponibles = list(df_limpio['Categoría'].unique())
categorias_seleccionadas = st.sidebar.multiselect(
    "🏷️ Seleccionar Categoría(s):",
    options=categorias_disponibles,
    default=categorias_disponibles
)

# Aplicar Filtros
df_filtrado = df_limpio[
    (df_limpio['Mes'].isin(meses_seleccionados)) &
    (df_limpio['Categoría'].isin(categorias_seleccionadas))
]

if df_filtrado.empty:
    st.warning("⚠️ No existen registros para la combinación de filtros seleccionada.")
    st.stop()

# 5. TARJETAS DE KPIs
total_ventas = df_filtrado['Monto en dólares'].sum()
total_tx = len(df_filtrado)
ticket_promedio = total_ventas / total_tx if total_tx > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3B82F6;">
            <div class="kpi-title">💰 Facturación Total</div>
            <div class="kpi-value" style="color: #60A5FA;">${total_ventas:,.2f} USD</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">🛒 Transacciones Totales</div>
            <div class="kpi-value" style="color: #34D399;">{total_tx:,}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">🎯 Ticket Promedio</div>
            <div class="kpi-value" style="color: #FBBF24;">${ticket_promedio:,.2f} USD</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. SECCIÓN DE GRÁFICOS INTERACTIVOS (MODO OSCURO)
col_left, col_right = st.columns(2)

# Gráfico 1: Evolución Mensual
with col_left:
    st.subheader("📈 Evolución de Ventas por Mes")
    ventas_mes = df_filtrado.groupby('Mes')['Monto en dólares'].sum().reset_index()
    
    orden_meses = ['Enero', 'Febrero', 'Marzo']
    ventas_mes['Mes'] = pd.Categorical(ventas_mes['Mes'], categories=orden_meses, ordered=True)
    ventas_mes = ventas_mes.sort_values('Mes')

    fig_mes = px.bar(
        ventas_mes,
        x='Mes',
        y='Monto en dólares',
        text_auto='$.2s',
        color='Mes',
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B']
    )
    fig_mes.update_traces(textposition='outside')
    fig_mes.update_layout(
        template='plotly_dark',
        plot_bgcolor='#1E293B',
        paper_bgcolor='#1E293B',
        xaxis_title=None,
        yaxis_title="Monto ($ USD)",
        showlegend=False,
        font=dict(family="Calibri, sans-serif", size=13),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_mes, use_container_width=True)

# Gráfico 2: Ventas por Categoría (Dona)
with col_right:
    st.subheader("🏷️ Participación por Categoría")
    ventas_cat = df_filtrado.groupby('Categoría')['Monto en dólares'].sum().reset_index()
    
    fig_cat = px.pie(
        ventas_cat,
        values='Monto en dólares',
        names='Categoría',
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_cat.update_traces(textinfo='percent+label', pull=[0.02]*len(ventas_cat))
    fig_cat.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1E293B',
        font=dict(family="Calibri, sans-serif", size=13),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# Gráfico 3: Ranking Top 5 Productos (MULTICOLOR)
st.subheader("🏆 Top 5 Productos con Mayor Facturación")
top_prod = df_filtrado.groupby('Concepto')['Monto en dólares'].sum().reset_index().sort_values(by='Monto en dólares', ascending=True).tail(5)

fig_prod = px.bar(
    top_prod,
    x='Monto en dólares',
    y='Concepto',
    orientation='h',
    text_auto='$.2s',
    color='Concepto',  # Asigna un color distintivo a cada producto
    color_discrete_sequence=px.colors.qualitative.Bold  # Paleta de colores vivos y variados
)
fig_prod.update_traces(textposition='outside')
fig_prod.update_layout(
    template='plotly_dark',
    plot_bgcolor='#1E293B',
    paper_bgcolor='#1E293B',
    showlegend=False,  # Oculta la leyenda redundante para mantener el diseño limpio
    xaxis_title="Monto ($ USD)",
    yaxis_title=None,
    font=dict(family="Calibri, sans-serif", size=13),
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_prod, use_container_width=True)

# 7. TABLA DESPLEGABLE CON DETALLE DE DATOS
with st.expander("🔍 Explorar y Exportar Datos Detallados"):
    st.markdown("Tabla con los registros filtrados seleccionados actualmente en el panel:")
    st.dataframe(
        df_filtrado[['Mes', 'Categoría', 'Concepto', 'Monto en dólares']],
        use_container_width=True
    )
    
    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Filtrado (CSV)",
        data=csv_data,
        file_name="reporte_ventas_filtrado_Q1_2026.csv",
        mime="text/csv"
    )