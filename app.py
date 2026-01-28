import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import re

# Configuración Pro
st.set_page_config(page_title="Scanner 606 Pro RD", layout="wide", page_icon="🏦")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #002d5a; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Configura la API Key en Secrets.")

st.title("🏦 Scanner 606 Inteligente")
st.write("Optimizado para facturas dominicanas (Farmaconal, Supermercados, etc.)")

with st.sidebar:
    st.header("⚙️ Configuración")
    periodo = st.text_input("Periodo (AAAAMM)", value="202601")

archivos = st.file_uploader("Sube tus facturas", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if archivos:
    if st.button(f"🔍 Procesar {len(archivos)} Factura(s)"):
        resultados = []
        progreso = st.progress(0)
        # Usamos flash-latest que es más rápido y flexible con imágenes
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        for i, archivo in enumerate(archivos):
            try:
                img = Image.open(archivo)
                
                # Prompt reforzado para evitar errores de formato
                prompt = """Analiza esta factura dominicana y extrae:
                1. RNC Emisor (9 u 11 dígitos)
                2. NCF (ej: B01000...)
                3. Día del mes (2 dígitos)
                4. Monto Total (solo números)
                Responde EXCLUSIVAMENTE en este formato: RNC|NCF|DIA|MONTO
                Si no estás seguro, intenta adivinar solo los números."""
                
                response = model.generate_content([prompt, img])
                res_text = response.text.strip()
                
                # LIMPIADOR MAESTRO: Busca el patrón RNC|NCF|DIA|MONTO aunque haya basura alrededor
                match = re.search(r'(\d{9,11})\|([A-Z0-9]+)\|(\d{1,2})\|([\d\.,]+)', res_text)
                
                if match:
                    rnc = match.group(1)
                    ncf = match.group(2)
                    dia = match.group(3).zfill(2)
                    monto = match.group(4).replace(',', '')
                    
                    fecha = f"{periodo}{dia}"
                    linea = f"{rnc}|1|02|{ncf}||{fecha}||{monto}|0.00|{monto}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                    
                    resultados.append({"RNC": rnc, "NCF": ncf, "Monto": monto, "Linea": linea})
                else:
                    st.warning(f"No se pudo extraer formato exacto de {archivo.name}, reintentando...")
            except Exception as e:
                st.error(f"Error técnico en {archivo.name}")
            
            progreso.progress((i + 1) / len(archivos))

        if resultados:
            st.success("✅ Procesado con éxito")
            df = pd.DataFrame(resultados)
            st.dataframe(df[["RNC", "NCF", "Monto"]], use_container_width=True)
            
            txt_data = "\n".join(df["Linea"].tolist())
            st.download_button("📥 Descargar TXT 606", data=txt_data, file_name=f"606_{periodo}.txt")
