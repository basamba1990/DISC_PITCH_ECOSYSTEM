import openai
import streamlit as st
import os
from typing import Optional

class AudioTranscriber:
    def __init__(self):
        self.client = openai.OpenAI(api_key=st.secrets["openai_api_key"])
        self.max_size = 25 * 1024 * 1024  # 25MB

    def _validate_file(self, file_path: str) -> None:
        """Valide le fichier avant traitement"""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Fichier audio introuvable sur le serveur")
            
        if os.path.getsize(file_path) > self.max_size:
            raise ValueError(
                f"Fichier trop volumineux ({os.path.getsize(file_path)/1024/1024:.1f}MB > 25MB). "
                "Veuillez réduire la durée ou la qualité audio."
            )

    def transcribe(
        self, 
        file_path: str,
        language: Optional[str] = "fr",
        prompt: Optional[str] = None
    ) -> str:
        """
        Effectue la transcription audio avec Whisper-1
        Args:
            file_path: Chemin du fichier audio
            language: Langue cible (None pour auto-détection)
            prompt: Prompt de contexte pour améliorer la transcription
        Returns:
            Texte transcrit
        """
        try:
            self._validate_file(file_path)
            
            with open(file_path, "rb") as audio_file:
                return self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language=language,
                    prompt=prompt  # CORRECTION ICI (promchill → prompt)
                ).text

        except openai.APIConnectionError as e:
            raise ConnectionError(
                "Échec de connexion à l'API OpenAI. "
                "Vérifiez votre connexion Internet."
            ) from e
            
        except openai.RateLimitError as e:
            raise RuntimeError(
                "Quota API dépassé. Veuillez réessayer plus tard ou "
                "contactez l'administrateur."
            ) from e
            
        except openai.APIError as e:
            raise RuntimeError(
                f"Erreur de l'API OpenAI: {str(e)}"
            ) from e

    def batch_transcribe(self, file_list: list) -> dict:
        """Transcription de plusieurs fichiers (pour usage futur)"""
        results = {}
        for file_path in file_list:
            try:
                results[file_path] = self.transcribe(file_path)
            except Exception as e:
                results[file_path] = str(e)
        return results

# Interface simplifiée pour Streamlit
def transcribe_audio(file_path: str) -> str:
    transcriber = AudioTranscriber()
    return transcriber.transcribe(file_path)
