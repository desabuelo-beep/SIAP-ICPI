import streamlit as st
import openpyxl
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="SIAP-ICPI | QUADRUM",
    page_icon="🏛️",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    posibles = [
        "SIAP_ICPI_v1_0_PMV_FINAL.xlsx",
        "/mount/src/siap-icpi/SIAP_ICPI_v1_0_PMV_FINAL.xlsx",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "SIAP_ICPI_v1_0_PMV_FINAL.xlsx"),
    ]
    ruta = next((p for p in posibles if os.path.exists(p)), None)
    if ruta is None:
        raise FileNotFoundError(
            f"Excel no encontrado. Archivos visibles: {os.listdir('.')}"
        )
    wb = openpyxl.load_workbook(ruta, data_only=True)
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
            'P_i': float(r[1]) if r[1] is not None else 0.0,
            'V_i': int(r[9]) if r[9] is not None else 0,
            'T_i': float(r[10]) if r[10] is not None else 0.0,
        }
        for r in ws14.iter_rows(min_row=6, max_row=25, values_only=True)
        if r[0]
    ]
    wb.close()
    return d

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

st.subheader("Índices Maestros del Sistema")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ICPI Global",        f"{icpi:.1f}%",   avep(icpi))
c2.metric("ICM SIGAD Oficial",  f"{icm:.0f}%",    "Auto-reporte")
c3.metric("Brecha ICM-ICPI",    f"{brecha:.2f} pp",
          "⚠️ MOM-I Activa" if brecha > 30
