import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Scanner 606 RD", layout="wide")
st.title("🏦 Scanner 606 - Versión 2026")

# Configuración de la API
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Intentamos conectar con el modelo flash sin prefijos de versión
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("✅ Sistema listo para procesar.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
else:
    st.error("❌ Falta la API Key en Secrets.")

archivo = st.file_uploader("Sube tu factura", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Factura seleccionada", width=400)
    
    if st.button("🚀 Extraer Datos"):
        try:
            # Prompt optimizado para contabilidad dominicana
            prompt = "Extrae de esta factura dominicana: RNC emisor, NCF, Día, Monto total. Formato: RNC|NCF|DIA|MONTO"
            
            with st.spinner('Procesando con IA...'):
                # Usamos la sintaxis más moderna
                response = model.generate_content([prompt, img])
                
                if response.text:
                    texto = response.text.strip()
                    st.info(f"Lectura: {texto}")
                    
                    if "|" in texto:
                        datos = texto.split('|')
                        df = pd.DataFrame([{
                            "RNC": datos[0], 
                            "NCF": datos[1], 
                            "Día": datos[2], 
                            "Monto": datos[3]
                        }])
                        st.table(df)
                    else:
                        st.warning("La IA respondió en un formato inesperado. Intente de nuevo.")
        except Exception as e:
            st.error(f"Error crítico: {e}")
            st.info("💡 Sugerencia: Si el error persiste, intenta crear una NUEVA API Key en Google AI Studio, a veces las llaves viejas se bloquean.")
