import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(page_title="Scanner 606 RD - Conexión Directa", layout="wide")
st.title("🏦 Scanner 606 RD")

# Recuperar la llave desde Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🔑 Error: No se encontró la API Key en los Secrets.")
else:
    archivo = st.file_uploader("Sube tu factura", type=["jpg", "png", "jpeg"])

    if archivo:
        # Mostrar la imagen
        img = Image.open(archivo)
        st.image(img, width=400)
        
        if st.button("🚀 Procesar Factura"):
            try:
                # Convertir imagen a Base64 para enviarla
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # URL de Google (Forzando la versión v1 estable)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Eres un contador dominicano. Extrae de esta factura: RNC emisor, NCF, Día, Monto total. Responde solo en este formato: RNC|NCF|DIA|MONTO"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}
                        ]
                    }]
                }

                with st.spinner('Comunicando directamente con Google...'):
                    response = requests.post(url, json=payload)
                    res_json = response.json()

                    if response.status_code == 200:
                        texto = res_json['candidates'][0]['content']['parts'][0]['text']
                        st.success("✅ Datos extraídos:")
                        st.write(texto)
                        
                        # Crear el botón de descarga aquí si el formato es correcto
                        if "|" in texto:
                            st.info("¡Excelente! La conexión directa funcionó.")
                    else:
                        st.error(f"Error de Google: {res_json.get('error', {}).get('message', 'Desconocido')}")
                        st.write("Detalle técnico:", res_json)
            except Exception as e:
                st.error(f"Error en el proceso: {e}")
