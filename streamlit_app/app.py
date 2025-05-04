import streamlit as st
import tempfile
import openai
import os
import time
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from whisper_utils import transcribe_audio
from streamlit_extras.stylable_container import stylable_container

# Configuration CSS sécurisée
def load_custom_css():
    """Charge le CSS personnalisé avec fallback"""
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
            :root {
                --primary-blue: #002c5f;
                --secondary-orange: #f47c20;
                --success-green: #50BFA5;
                --neutral-light: #f8f9fa;
                --text-dark: #2F4F4F;
                --error-red: #e74c3c;
            }
            body { font-family: Arial, sans-serif; }
            .stButton>button { 
                background: var(--primary-blue)!important; 
                color: white!important;
                border-radius: 8px;
            }
            div[data-testid="stFileUploader"] {
                border: 2px dashed var(--primary-blue)!important;
                border-radius: 12px;
            }
        </style>
        """, unsafe_allow_html=True)
        st.warning("Style personnalisé non trouvé - Mode minimal activé")

load_custom_css()

# Initialisation de l'application
def init_app():
    """Configure l'application et charge le logo"""
    st.set_page_config(
        page_title="GENUP2050 - Coach Pitch & DISC",
        page_icon="🚀",
        layout="centered"
    )
    
    try:
        logo = Image.open("logo_genup2050.png")
        st.image(logo, width=250)
    except FileNotFoundError:
        st.title("GENUP2050 - Coach Pitch")
        st.warning("Logo non trouvé")

init_app()

# Classe PDF sécurisée
class CustomPDF(FPDF):
    """Génère le PDF avec vérification du logo"""
    def header(self):
        try:
            if os.path.exists("logo_genup2050.png"):
                self.image("logo_genup2050.png", x=10, y=8, w=30)
        except Exception as e:
            pass  # Continue sans logo si erreur
        
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

# Génération du PDF avec gestion d'erreur
def generate_pdf(user_name, transcription, profile, feedback):
    """Génère le PDF avec vérifications"""
    try:
        pdf = CustomPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Entête
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
        pdf.multi_cell(0, 10, "TRANSCRIPTION DU PITCH :\n" + transcription)
        pdf.ln(5)
        pdf.multi_cell(0, 10, "FEEDBACK PERSONNALISÉ :\n" + feedback)
        
        filename = f"{user_name}_rapport_pitch_GENUP2050.pdf"
        pdf.output(filename)
        return filename
    except Exception as e:
        st.error(f"Erreur génération PDF : {str(e)}")
        return None

# Interface principale
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

# Téléversement de fichier sécurisé
with stylable_container("upload_box", css_styles="""
    padding: 25px; 
    border: 2px dashed var(--primary-blue);
    border-radius: 15px;
    background-color: var(--neutral-light);
"""):
    video_file = st.file_uploader("📤 Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "wav", "mp3"])

# Process principal avec gestion d'erreur complète
if video_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            temp_file.write(video_file.read())
            temp_file_path = temp_file.name
        except Exception as e:
            st.error(f"Erreur écriture fichier temporaire : {str(e)}")
            st.stop()

    try:
        with st.status("Analyse en cours...", expanded=True) as status:
            try:
                st.write("🔍 Traitement audio...")
                transcription = transcribe_audio(temp_file_path)
                status.update(label="Analyse réussie ✅", state="complete")
            except Exception as e:
                status.update(label="Échec de l'analyse ❌", state="error")
                raise e

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
            
            if profile and transcription:
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[{
                            "role": "user",
                            "content": f"""
                            Tu es un coach expert en méthode DISC. 
                            Profil: {profile}
                            Transcription: {transcription}
                            
                            Génère un feedback structuré avec :
                            1. 2 points forts
                            2. 2 axes d'amélioration
                            3. 1 conseil pratique
                            """
                        }],
                        temperature=0.7,
                        max_tokens=500
                    )
                    feedback = response.choices[0].message.content
                    st.markdown("##### Feedback personnalisé")
                    st.success(feedback)
                except Exception as e:
                    st.error(f"Erreur génération feedback : {str(e)}")

        with tabs[2]:
            user_name = st.text_input("Entrez votre prénom/pseudo", key="user_name")
            if user_name and st.button("Générer PDF", type="primary"):
                if 'feedback' in locals() and transcription:
                    pdf_path = generate_pdf(user_name, transcription, profile, feedback)
                    if pdf_path:
                        try:
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📥 Télécharger le rapport",
                                    data=f,
                                    file_name=pdf_path,
                                    mime="application/pdf"
                                )
                            st.toast("Rapport généré avec succès !", icon="🎉")
                        except Exception as e:
                            st.error(f"Erreur téléchargement PDF : {str(e)}")
                else:
                    st.warning("Veuillez d'abord générer le feedback")

    except Exception as e:
        st.error(f"""
        **Erreur critique :**
        ```python
        {str(e)}
        ```
        Veuillez réessayer ou contacter le support.
        """)
    finally:
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except Exception as e:
            st.error(f"Erreur nettoyage fichier : {str(e)}")
