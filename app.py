import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import tempfile
import base64

#Logo AuriX
def mostrar_logo(path_logo):
    with open(path_logo, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 10px;">
            <img src="data:image/png;base64,{encoded}" width="400"/>
        </div>
        """,
        unsafe_allow_html=True
    )
mostrar_logo("logoaurix.png")  

st.title("📈 Análisis de Frecuencia Cardíaca")

#Datos del paciente
st.sidebar.header("🩺 Datos del paciente")
nombre_paciente = st.sidebar.text_input("Nombre del paciente")
edad_paciente = st.sidebar.number_input("Edad", min_value=0, max_value=120, step=1)
observaciones = st.sidebar.text_area("Observaciones médicas")

#SECCION DE FRECUENCIA CARDIACA
#Subida del archivo
uploaded_file = st.file_uploader("Subí tu archivo CSV de Aurix", type=["csv"])

#Subida del archivo
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = df.rename(columns={'time': 'fecha', 'value': 'frecuencia_cardíaca'})
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha']).sort_values('fecha')

    # Cálculo de estadísticas
    min_fc = df['frecuencia_cardíaca'].min()
    max_fc = df['frecuencia_cardíaca'].max()
    avg_fc = df['frecuencia_cardíaca'].mean()
    total = len(df)
    en_arritmia = df[df['frecuencia_cardíaca'] > 70].shape[0]
    carga_arritmica = (en_arritmia / total) * 100 if total > 0 else 0

    #Mostrar estadisticas
    st.markdown(f"""
    ### 📊 Estadísticas
    - 🔻 Frecuencia mínima: {min_fc:.2f} lpm
    - 🔺 Frecuencia máxima: {max_fc:.2f} lpm
    - 📈 Frecuencia promedio: {avg_fc:.2f} lpm
    - ❤️ Carga arrítmica (>70 lpm): {carga_arritmica:.2f} %
    """)
    
    #Grafico interactivo FC
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['frecuencia_cardíaca'], mode='lines', line=dict(color='crimson', width=2)))
    fig.update_layout(title='Evolución de la Frecuencia Cardíaca', xaxis_title='Fecha y Hora', yaxis_title='Frecuencia (lpm)', template='plotly_white')
    st.plotly_chart(fig)

    #Grafico para pdf
    plt.figure(figsize=(10, 5))
    plt.plot(df['fecha'], df['frecuencia_cardíaca'], color='crimson', linewidth=2)
    plt.title('Evolución de la Frecuencia Cardíaca')
    plt.xlabel('Fecha y Hora')
    plt.ylabel('Frecuencia (lpm)')
    plt.grid(True)
    plt.tight_layout()
    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_img.name)
    plt.close()

    #Generacion de pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Informe de Frecuencia Cardíaca", ln=True, align="C")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().date()}", ln=True)
    pdf.ln(5)
    #Datos de paciente
    pdf.cell(0, 10, f"Nombre del paciente: {nombre_paciente}", ln=True)
    pdf.cell(0, 10, f"Edad: {edad_paciente} años", ln=True)
    pdf.ln(5)
    if observaciones:
        pdf.multi_cell(0, 10, f"Observaciones: {observaciones}")
        pdf.ln(5)
    #Estadisticas    
    pdf.cell(0, 10, f"Frecuencia mínima: {min_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Frecuencia máxima: {max_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Frecuencia promedio: {avg_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Carga arrítmica (>70 lpm): {carga_arritmica:.2f} %", ln=True)
    pdf.ln(5)
    pdf.image(tmp_img.name, x=10, w=190)

    #Boton para descargar pdf
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_pdf.name)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button(
            label="📥 Descargar informe PDF",
            data=f,
            file_name="informe_frecuencia_cardiaca.pdf",
            mime="application/pdf",
        )
#-------------------------------------SECCION ECG---------------------------------------
from scipy.signal import butter, filtfilt

st.header("Señal ECG")
uploaded_ecg_file = st.file_uploader("Subí tu archivo CSV de ECG", type=["csv"], key="ecg")

# Funciones de filtrado
def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    return butter(order, [low, high], btype='band')

def aplicar_filtro_bandpass(data, fs, lowcut=0.5, highcut=15):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return filtfilt(b, a, data)

# Si se sube archivo
if uploaded_ecg_file is not None:
    df_ecg = pd.read_csv(uploaded_ecg_file)

    # Verificar columnas
    if 'timestamp_ms' in df_ecg.columns and 'ecg' in df_ecg.columns:
        fs = 200  # Frecuencia de muestreo (Hz)

        # Filtrar señal
        df_ecg["ecg_filtrado"] = aplicar_filtro_bandpass(df_ecg["ecg"], fs)

        # Calcular tiempo en segundos
        df_ecg["tiempo_s"] = df_ecg["timestamp_ms"] / 1000.0

        # Gráfico
        fig_ecg = go.Figure()
        fig_ecg.add_trace(go.Scatter(
            x=df_ecg["tiempo_s"],
            y=df_ecg["ecg_filtrado"],
            name="Filtrado (0.5–15 Hz)",
            line=dict(color="blue", width=2)
        ))

        # Estilo ECG con fondo cuadriculado
        fig_ecg.update_layout(
            title="Señal ECG Filtrada (en segundos)",
            xaxis_title="Tiempo (s)",
            yaxis_title="ECG (mV)",
            template="plotly_white",
            height=500,
            hovermode="x unified",
            xaxis=dict(
                showgrid=True,
                gridcolor='LightPink',
                dtick=0.2  # líneas verticales cada 0.2 segundos
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='LightPink',
                dtick=0.5  # líneas horizontales cada 0.5 mV
            )
        )

        st.plotly_chart(fig_ecg)
    else:
        st.error("Las columnas esperadas ('timestamp_ms' y 'ecg') no están presentes.")

