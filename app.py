import os
import streamlit as st
import openpyxl
import pandas as pd
import plotly.graph_objects as go
 
st.set_page_config(
    page_title="QUADRUM | SIAP-ICPI v1.0",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.markdown("""
<style>
    .metric-card {
        background: white; border-radius: 12px; padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #003087; margin-bottom: 10px;
    }
    .alert-red {
        background: #fff0f0; border-left: 4px solid #e53e3e;
        padding: 12px 16px; border-radius: 8px; margin: 8px 0;
    }
    .alert-green {
        background: #f0fff4; border-left: 4px solid #38a169;
        padding: 12px 16px; border-radius: 8px; margin: 8px 0;
    }
    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #003087;
        border-bottom: 2px solid #003087;
        padding-bottom: 6px; margin-bottom: 16px;
    }
    div[data-testid="stMetric"] {
        background: white; border-radius: 10px;
        padding: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)
 
 
@st.cache_data(show_spinner="Cargando motor SIAP-ICPI...")
def cargar_datos():
    archivos = os.listdir('.')
    xlsx = [f for f in archivos if '.xlsx' in f.lower() and not f.startswith('~')]
    if not xlsx:
        raise FileNotFoundError(f"Sin Excel. Listado: {archivos}")
 
    wb = openpyxl.load_workbook(xlsx[0], data_only=True)
    d = {}
 
    ws14 = wb['H14_CALCULO_ICPI']
    d['icpi'] = float(ws14['B32'].value or 41.24)
    ws01 = wb['H01_PARAMETROS_GENERALES']
    d['icm'] = float(ws01['B12'].value or 1.0) * 100
    ws16 = wb['H16_ITAM_TRANSPARENCIA']
    d['itam'] = float(ws16['B27'].value or 0.621) * 100
    ws15 = wb['H15_INDICES_COMPLEMENTARIOS']
    d['ife'] = float(ws15['B31'].value or 85.0)
    d['ssc'] = float(ws15['B44'].value or 0.0285) * 100
    avep_raw = ws14['B36'].value
    d['avep'] = str(avep_raw) if avep_raw else "⚠️ Transición Crítica"
 
    ws18 = wb['H18_IED_EFICIENCIA_DIRECTIVA']
    d['ied'] = [
        {'Dirección': str(r[0]), 'Metas': int(r[1] or 0),
         'IED': float(r[2]) * 100, 'Nivel': str(r[4] or '')}
        for r in ws18.iter_rows(min_row=7, max_row=14, values_only=True)
        if r[0] and r[2] is not None
    ]
 
    ws05 = wb['H05_METAS_PDOT']
    meta_desc = {}
    meta_ods  = {}
    meta_pi   = {}
    for i, row in enumerate(ws05.iter_rows(values_only=True), 1):
        if 7 <= i <= 26 and row[0]:
            k = str(row[0])
            meta_desc[k] = str(row[1])[:50] if row[1] else k
            meta_ods[k]  = str(row[14]) if len(row) > 14 and row[14] else 'N/A'
            meta_pi[k]   = float(row[7]) if row[7] else 0.0
 
    metas = []
    for row in ws14.iter_rows(min_row=6, max_row=25, values_only=True):
        if row[0]:
            k = str(row[0])
            metas.append({
                'Meta':       k,
                'Descripción': meta_desc.get(k, k),
                'P_i':        float(row[1] or 0),
                'V_i':        int(row[9]) if row[9] is not None else 0,
                'T_i':        float(row[10] or 0),
                'ICPI_i':     float(row[15] or 0),
                'ODS_Cluster': meta_ods.get(k, 'N/A'),
            })
    d['metas'] = metas
 
    # ── ODS clusters (calculado en Python) ──────────────────────
    clusters = {
        'Gobernanza':     {'num': 0.0, 'den': 0.0, 'count': 0},
        'Infraestructura':{'num': 0.0, 'den': 0.0, 'count': 0},
        'Inclusion':      {'num': 0.0, 'den': 0.0, 'count': 0},
    }
    for m in metas:
        c = m['ODS_Cluster']
        if c in clusters:
            clusters[c]['num']   += m['P_i'] * m['ICPI_i']
            clusters[c]['den']   += m['P_i']
            clusters[c]['count'] += 1
    d['ods_clusters'] = {
        k: {
            'icpi':  round(v['num']/v['den'], 1) if v['den'] > 0 else 0,
            'count': v['count'],
        }
        for k, v in clusters.items()
    }
 
    ws09 = wb['H09_EJECUCION_PRESUPUESTARIA']
    presup = []
    for r in ws09.iter_rows(min_row=5, max_row=24, values_only=True):
        if r[1] and r[5] and r[9]:
            try:
                presup.append({'Meta': str(r[1]), 'Codificado': float(r[5]),
                               'Devengado': float(r[9]),
                               'T_i': float(r[10] or 0)})
            except Exception:
                continue
    d['presupuesto'] = presup
 
    ws17 = wb['H17_SENSIBILIDAD_DELTA']
    sensib = []
    for r in ws17.iter_rows(min_row=6, max_row=25, values_only=True):
        if r[0] and r[1]:
            try:
                sensib.append({'Meta': str(r[0]), 'Delta_ICPI': float(r[1])})
            except Exception:
                continue
    d['sensibilidad'] = sorted(sensib, key=lambda x: x['Delta_ICPI'], reverse=True)[:5]
 
    wb.close()
    return d
 
 
def avep_label(v):
    if v >= 90: return "⭐ Excelencia en Trazabilidad"
    if v >= 70: return "✅ Gestión por Mandato"
    if v >= 40: return "⚠️ Transición Crítica"
    if v >= 20: return "🔶 Gestión por Ocurrencia"
    return "🔴 Ruptura Sistémica"
 
 
def color_sem(v, alto=70, medio=55):
    return "#38a169" if v >= alto else "#d69e2e" if v >= medio else "#e53e3e"
 
 
# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0'>
        <div style='font-size:2.5rem'>🏛️</div>
        <div style='font-size:1.2rem;font-weight:700;color:#003087'>QUADRUM</div>
        <div style='font-size:0.75rem;color:#666'>SIAP-ICPI v1.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    pagina = st.radio("", [
        "📊 Dashboard Ejecutivo",
        "🎯 Análisis de Metas",
        "🏢 Tablero IED",
        "🔔 Señales MOM",
        "🌍 Alineación ODS & Género",
        "👥 Vista Ciudadana TAC",
    ], label_visibility="collapsed")
    st.divider()
    st.caption("GAD Municipal de Montecristi\nPeríodo Fiscal 2024\nJavo Delgado Santana")
 
# ── CARGA ─────────────────────────────────────────────────────────
try:
    datos = cargar_datos()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()
 
icpi   = datos['icpi']
icm    = datos['icm']
brecha = icm - icpi
 
 
# ════════════════════════════════════════════════════════════════
# DASHBOARD EJECUTIVO
# ════════════════════════════════════════════════════════════════
if pagina == "📊 Dashboard Ejecutivo":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#003087,#0055b3);
                padding:28px 32px;border-radius:12px;margin-bottom:24px;
                box-shadow:0 4px 16px rgba(0,48,135,0.3)'>
        <h1 style='color:white;margin:0;font-size:1.8rem'>
            🏛️ SIAP-ICPI v1.0 — QUADRUM
        </h1>
        <p style='color:#90b8f8;margin:6px 0 0 0'>
            Sistema de Integridad Algorítmica Preventiva &nbsp;|&nbsp;
            GAD Municipal de Montecristi &nbsp;|&nbsp; Período Fiscal 2024
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("ICPI Global",     f"{icpi:.1f}%",  avep_label(icpi))
    c2.metric("ICM SIGAD",       f"{icm:.0f}%",   "Auto-reporte")
    c3.metric("Brecha ICM-ICPI", f"{brecha:.1f} pp",
              "⚠️ MOM-I Activa" if brecha > 30 else "Normal",
              delta_color="inverse")
    c4.metric("ITAM",            f"{datos['itam']:.1f}%")
    c5.metric("IFE Electoral",   f"{datos['ife']:.1f}%")
    c6.metric("SSC Patronato",   f"{datos['ssc']:.2f}%")
 
    st.divider()
    col_a, col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-title">Medidor ICPI Global</div>',
                    unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=icpi,
            number={'suffix': '%'},
            delta={'reference': icm, 'valueformat': '.1f', 'suffix': ' pp vs ICM'},
            title={'text': avep_label(icpi)},
            gauge={
                'axis': {'range': [0,100]},
                'bar': {'color': "#003087", 'thickness': 0.25},
                'steps': [
                    {'range': [0,  20], 'color': '#fed7d7'},
                    {'range': [20, 40], 'color': '#feebc8'},
                    {'range': [40, 70], 'color': '#fefcbf'},
                    {'range': [70, 90], 'color': '#c6f6d5'},
                    {'range': [90,100], 'color': '#9ae6b4'},
                ],
                'threshold': {'line': {'color':'#e53e3e','width':4},
                              'thickness':0.85, 'value':icm}
            }
        ))
        fig_g.update_layout(height=320, margin=dict(t=60,b=20,l=30,r=30),
                             paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_g, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-title">Brecha ICM vs ICPI</div>',
                    unsafe_allow_html=True)
        fig_b = go.Figure()
        fig_b.add_bar(
            x=["ICM SIGAD\n(auto-reporte)", "ICPI SIAP\n(verificado)"],
            y=[icm, icpi], marker_color=["#4299e1","#003087"],
            text=[f"<b>{icm:.0f}%</b>", f"<b>{icpi:.1f}%</b>"],
            textposition='outside', width=[0.4,0.4])
        fig_b.add_annotation(x=0.5, y=72,
            text=f"<b>Brecha: {brecha:.1f} pp</b>", showarrow=False,
            font=dict(size=18, color="#e53e3e"), xref="paper",
            bgcolor="white", bordercolor="#e53e3e", borderwidth=2, borderpad=6)
        fig_b.update_layout(height=320, yaxis=dict(range=[0,125]),
                             margin=dict(t=20,b=20,l=20,r=20),
                             showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_b, use_container_width=True)
 
    st.divider()
    col_c, col_d = st.columns(2)
 
    with col_c:
        st.markdown('<div class="section-title">Radar de Índices</div>',
                    unsafe_allow_html=True)
        cats = ['ICPI','ITAM','IFE','IED Prom.','SSC×10']
        ied_prom = (sum(x['IED'] for x in datos['ied'])/len(datos['ied'])
                    ) if datos['ied'] else 0
        vals_act  = [icpi, datos['itam'], datos['ife'], ied_prom, datos['ssc']*10]
        vals_meta = [60, 60, 80, 70, 30]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=vals_act+[vals_act[0]],
            theta=cats+[cats[0]], fill='toself', name='Actual',
            line_color='#003087', fillcolor='rgba(0,48,135,0.15)'))
        fig_r.add_trace(go.Scatterpolar(r=vals_meta+[vals_meta[0]],
            theta=cats+[cats[0]], fill='toself', name='Meta',
            line_color='#38a169', fillcolor='rgba(56,161,105,0.1)',
            line_dash='dash'))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            height=300, margin=dict(t=30,b=30,l=30,r=30),
            paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_r, use_container_width=True)
 
    with col_d:
        st.markdown('<div class="section-title">Top 5 Metas — Mayor Impacto ICPI</div>',
                    unsafe_allow_html=True)
        if datos['sensibilidad']:
            df_s = pd.DataFrame(datos['sensibilidad'])
            fig_s = go.Figure(go.Bar(
                x=df_s['Delta_ICPI'], y=df_s['Meta'], orientation='h',
                marker_color='#003087',
                text=[f"+{x:.4f}" for x in df_s['Delta_ICPI']],
                textposition='outside'))
            fig_s.update_layout(height=300, xaxis_title="Δ ICPI si Vi=1",
                                 margin=dict(t=10,b=10,l=10,r=60),
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_s, use_container_width=True)
 
    st.divider()
    c1,c2,c3 = st.columns(3)
    cert = sum(1 for m in datos['metas'] if m['V_i']==1)
    pt = sum(p['Codificado'] for p in datos['presupuesto'])
    dt = sum(p['Devengado']  for p in datos['presupuesto'])
    ejec = (dt/pt*100) if pt > 0 else 0
    with c1:
        st.markdown(f"""<div class="metric-card">
            <b>🎯 ICPI: {icpi:.1f}% — {avep_label(icpi)}</b><br>
            <span style='color:#666;font-size:0.9rem'>
            ICM oficial: {icm:.0f}% | Brecha verificada: {brecha:.1f} pp<br>
            8 silos de información analizados algorítmicamente.
            </span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <b>📋 Metas Certificadas: {cert}/20</b><br>
            <span style='color:#666;font-size:0.9rem'>
            {cert} metas con trazabilidad documental completa.<br>
            {20-cert} con brechas recuperables vía LOTAIP/SERCOP.
            </span></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <b>💰 Ejecución: {ejec:.1f}%</b><br>
            <span style='color:#666;font-size:0.9rem'>
            Devengado: ${dt:,.0f}<br>
            Codificado: ${pt:,.0f}
            </span></div>""", unsafe_allow_html=True)
 
 
# ════════════════════════════════════════════════════════════════
# ANÁLISIS DE METAS
# ════════════════════════════════════════════════════════════════
elif pagina == "🎯 Análisis de Metas":
    st.markdown("## 🎯 Análisis de Metas PDOT")
    st.caption("20 metas estratégicas | Variables Vi, Ti por meta")
 
    df_m = pd.DataFrame(datos['metas'])
    df_m['Estado'] = df_m.apply(
        lambda r: '✅ Certificada' if r['V_i']==1 and r['T_i']>=0.7
        else ('⚠️ En Proceso' if r['T_i']>0 else '🔴 Sin Avance'), axis=1)
    df_m['T_i_%'] = (df_m['T_i']*100).round(1)
 
    col1,col2 = st.columns(2)
    with col1:
        filtro = st.multiselect("Estado",
            ['✅ Certificada','⚠️ En Proceso','🔴 Sin Avance'],
            default=['✅ Certificada','⚠️ En Proceso','🔴 Sin Avance'])
    with col2:
        min_ti = st.slider("Avance mínimo (%)", 0, 100, 0)
 
    df_f = df_m[df_m['Estado'].isin(filtro) & (df_m['T_i_%'] >= min_ti)]
 
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total", len(df_m))
    c2.metric("Certificadas", sum(df_m['V_i']==1))
    c3.metric("En proceso",   sum((df_m['V_i']==0)&(df_m['T_i']>0)))
    c4.metric("Sin avance",   sum(df_m['T_i']==0))
 
    st.divider()
    col_a,col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-title">Vi vs Ti por Meta</div>',
                    unsafe_allow_html=True)
        fig_sc = go.Figure()
        for estado, color in [('✅ Certificada','#38a169'),
                               ('⚠️ En Proceso','#d69e2e'),
                               ('🔴 Sin Avance','#e53e3e')]:
            de = df_f[df_f['Estado']==estado]
            if not de.empty:
                fig_sc.add_trace(go.Scatter(
                    x=de['T_i_%'], y=de['V_i'], mode='markers+text',
                    name=estado, marker=dict(size=14,color=color,opacity=0.8),
                    text=de['Meta'], textposition='top center',
                    textfont=dict(size=9)))
        fig_sc.update_layout(height=380, xaxis_title="Avance Ti (%)",
            yaxis=dict(title="Vi", tickvals=[0,1],
                       ticktext=["Sin trazabilidad","Certificada"]),
            margin=dict(t=20,b=40,l=60,r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(248,249,252,1)',
            legend=dict(x=0, y=-0.3, orientation='h'))
        st.plotly_chart(fig_sc, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-title">Avance Ti por Meta</div>',
                    unsafe_allow_html=True)
        ds = df_f.sort_values('T_i_%', ascending=True)
        fig_ti = go.Figure(go.Bar(
            x=ds['T_i_%'], y=ds['Meta'], orientation='h',
            marker_color=[color_sem(v) for v in ds['T_i_%']],
            text=[f"{v:.1f}%" for v in ds['T_i_%']],
            textposition='outside'))
        fig_ti.add_vline(x=70, line_dash="dash", line_color="#003087",
                         annotation_text="Meta 70%")
        fig_ti.update_layout(height=380, xaxis=dict(range=[0,120]),
                              margin=dict(t=10,b=10,l=10,r=50),
                              paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(248,249,252,1)')
        st.plotly_chart(fig_ti, use_container_width=True)
 
    st.markdown('<div class="section-title">Tabla Detalle</div>',
                unsafe_allow_html=True)
    df_t = df_f[['Meta','Descripción','ODS_Cluster','P_i','T_i_%','V_i','Estado']].copy()
    df_t.columns = ['ID','Descripción','ODS','Peso P_i','Ti%','Vi','Estado']
    df_t['Peso P_i'] = df_t['Peso P_i'].round(4)
    st.dataframe(df_t, use_container_width=True, height=380,
                 column_config={'Ti%': st.column_config.ProgressColumn(
                     min_value=0, max_value=100, format="%.1f%%")})
 
 
# ════════════════════════════════════════════════════════════════
# TABLERO IED
# ════════════════════════════════════════════════════════════════
elif pagina == "🏢 Tablero IED":
    st.markdown("## 🏢 Tablero de Soporte a la Decisión — IED")
    st.info("ℹ️ El IED evalúa **procesos**, no personas. Insumo técnico objetivo "
            "para la Dirección de Talento Humano.", icon="📋")
 
    df_ied = pd.DataFrame(datos['ied']).sort_values('IED', ascending=False)
 
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Promedio IED", f"{df_ied['IED'].mean():.1f}%")
    c2.metric("Proceso Ejemplar (>85%)", len(df_ied[df_ied['IED']>=85]))
    c3.metric("Con Brechas (55-70%)",
              len(df_ied[(df_ied['IED']>=55)&(df_ied['IED']<70)]))
    c4.metric("Proceso Crítico (<55%)", len(df_ied[df_ied['IED']<55]))
 
    st.divider()
    col_a,col_b = st.columns([3,2])
 
    with col_a:
        st.markdown('<div class="section-title">IED por Dirección</div>',
                    unsafe_allow_html=True)
        fig_ied = go.Figure(go.Bar(
            x=df_ied['IED'], y=df_ied['Dirección'], orientation='h',
            marker_color=[color_sem(v) for v in df_ied['IED']],
            text=[f"<b>{v:.1f}%</b>" for v in df_ied['IED']],
            textposition='outside'))
        fig_ied.add_vline(x=85, line_dash="dash", line_color="#38a169",
                          annotation_text="85% Excelente")
        fig_ied.add_vline(x=55, line_dash="dot",  line_color="#e53e3e",
                          annotation_text="55% Crítico")
        fig_ied.update_layout(height=400, xaxis=dict(range=[0,120]),
                               margin=dict(t=20,b=20,l=20,r=60),
                               paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(248,249,252,1)')
        st.plotly_chart(fig_ied, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-title">Escala de Referencia</div>',
                    unsafe_allow_html=True)
        for nivel, rango, color, accion in [
            ("⭐ Proceso Ejemplar","≥95%","#38a169","Compartir metodología"),
            ("✅ Proceso Sólido","85–94%","#48bb78","Monitoreo mensual"),
            ("✅ En Desarrollo","70–84%","#68d391","Completar documentación"),
            ("⚠️ Con Brechas","55–69%","#d69e2e","Revisión de flujos"),
            ("🔴 Proceso Crítico","<55%","#e53e3e","Atención prioritaria"),
        ]:
            st.markdown(f"""
            <div style='border-left:4px solid {color};padding:8px 12px;
                        margin:6px 0;background:white;border-radius:4px'>
                <b style='color:{color}'>{nivel}</b> — {rango}<br>
                <small style='color:#666'>📌 {accion}</small>
            </div>""", unsafe_allow_html=True)
 
    st.divider()
    st.markdown('<div class="section-title">Informes Técnicos de Congruencia</div>',
                unsafe_allow_html=True)
    for _, row in df_ied.iterrows():
        v = row['IED']
        tipo = ("Informe de Reconocimiento" if v >= 85
                else "Informe de Seguimiento" if v >= 55
                else "Informe de Atención Prioritaria")
        rec  = ("Trazabilidad completa. Documentar buenas prácticas." if v >= 85
                else "Brechas recuperables. Regularizar LOTAIP y SERCOP." if v >= 55
                else "Brechas sistémicas. Activar plan de fortalecimiento mensual.")
        c = color_sem(v)
        st.markdown(f"""
        <div style='background:white;border-radius:8px;padding:12px 16px;
                    margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,0.07);
                    border-left:4px solid {c}'>
            <b>{row['Dirección']}</b>
            <span style='float:right;background:{c};color:white;
                         padding:2px 10px;border-radius:20px;font-size:0.85rem'>
                {v:.1f}%</span><br>
            <small style='color:#555'>📄 {tipo} | 🎯 {rec}</small>
        </div>""", unsafe_allow_html=True)
 
    st.caption("⚠️ Los Informes Técnicos son evidencia algorítmica objetiva. "
               "No reemplazan los procedimientos de la normativa del servicio público.")
 
 
# ════════════════════════════════════════════════════════════════
# SEÑALES MOM
# ════════════════════════════════════════════════════════════════
elif pagina == "🔔 Señales MOM":
    st.markdown("## 🔔 Señales de Atención Temprana — Protocolos MOM")
    st.caption("Mutación del Objeto de Medición | Las señales indican oportunidades de mejora.")
 
    st.markdown("### MOM-I — Fragmentación Selectiva")
    c1,c2 = st.columns([2,1])
    with c1:
        st.markdown("""<div class="alert-red">
            <b>⚠️ SEÑAL ACTIVA — Severidad Alta</b><br><br>
            El GAD reportó <b>9 de 20 metas</b> en SIGAD (41.4% del presupuesto).<br>
            ICM=100% calculado sobre ese subconjunto reducido.<br><br>
            <b>Evidencia:</b> $3,939,101 reportados vs $9,525,000 universo PDOT.<br>
            <b>Acción:</b> Ampliar reporte SIGAD a las 20 metas del PDOT.
        </div>""", unsafe_allow_html=True)
    with c2:
        fig_m1 = go.Figure(go.Pie(
            labels=['En SIGAD','Sin reporte'], values=[9,11],
            marker_colors=['#4299e1','#fed7d7'], hole=0.5,
            textinfo='label+value'))
        fig_m1.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0),
                              showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_m1, use_container_width=True)
 
    st.divider()
    st.markdown("### MOM-II — Sustitución Estratégica")
    st.markdown("""<div class="alert-green">
        <b>✅ SIN SEÑAL — Estado Normal</b><br><br>
        El POA 2024 mantiene integridad documental.
        No se detectaron modificaciones sistemáticas durante el ejercicio fiscal.
    </div>""", unsafe_allow_html=True)
 
    st.divider()
    st.markdown("### MOM-III — Inflación de Unidades de Medida")
    c3,c4 = st.columns([2,1])
    with c3:
        st.markdown("""<div class="alert-red">
            <b>⚠️ SEÑAL ACTIVA — Severidad Alta</b><br><br>
            <b>Meta PDOT-012:</b> Unidad móvil de salud comunitaria<br>
            • Unidad PDOT: <em>Unidad operativa</em><br>
            • Unidad SIGAD: <em>Contactos sistema salud</em><br>
            • Declarado: <b>8,295%</b> | Devengado real: <b>8%</b><br><br>
            <b>Acción:</b> Restablecer unidad original del PDOT.
        </div>""", unsafe_allow_html=True)
    with c4:
        fig_m3 = go.Figure(go.Bar(
            x=['Declarado','Real'], y=[8295, 8],
            marker_color=['#e53e3e','#38a169'],
            text=['8,295%','8%'], textposition='outside'))
        fig_m3.update_layout(height=220, margin=dict(t=10,b=10,l=10,r=10),
                              paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_m3, use_container_width=True)
 
    st.divider()
    st.markdown("### Clasificación de Señales")
    c1,c2,c3 = st.columns(3)
    for col, tipo, desc in [
        (c1,"Señal Tipo A — Brecha Documental",
         "La ejecución existe pero la documentación está incompleta en LOTAIP."),
        (c2,"Señal Tipo B — Proceso sin Registro",
         "Ausencia de registro en SERCOP o LOTAIP para meta con presupuesto."),
        (c3,"Señal Tipo C — Anomalía en Indicador",
         "Cumplimiento declarado supera 5× la meta con devengado <10%."),
    ]:
        col.markdown(f"""
        <div style='background:white;border-radius:8px;padding:16px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.07)'>
            <b>{tipo}</b><br><small style='color:#666'>{desc}</small>
        </div>""", unsafe_allow_html=True)
 
 
# ════════════════════════════════════════════════════════════════
# ODS & GÉNERO / GENERACIONAL  ← NUEVA PÁGINA
# ════════════════════════════════════════════════════════════════
elif pagina == "🌍 Alineación ODS & Género":
 
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a5276,#2980b9);
                padding:24px 32px;border-radius:12px;margin-bottom:24px'>
        <h2 style='color:white;margin:0'>🌍 Alineación ODS — Agenda 2030</h2>
        <p style='color:#aed6f1;margin:6px 0 0 0'>
            Desagregación ICPI por Clúster ODS &nbsp;|&nbsp;
            Enfoque Género y Generacional &nbsp;|&nbsp;
            Reportabilidad ante CAF · BID · Banco Mundial
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    ods = datos['ods_clusters']
    gov_icpi  = ods['Gobernanza']['icpi']
    inf_icpi  = ods['Infraestructura']['icpi']
    inc_icpi  = ods['Inclusion']['icpi']
 
    # ── Sección 1: KPIs ODS ─────────────────────────────────────
    st.markdown('<div class="section-title">ICPI por Clúster ODS (Agenda 2030)</div>',
                unsafe_allow_html=True)
    cg, ci, cn = st.columns(3)
 
    for col, nombre, icpi_c, ods_str, icono, color, mensaje in [
        (cg, "Gobernanza",      gov_icpi, "ODS 16 · ODS 17", "🏛️",
         "#4299e1",
         "✅ Base institucional sólida — elegible para financiamiento CAF"),
        (ci, "Infraestructura", inf_icpi, "ODS 6 · 9 · 11 · 13", "🏗️",
         "#e67e22",
         "⚠️ Brechas documentales — oportunidad de inversión BID/BM"),
        (cn, "Inclusión Social", inc_icpi, "ODS 1 · 3 · 4 · 5 · 10", "🤝",
         "#9b59b6",
         "🔴 Brecha crítica — argumento prioritario para financiamiento social"),
    ]:
        bg = "#f0fff4" if icpi_c >= 70 else "#fffff0" if icpi_c >= 40 else "#fff0f0"
        bc = "#38a169" if icpi_c >= 70 else "#d69e2e" if icpi_c >= 40 else "#e53e3e"
        col.markdown(f"""
        <div style='background:{bg};border-radius:12px;padding:20px;
                    border-left:5px solid {bc};
                    box-shadow:0 2px 8px rgba(0,0,0,0.07)'>
            <div style='font-size:2rem'>{icono}</div>
            <div style='font-size:1rem;font-weight:700;color:#2d3748'>{nombre}</div>
            <div style='font-size:0.8rem;color:#718096;margin:2px 0'>{ods_str}</div>
            <div style='font-size:2rem;font-weight:800;color:{bc}'>{icpi_c:.1f}%</div>
            <div style='font-size:0.75rem;color:#555;margin-top:6px'>{mensaje}</div>
        </div>""", unsafe_allow_html=True)
 
    st.divider()
 
    # ── Sección 2: Gráficos ODS ──────────────────────────────────
    col_a, col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-title">ICPI vs Meta por Clúster ODS</div>',
                    unsafe_allow_html=True)
        clusters_nombres = ['🏛️ Gobernanza\n(ODS 16-17)',
                             '🏗️ Infraestructura\n(ODS 6,9,11,13)',
                             '🤝 Inclusión\n(ODS 1,3,4,5,10)']
        valores = [gov_icpi, inf_icpi, inc_icpi]
        colores = [color_sem(v) for v in valores]
        fig_ods = go.Figure()
        fig_ods.add_bar(x=clusters_nombres, y=valores,
                        marker_color=colores,
                        text=[f"<b>{v:.1f}%</b>" for v in valores],
                        textposition='outside', name='ICPI Actual')
        fig_ods.add_bar(x=clusters_nombres, y=[60, 60, 60],
                        marker_color='rgba(0,48,135,0.15)',
                        marker_line_color='#003087', marker_line_width=2,
                        name='Meta DGIP 60%', text=['','',''],
                        textposition='none')
        fig_ods.update_layout(height=360, yaxis=dict(range=[0,110]),
                               barmode='overlay',
                               margin=dict(t=20,b=60,l=20,r=20),
                               paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(0,0,0,0)',
                               legend=dict(x=0.6, y=1.1))
        st.plotly_chart(fig_ods, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-title">Distribución de Metas por Clúster</div>',
                    unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=['🏛️ Gobernanza (5)', '🏗️ Infraestructura (8)',
                    '🤝 Inclusión (7)'],
            values=[5, 8, 7],
            marker_colors=['#4299e1','#e67e22','#9b59b6'],
            hole=0.45,
            textinfo='label+percent',
            textfont=dict(size=11)))
        fig_pie.update_layout(height=360,
                               margin=dict(t=20,b=20,l=20,r=20),
                               paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
 
    st.divider()
 
    # ── Sección 3: Tabla ODS detalle ─────────────────────────────
    st.markdown('<div class="section-title">Metas por Clúster ODS — Estado Detallado</div>',
                unsafe_allow_html=True)
 
    df_ods = pd.DataFrame(datos['metas'])
    df_ods['T_i_%']  = (df_ods['T_i']*100).round(1)
    df_ods['Estado'] = df_ods.apply(
        lambda r: '✅ Certificada' if r['V_i']==1 and r['T_i']>=0.7
        else ('⚠️ En Proceso' if r['T_i']>0 else '🔴 Sin Avance'), axis=1)
 
    tab1, tab2, tab3 = st.tabs(
        ["🏛️ Gobernanza (ODS 16-17)",
         "🏗️ Infraestructura (ODS 6,9,11,13)",
         "🤝 Inclusión (ODS 1,3,4,5,10)"])
 
    for tab, cluster in [(tab1,'Gobernanza'),(tab2,'Infraestructura'),(tab3,'Inclusion')]:
        with tab:
            df_c = df_ods[df_ods['ODS_Cluster']==cluster][
                ['Meta','Descripción','P_i','T_i_%','V_i','Estado']].copy()
            df_c.columns = ['ID','Descripción','Peso P_i','Ti%','Vi','Estado']
            df_c['Peso P_i'] = df_c['Peso P_i'].round(4)
            st.dataframe(df_c, use_container_width=True,
                         column_config={'Ti%': st.column_config.ProgressColumn(
                             min_value=0, max_value=100, format="%.1f%%")})
 
    st.divider()
 
    # ── Sección 4: Género y Generacional ────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#6b21a8,#a855f7);
                padding:16px 20px;border-radius:10px;margin-bottom:16px'>
        <h3 style='color:white;margin:0;font-size:1.1rem'>
            ♀️👴 Enfoque Género y Generacional — ODS 5 · ODS 10
        </h3>
        <p style='color:#e9d5ff;margin:4px 0 0 0;font-size:0.85rem'>
            Metas con impacto directo en equidad de género y grupos etáreos vulnerables
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    genero_data = [
        {
            'meta': 'PDOT-008', 'cat': '♀️ Género', 'ods': 'ODS 5',
            'desc': 'Guardería comunitaria para madres trabajadoras',
            'vi': 0, 'ti': 0.0,
            'impacto': 'Conciliación trabajo-familia para mujeres. '
                       'Elimina barrera de género en participación laboral.',
            'ods_meta': 'ODS 5.4 — Reconocer y valorar el trabajo doméstico no remunerado',
        },
        {
            'meta': 'PDOT-018', 'cat': '👴 Generacional', 'ods': 'ODS 10',
            'desc': 'Programa de atención a grupos vulnerables: adultos mayores y discapacidad',
            'vi': 0, 'ti': 0.0,
            'impacto': 'Protección social para adultos mayores y personas con discapacidad. '
                       'Sin trazabilidad documental al cierre 2024.',
            'ods_meta': 'ODS 10.2 — Potenciar la inclusión de todas las personas',
        },
        {
            'meta': 'PDOT-012', 'cat': '♀️👴 Género/Generacional', 'ods': 'ODS 3',
            'desc': 'Unidad móvil de salud comunitaria',
            'vi': 1, 'ti': 0.08,
            'impacto': 'Atención primaria en zonas rurales. Impacto diferenciado '
                       'en mujeres embarazadas y adultos mayores.',
            'ods_meta': 'ODS 3.8 — Cobertura universal de salud',
        },
        {
            'meta': 'PDOT-007', 'cat': '👶 Generacional', 'ods': 'ODS 4',
            'desc': 'Equipamiento educativo establecimientos rurales',
            'vi': 1, 'ti': 0.78,
            'impacto': 'Inversión en infancia y juventud rural. '
                       'Avance: 78% con documentación verificada.',
            'ods_meta': 'ODS 4.1 — Educación primaria y secundaria de calidad',
        },
        {
            'meta': 'PDOT-006', 'cat': '👶 Generacional', 'ods': 'ODS 3',
            'desc': 'Centro de salud tipo C parroquia rural Aníbal San Andrés',
            'vi': 0, 'ti': 0.08,
            'impacto': 'Infraestructura de salud para comunidades rurales. '
                       'Brecha documental: sin trazabilidad en LOTAIP.',
            'ods_meta': 'ODS 3.c — Fortalecer recursos de salud en países en desarrollo',
        },
    ]
 
    for item in genero_data:
        color_vi = "#38a169" if item['vi']==1 else "#e53e3e"
        color_ti = color_sem(item['ti']*100)
        bg = "#fdf4ff" if '♀️' in item['cat'] else \
             "#eff6ff" if '👴' in item['cat'] else "#f0fff4"
 
        with st.expander(
            f"{item['cat']} | {item['meta']} — {item['desc'][:55]}... | {item['ods']}"
        ):
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.markdown(f"""
                <div style='background:{bg};border-radius:8px;padding:12px'>
                    <b style='color:#6b21a8'>{item['ods_meta']}</b><br>
                    <span style='color:#555;font-size:0.9rem'>{item['impacto']}</span>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.metric("Vi (Evidencia)",
                          "✅ Sí" if item['vi']==1 else "❌ No")
            with col3:
                st.metric("Avance Ti", f"{item['ti']*100:.0f}%")
            st.progress(min(item['ti'], 1.0),
                        text=f"Avance físico {item['ti']*100:.0f}%")
 
    # Mensaje bilateral
    st.markdown("""
    <div style='background:#f0f9ff;border-radius:10px;padding:16px 20px;
                border-left:4px solid #0284c7;margin-top:16px'>
        <b>🌐 Blindaje Multilateral — ODS & Bilaterales</b><br>
        <div style='color:#555;font-size:0.9rem;margin-top:8px'>
        El <b>ICPI de Inclusión Social de 20%</b> (ODS 1,3,4,5,10) es el argumento 
        más poderoso ante organismos multilaterales: demuestra que <b>$3.8M destinados 
        a grupos vulnerables carecen de trazabilidad algorítmica verificable</b>.<br><br>
        El <b>ICPI de Gobernanza de 77.3%</b> (ODS 16-17) certifica la base institucional 
        que hace al GAD elegible para financiamiento CAF bajo el marco 
        <em>Gobernanza Anticipatoria</em>.<br><br>
        El silo SERCOP está mapeado bajo el estándar <b>OCDS</b> 
        (Open Contracting Data Standard), garantizando interoperabilidad con los 
        sistemas de seguimiento del Banco Mundial y el BID.
        </div>
    </div>
    """, unsafe_allow_html=True)
 
 
# ════════════════════════════════════════════════════════════════
# VISTA CIUDADANA TAC
# ════════════════════════════════════════════════════════════════
elif pagina == "👥 Vista Ciudadana TAC":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#2d3748,#4a5568);
                padding:24px;border-radius:12px;margin-bottom:20px'>
        <h2 style='color:white;margin:0'>👥 Portal TAC</h2>
        <p style='color:#a0aec0;margin:4px 0 0 0'>
            Transparencia Algorítmica Ciudadana | GAD Municipal de Montecristi
        </p>
    </div>""", unsafe_allow_html=True)
 
    st.markdown("> 🏛️ **¿Qué es esto?** Verificamos algorítmicamente si lo que "
                "el municipio planificó, ejecutó y reportó es congruente.")
 
    icono = "🟢" if icpi >= 70 else "🟡" if icpi >= 40 else "🔴"
    c_icpi = color_sem(icpi, 70, 40)
    st.markdown(f"""
    <div style='background:white;border-radius:16px;padding:28px;text-align:center;
                box-shadow:0 4px 12px rgba(0,0,0,0.1);margin:16px 0'>
        <div style='font-size:4rem'>{icono}</div>
        <div style='font-size:2rem;font-weight:700;color:{c_icpi}'>
            {icpi:.1f}% de Congruencia</div>
        <div style='color:#666;margin-top:8px'>{avep_label(icpi)}</div>
        <div style='color:#999;font-size:0.85rem;margin-top:4px'>
            El municipio declaró {icm:.0f}% — la verificación arroja {icpi:.1f}%
        </div>
    </div>""", unsafe_allow_html=True)
 
    st.markdown("### ¿Qué significa esto para ti?")
    c1,c2,c3 = st.columns(3)
    cert = sum(1 for m in datos['metas'] if m['V_i']==1)
    for col, ico, val, txt in [
        (c1,"📋",f"{cert} de 20","obras con documentos públicos verificados"),
        (c2,"🔍",f"{datos['ife']:.0f}%","promesas de campaña convertidas en proyectos"),
        (c3,"📖",f"{datos['itam']:.0f}%","documentos públicos accesibles en línea (LOTAIP)"),
    ]:
        col.markdown(f"""
        <div style='background:white;border-radius:12px;padding:20px;text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
            <div style='font-size:2.5rem'>{ico}</div>
            <div style='font-size:1.5rem;font-weight:700;color:#003087'>{val}</div>
            <div style='color:#666;font-size:0.9rem'>{txt}</div>
        </div>""", unsafe_allow_html=True)
 
    st.divider()
    st.markdown("### Estado de Obras y Proyectos")
    for m in datos['metas']:
        ti = m['T_i'] * 100
        vi = m['V_i']
        ico_m = "✅" if vi==1 and ti>=70 else "🔄" if ti>0 else "⏳"
        with st.expander(f"{ico_m} {m['Meta']} — {m['Descripción']}"):
            cx,cy = st.columns([3,1])
            with cx:
                st.progress(min(ti/100, 1.0), text=f"Avance: {ti:.1f}%")
                st.write("**Documentos verificados:**",
                         "✅ Accesibles en LOTAIP" if vi==1
                         else "⚠️ No disponibles públicamente")
            with cy:
                st.metric("Avance", f"{ti:.1f}%")
                st.metric("Documentado", "Sí" if vi==1 else "No")
 
    st.markdown("""
    <div style='background:#ebf8ff;border-radius:8px;padding:16px;
                border-left:4px solid #4299e1;margin-top:16px'>
        <b>💡 ¿Cómo ejercer tu derecho a la información?</b>
        <ul>
            <li>Consulta directa al GAD Municipal de Montecristi</li>
            <li>Solicitud LOTAIP (Ley Orgánica de Transparencia)</li>
            <li>Defensoría del Pueblo del Ecuador</li>
        </ul>
    </div>""", unsafe_allow_html=True)
 
 
# ── FOOTER ────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;color:#999;font-size:0.78rem;padding:8px 0'>
    <b>SIAP-ICPI v1.0</b> | Plataforma QUADRUM |
    GAD Municipal de Montecristi 2024 |
    Autor: Javo Delgado Santana |
    <a href='https://github.com/desabuelo-beep/SIAP-ICPI' target='_blank'>GitHub</a>
</div>""", unsafe_allow_html=True)
