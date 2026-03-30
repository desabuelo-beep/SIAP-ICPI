import os
import streamlit as st
import openpyxl
import pandas as pd
import plotly.graph_objects as go

# Forzar directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="SIAP-ICPI | QUADRUM",
    page_icon="🏛️",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    wb = openpyxl.load_workbook(
        "SIAP_ICPI_v1_0_PMV_FINAL.xlsx", data_only=True
    )
    d = {}
    ws14 = wb['H14_CALCULO_ICPI']
    d['icpi'] = ws14['B32'].value or 41.24
    ws01 = wb['H01_PARAMETROS_GENERALES']
    d['icm'] = (ws01['B12'].value or 1.0) * 100
    ws16 = wb['H16_ITAM_TRANSPARENCIA']
    d['itam'] = (ws16['B27'].value or 0.621) * 100
    ws15 = wb['H15_INDICES_COMPLEMENTARIOS']
    d['ife'] = ws15['B31'].value or 85.0
    d['ssc'] = (ws15['B44'].value or 0.0285) * 100
    ws18 = wb['H18_IED_EFICIENCIA_DIRECTIVA']
    d['ied'] = [
        {'Dirección': str(r[0]), 'IED': float(r[2]) * 100}
        for r in ws18.iter_rows(min_row=7, max_row=14, values_only=True)
        if r[0] and r[2] is not None
    ]
    d['metas'] = [
        {
            'Meta': str(r[0]),
            'V_i': int(r[9]) if r[9] is not None else 0,
            'T_i': float(r[10]) if r[10] is not None else 0.0,
        }
        for r in ws14.iter_rows(min_row=6, max_row=25, values_only=True)
        if r[0]
    ]
    wb.close()
    return d

# HEADER
st.markdown("""
<div style='background:#003087;padding:20px;border-radius:8px;margin-bottom:20px'>
<h1 style='color:white;margin:0'>🏛️ SIAP-ICPI v1.0 — QUADRUM</h1>
<p style='color:#90b8f8;margin:4px 0 0 0'>
Sistema de Integridad Algorítmica Preventiva | 
GAD Municipal de Montecristi | Período 2024
</p>
</div>
""", unsafe_allow_html=True)

try:
    datos = cargar_datos()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

icpi   = datos['icpi']
icm    = datos['icm']
brecha = icm - icpi

def avep(v):
    if v >= 90: return "⭐ Excelencia"
    if v >= 70: return "✅ Gestión por Mandato"
    if v >= 40: return "⚠️ Transición Crítica"
    if v >= 20: return "🔶 Gestión por Ocurrencia"
    return "🔴 Ruptura Sistémica"

# KPIs
st.subheader("Índices Maestros del Sistema")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ICPI Global",        f"{icpi:.1f}%",    avep(icpi))
c2.metric("ICM SIGAD Oficial",  f"{icm:.0f}%",     "Auto-reporte")
c3.metric("Brecha ICM-ICPI",    f"{brecha:.2f} pp",
          "⚠️ MOM-I Activa" if brecha > 30 else "Normal",
          delta_color="inverse")
c4.metric("ITAM Transparencia", f"{datos['itam']:.1f}%")
c5.metric("IFE Electoral",      f"{datos['ife']:.1f}%")

st.divider()

# GAUGE + BRECHA
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Medidor ICPI")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=icpi,
        delta={'reference': icm, 'valueformat': '.1f'},
        title={'text': "ICPI vs ICM Oficial"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#003087"},
            'steps': [
                {'range': [0,  20], 'color': '#ff4444'},
                {'range': [20, 40], 'color': '#ff8800'},
                {'range': [40, 70], 'color': '#ffcc00'},
                {'range': [70, 90], 'color': '#44bb44'},
                {'range': [90,100], 'color': '#008800'},
            ],
            'threshold': {'line': {'color':'red','width':3},
                          'thickness': 0.8, 'value': icm}
        }
    ))
    fig.update_layout(height=300, margin=dict(t=40,b=0,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Brecha ICM vs ICPI")
    fig2 = go.Figure()
    fig2.add_bar(
        x=["ICM SIGAD (auto-reporte)", "ICPI SIAP (verificado)"],
        y=[icm, icpi],
        marker_color=["#2196F3", "#003087"],
        text=[f"{icm:.0f}%", f"{icpi:.1f}%"],
        textposition='outside'
    )
    fig2.add_annotation(
        x=0.5, y=(icm + icpi) / 2,
        text=f"Brecha: {brecha:.2f} pp",
        showarrow=False,
        font=dict(size=16, color="red"),
        xref="paper"
    )
    fig2.update_layout(height=300, yaxis=dict(range=[0,115]),
        margin=dict(t=20,b=20,l=20,r=20), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# IED + METAS
col_c, col_d = st.columns(2)
with col_c:
    st.subheader("IED por Dirección")
    df_ied = pd.DataFrame(datos['ied'])
    if not df_ied.empty:
        df_ied = df_ied.sort_values('IED', ascending=True)
        colores = ['#ff4444' if v < 55 else '#ffcc00' if v < 70
                   else '#44bb44' for v in df_ied['IED']]
        fig3 = go.Figure(go.Bar(
            x=df_ied['IED'], y=df_ied['Dirección'],
            orientation='h', marker_color=colores,
            text=[f"{v:.1f}%" for v in df_ied['IED']],
            textposition='outside'
        ))
        fig3.update_layout(height=320, xaxis=dict(range=[0,115]),
            margin=dict(t=10,b=10,l=10,r=60))
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("Estado Metas PDOT")
    df_m = pd.DataFrame(datos['metas'])
    if not df_m.empty:
        cert = len(df_m[df_m['V_i'] == 1])
        proc = len(df_m[(df_m['V_i'] == 0) & (df_m['T_i'] > 0)])
        sin  = len(df_m[df_m['T_i'] == 0])
        fig4 = go.Figure(go.Pie(
            labels=['Certificadas (Vi=1)', 'En proceso', 'Sin avance'],
            values=[cert, proc, sin],
            marker_colors=['#44bb44', '#ffcc00', '#ff4444'],
            hole=0.4
        ))
        fig4.update_layout(height=320,
            margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# MOM SIGNALS
st.subheader("🔔 Señales de Atención Temprana (MOM)")
m1, m2, m3 = st.columns(3)
m1.error(
    "**MOM-I — Fragmentación Selectiva**\n\n"
    "9 de 20 metas reportadas en SIGAD\n\n"
    "41.4% del presupuesto estratégico\n\n"
    "ICM=100% sobre universo reducido"
)
m2.success(
    "**MOM-II — Sustitución de Metas**\n\n"
    "✅ Sin señal activa\n\n"
    "POA mantiene integridad documental"
)
m3.error(
    "**MOM-III — Inflación de Unidades**\n\n"
    "PDOT-012: 8,295% declarado\n\n"
    "vs 8% devengado real\n\n"
    "Unidad de medida inconsistente"
)

st.divider()
st.caption(
    "SIAP-ICPI v1.0 | Plataforma QUADRUM | "
    "GAD Municipal de Montecristi 2024 | "
    "Autor: Javier Delgado Santana | "
    "github.com/desabuelo-beep/SIAP-ICPI"
)
