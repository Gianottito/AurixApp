import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import tempfile

st.title("📈 Análisis de Frecuencia Cardíaca")

uploaded_file = st.file_uploader("Subí tu archivo CSV con columnas 'time' y 'value'", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = df.rename(columns={'time': 'fecha', 'value': 'frecuencia_cardíaca'})
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha']).sort_values('fecha')

    min_fc = df['frecuencia_cardíaca'].min()
    max_fc = df['frecuencia_cardíaca'].max()
    avg_fc = df['frecuencia_cardíaca'].mean()
    total = len(df)
    en_arritmia = df[df['frecuencia_cardíaca'] > 70].shape[0]
    carga_arritmica = (en_arritmia / total) * 100 if total > 0 else 0

    st.markdown(f"""
    ### 📊 Estadísticas
    - 🔻 Frecuencia mínima: {min_fc:.2f} lpm
    - 🔺 Frecuencia máxima: {max_fc:.2f} lpm
    - 📈 Frecuencia promedio: {avg_fc:.2f} lpm
    - ❤️ Carga arrítmica (>70 lpm): {carga_arritmica:.2f} %
    """)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha'], y=df['frecuencia_cardíaca'], mode='lines', line=dict(color='crimson', width=2)))
    fig.update_layout(title='Evolución de la Frecuencia Cardíaca', xaxis_title='Fecha y Hora', yaxis_title='Frecuencia (lpm)', template='plotly_white')
    st.plotly_chart(fig)

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

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Informe de Frecuencia Cardíaca", ln=True, align="C")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, f"Frecuencia mínima: {min_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Frecuencia máxima: {max_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Frecuencia promedio: {avg_fc:.2f} lpm", ln=True)
    pdf.cell(0, 10, f"Carga arrítmica (>70 lpm): {carga_arritmica:.2f} %", ln=True)
    pdf.ln(10)
    pdf.image(tmp_img.name, x=10, w=190)

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_pdf.name)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button(
            label="📥 Descargar informe PDF",
            data=f,
            file_name="informe_frecuencia_cardiaca.pdf",
            mime="application/pdf",
        )
