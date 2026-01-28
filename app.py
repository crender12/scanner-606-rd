import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Scanner 606 Pro", layout="wide")

# Título
st.title("🏦 Scanner 606 RD")

# 1. Configurar la Llave directamente desde los Secrets
try:
    if "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=key)
        st.success("✅ Conexión con Google establecida.")
    else:
        st.error("❌ No se encontró la GEMINI_API_KEY en Secrets.")
except Exception as e:
    st.error(f"Error configurando la llave: {e}")

# 2. Subida de archivos
archivo = st.file_uploader("Sube una factura", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Imagen cargada", width=300)
    
    if st.button("Procesar Factura"):
        try:
            # Usamos el modelo más estable
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = "Actúa como contador. Extrae de esta factura: RNC Emisor, NCF, Día, Monto Total. Responde en este formato: RNC|NCF|DIA|MONTO"
            
            with st.spinner('La IA está leyendo la factura...'):
                response = model.generate_content([prompt, img])
                st.info(f"Respuesta de la IA: {response.text}")
                
                # Intentar mostrar en tabla
                datos = response.text.split('|')
                if len(datos) >= 4:
                    df = pd.DataFrame([{"RNC": datos[0], "NCF": datos[1], "Día": datos[2], "Monto": datos[3]}])
                    st.table(df)
        except Exception as e:
            st.error(f"Error detallado: {e}")
            st.write("Copia este error y pásamelo para decirte qué dice Google.")
