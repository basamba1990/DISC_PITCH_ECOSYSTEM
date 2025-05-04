import streamlit as st
import tempfile
import openai
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from whisper_utils import transcribe_audio
from streamlit_extras.stylable_container import stylable_container

# Configuration CSS personnalisée
def load_custom_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css("style.css")

# Configuration de la page
st.set_page_config(
    page_title="GENUP2050 - Coach Pitch & DISC",
    page_icon=":rocket:",
    layout="centered"
)

# En-tête avec logo
logo = Image.open("logo_genup2050.png")
st.image(logo, width=250)

# Page d'accueil avec instructions
with st.expander("📘 Bienvenue sur Coach Pitch & DISC - Clique ici pour commencer", expanded=True):
    st.markdown("""
    ## Comment fonctionne cette application ?

    Cette application t'aide à **améliorer ton pitch vidéo** grâce à l'**IA** et à la **méthode DISC**.

    ### Étapes :
    1. **Téléverse ta vidéo** de pitch
    2. Transcription automatique par IA
    3. Sélectionne ton **profil DISC**
    4. Reçois un **feedback personnalisé**
    5. Génère ton **rapport PDF**

    ---
    ### Vidéo Démo :
    """)
    st.video("https://www.smooovebox.com/vf/87187b4f68f27b47a8391227df36d06dd0ac53c9")
    
    st.markdown("""
    ---
    ## Conseils par profil DISC
    <div style="padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="color: #002c5f;">🔴 Dominant (D)</h4>
        <ul>
            <li>Focus sur les résultats</li>
            <li>Direct et concis</li>
        </ul>
    </div>
    <div style="padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="color: #f47c20;">🟡 Influent (I)</h4>
        <ul>
            <li>Énergie et enthousiasme</li>
            <li>Stories inspirantes</li>
        </ul>
    </div>
    <div style="padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="color: #50BFA5;">🟢 Stable (S)</h4>
        <ul>
            <li>Ton rassurant</li>
            <li>Approche collaborative</li>
        </ul>
    </div>
    <div style="padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="color: #2F4F4F;">🔵 Conforme (C)</h4>
        <ul>
            <li>Précision des détails</li>
            <li>Structure rigoureuse</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Classe PDF personnalisée
class CustomPDF(FPDF):
    def header(self):
        if os.path.exists("logo_genup2050.png"):
            self.image("logo_genup2050.png", x=10, y=8, w=30)
        self.set_font("Arial", 'B', 15)
        self.set_text_color(0, 44, 95)
        self.cell(80)
        self.cell(30, 10, "Rapport Pitch & DISC", 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(0, 44, 95)
        self.cell(0, 10, f'GENUP2050 | Page {self.page_no()}', 0, 0, 'C')

# Génération du PDF
def generate_pdf(user_name, transcription, profile, feedback):
    pdf = CustomPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Entête
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Date : {datetime.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Informations utilisateur
    pdf.set_fill_color(244, 124, 32)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f" Prénom/Pseudo : {user_name} ", ln=True, fill=True)
    pdf.cell(0, 10, f" Profil DISC : {profile} ", ln=True, fill=True)
    pdf.ln(5)
    
    # Contenu
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, "TRANSCRIPTION DU PITCH")
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, transcription)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, "FEEDBACK PERSONNALISÉ")
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, feedback)
    
    filename = f"{user_name}_rapport_pitch_GENUP2050.pdf"
    pdf.output(filename)
    return filename

# Téléversement de fichier
with stylable_container("upload_box", css_styles="""
    padding: 25px; 
    border: 2px dashed #002c5f;
    border-radius: 15px;
    background-color: #f8f9fa;
"""):
    video_file = st.file_uploader("📤 Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "wav", "mp3"])

# Process principal
if video_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    try:
        # Transcription audio
        with st.status("Analyse en cours...", expanded=True) as status:
            st.write("🔍 Décodage du fichier audio...")
            transcription = transcribe_audio(temp_file_path)
            status.update(label="Analyse terminée avec succès ! ✅", state="complete", expanded=False)
        
        tabs = st.tabs(["📝 Transcription", "📊 Feedback DISC", "📄 Rapport PDF"])

        with tabs[0]:
            st.subheader("Transcription générée")
            st.text_area("Résultat :", transcription, height=300, key="transcription_area")

        with tabs[1]:
            profile = st.selectbox(
                "Profil DISC",
                options=["Dominant (D)", "Influent (I)", "Stable (S)", "Conforme (C)"],
                key="disc_profile"
            )
            
            def generate_feedback(text, disc_type):
                prompt = f"""
                Tu es un coach expert en méthode DISC. 
                Profil de l'utilisateur : {disc_type}
                Transcription du pitch :
                \"\"\"{text}\"\"\"

                Génère un feedback structuré avec :
                1. 2 points forts spécifiques au profil
                2. 2 axes d'amélioration adaptés
                3. 1 conseil pratique immédiatement applicable
                """
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content

            if profile and transcription:
                feedback = generate_feedback(transcription, profile)
                st.markdown("##### Feedback personnalisé")
                st.success(feedback)

        with tabs[2]:
            user_name = st.text_input("Entrez votre prénom ou pseudo", key="user_name")
            if user_name and st.button("Générer le rapport PDF", type="primary"):
                pdf_path = generate_pdf(user_name, transcription, profile, feedback)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger le rapport complet",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf",
                        key="pdf_download"
                    )
                st.toast("Rapport généré avec succès !", icon="🎉")

    except Exception as e:
        st.error(f"""
        **Erreur lors du traitement :**
        ```
        {str(e)}
        ```
        Veuillez vérifier :
        1. La taille du fichier (max 25MB)
        2. La qualité audio
        3. Votre connexion Internet
        """)
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
