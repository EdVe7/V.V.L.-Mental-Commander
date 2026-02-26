import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAZIONE E DESIGN GOOGLE-PGA
# ==========================================
st.set_page_config(page_title="V.V.L. Mind Lab", page_icon="🧠", layout="centered")

# CSS per interfaccia pulita e professionale
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stSlider [data-baseweb="slider"] { margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SPLASH SCREEN (LOGO 3 SECONDI)
# ==========================================
if 'mind_splash' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='text-align:center; color:#2CB8C8;'>V.V.L. MIND LAB</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Mental Performance Training - Road to 2040</p>", unsafe_allow_html=True)
    time.sleep(3)
    placeholder.empty()
    st.session_state['mind_splash'] = True

# ==========================================
# 3. CONNESSIONE DATI E SICUREZZA
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

if "auth" not in st.session_state:
    pwd = st.text_input("Inserisci Password Olimpica", type="password")
    if pwd == "olimpiadi2040":
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# Pulizia e conversione date
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])

# ==========================================
# 4. FUNZIONE PDF (Libreria FPDF Classica)
# ==========================================
def create_pdf_classic(data, period_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "V.V.L. MIND LAB - PERFORMANCE REPORT", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Periodo: {period_name} | Generato: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(10)

    if not data.empty:
        # Calcolo Medie
        medie = data[['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']].mean()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, "Medie Mental Skill del Periodo:", 0, 1)
        pdf.set_font("Arial", '', 12)
        for cat, val in medie.items():
            pdf.cell(190, 8, f"- {cat}: {round(val, 2)} / 5", 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, "Storico Tornei nel Periodo:", 0, 1)
        pdf.set_font("Arial", '', 10)
        for i, row in data.iterrows():
            pdf.cell(190, 7, f"{row['Data'].strftime('%Y-%m-%d')} - {row['Torneo']} - Score: {row['Score']}", 0, 1)
    
    # Restituisce il PDF come stringa di byte compatibile con Streamlit
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. OBIETTIVI LUNGO TERMINE (VISION 2040)
# ==========================================
st.title("🏆 V.V.L. Mind Lab & Vision")
with st.expander("🎯 LA TUA VISIONE: OLIMPIADI 2040"):
    st.markdown("""
    **Missione:** Diventare il giocatore più resiliente del Tour.
    - **Obiettivo Tecnico:** Punteggio medio < 70.0 entro il 2030.
    - **Obiettivo Mentale:** Routine pre-colpo automatizzata al 100%.
    - **Motto:** *Il processo batte il risultato.*
    """)

# ==========================================
# 6. INPUT POST-TORNEO
# ==========================================
st.subheader("📝 Analisi Fine Gara")
with st.form("mind_review", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        torneo = st.text_input("Torneo o Campo")
        score = st.number_input("Punteggio Finale", min_value=50, value=72)
    with col2:
        acc = st.select_slider("Accettazione Errore", options=[1,2,3,4,5], value=3)
        rou = st.select_slider("Costanza Routine", options=[1,2,3,4,5], value=3)
    
    col3, col4 = st.columns(2)
    with col3:
        dec = st.select_slider("Decisione/Immagine", options=[1,2,3,4,5], value=3)
        foc = st.select_slider("Focus Presente", options=[1,2,3,4,5], value=3)
    with col4:
        ene = st.select_slider("Gestione Energia", options=[1,2,3,4,5], value=3)
        ten = st.select_slider("Tensione (1=Ok, 5=Blocco)", options=[1,2,3,4,5], value=2)

    note = st.text_area("Cosa porti a casa da questa giornata?")
    
    if st.form_submit_button("REGISTRA PERFORMANCE MENTALE 🚀"):
        nuovo = pd.DataFrame([{
            "Data": datetime.now(), "Torneo": torneo, "Score": score,
            "Accettazione": acc, "Routine": rou, "Decisione": dec,
            "Focus": foc, "Energia": ene, "Tensione": ten, "Note": note
        }])
        df_updated = pd.concat([df, nuovo], ignore_index=True)
        conn.update(data=df_updated)
        st.success("Analisi salvata. Ogni dato ti avvicina al 2040.")
        time.sleep(1)
        st.rerun()

# ==========================================
# 7. REPORTISTICA E GRAFICI AVANZATI
# ==========================================
if not df.empty:
    st.divider()
    st.header("📊 Analisi della Tenuta Mentale")
    
    periodo = st.selectbox("Seleziona Arco Temporale:", 
                          ["Ultimi 7 giorni", "Ultimo Mese", "Ultimi 6 Mesi", "Ultimo Anno", "Lifelong"])
    
    # Filtro Temporale Dinamico
    oggi = datetime.now()
    if periodo == "Ultimi 7 giorni":
        df_f = df[df['Data'] >= (oggi - timedelta(days=7))]
    elif periodo == "Ultimo Mese":
        df_f = df[df['Data'] >= (oggi - timedelta(days=30))]
    elif periodo == "Ultimi 6 Mesi":
        df_f = df[df['Data'] >= (oggi - timedelta(days=182))]
    elif periodo == "Ultimo Anno":
        df_f = df[df['Data'] >= (oggi - timedelta(days=365))]
    else:
        df_f = df

    if not df_f.empty:
        # RADAR CHART (Sempre visibile per analisi immediata)
        medie_f = df_f[['Accettazione', 'Routine', 'Decisione', 'Focus', 'Energia']].mean()
        
        fig = go.Figure(go.Scatterpolar(
            r=medie_f.values,
            theta=medie_f.index,
            fill='toself',
            line_color='#2CB8C8',
            name=periodo
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            title=f"Profilo Mentale Medio: {periodo}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        

        # DOWNLOAD PDF (Libreria FPDF Classica)
        st.subheader("📩 Esporta Report")
        try:
            pdf_out = create_pdf_classic(df_f, periodo)
            st.download_button(
                label=f"Scarica PDF {periodo}",
                data=pdf_out,
                file_name=f"VVL_Mind_Report_{periodo.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Errore nella generazione PDF: {e}")

        with st.expander("📖 Diario Storico"):
            st.dataframe(df_f.sort_values(by="Data", ascending=False), hide_index=True)
