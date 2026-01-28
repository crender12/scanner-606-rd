import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Scanner 606 RD", page_icon="🏦")
st.title("🏦 Scanner 606 Pro")

# Usar la llave desde los Secrets (es más seguro y estable)
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Intentar inicializar el modelo
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("✅ Sistema listo para procesar facturas.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
else:
    st.warning("⚠️ Por favor, introduce la API Key en los Secrets de Streamlit.")

archivo = st.file_uploader("Sube una factura (JPG o PNG)", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 PROCESAR FACTURA"):
        try:
            prompt = "Actúa como contador dominicano. Extrae: RNC emisor, NCF, Día, Monto total. Responde solo: RNC|NCF|DIA|MONTO"
            
            with st.spinner('IA analizando...'):
                response = model.generate_content([prompt, img])
                st.info(f"Datos: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Si dice 'Expired', intenta crear la llave de nuevo en AI Studio, a veces la primera falla.")
