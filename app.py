import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import re

# 1. Configuración de la página
st.set_page_config(page_title="Scanner 606 Pro RD", layout="wide", page_icon="🏦")

# Estilo visual profesional
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .stButton>button { background-color: #002d5a; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .main-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Configuración de la IA
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets de Streamlit.")

st.title("🏦 Scanner 606 Inteligente")
st.write("Carga tus facturas y genera el reporte TXT para la DGII de forma automática.")

# 3. Sidebar
with st.sidebar:
    st.header("Configuración")
    periodo = st.text_input("Periodo (AAAAMM)", value="202601")
    st.divider()
    st.info("Esta herramienta usa Inteligencia Artificial para extraer RNC, NCF y montos.")

# 4. Carga de archivos
archivos = st.file_uploader("Subir imágenes de facturas", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if archivos:
    if st.button(f"🚀 PROCESAR {len(archivos)} FACTURA(S)"):
        resultados = []
        progreso = st.progress(0)
        
        # Usamos el modelo estable Pro para evitar errores de versión
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        for i, archivo in enumerate(archivos):
            try:
                img = Image.open(archivo)
                
                prompt = """Eres un experto contable dominicano. Analiza esta factura y extrae:
                - RNC Emisor (solo números)
                - NCF (debe empezar con B01, B02, B11, etc.)
                - Día (2 dígitos)
                - Monto Total (solo números, sin comas)
                Responde únicamente en este formato exacto: RNC|NCF|DIA|MONTO"""
                
                response = model.generate_content([prompt, img])
                texto_respuesta = response.text.strip()
                
                # Limpiar la respuesta por si la IA agrega texto extra
                match = re.search(r'(\d+)\|(B\d+)\|(\d+)\|([\d\.]+)', texto_respuesta)
                
                if match:
                    rnc_e = match.group(1)
                    ncf_e = match.group(2)
                    dia_e = match.group(3).zfill(2)
                    monto_e = match.group(4)
                else:
                    # Intento de dividir si no hay match perfecto
                    partes = texto_respuesta.split('|')
                    rnc_e, ncf_e, dia_e, monto_e = [p.strip() for p in partes[:4]]
                
                fecha = f"{periodo}{dia_e[:2]}"
                # Estructura básica 606
                linea = f"{rnc_e}|1|02|{ncf_e}||{fecha}||{monto_e}|0.00|{monto_e}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                
                resultados.append({
                    "Factura": archivo.name,
                    "RNC": rnc_e,
                    "NCF": ncf_e,
                    "Monto": monto_e,
                    "Linea": linea
                })
                
            except Exception as e:
                st.error(f"Error procesando {archivo.name}. Intente con una foto más clara.")
            
            progreso.progress((i + 1) / len(archivos))

        if resultados:
            st.divider()
            df = pd.DataFrame(resultados)
            st.subheader("📊 Datos Extraídos")
            st.dataframe(df[["RNC", "NCF", "Monto"]], use_container_width=True)
            
            # Generar TXT
            txt_content = "\n".join([r["Linea"] for r in resultados])
            st.download_button(
                label="📥 Descargar TXT para DGII",
                data=txt_content,
                file_name=f"606_{periodo}.txt",
                mime="text/plain"
            )
