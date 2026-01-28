import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Scanner 606 Pro RD", layout="wide")

st.title("🏦 Scanner 606 Pro - Inteligencia Contable")
st.markdown("---")

# Obtener la llave desde los secretos de la nube
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("Falta la API Key en la configuración.")

with st.sidebar:
    st.header("Configuración")
    periodo = st.text_input("Periodo (AAAAMM)", value="202601")
    st.info("Sube las fotos de tus facturas y generaremos el TXT.")

archivos = st.file_uploader("Sube tus facturas (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if archivos:
    resultados = []
    if st.button(f"🚀 Procesar {len(archivos)} Facturas"):
        progreso = st.progress(0)
        for i, archivo in enumerate(archivos):
            img = Image.open(archivo)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Extrae: RNC emisor, NCF, Día (2 dígitos), Monto Total. Responde: RNC|NCF|DIA|MONTO"
            try:
                response = model.generate_content([prompt, img])
                datos = response.text.strip().split('|')
                if len(datos) >= 4:
                    rnc_e, ncf_e, dia_e, monto_e = [d.strip() for d in datos[:4]]
                    fecha = f"{periodo}{dia_e.zfill(2)}"
                    linea = f"{rnc_e}|1|02|{ncf_e}||{fecha}||{monto_e}|0.00|{monto_e}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                    resultados.append({"RNC": rnc_e, "NCF": ncf_e, "Monto": monto_e, "Linea": linea})
            except:
                st.error(f"Error en {archivo.name}")
            progreso.progress((i + 1) / len(archivos))

        if resultados:
            df = pd.DataFrame(resultados)
            st.table(df[["RNC", "NCF", "Monto"]])
            txt_data = "\n".join(df["Linea"].tolist())
            st.download_button("📥 Descargar TXT", txt_data, f"606_{periodo}.txt", "text/plain")