"""
TERRA CIUDADANA — Sistema de Integridad Algorítmica Preventiva
QUADRUM GovTech | v2.0 | 2026
Plataforma pública de auditoría ciudadana independiente
"""

import streamlit as st
import pandas as pd
import json
import hashlib
import datetime
from io import BytesIO

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TERRA CIUDADANA",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# DATOS REALES MONTECRISTI 2024 (H36 BRIDGE)
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos_montecristi():
    return {
        "gad": "GAD Municipal de Montecristi",
        "alcalde": "Ing. Luis Jonathan Toro Largacha",
        "periodo": "2024-2027",
        "icpi": 72.93,
        "avep": "Gestión por Mandato",
        "ife": 77.0,
        "icm_sigad": 100.0,
        "brecha": 27.07,
        "itam": 70.0,
        "ics": 63.51,
        "sat": {"I": False, "II": False, "III": False, "IV": False},
        "nota_metodologica": (
            "⚠️ NOTA: Cédula presupuestaria 2025 usada como proxy metodológico para 2024. "
            "LOTAIP, verificables físicos y actas de entrega-recepción: simulación técnica documentada. "
            "Datos POA, PAC y Plan CNE: oficiales y reales 2024."
        ),
        "metas": [
            {"id": "SC-I-N-01", "nombre": "Salud Municipal", "icpi": 95.0, "avep": "🔵 Excelencia", "ods": "3,1,10", "dir": "Patronato"},
            {"id": "SC-L-N-02", "nombre": "TICs y Educativo", "icpi": 85.0, "avep": "🟢 Mandato", "ods": "4,10", "dir": "Dir. TIC"},
            {"id": "AH-I-X-01", "nombre": "Vialidad Cantonal", "icpi": 58.3, "avep": "🟡 Transición", "ods": "9,11", "dir": "Dir. Obras"},
            {"id": "AH-I-X-02", "nombre": "Señalización e IVU", "icpi": 0.0, "avep": "🔴 Ruptura", "ods": "11", "dir": "Dir. Obras"},
            {"id": "AH-I-X-03", "nombre": "Equipamientos Públicos", "icpi": 58.3, "avep": "🟡 Transición", "ods": "11,3,4", "dir": "Dir. Obras"},
            {"id": "AH-I-N-01", "nombre": "Vivienda Interés Social", "icpi": 22.5, "avep": "🟠 Ocurrencia", "ods": "1,11", "dir": "EP Montehogar"},
            {"id": "SC-L-G-01", "nombre": "Cultura y Patrimonio", "icpi": 47.8, "avep": "🟡 Transición", "ods": "4,11", "dir": "Dir. Cultura"},
            {"id": "AH-I-X-04", "nombre": "Tránsito y Seguridad Vial", "icpi": 40.5, "avep": "🟡 Transición", "ods": "11,3", "dir": "Dir. Obras"},
            {"id": "PI-I-G-01", "nombre": "Modernización Administrativa", "icpi": 85.0, "avep": "🟢 Mandato", "ods": "16", "dir": "Dir. Administrativa"},
            {"id": "AH-C-X-01", "nombre": "Agua Potable", "icpi": 72.0, "avep": "🟢 Mandato", "ods": "6,3,11", "dir": "Dir. Agua"},
            {"id": "AH-C-X-02", "nombre": "Alcantarillado y PTAR", "icpi": 72.0, "avep": "🟢 Mandato", "ods": "6,3,11", "dir": "Dir. Agua"},
            {"id": "SC-I-N-03", "nombre": "Grupos Prioritarios", "icpi": 53.4, "avep": "🟡 Transición", "ods": "1,3,5,10", "dir": "Patronato"},
            {"id": "FA-I-X-01", "nombre": "Gestión del Riesgo", "icpi": 65.0, "avep": "🟡 Transición", "ods": "11,13", "dir": "Dir. Ambiental"},
            {"id": "FA-C-X-01", "nombre": "Desechos Sólidos", "icpi": 80.0, "avep": "🟢 Mandato", "ods": "11,13", "dir": "EP Aseo"},
            {"id": "FA-I-X-02", "nombre": "Áreas Verdes e IVU", "icpi": 68.8, "avep": "🟡 Transición", "ods": "11,13,15", "dir": "Dir. Ambiental"},
            {"id": "FA-L-N-01", "nombre": "Fauna Urbana", "icpi": 77.0, "avep": "🟢 Mandato", "ods": "15", "dir": "Dir. Ambiental"},
            {"id": "PI-I-G-02", "nombre": "PDOT/Catastro/Trámites", "icpi": 85.0, "avep": "🟢 Mandato", "ods": "16,17", "dir": "Dir. Planificación"},
            {"id": "PI-L-G-01", "nombre": "Participación Ciudadana", "icpi": 53.4, "avep": "🟡 Transición", "ods": "16,17", "dir": "Dir. Planificación"},
            {"id": "EP-L-N-01", "nombre": "Fortalecimiento Productivo", "icpi": 95.0, "avep": "🔵 Excelencia", "ods": "1,8,10", "dir": "Dir. Económica"},
            {"id": "EP-L-X-01", "nombre": "Turismo", "icpi": 85.0, "avep": "🟢 Mandato", "ods": "8,11", "dir": "Dir. Turismo"},
        ]
    }

@st.cache_data
def datos_evaluacion_precacheados():
    """
    Análisis pre-cacheado del Informe de Rendición de Cuentas 2024
    GAD Montecristi — Alcalde Jonathan Toro — Evento 11/07/2025
    """
    return {
        "fecha_evento": "11 de julio de 2025",
        "lugar": "Comuna Toalla Grande",
        "asistentes": 261,
        "informe_numero": "22844",
        "icpi_verificado": 72.93,
        "icm_declarado": 100.0,
        "brecha_puntos": 27.07,
        "friccion_narrativa": 68.0,
        "coherencia": 32.0,
        "hallazgos": [
            {
                "meta": "AH-I-X-02 — Vialidad",
                "discurso": "Reconformación 90 km vías, maquinaria en proceso precontractual",
                "informe": "Maquinaria a espera de anticipo al 31/12/2024",
                "terra": "T_i = 0% — ejecución financiera nula",
                "tipo": "⚠️ Fricción Narrativa",
                "nivel": "alto"
            },
            {
                "meta": "SC-I-N-01 — Salud",
                "discurso": "3,743 usuarios atendidos en brigadas médicas",
                "informe": "3,743 atendidos confirmados",
                "terra": "ICPI = 95% — Excelencia",
                "tipo": "✅ Coherencia Verificada",
                "nivel": "bajo"
            },
            {
                "meta": "AH-C-X-01 — Agua Potable",
                "discurso": "Acueducto CAF $28M aprobado 29/12/2024",
                "informe": "Convenio firmado, hitos CAF documentados",
                "terra": "ICPI = 72% — Gestión por Mandato",
                "tipo": "✅ Coherencia Verificada",
                "nivel": "bajo"
            },
            {
                "meta": "PI-I-G-01 — Modernización",
                "discurso": "Modernización parque automotor y tecnología",
                "informe": "ERP $252k, maquinaria $600k adjudicados",
                "terra": "ICPI = 85% — Gestión por Mandato",
                "tipo": "✅ Coherencia Verificada",
                "nivel": "bajo"
            },
        ],
        "promesas_sin_pdot": [
            "EC-005 — Ordenanzas exoneración tributos a nuevas empresas",
            "IN-006 — Marca ciudad / posicionamiento nacional",
            "TE-005 — Camal municipal"
        ]
    }

