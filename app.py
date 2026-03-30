if uploaded_file is not None:
    try:
        # 1. Leer el CSV sin forzar encabezados y tratando todo como texto
        df = pd.read_csv(uploaded_file, header=None, dtype=str)
        st.success("✅ ¡Archivo cargado correctamente!")

        # Mostrar los datos crudos
        with st.expander("Ver datos originales"):
            st.dataframe(df)

        # --- KPIs Principales ---
        st.header("📈 Indicadores Clave de Acción Ciudadana")
        
        # 2. Búsqueda dinámica para evitar el IndexError
        # Validamos que el archivo tenga datos antes de procesar
        if len(df) > 0:
            # Buscamos en qué fila se encuentra la palabra "IFE" (el título de tus KPIs en H24)
            # asumiendo que está en la primera columna (índice 0)
            fila_titulos_kpi = df[df[0].astype(str).str.contains("IFE", na=False)].index
            
            if len(fila_titulos_kpi) > 0:
                # Tomamos el índice de la fila de los títulos
                idx_titulos = fila_titulos_kpi[0]
                
                # La fila con los valores numéricos está exactamente debajo (+1)
                kpi_row = df.iloc[idx_titulos + 1] 
                
                # Desplegamos las métricas (Ajusta los índices [0], [3], [6], [9] según tus comas)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Fidelidad Electoral (IFE)", str(kpi_row[0]))
                col2.metric("Rendición de Cuentas", str(kpi_row[3]))
                col3.metric("Control Social (SSC)", str(kpi_row[6]))
                col4.metric("Transparencia LOTAIP", str(kpi_row[9]))
            else:
                st.warning("⚠️ No se encontró la sección de Indicadores (IFE) en el CSV.")
        else:
            st.error("⚠️ El archivo está vacío o no se pudo leer correctamente.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
