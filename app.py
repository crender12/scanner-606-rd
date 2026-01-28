import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

# Configuración visual Pro
st.set_page_config(page_title="Scanner 606 Pro RD", layout="wide", page_icon="🏦")

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .status-box { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Scanner 606 Pro")
st.subheader("Inteligencia Artificial para Contabilidad Dominicana")

# Configuración de la API con manejo de errores
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🔑 Error: Configura la API Key en los Secrets de Streamlit.")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2618/2618576.png", width=100)
    st.header("Panel de Control")
    periodo = st.text_input("Periodo (AAAAMM)", value="202601")
    st.divider()
    st.write("📞 **Soporte Técnico:**")
    st.write("Tu Nombre/Empresa")

# Carga de archivos
archivos = st.file_uploader("Subir facturas (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if archivos:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"📂 {len(archivos)} archivos cargados.")
        boton = st.button("🚀 PROCESAR AHORA")

    if boton:
        resultados = []
        progreso = st.progress(0)
        
        for i, archivo in enumerate(archivos):
            try:
                img = Image.open(archivo)
                # Redimensionar para asegurar que pase por la API
                img.thumbnail((1000, 1000))
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt más estricto para evitar errores
                prompt = """Actúa como experto contable dominicano. Extrae de esta factura:
                1. RNC Emisor (solo números)
                2. NCF (ej: B01...)
                3. Día del mes (2 dígitos)
                4. Monto Total (solo números)
                Responde estrictamente en este formato: RNC|NCF|DIA|MONTO"""
                
                response = model.generate_content([prompt, img])
                texto = response.text.strip()
                
                # Limpieza de la respuesta
                if "|" in texto:
                    datos = texto.split('|')
                    rnc_e = datos[0].strip()
                    ncf_e = datos[1].strip()
                    dia_e = datos[2].strip().zfill(2)
                    monto_e = datos[3].strip().replace(',', '')
                    
                    fecha = f"{periodo}{dia_e}"
                    linea = f"{rnc_e}|1|02|{ncf_e}||{fecha}||{monto_e}|0.00|{monto_e}|0.00|0.00|0.00|0.00|0.00|0.00||0.00|0.00|0.00|0.00|0.00|3"
                    
                    resultados.append({
                        "RNC Emisor": rnc_e,
                        "NCF": ncf_e,
                        "Monto": monto_e,
                        "Línea 606": linea
                    })
            except Exception as e:
                st.error(f"Error en {archivo.name}: {str(e)}")
            
            progreso.progress((i + 1) / len(archivos))

        if resultados:
            with col2:
                st.success("✅ Procesamiento completado")
                df = pd.DataFrame(resultados)
                # Tabla elegante
                st.dataframe(df[["RNC Emisor", "NCF", "Monto"]], use_container_width=True)
                
                # Generar TXT para descargar
                txt_content = "\n".join([r["Línea 606"] for r in resultados])
                st.download_button(
                    label="📥 Descargar Formato 606 (.txt)",
                    data=txt_content,
                    file_name=f"606_{periodo}.txt",
                    mime="text/plain"
                )