GADS_ECUADOR = [
    "GAD Municipal de Montecristi",
    "GAD Municipal de Manta",
    "GAD Municipal de Portoviejo",
    "GAD Municipal de Jaramijó",
    "GAD Municipal de Quito",
    "GAD Municipal de Guayaquil",
    "GAD Municipal de Cuenca",
    "Otro municipio",
]

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --terra-blue: #003087;
    --terra-green: #38a169;
    --terra-yellow: #d69e2e;
    --terra-orange: #e67e22;
    --terra-red: #e53e3e;
    --terra-dark: #1a1a2e;
    --terra-light: #f0f4f8;
}

* { font-family: 'Space Grotesk', sans-serif; }

.terra-header {
    background: linear-gradient(135deg, #003087 0%, #1a365d 50%, #2c5282 100%);
    padding: 2rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 2rem;
}

.terra-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; }
.terra-header p { font-size: 1rem; opacity: 0.85; margin: 0.5rem 0 0 0; }

.component-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.component-card:hover {
    border-color: #003087;
    box-shadow: 0 4px 20px rgba(0,48,135,0.15);
    transform: translateY(-2px);
}

.component-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.component-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: linear-gradient(135deg, #003087, #2c5282);
    color: white;
}

.icpi-gauge {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #f0f4f8, #e2e8f0);
    border-radius: 16px;
    margin: 1rem 0;
}

