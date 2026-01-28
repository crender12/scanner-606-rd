import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Scanner 606 RD - Estable", layout="wide")
st.title("🏦 Scanner 606 Dominicano")

# 2. Configuración de la API (FORZANDO VERSIÓN ESTABLE)
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Usamos el modelo sin prefijos raros para que Google elija la versión estable automática
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("✅ Sistema conectado correctamente.")
    except Exception as e:
        st.error(f"Error de configuración: {e}")
else:
    st.error("❌ Falta la API Key en Secrets.")

# 3. Interfaz de usuario
periodo = st.sidebar.text_input("Periodo (AAAAMM)", value="202601")
archivo = st.file_uploader("Sube una factura nítida", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Factura cargada", width=400)
    
    if st.button("🚀 Procesar Factura"):
        try:
            # Prompt optimizado
            prompt = "Eres un contador experto. Lee esta factura y entrega: RNC emisor, NCF, Día, Monto total. Formato: RNC|NCF|DIA|MONTO"
            
            with st.spinner('Analizando datos...'):
                # Aquí está el truco: generamos contenido de forma simple
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.info(f"Datos recibidos: {response.text}")
                    datos = response.text.split('|')
                    
                    if len(datos) >= 4:
                        res_dict = {
                            "RNC Emisor": datos[0].strip(),
                            "NCF": datos[1].strip(),
                            "Día": datos[2].strip().zfill(2),
                            "Monto": datos[3].strip()
                        }
                        st.table(pd.DataFrame([res_dict]))
                        
                        # Generar línea 606
                        fecha = f"{periodo}{res_dict['Día'][:2]}"
                        monto = res_dict['Monto'].replace(',', '')
                        linea = f"{res_dict['RNC Emisor']}|1|02|{res_dict['NCF']}||{fecha}||{monto}|0.00|{monto}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                        
                        st.download_button("📥 Descargar TXT", data=linea, file_name=f"606_{periodo}.txt")
                else:
                    st.warning("La IA no pudo leer texto en la imagen.")
                    
        except Exception as e:
            # Si el error 404 persiste, intentamos con el modelo Pro automáticamente
            st.warning("Reintentando con modelo alternativo...")
            try:
                model_alt = genai.GenerativeModel('gemini-1.5-pro')
                response = model_alt.generate_content([prompt, img])
                st.write(response.text)
            except Exception as e2:
                st.error(f"Error persistente: {e2}")
