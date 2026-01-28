import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# Configuración de página con icono de banco
st.set_page_config(page_title="Scanner 606 Pro RD", layout="wide", page_icon="🏦")

# Diseño Premium con CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #003366; color: white; border-radius: 8px; font-weight: bold; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Título con estilo
st.title("🏦 Scanner 606 Inteligente")
st.caption("Solución Profesional para Reportes de Gastos DGII")
st.divider()

# Validación de API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Configura la API Key en los Secrets de Streamlit.")

# Sidebar informativa
with st.sidebar:
    st.header("⚙️ Panel de Control")
    periodo = st.text_input("Periodo Fiscal (AAAAMM)", value="202601")
    st.info("Sube las fotos de tus facturas y la IA extraerá los datos automáticamente para el formato 606.")

# Subida de archivos
archivos = st.file_uploader("Arrastra aquí tus facturas", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if archivos:
    if st.button(f"🔍 Procesar {len(archivos)} Factura(s)"):
        resultados = []
        progreso = st.progress(0)
        
        for i, archivo in enumerate(archivos):
            try:
                img = Image.open(archivo)
                # EL ARREGLO ESTÁ AQUÍ: 'gemini-1.5-flash-latest'
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                prompt = "Extrae de esta factura dominicana: RNC emisor, NCF, Día (2 dígitos), Monto Total. Responde estrictamente: RNC|NCF|DIA|MONTO"
                
                response = model.generate_content([prompt, img])
                datos = response.text.strip().split('|')
                
                if len(datos) >= 4:
                    rnc_e, ncf_e, dia_e, monto_e = [d.strip() for d in datos[:4]]
                    fecha = f"{periodo}{dia_e.zfill(2)}"
                    # Línea formato 606 DGII
                    linea = f"{rnc_e}|1|02|{ncf_e}||{fecha}||{monto_e}|0.00|{monto_e}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                    resultados.append({"RNC": rnc_e, "NCF": ncf_e, "Monto": monto_e, "Linea": linea})
            except Exception as e:
                st.error(f"Error en {archivo.name}: Verifique la nitidez de la imagen.")
            
            progreso.progress((i + 1) / len(archivos))

        if resultados:
            st.success("🎉 ¡Extracción exitosa!")
            df = pd.DataFrame(resultados)
            
            # Mostrar tabla elegante
            st.subheader("📋 Datos Extraídos")
            st.dataframe(df[["RNC", "NCF", "Monto"]], use_container_width=True)
            
            # Botón de descarga TXT
            txt_data = "\n".join(df["Linea"].tolist())
            st.download_button(
                label="📥 Descargar TXT para DGII",
                data=txt_data,
                file_name=f"606_{periodo}.txt",
                mime="text/plain"
            )
