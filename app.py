import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Scanner 606 RD Pro", layout="wide")
st.title("🏦 Scanner 606 Dominicano")

# 1. Configuración de la API con tu nueva llave
# Nota: Es mejor que esta llave esté en Settings > Secrets como GEMINI_API_KEY
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key="AIzaSyBOfHfs5Wx5hKXyNEFhvqOEuS8ngaAgx1U" # Tu nueva llave

genai.configure(api_key=api_key)

# 2. Selección del modelo (Intentando la versión más estable primero)
try:
    # Esta es la forma más segura de llamar al modelo en 2026
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    st.success("✅ Conexión establecida con la nueva llave.")
except Exception as e:
    st.error(f"Error al conectar con el modelo: {e}")

# 3. Interfaz de usuario
archivo = st.file_uploader("Sube una foto de la factura", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Factura cargada", width=400)
    
    if st.button("🚀 Extraer Datos"):
        try:
            # Prompt optimizado
            prompt = "Actúa como contador dominicano. Extrae: RNC emisor, NCF, Día, Monto total. Responde solo: RNC|NCF|DIA|MONTO"
            
            with st.spinner('Analizando imagen...'):
                response = model.generate_content([prompt, img])
                
                if response.text:
                    resultado = response.text.strip()
                    st.info(f"Datos detectados: {resultado}")
                    
                    if "|" in resultado:
                        datos = resultado.split('|')
                        df = pd.DataFrame([{
                            "RNC": datos[0], 
                            "NCF": datos[1], 
                            "Día": datos[2], 
                            "Monto": datos[3]
                        }])
                        st.table(df)
                        
                        # Generar el TXT para la DGII
                        linea = f"{datos[0]}|1|02|{datos[1]}||202601{datos[2].zfill(2)}||{datos[3]}|||||||||||||3"
                        st.download_button("📥 Descargar 606.txt", data=linea, file_name="606_reporte.txt")
                
        except Exception as e:
            st.error(f"Hubo un problema: {e}")
            st.info("Prueba a darle al botón de nuevo, a veces la primera conexión falla.")

