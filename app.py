import os
import sys
import streamlit as st
import openpyxl
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="QUADRUM | SIAP-ICPI v1.0",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fc; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #003087;
        margin-bottom: 10px;
    }
    .alert-red {
        background: #fff0f0;
        border-left: 4px solid #e53e3e;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .alert-green {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .alert-yellow {
        background: #fffff0;
        border-left: 4px solid #d69e2e;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .header-box {
        background: linear-gradient(135deg, #003087 0%, #0055b3 100%);
        padding: 28px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0,48,135,0.3);
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #003087;
        border-bottom: 2px solid #003087;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)


# ── CARGA DE DATOS ───────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando motor SIAP-ICPI...")
def cargar_datos():
    # Buscar el Excel en todos los directorios posibles
    directorios = [
        '/mount/src/siap-icpi',
        os.path.dirname(os.path.abspath(__file__)),
        '.',
        '/app',
    ]
    ruta = None
    for d in directorios:
        try:
            for f in os.listdir(d):
                if 'SIAP' in f and f.endswith('.xlsx'):
                    ruta = os.path.join(d, f)
                    break
        except Exception:
            continue
        if ruta:
            break

    if ruta is None:
        raise FileNotFoundError(
            "No se encontró el archivo Excel del motor SIAP-ICPI. "
            "Verifique que SIAP_ICPI_v1_0_PMV_FINAL.xlsx está en el repositorio."
        )

    wb = openpyxl.load_workbook(ruta, data_only=True)
    d = {}

    # ICPI Global (H14)
    ws14 = wb['H14_CALCULO_ICPI']
    icpi_raw = ws14['B32'].value
    d['icpi'] = float(icpi_raw) if icpi_raw else 41.24

    # ICM (H01)
    ws01 = wb['H01_PARAMETROS_GENERALES']
    icm_raw = ws01['B12'].value
    d['icm'] = float(icm_raw) * 100 if icm_raw else 100.0

    # ITAM (H16)
    ws16 = wb['H16_ITAM_TRANSPARENCIA']
    itam_raw = ws16['B27'].value
    d['itam'] = float(itam_raw) * 100 if itam_raw else 62.1

    # IFE y SSC (H15)
    ws15 = wb['H15_INDICES_COMPLEMENTARIOS']
    ife_raw = ws15['B31'].value
    d['ife'] = float(ife_raw) if ife_raw else 85.0
    ssc_raw = ws15['B44'].value
    d['ssc'] = float(ssc_raw) * 100 if ssc_raw else 2.85

    # AVEP (H14)
    avep_raw = ws14['B36'].value
    d['avep'] = str(avep_raw) if avep_raw else "⚠️ Transición Crítica"

    # IED por Dirección (H18)
    ws18 = wb['H18_IED_EFICIENCIA_DIRECTIVA']
    ied_list = []
    for row in ws18.iter_rows(min_row=7, max_row=14, values_only=True):
        if row[0] and row[2] is not None:
            try:
                ied_list.append({
                    'Dirección': str(row[0]),
                    'Metas': int(row[1]) if row[1] else 0,
                    'IED': float(row[2]) * 100,
                    'Semáforo': str(row[3]) if row[3] else '',
                    'Nivel': str(row[4]) if row[4] else '',
                })
            except Exception:
                continue
    d['ied'] = ied_list

    # Metas PDOT (H14 + H05)
    ws05 = wb['H05_METAS_PDOT']
    meta_desc = {}
    for row in ws05.iter_rows(min_row=6, max_row=25, values_only=True):
        if row[0] and row[1]:
            meta_desc[str(row[0])] = str(row[1])[:50]

    metas = []
    for row in ws14.iter_rows(min_row=6, max_row=25, values_only=True):
        if row[0]:
            meta_id = str(row[0])
            try:
                metas.append({
                    'Meta': meta_id,
                    'Descripción': meta_desc.get(meta_id, meta_id),
                    'P_i': float(row[1]) if row[1] else 0.0,
                    'V_i': int(row[9]) if row[9] is not None else 0,
                    'T_i': float(row[10]) if row[10] is not None else 0.0,
                    'ICPI_i': float(row[13]) if len(row) > 13 and row[13] else 0.0,
                })
            except Exception:
                continue
    d['metas'] = metas

    # MOM señales (H11)
    ws11 = wb['H11_ALERTAS_MOM']
    mom_data = {'MOM_I': 'Sin dato', 'MOM_II': 'Sin dato', 'MOM_III': 'Sin dato'}
    for row in ws11.iter_rows(values_only=True):
        if row[0] and isinstance(row[0], str):
            if 'MOM-I' in row[0] and row[1]:
                mom_data['MOM_I'] = str(row[1])[:80]
            elif 'MOM-II' in row[0] and row[1]:
                mom_data['MOM_II'] = str(row[1])[:80]
            elif 'MOM-III' in row[0] and row[1]:
                mom_data['MOM_III'] = str(row[1])[:80]
    d['mom'] = mom_data

    # Presupuesto por eje (H09)
    ws09 = wb['H09_EJECUCION_PRESUPUESTARIA']
    presup = []
    for row in ws09.iter_rows(min_row=5, max_row=24, values_only=True):
        if row[1] and row[5] and row[9]:
            try:
                presup.append({
                    'Meta': str(row[1]),
                    'Codificado': float(row[5]),
                    'Devengado': float(row[9]),
                    'T_i': float(row[10]) if row[10] else 0.0,
                })
            except Exception:
                continue
    d['presupuesto'] = presup

    # H17 Sensibilidad
    ws17 = wb['H17_SENSIBILIDAD_DELTA']
    sensib = []
    for row in ws17.iter_rows(min_row=6, max_row=25, values_only=True):
        if row[0] and row[1]:
            try:
                sensib.append({
                    'Meta': str(row[0]),
                    'Delta_ICPI': float(row[1]) if row[1] else 0.0,
                })
            except Exception:
                continue
    d['sensibilidad'] = sorted(sensib, key=lambda x: x['Delta_ICPI'], reverse=True)[:5]

    wb.close()
    return d


# ── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0'>
        <div style='font-size:2.5rem'>🏛️</div>
        <div style='font-size:1.2rem;font-weight:700;color:#003087'>QUADRUM</div>
        <div style='font-size:0.75rem;color:#666'>SIAP-ICPI v1.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    pagina = st.radio(
        "Navegación",
        ["📊 Dashboard Ejecutivo",
         "🎯 Análisis de Metas",
         "🏢 Tablero IED",
         "🔔 Señales MOM",
         "👥 Vista Ciudadana TAC"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("""
    <div style='font-size:0.75rem;color:#888;text-align:center'>
    <b>GAD Municipal de Montecristi</b><br>
    Período Fiscal 2024<br>
    Autor: Ronald J. Delgado Santana
    </div>
    """, unsafe_allow_html=True)


# ── CARGA ────────────────────────────────────────────────────────
try:
    datos = cargar_datos()
except Exception as e:
    st.error(f"⚠️ {e}")
    st.info("Asegúrese de que el archivo `SIAP_ICPI_v1_0_PMV_FINAL.xlsx` "
            "está en el repositorio de GitHub.")
    st.stop()

icpi   = datos['icpi']
icm    = datos['icm']
brecha = icm - icpi


def avep_label(v):
    if v >= 90: return "⭐ Excelencia en Trazabilidad"
    if v >= 70: return "✅ Gestión por Mandato"
    if v >= 40: return "⚠️ Transición Crítica"
    if v >= 20: return "🔶 Gestión por Ocurrencia"
    return "🔴 Ruptura Sistémica"


def color_semaforo(v, umbrales=(70, 55)):
    if v >= umbrales[0]: return "#38a169"
    if v >= umbrales[1]: return "#d69e2e"
    return "#e53e3e"


# ════════════════════════════════════════════════════════════════
# PÁGINA 1 — DASHBOARD EJECUTIVO
# ════════════════════════════════════════════════════════════════
if pagina == "📊 Dashboard Ejecutivo":

    # Header
    st.markdown(f"""
    <div class="header-box">
        <h1 style='color:white;margin:0;font-size:1.8rem'>
            🏛️ SIAP-ICPI v1.0 — QUADRUM
        </h1>
        <p style='color:#90b8f8;margin:6px 0 0 0'>
            Sistema de Integridad Algorítmica Preventiva &nbsp;|&nbsp;
            GAD Municipal de Montecristi &nbsp;|&nbsp; Período Fiscal 2024
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs fila 1
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("ICPI Global",       f"{icpi:.1f}%",  avep_label(icpi))
    c2.metric("ICM SIGAD",         f"{icm:.0f}%",   "Auto-reporte oficial")
    c3.metric("Brecha ICM-ICPI",   f"{brecha:.1f} pp",
              "⚠️ MOM-I Activa" if brecha > 30 else "Normal",
              delta_color="inverse")
    c4.metric("ITAM Transparencia",f"{datos['itam']:.1f}%")
    c5.metric("IFE Electoral",     f"{datos['ife']:.1f}%")
    c6.metric("SSC Patronato",     f"{datos['ssc']:.2f}%")

    st.divider()

    # Gauge + Barras
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Medidor ICPI Global</div>',
                    unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=icpi,
            number={'suffix': '%', 'font': {'size': 36}},
            delta={'reference': icm, 'valueformat': '.1f',
                   'suffix': ' pp vs ICM'},
            title={'text': avep_label(icpi), 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'ticksuffix': '%'},
                'bar': {'color': "#003087", 'thickness': 0.25},
                'bgcolor': "white",
                'borderwidth': 2,
                'steps': [
                    {'range': [0,  20], 'color': '#fed7d7'},
                    {'range': [20, 40], 'color': '#feebc8'},
                    {'range': [40, 70], 'color': '#fefcbf'},
                    {'range': [70, 90], 'color': '#c6f6d5'},
                    {'range': [90,100], 'color': '#9ae6b4'},
                ],
                'threshold': {
                    'line': {'color': '#e53e3e', 'width': 4},
                    'thickness': 0.85,
                    'value': icm
                }
            }
        ))
        fig_g.update_layout(height=320,
                             margin=dict(t=60, b=20, l=30, r=30),
                             paper_bgcolor='rgba(0,0,0,0)',
                             font_family="Arial")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Brecha ICM-ICPI (pp)</div>',
                    unsafe_allow_html=True)
        fig_b = go.Figure()
        fig_b.add_bar(
            x=["ICM SIGAD\n(auto-reporte)", "ICPI SIAP\n(verificado)"],
            y=[icm, icpi],
            marker_color=["#4299e1", "#003087"],
            marker_line_color=["#2b6cb0", "#001a5c"],
            marker_line_width=1.5,
            text=[f"<b>{icm:.0f}%</b>", f"<b>{icpi:.1f}%</b>"],
            textposition='outside',
            textfont=dict(size=16),
            width=[0.4, 0.4]
        )
        fig_b.add_annotation(
            x=0.5, y=70,
            text=f"<b>Brecha: {brecha:.1f} pp</b>",
            showarrow=False,
            font=dict(size=18, color="#e53e3e"),
            xref="paper",
            bgcolor="white",
            bordercolor="#e53e3e",
            borderwidth=2,
            borderpad=6
        )
        fig_b.update_layout(
            height=320,
            yaxis=dict(range=[0, 125], ticksuffix='%'),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Arial"
        )
        st.plotly_chart(fig_b, use_container_width=True)

    st.divider()

    # Radar de Índices
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-title">Radar de Índices del Sistema</div>',
                    unsafe_allow_html=True)
        categorias = ['ICPI', 'ITAM', 'IFE', 'IED Promedio', 'SSC×10']
        valores_act = [
            icpi,
            datos['itam'],
            datos['ife'],
            sum(x['IED'] for x in datos['ied']) / len(datos['ied']) if datos['ied'] else 0,
            datos['ssc'] * 10,
        ]
        valores_meta = [60, 60, 80, 70, 30]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=valores_act + [valores_act[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name='Actual',
            line_color='#003087',
            fillcolor='rgba(0,48,135,0.15)'
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=valores_meta + [valores_meta[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name='Meta DGIP',
            line_color='#38a169',
            fillcolor='rgba(56,161,105,0.1)',
            line_dash='dash'
        ))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=300,
            margin=dict(t=30, b=30, l=30, r=30),
            legend=dict(x=0.8, y=1.1),
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Arial"
        )
        st.plotly_chart(fig_r, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-title">Top 5 Metas — Mayor Impacto ICPI</div>',
                    unsafe_allow_html=True)
        if datos['sensibilidad']:
            df_s = pd.DataFrame(datos['sensibilidad'])
            fig_s = go.Figure(go.Bar(
                x=[f"{x:.4f}" for x in df_s['Delta_ICPI']],
                y=df_s['Meta'],
                orientation='h',
                marker_color='#003087',
                text=[f"+{x:.4f}" for x in df_s['Delta_ICPI']],
                textposition='outside',
            ))
            fig_s.update_layout(
                height=300,
                xaxis_title="Δ ICPI si Vi=1",
                margin=dict(t=10, b=10, l=10, r=60),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Arial"
            )
            st.plotly_chart(fig_s, use_container_width=True)
        else:
            st.info("Datos de sensibilidad no disponibles.")

    # Resumen textual
    st.divider()
    st.markdown('<div class="section-title">Síntesis Ejecutiva del Período 2024</div>',
                unsafe_allow_html=True)
    col_e, col_f, col_g = st.columns(3)
    with col_e:
        st.markdown(f"""
        <div class="metric-card">
            <b>🎯 ICPI Global: {icpi:.1f}%</b><br>
            <span style='color:#666;font-size:0.9rem'>
            Clasificación AVEP: {avep_label(icpi)}<br>
            El GAD reporta ICM={icm:.0f}% pero la verificación 
            algorítmica de 8 silos arroja {icpi:.1f}%, 
            una brecha de <b>{brecha:.1f} pp</b>.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_f:
        cert = sum(1 for m in datos['metas'] if m['V_i'] == 1)
        st.markdown(f"""
        <div class="metric-card">
            <b>📋 Metas Certificadas: {cert}/20</b><br>
            <span style='color:#666;font-size:0.9rem'>
            {cert} metas tienen trazabilidad documental completa 
            en los 8 silos. Las {20-cert} restantes presentan 
            brechas recuperables mediante publicación en LOTAIP y SERCOP.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_g:
        presup_total = sum(p['Codificado'] for p in datos['presupuesto'])
        devengado_total = sum(p['Devengado'] for p in datos['presupuesto'])
        ejec_pct = (devengado_total / presup_total * 100) if presup_total > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <b>💰 Ejecución Presupuestaria: {ejec_pct:.1f}%</b><br>
            <span style='color:#666;font-size:0.9rem'>
            Devengado: ${devengado_total:,.0f}<br>
            Codificado: ${presup_total:,.0f}<br>
            Universo estratégico PDOT: $9,525,000
            </span>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# PÁGINA 2 — ANÁLISIS DE METAS
# ════════════════════════════════════════════════════════════════
elif pagina == "🎯 Análisis de Metas":
    st.markdown("## 🎯 Análisis de Metas PDOT")
    st.caption("20 metas estratégicas | Variables Vi, Ti y ICPI_i por meta")

    if not datos['metas']:
        st.warning("No se pudieron cargar las metas.")
        st.stop()

    df_m = pd.DataFrame(datos['metas'])
    df_m['Estado'] = df_m.apply(
        lambda r: '✅ Certificada' if r['V_i'] == 1 and r['T_i'] >= 0.7
        else ('⚠️ En Proceso' if r['T_i'] > 0
              else '🔴 Sin Avance'), axis=1
    )
    df_m['T_i_%'] = (df_m['T_i'] * 100).round(1)

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_estado = st.multiselect(
            "Filtrar por estado",
            ['✅ Certificada', '⚠️ En Proceso', '🔴 Sin Avance'],
            default=['✅ Certificada', '⚠️ En Proceso', '🔴 Sin Avance']
        )
    with col2:
        min_ti = st.slider("Avance mínimo T_i (%)", 0, 100, 0)

    df_f = df_m[
        df_m['Estado'].isin(filtro_estado) &
        (df_m['T_i_%'] >= min_ti)
    ]

    # Métricas rápidas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total metas", len(df_m))
    c2.metric("Certificadas (Vi=1)", sum(df_m['V_i'] == 1))
    c3.metric("En proceso", sum((df_m['V_i'] == 0) & (df_m['T_i'] > 0)))
    c4.metric("Sin avance", sum(df_m['T_i'] == 0))

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        # Scatter Vi vs Ti
        st.markdown('<div class="section-title">Vi vs Ti por Meta</div>',
                    unsafe_allow_html=True)
        colores_scatter = ['#38a169' if e == '✅ Certificada'
                           else '#d69e2e' if e == '⚠️ En Proceso'
                           else '#e53e3e'
                           for e in df_f['Estado']]
        fig_sc = go.Figure()
        for estado, color in [('✅ Certificada','#38a169'),
                               ('⚠️ En Proceso','#d69e2e'),
                               ('🔴 Sin Avance','#e53e3e')]:
            d_e = df_f[df_f['Estado'] == estado]
            if not d_e.empty:
                fig_sc.add_trace(go.Scatter(
                    x=d_e['T_i_%'], y=d_e['V_i'],
                    mode='markers+text',
                    name=estado,
                    marker=dict(size=14, color=color, opacity=0.8),
                    text=d_e['Meta'],
                    textposition='top center',
                    textfont=dict(size=9)
                ))
        fig_sc.update_layout(
            height=380,
            xaxis_title="Avance Físico Ti (%)",
            yaxis=dict(title="Evidencia Vi", tickvals=[0,1],
                       ticktext=["Sin trazabilidad (0)","Certificada (1)"]),
            margin=dict(t=20, b=40, l=60, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,249,252,1)',
            font_family="Arial",
            legend=dict(x=0, y=-0.25, orientation='h')
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_b:
        # Barras Ti por meta
        st.markdown('<div class="section-title">Avance T_i por Meta (%)</div>',
                    unsafe_allow_html=True)
        df_sort = df_f.sort_values('T_i_%', ascending=True)
        colores_bar = [color_semaforo(v) for v in df_sort['T_i_%']]
        fig_ti = go.Figure(go.Bar(
            x=df_sort['T_i_%'],
            y=df_sort['Meta'],
            orientation='h',
            marker_color=colores_bar,
            text=[f"{v:.1f}%" for v in df_sort['T_i_%']],
            textposition='outside',
        ))
        fig_ti.add_vline(x=70, line_dash="dash", line_color="#003087",
                         annotation_text="Meta 70%")
        fig_ti.update_layout(
            height=380,
            xaxis=dict(range=[0, 120], ticksuffix='%'),
            margin=dict(t=10, b=10, l=10, r=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,249,252,1)',
            font_family="Arial"
        )
        st.plotly_chart(fig_ti, use_container_width=True)

    # Tabla detalle
    st.markdown('<div class="section-title">Tabla Detalle de Metas</div>',
                unsafe_allow_html=True)
    df_tabla = df_f[['Meta', 'Descripción', 'P_i', 'T_i_%', 'V_i', 'Estado']].copy()
    df_tabla.columns = ['ID Meta', 'Descripción', 'Peso P_i', 'Avance Ti%', 'Vi', 'Estado']
    df_tabla['Peso P_i'] = df_tabla['Peso P_i'].round(4)
    st.dataframe(df_tabla, use_container_width=True, height=380,
                 column_config={
                     'Avance Ti%': st.column_config.ProgressColumn(
                         min_value=0, max_value=100, format="%.1f%%"),
                     'Vi': st.column_config.NumberColumn(format="%d"),
                 })


# ════════════════════════════════════════════════════════════════
# PÁGINA 3 — TABLERO IED
# ════════════════════════════════════════════════════════════════
elif pagina == "🏢 Tablero IED":
    st.markdown("## 🏢 Tablero de Soporte a la Decisión — IED")
    st.caption(
        "Índice de Eficiencia Directiva por unidad | "
        "Insumo técnico para la Dirección de Talento Humano"
    )
    st.info(
        "ℹ️ El IED evalúa **procesos**, no personas. Es un insumo técnico objetivo. "
        "La acción institucional corresponde a la Dirección de Talento Humano.",
        icon="📋"
    )

    if not datos['ied']:
        st.warning("Datos IED no disponibles.")
        st.stop()

    df_ied = pd.DataFrame(datos['ied'])
    df_ied = df_ied.sort_values('IED', ascending=False)

    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Promedio IED", f"{df_ied['IED'].mean():.1f}%")
    c2.metric("Proceso Ejemplar (>85%)",
              len(df_ied[df_ied['IED'] >= 85]))
    c3.metric("Con Brechas (55-70%)",
              len(df_ied[(df_ied['IED'] >= 55) & (df_ied['IED'] < 70)]))
    c4.metric("Proceso Crítico (<55%)",
              len(df_ied[df_ied['IED'] < 55]))

    st.divider()
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="section-title">IED por Dirección / Proceso</div>',
                    unsafe_allow_html=True)
        colores = [color_semaforo(v) for v in df_ied['IED']]
        fig_ied = go.Figure(go.Bar(
            x=df_ied['IED'],
            y=df_ied['Dirección'],
            orientation='h',
            marker_color=colores,
            marker_line_color=[c.replace(')', ', 0.8)').replace('rgb','rgba')
                                for c in colores],
            text=[f"<b>{v:.1f}%</b>" for v in df_ied['IED']],
            textposition='outside',
        ))
        fig_ied.add_vline(x=85, line_dash="dash", line_color="#38a169",
                          annotation_text="Excelente 85%",
                          annotation_position="top right")
        fig_ied.add_vline(x=55, line_dash="dot", line_color="#e53e3e",
                          annotation_text="Crítico 55%",
                          annotation_position="bottom right")
        fig_ied.update_layout(
            height=400,
            xaxis=dict(range=[0, 120], ticksuffix='%'),
            margin=dict(t=20, b=20, l=20, r=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,249,252,1)',
            font_family="Arial"
        )
        st.plotly_chart(fig_ied, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Escala de Referencia</div>',
                    unsafe_allow_html=True)
        escala = [
            ("⭐ Proceso Ejemplar", "≥ 95%", "#38a169",
             "Compartir metodología"),
            ("✅ Proceso Sólido", "85–94%", "#48bb78",
             "Monitoreo mensual"),
            ("✅ En Desarrollo", "70–84%", "#68d391",
             "Completar documentación"),
            ("⚠️ Con Brechas", "55–69%", "#d69e2e",
             "Revisión de flujos"),
            ("🔴 Proceso Crítico", "< 55%", "#e53e3e",
             "Atención prioritaria"),
        ]
        for nivel, rango, color, accion in escala:
            st.markdown(f"""
            <div style='border-left:4px solid {color};padding:8px 12px;
                        margin:6px 0;background:white;border-radius:4px'>
                <b style='color:{color}'>{nivel}</b> — {rango}<br>
                <small style='color:#666'>📌 {accion}</small>
            </div>
            """, unsafe_allow_html=True)

    # Tabla IED
    st.divider()
    st.markdown('<div class="section-title">Informe Técnico de Congruencia por Proceso</div>',
                unsafe_allow_html=True)
    for _, row in df_ied.iterrows():
        ied_v = row['IED']
        if ied_v >= 85:
            tipo = "Informe de Reconocimiento"
            rec = "La unidad registra trazabilidad completa. Documentar buenas prácticas."
        elif ied_v >= 55:
            tipo = "Informe de Seguimiento"
            rec = "Brechas documentales recuperables. Regularizar LOTAIP y SERCOP."
        else:
            tipo = "Informe de Atención Prioritaria"
            rec = "Brechas sistémicas. Activar plan de fortalecimiento con seguimiento mensual."

        color = color_semaforo(ied_v)
        st.markdown(f"""
        <div style='background:white;border-radius:8px;padding:12px 16px;
                    margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,0.07);
                    border-left:4px solid {color}'>
            <b>{row['Dirección']}</b>
            <span style='float:right;background:{color};color:white;
                         padding:2px 10px;border-radius:20px;font-size:0.85rem'>
                {ied_v:.1f}%
            </span><br>
            <small style='color:#555'>
                📄 {tipo} &nbsp;|&nbsp; 🎯 {rec}
            </small>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        "⚠️ Los Informes Técnicos de Congruencia son evidencia algorítmica objetiva. "
        "No reemplazan los procedimientos establecidos en la normativa del servicio público."
    )


# ════════════════════════════════════════════════════════════════
# PÁGINA 4 — SEÑALES MOM
# ════════════════════════════════════════════════════════════════
elif pagina == "🔔 Señales MOM":
    st.markdown("## 🔔 Señales de Atención Temprana — Protocolos MOM")
    st.caption(
        "Mutación del Objeto de Medición | "
        "Las señales MOM indican oportunidades de mejora, no sanciones."
    )

    # MOM-I
    st.markdown("### MOM-I — Fragmentación Selectiva del Universo Evaluado")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="alert-red">
            <b>⚠️ SEÑAL ACTIVA — Severidad: Alta</b><br><br>
            El GAD reportó <b>9 de 20 metas</b> del universo SIAP en el sistema SIGAD.
            El ICM=100% se calcula sobre ese subconjunto que representa el
            <b>41.4% del presupuesto estratégico</b>.<br><br>
            <b>Evidencia:</b> $3,939,101 reportados vs $9,525,000 del universo PDOT.<br>
            <b>Acción recomendada:</b> Ampliar el reporte SIGAD a las 20 metas del PDOT.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        fig_mom1 = go.Figure(go.Pie(
            labels=['Metas en SIGAD', 'Metas sin reporte'],
            values=[9, 11],
            marker_colors=['#4299e1', '#fed7d7'],
            hole=0.5,
            textinfo='label+value'
        ))
        fig_mom1.update_layout(
            height=200, margin=dict(t=0,b=0,l=0,r=0),
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_mom1, use_container_width=True)

    st.divider()

    # MOM-II
    st.markdown("### MOM-II — Sustitución Estratégica de Metas")
    st.markdown("""
    <div class="alert-green">
        <b>✅ SIN SEÑAL — Estado: Normal</b><br><br>
        El POA 2024 mantiene integridad documental. Los hashes de inicio y cierre
        del período son idénticos, confirmando que no hubo modificaciones 
        sistemáticas en las metas durante el ejercicio fiscal.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # MOM-III
    st.markdown("### MOM-III — Inflación de Unidades de Medida")
    col3, col4 = st.columns([2, 1])
    with col3:
        st.markdown("""
        <div class="alert-red">
            <b>⚠️ SEÑAL ACTIVA — Severidad: Alta</b><br><br>
            <b>Meta PDOT-012:</b> Unidad móvil de salud comunitaria<br>
            • Unidad PDOT: <em>Unidad operativa</em><br>
            • Unidad SIGAD reportada: <em>Contactos sistema salud</em><br>
            • Cumplimiento declarado: <b>8,295%</b><br>
            • Devengado real: <b>8%</b><br><br>
            La unidad de medida fue cambiada de "unidades" a "contactos",
            produciendo una inflación artifical del indicador de 103×.<br><br>
            <b>Acción recomendada:</b> Verificar definición operativa del indicador
            y restablecer unidad original del PDOT.
        </div>
        """, unsafe_allow_html=True)
    with col4:
        fig_mom3 = go.Figure(go.Bar(
            x=['Cumplimiento\nDeclarado', 'Devengado\nReal'],
            y=[8295, 8],
            marker_color=['#e53e3e', '#38a169'],
            text=['8,295%', '8%'],
            textposition='outside',
        ))
        fig_mom3.update_layout(
            height=220,
            yaxis_title="% Cumplimiento",
            margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig_mom3, use_container_width=True)

    st.divider()

    # Marco metodológico
    st.markdown("### Marco Metodológico MOM")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='background:white;border-radius:8px;padding:16px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07)'>
            <b>Señal Tipo A — Brecha Documental</b><br>
            <small>DIC-A: Desviación por inconsistencias en el registro.
            La ejecución existe pero la documentación está incompleta o con 
            enlace roto en LOTAIP.</small>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background:white;border-radius:8px;padding:16px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07)'>
            <b>Señal Tipo B — Proceso sin Registro Público</b><br>
            <small>DIC-B: Ausencia de registro en SERCOP o LOTAIP para una meta
            con presupuesto codificado. Meta existe en POA pero sin evidencia 
            documental accesible.</small>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background:white;border-radius:8px;padding:16px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07)'>
            <b>Señal Tipo C — Anomalía en Indicador</b><br>
            <small>DIC-C: Desconexión estadística entre el cumplimiento declarado
            y la ejecución presupuestaria. Se activa cuando el porcentaje declarado
            supera 5× la meta planificada con devengado &lt;10%.</small>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# PÁGINA 5 — VISTA CIUDADANA TAC
# ════════════════════════════════════════════════════════════════
elif pagina == "👥 Vista Ciudadana TAC":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#2d3748,#4a5568);
                padding:24px;border-radius:12px;margin-bottom:20px'>
        <h2 style='color:white;margin:0'>👥 Portal TAC</h2>
        <p style='color:#a0aec0;margin:4px 0 0 0'>
            Transparencia Algorítmica Ciudadana | 
            GAD Municipal de Montecristi | 2024
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    > 🏛️ **¿Qué es esto?** El sistema SIAP-ICPI verifica de manera algorítmica
    > si lo que el municipio planificó, ejecutó y reportó públicamente es congruente.
    > Aquí puedes ver los resultados en lenguaje ciudadano.
    """)

    # Semáforo principal
    color_icpi = color_semaforo(icpi, (70, 40))
    st.markdown(f"""
    <div style='background:white;border-radius:16px;padding:28px;
                text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.1);
                margin:16px 0'>
        <div style='font-size:4rem;margin-bottom:8px'>
            {"🟢" if icpi >= 70 else "🟡" if icpi >= 40 else "🔴"}
        </div>
        <div style='font-size:2rem;font-weight:700;color:{color_icpi}'>
            {icpi:.1f}% de Congruencia
        </div>
        <div style='color:#666;margin-top:8px'>
            {avep_label(icpi)}
        </div>
        <div style='color:#999;font-size:0.85rem;margin-top:4px'>
            El municipio declaró {icm:.0f}% — la verificación algorítmica arroja {icpi:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Indicadores ciudadanos
    st.markdown("### ¿Qué significa esto para ti?")
    c1, c2, c3 = st.columns(3)

    cert = sum(1 for m in datos['metas'] if m['V_i'] == 1)
    with c1:
        st.markdown(f"""
        <div style='background:white;border-radius:12px;padding:20px;
                    text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
            <div style='font-size:2.5rem'>📋</div>
            <div style='font-size:1.5rem;font-weight:700;color:#003087'>
                {cert} de 20
            </div>
            <div style='color:#666;font-size:0.9rem'>
                obras y proyectos con documentos públicos verificados
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div style='background:white;border-radius:12px;padding:20px;
                    text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
            <div style='font-size:2.5rem'>🔍</div>
            <div style='font-size:1.5rem;font-weight:700;color:#d69e2e'>
                {datos['ife']:.0f}%
            </div>
            <div style='color:#666;font-size:0.9rem'>
                de las promesas de campaña se convirtieron en proyectos reales
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div style='background:white;border-radius:12px;padding:20px;
                    text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
            <div style='font-size:2.5rem'>📖</div>
            <div style='font-size:1.5rem;font-weight:700;color:#38a169'>
                {datos['itam']:.0f}%
            </div>
            <div style='color:#666;font-size:0.9rem'>
                de los documentos públicos son accesibles en línea (LOTAIP)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Estado de obras ciudadano
    st.markdown("### Estado de Obras y Proyectos")
    st.caption("Haz clic en una meta para ver su estado de avance")

    for m in datos['metas']:
        ti_pct = m['T_i'] * 100
        vi = m['V_i']
        color = "#38a169" if vi == 1 and ti_pct >= 70 else \
                "#d69e2e" if ti_pct > 0 else "#e53e3e"
        icono = "✅" if vi == 1 and ti_pct >= 70 else \
                "🔄" if ti_pct > 0 else "⏳"

        with st.expander(f"{icono} {m['Meta']} — {m['Descripción']}"):
            col_x, col_y = st.columns([3,1])
            with col_x:
                st.progress(min(ti_pct/100, 1.0),
                            text=f"Avance físico: {ti_pct:.1f}%")
                st.markdown(f"""
                **Documentos públicos verificados:** 
                {"✅ Sí — contratos y actas accesibles en LOTAIP" if vi == 1 
                 else "⚠️ No — documentación no disponible públicamente"}
                """)
            with col_y:
                st.metric("Avance", f"{ti_pct:.1f}%")
                st.metric("Documentado", "Sí" if vi == 1 else "No")

    st.divider()
    st.markdown("""
    <div style='background:#ebf8ff;border-radius:8px;padding:16px;
                border-left:4px solid #4299e1'>
        <b>💡 ¿Cómo usar esta información?</b><br>
        Si una obra en tu comunidad no aparece como "verificada" o el avance 
        es inferior al esperado, tienes derecho a solicitar información mediante:
        <ul>
            <li>Consulta directa al GAD Municipal</li>
            <li>Solicitud LOTAIP (Ley Orgánica de Transparencia)</li>
            <li>Defensoría del Pueblo del Ecuador</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ── FOOTER GLOBAL ────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;color:#999;font-size:0.78rem;padding:8px 0'>
    <b>SIAP-ICPI v1.0</b> | Plataforma QUADRUM | GAD Municipal de Montecristi 2024 |
    Autor: Ronald J. Delgado Santana |
    <a href='https://github.com/desabuelo-beep/SIAP-ICPI' target='_blank'>
        github.com/desabuelo-beep/SIAP-ICPI
    </a>
</div>
""", unsafe_allow_html=True)