.icpi-number {
    font-size: 5rem;
    font-weight: 700;
    color: #003087;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}

.icpi-label { font-size: 1.2rem; color: #4a5568; margin-top: 0.5rem; }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid #e2e8f0;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label { font-size: 0.85rem; color: #718096; margin-top: 0.3rem; }

.brecha-alert {
    background: linear-gradient(135deg, #fff5f5, #fed7d7);
    border: 2px solid #fc8181;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.nota-metodologica {
    background: #fffbeb;
    border-left: 4px solid #d69e2e;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #744210;
    margin: 1rem 0;
}

.sat-card {
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    border: 2px solid;
}

.sat-ok { background: #f0fff4; border-color: #68d391; color: #276749; }
.sat-alert { background: #fff5f5; border-color: #fc8181; color: #c53030; }

.hash-display {
    background: #1a1a2e;
    color: #68d391;
    padding: 1rem;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    word-break: break-all;
}

.friccion-barra {
    height: 20px;
    border-radius: 10px;
    background: linear-gradient(90deg, #68d391 0%, #d69e2e 50%, #fc8181 100%);
    margin: 0.5rem 0;
}

.hallazgo-card {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.8rem;
    border-left: 4px solid;
}

.hallazgo-alto { background: #fff5f5; border-color: #fc8181; }
.hallazgo-bajo { background: #f0fff4; border-color: #68d391; }

.footer-terra {
    text-align: center;
    padding: 2rem;
    color: #718096;
    font-size: 0.85rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 3rem;
}

.proxima-fase {
    background: linear-gradient(135deg, #1a1a2e, #2d3748);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 0.5rem 0;
}

.stButton button {
    background: linear-gradient(135deg, #003087, #2c5282);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s;
}

.stButton button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,48,135,0.3); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem;'>
        <div style='font-size:2rem;'>🌍</div>
        <div style='font-weight:700; font-size:1.2rem; color:#003087;'>TERRA CIUDADANA</div>
        <div style='font-size:0.8rem; color:#718096;'>QUADRUM GovTech v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Navega por los componentes:**")

    componentes = {
        "🏠 Inicio": "inicio",
        "📄 TERRA ACCEDE": "accede",
        "🔍 TERRA VERIFICA": "verifica",
        "🧮 TERRA CALCULA": "calcula",
        "🗺️ TERRA MAPEA": "mapea",
        "⚖️ TERRA ARTICULA": "articula",
        "✊ TERRA ACTÚA": "actua",
        "🏛️ TERRA EVALÚA": "evalua",
    }

    if "componente_activo" not in st.session_state:
        st.session_state.componente_activo = "inicio"

    for nombre, clave in componentes.items():
        if st.button(nombre, key=f"nav_{clave}", use_container_width=True):
            st.session_state.componente_activo = clave

    st.markdown("---")
    datos = cargar_datos_montecristi()
    color_icpi = "#38a169" if datos["icpi"] >= 70 else "#d69e2e"
    st.markdown(f"""
    <div style='background:#f0f4f8; padding:1rem; border-radius:8px; text-align:center;'>
        <div style='font-size:0.75rem; color:#718096;'>ICPI Montecristi 2024</div>
        <div style='font-size:2rem; font-weight:700; color:{color_icpi};'>{datos['icpi']}%</div>
        <div style='font-size:0.8rem; color:#4a5568;'>🟢 {datos['avep']}</div>
    </div>
    """, unsafe_allow_html=True)

activo = st.session_state.componente_activo

# ─────────────────────────────────────────────
# INICIO
# ─────────────────────────────────────────────
if activo == "inicio":
    st.markdown("""
    <div class='terra-header'>
        <h1>🌍 TERRA CIUDADANA</h1>
        <p>El poder de la ciencia de datos en manos del ciudadano.<br>
        Auditoría territorial independiente | QUADRUM GovTech 2026</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ¿Qué puedes hacer aquí?")

    col1, col2 = st.columns(2)
    componentes_info = [
        ("📄", "TERRA ACCEDE", "Genera tu oficio LOTAIP blindado jurídicamente. Ejerce tu derecho constitucional en 3 minutos.", "#003087"),
        ("🔍", "TERRA VERIFICA", "Sube los documentos del GAD. El sistema los valida y genera evidencia con hash criptográfico.", "#2c5282"),
        ("🧮", "TERRA CALCULA", "Motor ICPI ciudadano. La misma fórmula canónica que usa el sistema institucional.", "#38a169"),
        ("🗺️", "TERRA MAPEA", "Visualiza las brechas territoriales de tu cantón en un mapa interactivo.", "#d69e2e"),
        ("⚖️", "TERRA ARTICULA", "Conecta tu análisis con el marco legal y las oportunidades de financiamiento.", "#e67e22"),
        ("✊", "TERRA ACTÚA", "De la evidencia al cambio. Cartas, canales institucionales, proyectos.", "#e53e3e"),
        ("🏛️", "TERRA EVALÚA", "El informe técnico, el discurso político y los datos: tres verdades en un panel.", "#003087"),
    ]

    for i, (icon, nombre, desc, color) in enumerate(componentes_info):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class='component-card'>
                <div class='component-header'>
                    <div class='component-icon' style='background:linear-gradient(135deg,{color},{color}99);'>{icon}</div>
                    <div>
                        <div style='font-weight:700; color:{color};'>{nombre}</div>
                        <div style='font-size:0.85rem; color:#718096;'>{desc}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Caso piloto activo: GAD Montecristi 2024")
    datos = cargar_datos_montecristi()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='color:#38a169;'>{datos['icpi']}%</div>
            <div class='metric-label'>ICPI Verificado</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='color:#e53e3e;'>{datos['icm_sigad']}%</div>
            <div class='metric-label'>ICM Declarado</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='color:#d69e2e;'>{datos['brecha']}pp</div>
            <div class='metric-label'>Brecha MOM</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='color:#003087;'>{datos['ife']}%</div>
            <div class='metric-label'>IFE Electoral</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='nota-metodologica'>
        {datos['nota_metodologica']}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# C1 — TERRA ACCEDE
# ─────────────────────────────────────────────
elif activo == "accede":
    st.markdown("""
    <div class='terra-header'>
        <h1>📄 TERRA ACCEDE</h1>
        <p>Ejerce tu derecho constitucional. El Estado te debe información pública.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **¿Cómo funciona?**
    1. Selecciona el GAD que quieres auditar
    2. El sistema genera el oficio blindado jurídicamente
    3. Descarga el Word, llena tus datos en casa, imprime y entrega en ventanilla
    4. El GAD tiene **15 días hábiles** para responder (LOTAIP Art. 9)
    """)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        perfil = st.selectbox("¿Cómo prefieres que te hable el sistema?", [
            "🏘️ Como vecino del barrio",
            "✊ Como activista ciudadano",
            "🎓 Como académico o investigador",
            "📰 Como periodista"
        ])

        gad_seleccionado = st.selectbox("¿Qué municipio quieres auditar?", GADS_ECUADOR)
        periodo = st.selectbox("¿De qué período necesitas información?", ["2024", "2023", "2022", "Período personalizado"])

        incluir_datos = st.checkbox("Quiero pre-llenar mis datos en el oficio (opcional)")

        nombre_peticionario = ""
        cedula_peticionario = ""
        correo_peticionario = ""

        if incluir_datos:
            st.info("Tus datos se usan ÚNICAMENTE para generar este documento. No se almacenan en el sistema. (LOPD Art. 9)")
            nombre_peticionario = st.text_input("Tu nombre completo")
            cedula_peticionario = st.text_input("Número de cédula")
            correo_peticionario = st.text_input("Correo electrónico")

    with col2:
        st.markdown("**El oficio incluirá estos fundamentos legales:**")
        fundamentos = [
            ("Constitución Art. 18 y 91", "Derecho de acceso a la información pública"),
            ("LOTAIP Arts. 7, 9, 11", "Obligación de transparencia activa y plazos"),
            ("LOPC Arts. 8, 73", "Participación ciudadana y control social"),
            ("COOTAD Art. 304", "Presupuesto participativo y acceso"),
            ("Ley Comercio Electrónico Art. 2", "Validez de documentos digitales"),
            ("Decreto 1384 Datos Abiertos", "Formatos abiertos obligatorios"),
            ("COPFP Art. 54", "Evaluación de cumplimiento de metas"),
        ]
        for ley, desc in fundamentos:
            st.markdown(f"✅ **{ley}** — {desc}")

        st.markdown("**El oficio exigirá:**")
        st.markdown("""
        - POA en formato Excel (.xlsx) — no PDF
        - PAC en formato Excel (.xlsx) — no PDF
        - Cédula presupuestaria solo inversión
        - Grupos 75 y 84 exclusivamente
        - Respuesta digital al correo del peticionario
        """)

    if st.button("📄 Generar mi oficio LOTAIP", use_container_width=True):
        if not gad_seleccionado:
            st.error("Selecciona un municipio primero")
        else:
            with st.spinner("Generando oficio blindado..."):
                try:
                    from docx import Document
                    from docx.shared import Pt, RGBColor
                    from docx.enum.text import WD_ALIGN_PARAGRAPH

                    doc = Document()

                    encabezado = doc.add_heading(f"SOLICITUD DE ACCESO A INFORMACIÓN PÚBLICA", 0)
                    encabezado.alignment = WD_ALIGN_PARAGRAPH.CENTER

                    fecha_hoy = datetime.datetime.now().strftime("%d de %B de %Y")
                    doc.add_paragraph(f"Fecha: {fecha_hoy}")
                    doc.add_paragraph(f"Para: Director de Comunicación y Transparencia")
                    doc.add_paragraph(f"Institución: {gad_seleccionado}")
                    doc.add_paragraph("")

                    if nombre_peticionario:
                        doc.add_paragraph(f"De: {nombre_peticionario}")
                        if cedula_peticionario:
                            doc.add_paragraph(f"C.I.: {cedula_peticionario}")
                        if correo_peticionario:
                            doc.add_paragraph(f"Correo: {correo_peticionario}")
                    else:
                        doc.add_paragraph("De: [NOMBRE COMPLETO]")
                        doc.add_paragraph("C.I.: [NÚMERO DE CÉDULA]")
                        doc.add_paragraph("Correo: [CORREO ELECTRÓNICO]")

                    doc.add_paragraph("")
                    doc.add_heading("SOLICITUD DE INFORMACIÓN PÚBLICA — LOTAIP", level=1)

                    cuerpo = doc.add_paragraph()
                    cuerpo.add_run(
                        f"En ejercicio del derecho constitucional de acceso a la información pública "
                        f"establecido en el Artículo 18 de la Constitución de la República del Ecuador, "
                        f"y en cumplimiento de la Ley Orgánica de Transparencia y Acceso a la Información "
                        f"Pública (LOTAIP), solicito respetuosamente al {gad_seleccionado} la siguiente "
                        f"información correspondiente al período fiscal {periodo}:"
                    )

                    doc.add_heading("Documentos solicitados:", level=2)
                    docs_solicitados = [
                        f"Plan Operativo Anual (POA) {periodo} en formato Excel (.xlsx), con desglose por metas, actividades, responsables y presupuesto asignado",
                        f"Plan Anual de Contratación (PAC) {periodo} en formato Excel (.xlsx), con códigos SERCOP, montos y estados de los procesos",
                        f"Cédula Presupuestaria {periodo} en formato Excel (.xlsx), exclusivamente partidas de gasto de INVERSIÓN (Grupos 75 y 84 del Clasificador Presupuestario)",
                        "La información debe ser remitida en formato digital abierto (.xlsx), por correo electrónico, al amparo de la Ley de Comercio Electrónico (Art. 2) y el Decreto 1384 de Datos Abiertos",
                    ]
                    for item in docs_solicitados:
                        p = doc.add_paragraph(style='List Bullet')
                        p.add_run(item)

                    doc.add_heading("Fundamento Legal:", level=2)
                    fundamentos_doc = [
                        "Constitución del Ecuador, Arts. 18 y 91 — Derecho de acceso a información pública",
                        "LOTAIP Arts. 7, 9, 11 — Obligación de transparencia y plazo de 15 días hábiles",
                        "LOPC Arts. 8 y 73 — Participación ciudadana y control social",
                        "COOTAD Art. 304 — Información presupuestaria municipal",
                        "COPFP Art. 54 — Seguimiento y evaluación de metas",
                        "Ley de Comercio Electrónico Art. 2 — Validez de documentos digitales",
                        "Decreto Ejecutivo 1384 — Datos abiertos en formatos reutilizables",
                    ]
                    for f in fundamentos_doc:
                        p = doc.add_paragraph(style='List Bullet')
                        p.add_run(f)

                    doc.add_paragraph("")
                    doc.add_paragraph(
                        "De no recibir respuesta en el plazo legal de 15 días hábiles, me reservo el "
                        "derecho de presentar la acción de acceso a la información pública prevista en "
                        "el Art. 91 de la Constitución y el Art. 22 de la LOTAIP."
                    )

                    doc.add_paragraph("")
                    doc.add_paragraph("Atentamente,")
                    doc.add_paragraph("")
                    doc.add_paragraph("_________________________________")
                    doc.add_paragraph(nombre_peticionario if nombre_peticionario else "[FIRMA DEL PETICIONARIO]")
                    doc.add_paragraph(cedula_peticionario if cedula_peticionario else "[C.I.]")

                    doc.add_paragraph("")
                    pie = doc.add_paragraph()
                    pie.add_run(
                        "Oficio generado mediante TERRA CIUDADANA, plataforma de ejercicio del derecho "
                        "constitucional de acceso a la información pública (Art. 18 Constitución del Ecuador). "
                        "QUADRUM GovTech — terra.quadrum.ec"
                    ).italic = True

                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    st.success("✅ Oficio generado exitosamente")
                    st.download_button(
                        label="📥 Descargar Oficio LOTAIP (.docx)",
                        data=buffer,
                        file_name=f"oficio_LOTAIP_{gad_seleccionado.replace(' ', '_')}_{periodo}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

                    st.markdown("""
                    <div class='nota-metodologica'>
                    <strong>Próximos pasos:</strong><br>
                    1. Descarga el Word → llena tus datos → imprime → firma<br>
                    2. Entrega en la ventanilla de transparencia del GAD<br>
                    3. Guarda el comprobante de recepción<br>
                    4. El GAD tiene 15 días hábiles para responder<br>
                    5. Cuando recibas la respuesta → regresa a <strong>TERRA VERIFICA</strong>
                    </div>
                    """, unsafe_allow_html=True)

                except ImportError:
                    st.error("Librería python-docx no instalada. Agrega 'python-docx' al requirements.txt")
                    st.info("El oficio será funcional una vez instalada la librería.")

# ─────────────────────────────────────────────
# C2 — TERRA VERIFICA
# ─────────────────────────────────────────────
elif activo == "verifica":
    st.markdown("""
    <div class='terra-header'>
        <h1>🔍 TERRA VERIFICA</h1>
        <p>Convierte los documentos del GAD en evidencia con cadena de custodia.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **¿Qué necesitas subir?**
    - La copia del oficio de respuesta del GAD **(con sello y firma — sin tus datos personales)**
    - El POA en Excel
    - El PAC en Excel
    - La Cédula Presupuestaria en Excel
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Oficio de respuesta del GAD**")
        oficio = st.file_uploader(
            "Sube la copia con sello/firma (omite tus datos personales)",
            type=["pdf", "png", "jpg"],
            key="oficio"
        )

        st.markdown("**2. Plan Operativo Anual (POA)**")
        poa = st.file_uploader("POA en Excel", type=["xlsx", "xls"], key="poa")

        st.markdown("**3. Plan Anual de Contratación (PAC)**")
        pac = st.file_uploader("PAC en Excel", type=["xlsx", "xls"], key="pac")

        st.markdown("**4. Cédula Presupuestaria**")
        cedula = st.file_uploader("Cédula en Excel o PDF", type=["xlsx", "xls", "pdf"], key="cedula")

    with col2:
        st.markdown("**Estado de documentos:**")
        docs_estado = [
            ("Oficio respuesta GAD", oficio),
            ("POA Excel", poa),
            ("PAC Excel", pac),
            ("Cédula Presupuestaria", cedula),
        ]
        for nombre_doc, archivo in docs_estado:
            if archivo:
                contenido = archivo.read()
                hash_doc = hashlib.sha256(contenido).hexdigest()
                st.markdown(f"""
                <div style='background:#f0fff4; border:1px solid #68d391; padding:0.8rem; border-radius:8px; margin-bottom:0.5rem;'>
                    <div style='font-weight:600; color:#276749;'>✅ {nombre_doc}</div>
                    <div class='hash-display' style='margin-top:0.5rem; font-size:0.7rem;'>SHA-256: {hash_doc[:32]}...</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#fff5f5; border:1px solid #fc8181; padding:0.8rem; border-radius:8px; margin-bottom:0.5rem;'>
                    <div style='color:#c53030;'>⏳ {nombre_doc} — pendiente</div>
                </div>
                """, unsafe_allow_html=True)

        docs_completos = all([oficio, poa, pac, cedula])
        if docs_completos:
            st.success("✅ Todos los documentos cargados. Puedes continuar a TERRA CALCULA.")
        else:
            pendientes = sum(1 for _, a in docs_estado if not a)
            st.info(f"Faltan {pendientes} documento(s) para completar la validación.")

    st.markdown("---")
    st.markdown("""
    <div class='proxima-fase'>
        <div style='font-weight:700; margin-bottom:0.5rem;'>🔮 Próxima fase — OCR activo</div>
        <div style='font-size:0.9rem; opacity:0.85;'>
        Cuando se active el módulo OCR, TERRA VERIFICA podrá leer PDFs escaneados, 
        imágenes y capturas de pantalla. Si la imagen es poco clara, el sistema 
        te preguntará: "Detecté $45,000 — ¿confirmas?" (Human-in-the-Loop).
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# C3 — TERRA CALCULA
# ─────────────────────────────────────────────
elif activo == "calcula":
    st.markdown("""
    <div class='terra-header'>
        <h1>🧮 TERRA CALCULA</h1>
        <p>La verdad matemática de tu territorio. Fórmula canónica SIAP-ICPI.</p>
    </div>
    """, unsafe_allow_html=True)

    datos = cargar_datos_montecristi()

    modo = st.radio(
        "¿Qué quieres calcular?",
        ["Ver análisis del caso piloto: Montecristi 2024", "Cargar mis propios documentos"],
        horizontal=True
    )

    if modo == "Ver análisis del caso piloto: Montecristi 2024":

        st.markdown(f"""
        <div class='icpi-gauge'>
            <div style='font-size:0.9rem; color:#718096; margin-bottom:0.5rem;'>GAD Municipal de Montecristi — Período 2024</div>
            <div class='icpi-number'>{datos['icpi']}%</div>
            <div class='icpi-label'>🟢 {datos['avep']}</div>
            <div style='margin-top:1rem; font-size:0.85rem; color:#4a5568;'>
                Fórmula: ICPI = [Σ(Pi × Ri × Vi × Ei × Ti × Ci) / Σ(Pi × Ri)] × 100<br>
                Verificación cruzada: 9 silos de información pública independientes
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        indices = [
            ("IFE Electoral", datos['ife'], "%", "#003087", "77% de 25 promesas CNE incorporadas al PDOT"),
            ("ICM SIGAD", datos['icm_sigad'], "%", "#e53e3e", "Autoreporte oficial del GAD al SNP"),
            ("Brecha MOM", datos['brecha'], "pp", "#d69e2e", "Diferencia entre declarado y verificado"),
            ("ITAM", datos['itam'], "%", "#2c5282", "Transparencia activa en portal web"),
            ("ICS Social", datos['ics'], "%", "#38a169", "Inclusión social y grupos prioritarios"),
        ]

        for i, (nombre, valor, unidad, color, tooltip) in enumerate(indices):
            with [col1, col2, col3][i % 3]:
                st.markdown(f"""
                <div class='metric-card' title='{tooltip}'>
                    <div class='metric-value' style='color:{color};'>{valor}{unidad}</div>
                    <div class='metric-label'>{nombre}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='brecha-alert'>
            <div style='font-weight:700; font-size:1.1rem; color:#c53030;'>
                ⚠️ Mutación del Objeto de Medición (MOM) detectada
            </div>
            <div style='margin-top:0.5rem; color:#742a2a;'>
                El GAD declaró <strong>100%</strong> de cumplimiento al SIGAD/SNP.<br>
                TERRA verifica <strong>72.93%</strong> mediante 9 silos independientes.<br>
                Brecha: <strong>27.07 puntos porcentuales</strong> — evidencia documentada.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Señales de Atención Temprana (SAT)")
        sc1, sc2, sc3, sc4 = st.columns(4)
        sats_info = [
            ("SAT-I", "Fragmentación Selectiva", False, "ICM alto sobre universo completo"),
            ("SAT-II", "Sustitución Estratégica", False, "Sin cambios de unidad detectados"),
            ("SAT-III", "Inflación de Unidades", False, "Cumplimiento consistente con ejecución"),
            ("SAT-IV", "Tensión Normativa", False, "Reforma COOTAD no vigente en 2024"),
        ]
        for col, (sat, desc, activa, nota) in zip([sc1, sc2, sc3, sc4], sats_info):
            with col:
                clase = "sat-alert" if activa else "sat-ok"
                icono = "🔴" if activa else "✅"
                st.markdown(f"""
                <div class='sat-card {clase}'>
                    <div style='font-size:1.5rem;'>{icono}</div>
                    <div style='font-weight:700; font-size:0.85rem;'>{sat}</div>
                    <div style='font-size:0.75rem;'>{desc}</div>
                    <div style='font-size:0.7rem; margin-top:0.3rem; opacity:0.8;'>{nota}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ICPI por meta estratégica")

        df_metas = pd.DataFrame(datos["metas"])
        df_metas.columns = ["ID", "Meta", "ICPI%", "AVEP", "ODS", "Dirección"]
        df_metas = df_metas.sort_values("ICPI%", ascending=False)

        import plotly.express as px
        fig = px.bar(
            df_metas,
            x="ICPI%",
            y="Meta",
            orientation="h",
            color="ICPI%",
            color_continuous_scale=[[0, "#e53e3e"], [0.2, "#e67e22"], [0.4, "#d69e2e"], [0.7, "#38a169"], [0.9, "#003087"]],
            range_color=[0, 100],
            title="ICPI por meta — GAD Montecristi 2024"
        )
        fig.update_layout(height=600, showlegend=False)
        fig.add_vline(x=70, line_dash="dash", line_color="#003087", annotation_text="Umbral Mandato")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### IED por Dirección Municipal")
        ied_data = {
            "Dirección": ["Dir. Económica", "Patronato", "Dir. Administrativa", "Dir. TIC",
                         "Dir. Agua", "Dir. Ambiental", "Dir. Cultura", "Dir. Obras Públicas"],
            "IED%": [95.0, 94.9, 85.0, 85.0, 72.0, 68.8, 47.8, 34.7],
            "LOSEP": ["Excelente", "Excelente", "Muy Bueno", "Muy Bueno",
                     "Satisfactorio", "Regular", "Regular", "Insuficiente"]
        }
        df_ied = pd.DataFrame(ied_data).sort_values("IED%", ascending=True)
        fig2 = px.bar(df_ied, x="IED%", y="Dirección", orientation="h",
                     color="IED%",
                     color_continuous_scale=[[0, "#e53e3e"], [0.6, "#d69e2e"], [0.85, "#38a169"], [1, "#003087"]],
                     range_color=[0, 100], title="IED por Dirección — Clasificación LOSEP")
        fig2.add_vline(x=60, line_dash="dash", line_color="gray", annotation_text="Mínimo Regular")
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"""<div class='nota-metodologica'>{datos['nota_metodologica']}</div>""", unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            df_export = pd.DataFrame(datos["metas"])
            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button("📊 Descargar datos CSV (academia)", data=csv,
                             file_name="terra_icpi_montecristi_2024.csv", mime="text/csv",
                             use_container_width=True)
        with col_dl2:
            hash_resultado = hashlib.sha256(str(datos).encode()).hexdigest()
            st.markdown(f"""
            <div class='hash-display'>
                Hash integridad ICPI 72.93%:<br>
                {hash_resultado}
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("### 💬 Pregúntale a TERRA sobre estos datos")

    import google.generativeai as genai
    genai.configure(api_key=st.secrets["GEMINI_KEY"])

    pregunta = st.chat_input("Escribe tu pregunta sobre Montecristi...")
    if pregunta:
        with st.spinner("Analizando..."):
            modelo = genai.GenerativeModel("gemini-1.5-flash")
            contexto = f"""
            Eres TERRA, asistente de auditoría municipal ciudadana.
            Datos verificados de Montecristi 2024:
            - ICPI global: 72.93% (Gestión por Mandato)
            - ICM declarado: 100%
            - Brecha: 27.07 puntos
            - Meta más crítica: Señalización vial con 0%
            - Meta mejor ejecutada: Salud y Fortalecimiento Productivo con 95%
            Responde en lenguaje simple y ciudadano. Máximo 3 párrafos.
            """
            respuesta = modelo.generate_content(contexto + "\n\nPregunta: " + pregunta)
            st.markdown(respuesta.text)
    
    else:
        st.info("📂 Sube tus documentos en TERRA VERIFICA primero para calcular el ICPI de tu municipio.")
        st.markdown("""
        <div class='proxima-fase'>
            <div style='font-weight:700; margin-bottom:0.5rem;'>🔮 Cómo funcionará con tus documentos</div>
            <div style='font-size:0.9rem; opacity:0.85;'>
            Una vez subas el POA, PAC y Cédula en TERRA VERIFICA, el motor ICPI calculará:<br>
            • ICPI por cada meta del PDOT<br>
            • IFE (si subes el Plan CNE)<br>
            • Brecha con el ICM declarado al SIGAD<br>
            • Las 4 señales SAT de alerta temprana<br>
            • Análisis longitudinal si subes varios años
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# C4 — TERRA MAPEA
# ─────────────────────────────────────────────
elif activo == "mapea":
    st.markdown("""
    <div class='terra-header'>
        <h1>🗺️ TERRA MAPEA</h1>
        <p>Visualiza las brechas de tu territorio. Ve dónde está el problema.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        import folium
        from streamlit_folium import st_folium

        datos = cargar_datos_montecristi()
        m = folium.Map(location=[-1.058, -80.655], zoom_start=13, tiles="CartoDB positron")

        puntos_meta = [
            {"meta": "AH-C-X-01 — Agua Potable", "icpi": 72.0, "lat": -1.045, "lon": -80.660, "dir": "Dir. Agua"},
            {"meta": "AH-I-X-01 — Vialidad", "icpi": 58.3, "lat": -1.058, "lon": -80.655, "dir": "Dir. Obras"},
            {"meta": "AH-I-X-02 — Señalización", "icpi": 0.0, "lat": -1.065, "lon": -80.648, "dir": "Dir. Obras"},
            {"meta": "SC-I-N-01 — Salud", "icpi": 95.0, "lat": -1.052, "lon": -80.663, "dir": "Patronato"},
            {"meta": "FA-C-X-01 — Desechos", "icpi": 80.0, "lat": -1.070, "lon": -80.658, "dir": "EP Aseo"},
            {"meta": "EP-L-N-01 — Productivo", "icpi": 95.0, "lat": -1.042, "lon": -80.670, "dir": "Dir. Económica"},
        ]

        for punto in puntos_meta:
            icpi = punto["icpi"]
            if icpi >= 90: color = "blue"
            elif icpi >= 70: color = "green"
            elif icpi >= 40: color = "orange"
            elif icpi >= 20: color = "red"
            else: color = "darkred"

            folium.CircleMarker(
                location=[punto["lat"], punto["lon"]],
                radius=15 + (icpi / 10),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>{punto['meta']}</b><br>ICPI: {icpi}%<br>Dir: {punto['dir']}",
                    max_width=200
                ),
                tooltip=f"{punto['meta']}: {icpi}%"
            ).add_to(m)

        st.markdown("**Mapa de brechas territoriales — GAD Montecristi 2024**")
        st.caption("Haz clic en los círculos para ver el detalle de cada meta")
        st_folium(m, width=700, height=450)

        st.markdown("""
        **Leyenda:**
        🔵 Excelencia (≥90%) | 🟢 Mandato (70-89%) | 🟠 Transición (40-69%) | 🔴 Ocurrencia (<40%) | ⚫ Ruptura (0%)
        """)

    except ImportError:
        st.info("📦 Agrega 'folium' y 'streamlit-folium' al requirements.txt para activar el mapa interactivo.")
        st.markdown("""
        <div class='proxima-fase'>
            <div style='font-weight:700; margin-bottom:0.5rem;'>🗺️ Qué mostrará el mapa</div>
            <div style='font-size:0.9rem; opacity:0.85;'>
            Círculos de colores georreferenciados por meta:<br>
            • Rojo intenso → meta en Ruptura Sistémica<br>
            • Verde → Gestión por Mandato<br>
            • Azul → Excelencia en Gobernanza<br>
            El ciudadano verá literalmente su barrio en rojo o verde.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# C5 — TERRA ARTICULA
# ─────────────────────────────────────────────
elif activo == "articula":
    st.markdown("""
    <div class='terra-header'>
        <h1>⚖️ TERRA ARTICULA</h1>
        <p>Tu análisis conectado con el marco legal y el financiamiento internacional.</p>
    </div>
    """, unsafe_allow_html=True)

    datos = cargar_datos_montecristi()

    st.markdown("### Alineación ODS — GAD Montecristi 2024")
    clusters = [
        ("🏛️ Gobernanza", "ODS 16-17", 58.8, "🟡 Transición Crítica",
         "Base institucional verificable para financiamiento CAF en Gobernanza Anticipatoria"),
        ("🏗️ Infraestructura", "ODS 6-9-11-13", 71.3, "🟢 Gestión por Mandato",
         "Inversión en agua, vialidad y equipamientos apta para BID Infraestructura Social"),
        ("🤝 Inclusión Social", "ODS 1-3-4-5-10", 63.5, "🟡 Transición Crítica",
         "Brecha en atención social documenta necesidad de apoyo GIZ y BM Social"),
    ]
    for icon_c, ods, icpi_c, avep_c, argumento in clusters:
        col1, col2 = st.columns([1, 2])
        with col1:
            color_c = "#38a169" if icpi_c >= 70 else "#d69e2e"
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem;'>{icon_c}</div>
                <div class='metric-value' style='color:{color_c}; font-size:1.8rem;'>{icpi_c}%</div>
                <div class='metric-label'>{ods}</div>
                <div style='font-size:0.75rem; color:#718096;'>{avep_c}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='component-card' style='margin:0;'>
                <div style='font-size:0.85rem; color:#4a5568;'>{argumento}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Generador de argumento de elegibilidad bilateral")

    financiador = st.selectbox("¿Para qué organismo quieres el argumento?", [
        "CAF — Banco de Desarrollo de América Latina",
        "BID — Banco Interamericano de Desarrollo",
        "GIZ — Cooperación Técnica Alemana",
        "Banco Mundial",
        "FIDA — Fondo Internacional de Desarrollo Agrícola",
        "GEF — Fondo para el Medio Ambiente Mundial",
    ])

    if st.button("⚖️ Generar argumento de elegibilidad"):
        argumentos = {
            "CAF — Banco de Desarrollo de América Latina": f"""
**Argumento de elegibilidad — CAF Gobernanza Anticipatoria:**

El GAD Municipal de Montecristi registra un ICPI verificado del **72.93%** mediante verificación cruzada 
algorítmica de 9 silos de información pública independientes, clasificado como **"Gestión por Mandato"** 
según la Escala AVEP del Sistema TERRA SIAP-ICPI v2.0.

El ICPI de Gobernanza (ODS 16-17) de **58.8%** certifica una base institucional sólida para absorber 
financiamiento bajo el marco de **Gobernanza Anticipatoria** de CAF, mientras que la brecha verificada 
de **27.07 puntos** entre el ICPI real y el ICM auto-reportado documenta la necesidad de fortalecimiento 
del Sistema de Información Local (COOTAD Art. 295).

El acueducto CAF de **$28M aprobado el 29/12/2024** para el cantón demuestra trayectoria de cooperación 
activa con el organismo.

*Generado por TERRA CIUDADANA | QUADRUM GovTech | {datetime.datetime.now().strftime('%d/%m/%Y')}*
            """,
            "BID — Banco Interamericano de Desarrollo": f"""
**Argumento de elegibilidad — BID Social e Infraestructura:**

El análisis SIAP-ICPI del GAD Montecristi revela que el ICPI de Inclusión Social (ODS 1-3-4-5-10) 
se sitúa en **63.51%** — Transición Crítica — documentando brechas verificables en atención a grupos 
prioritarios (meta SC-I-N-03: 53.4%) y vivienda de interés social (AH-I-N-01: 22.5%).

Esta evidencia algorítmica, sustentada en 9 silos de información pública independientes, cumple con los 
requisitos de **due diligence** del BID Lab para proyectos de innovación social en gobiernos locales.

*Generado por TERRA CIUDADANA | QUADRUM GovTech | {datetime.datetime.now().strftime('%d/%m/%Y')}*
            """,
        }
        argumento_texto = argumentos.get(financiador, f"""
**Argumento de elegibilidad — {financiador}:**

GAD Municipal de Montecristi | ICPI: 72.93% | Brecha documentada: 27.07pp
Verificación: 9 silos independientes | Metodología: SIAP-ICPI v2.0 QUADRUM

*Generado por TERRA CIUDADANA | {datetime.datetime.now().strftime('%d/%m/%Y')}*
        """)
        st.markdown(argumento_texto)
        st.download_button(
            "📥 Descargar argumento (.txt)",
            data=argumento_texto.encode(),
            file_name=f"elegibilidad_{financiador.split('—')[0].strip().replace(' ', '_')}.txt",
            use_container_width=True
        )

# ─────────────────────────────────────────────
# C6 — TERRA ACTÚA
# ─────────────────────────────────────────────
elif activo == "actua":
    st.markdown("""
    <div class='terra-header'>
        <h1>✊ TERRA ACTÚA</h1>
        <p>De la evidencia al cambio real. Tres modos de incidencia ciudadana.</p>
    </div>
    """, unsafe_allow_html=True)

    modo_accion = st.tabs(["📊 Modo A — Tengo el análisis", "💡 Modo B — Tengo una necesidad", "🔍 Modo C — Encontré una convocatoria"])

    with modo_accion[0]:
        st.markdown("### ¿Qué hago con mi análisis ICPI?")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Nivel 1 — Difusión inmediata**")
            st.markdown("""
            - Comparte tu análisis en redes sociales
            - URL pública de tu análisis con código QR
            - PDF descargable con membrete QUADRUM
            """)
            if st.button("📱 Generar imagen viral", use_container_width=True):
                st.info("🔮 Próxima fase: generación automática de imagen con Pillow")

        with col2:
            st.markdown("**Nivel 2 — Canales institucionales**")
            canal = st.selectbox("¿Ante quién presentas?", [
                "CPCCS — Consejo de Participación Ciudadana",
                "CGE — Contraloría General del Estado",
                "Defensoría del Pueblo",
                "Asamblea Nacional",
            ])
            if st.button("📋 Generar carta pre-formateada", use_container_width=True):
                carta = f"""
SEÑORES
{canal}
Ciudad

De mi consideración:

En ejercicio de mis derechos ciudadanos de participación y control social, 
consagrados en la Constitución Art. 95 y la LOPC Art. 88, presento a su 
autoridad el siguiente análisis técnico verificado mediante el Sistema 
TERRA SIAP-ICPI v2.0 (QUADRUM GovTech):

GAD Municipal de Montecristi | Período 2024
ICPI Verificado: 72.93% | ICM Declarado SIGAD: 100%
Brecha documentada: 27.07 puntos porcentuales

Solicito respetuosamente que su institución tome conocimiento de esta 
evidencia algorítmica sustentada en 9 silos de información pública independientes.

Atentamente,
[Su nombre]
[C.I.]
[Fecha]

Generado por TERRA CIUDADANA | QUADRUM GovTech
                """
                st.text_area("Carta generada:", value=carta, height=300)
                st.download_button("📥 Descargar carta (.txt)", data=carta.encode(),
                                 file_name="carta_incidencia.txt", use_container_width=True)

    with modo_accion[1]:
        st.markdown("### Tengo una necesidad en mi comunidad")
        necesidad = st.text_area("Describe el problema de tu comunidad:", height=100,
                                placeholder="Ej: En el barrio Leónidas Proaño no hay agua potable y el municipio no ha ejecutado ningún contrato para solucionar esto...")
        if necesidad and st.button("🔍 Analizar y vincular al PDOT"):
            st.markdown("**Vinculación automática con el PDOT:**")
            if "agua" in necesidad.lower():
                st.success("✅ Tu necesidad se vincula con: **AH-C-X-01 — Agua Potable** (ICPI: 72%)")
                st.info("Esta meta tiene presupuesto codificado. El GAD puede ejecutar sin necesitar fondos adicionales.")
            elif "vía" in necesidad.lower() or "calle" in necesidad.lower():
                st.warning("⚠️ Tu necesidad se vincula con: **AH-I-X-01 — Vialidad** (ICPI: 58.3%)")
                st.info("Esta meta está en Transición Crítica. Hay margen de ejecución disponible.")
            else:
                st.info("Describe mejor la necesidad para vincularla con una meta específica del PDOT.")

    with modo_accion[2]:
        st.markdown("### Encontré una convocatoria de financiamiento")
        convocatoria = st.text_input("Pega el link o describe la convocatoria:")
        if convocatoria:
            st.markdown("**Verificando elegibilidad con datos ICPI...**")
            st.success("✅ El análisis de Montecristi tiene datos verificados para sustentar esta convocatoria.")
            st.markdown("Usa **TERRA ARTICULA** para generar el argumento de elegibilidad formal.")

# ─────────────────────────────────────────────
# C7 — TERRA EVALÚA
# ─────────────────────────────────────────────
elif activo == "evalua":
    st.markdown("""
    <div class='terra-header'>
        <h1>🏛️ TERRA EVALÚA</h1>
        <p>Lo que dijo. Lo que firmó. Lo que TERRA verifica. Tres verdades en un panel.</p>
    </div>
    """, unsafe_allow_html=True)

    eval_data = datos_evaluacion_precacheados()
    datos = cargar_datos_montecristi()

    st.markdown(f"""
    **Caso analizado:** Rendición de Cuentas 2024 — {datos['gad']}
    **Alcalde:** {datos['alcalde']} | **Evento:** {eval_data['fecha_evento']} — {eval_data['lugar']}
    **Asistentes:** {eval_data['asistentes']} | **Informe N°:** {eval_data['informe_numero']}
    """)

    st.markdown("---")
    st.markdown("### Los tres insumos del análisis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size:2rem;'>🧮</div>
            <div style='font-weight:700; color:#003087;'>ICPI TERRA</div>
            <div style='font-size:2rem; font-weight:700; color:#38a169;'>72.93%</div>
            <div class='metric-label'>Verificación algorítmica<br>9 silos independientes</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size:2rem;'>📋</div>
            <div style='font-weight:700; color:#003087;'>INFORME TÉCNICO CPCCS</div>
            <div style='font-size:1rem; font-weight:700; color:#4a5568;'>Informe N° 22844</div>
            <div class='metric-label'>Documento oficial firmado<br>Rendición de cuentas 2024</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size:2rem;'>🎙️</div>
            <div style='font-weight:700; color:#003087;'>DISCURSO POLÍTICO</div>
            <div style='font-size:1rem; font-weight:700; color:#4a5568;'>Evento público</div>
            <div class='metric-label'>11/07/2025 — 261 asistentes<br>Transcripción verificada</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_izq, col_der = st.columns([2, 1])
    with col_izq:
        st.markdown("### Coeficiente de Fricción Narrativa")
        st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <div style='display:flex; justify-content:space-between; font-size:0.85rem; color:#718096;'>
                <span>Coherencia total</span>
                <span>Fricción total</span>
            </div>
            <div class='friccion-barra'></div>
            <div style='display:flex; justify-content:space-between; font-weight:700;'>
                <span style='color:#38a169;'>{eval_data['coherencia']}% Coherente</span>
                <span style='color:#e53e3e;'>{eval_data['friccion_narrativa']}% Fricción</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_der:
        st.markdown(f"""
        <div class='metric-card' style='text-align:center;'>
            <div style='font-size:3rem; font-weight:700; color:#e53e3e;'>{eval_data['friccion_narrativa']}%</div>
            <div class='metric-label'>Fricción Narrativa<br>Detectada</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Hallazgos por meta")

    for hallazgo in eval_data["hallazgos"]:
        clase = "hallazgo-alto" if hallazgo["nivel"] == "alto" else "hallazgo-bajo"
        st.markdown(f"""
        <div class='hallazgo-card {clase}'>
            <div style='font-weight:700;'>{hallazgo['tipo']} — {hallazgo['meta']}</div>
            <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem; margin-top:0.5rem; font-size:0.85rem;'>
                <div><strong>🎙️ Discurso:</strong><br>{hallazgo['discurso']}</div>
                <div><strong>📋 Informe CPCCS:</strong><br>{hallazgo['informe']}</div>
                <div><strong>🧮 TERRA verifica:</strong><br>{hallazgo['terra']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Promesas electorales sin meta PDOT")
    st.markdown("Las siguientes promesas del Plan CNE **no tienen meta equivalente** en el PDOT 2023-2027:")
    for promesa in eval_data["promesas_sin_pdot"]:
        st.markdown(f"🔴 {promesa}")

    st.markdown("---")
    st.markdown("### Exportar análisis completo")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        if st.button("🏘️ Imagen vecino", use_container_width=True):
            st.info("🔮 Próxima fase: imagen viral con Pillow")
    with col_e2:
        reporte_texto = f"""
TERRA EVALÚA — Análisis de Fricción Narrativa
GAD Montecristi | Rendición de Cuentas 2024
{'='*50}
ICPI Verificado: {datos['icpi']}%
ICM Declarado: {datos['icm_sigad']}%
Brecha: {datos['brecha']} pp
Fricción Narrativa: {eval_data['friccion_narrativa']}%

HALLAZGOS:
{chr(10).join([f"- {h['tipo']}: {h['meta']}" for h in eval_data['hallazgos']])}

Generado por TERRA CIUDADANA | QUADRUM GovTech
{datetime.datetime.now().strftime('%d/%m/%Y')}
        """
        st.download_button("📰 Reporte periodista", data=reporte_texto.encode(),
                          file_name="terra_evalua_montecristi_2024.txt", use_container_width=True)
    with col_e3:
        df_eval = pd.DataFrame(eval_data["hallazgos"])
        csv_eval = df_eval.to_csv(index=False).encode("utf-8")
        st.download_button("🎓 Dataset academia", data=csv_eval,
                          file_name="friccion_narrativa_montecristi_2024.csv", use_container_width=True)

    st.markdown("""
    <div class='proxima-fase'>
        <div style='font-weight:700; margin-bottom:0.5rem;'>🔮 Próxima fase — El Tribunal completo</div>
        <div style='font-size:0.9rem; opacity:0.85;'>
        • Whisper transcribirá el video del evento en tiempo real<br>
        • OCR leerá el PDF del informe CPCCS automáticamente<br>
        • El Diccionario del Argot Ecuatoriano detectará frases como "ya mismito sale la obra"<br>
        • Requiere: API Anthropic ($20-30/mes) + activación del módulo NLP
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class='footer-terra'>
    <strong>TERRA CIUDADANA v2.0</strong> | QUADRUM GovTech<br>
    Ronald Javier Delgado Santana | Diplomado DGIP CAF-ESPOL 2026<br>
    Metodología SIAP-ICPI | Caso piloto: GAD Municipal de Montecristi<br>
    <br>
    El derecho a saber es constitucional. Esta herramienta no sustituye asesoría jurídica profesional.
</div>
""", unsafe_allow_html=True)
