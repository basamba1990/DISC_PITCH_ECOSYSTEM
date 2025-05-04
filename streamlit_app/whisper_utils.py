import openai
import streamlit as st
import os
import subprocess
from typing import Optional
from mimetypes import guess_type

class AudioTranscriber:
    def __init__(self):
        self.client = openai.OpenAI(api_key=st.secrets["openai_api_key"])
        self.max_size = 25 * 1024 * 1024  # 25MB
        self.allowed_mimes = {
            'audio/wav', 'audio/mpeg', 'audio/mp4',
            'audio/webm', 'audio/ogg', 'audio/flac'
        }

    def _validate_file(self, file_path: str) -> None:
        """Valide le format et la taille du fichier"""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Fichier audio introuvable")
            
        if os.path.getsize(file_path) > self.max_size:
            raise ValueError(
                f"Fichier trop volumineux ({os.path.getsize(file_path)/1e6:.1f}MB > 25MB)"
            )

        mime_type, _ = guess_type(file_path)
        if mime_type not in self.allowed_mimes:
            raise ValueError(f"Format {mime_type} non supporté")

    def _convert_to_compatible_format(self, input_path: str) -> str:
        """Convertit le fichier en WAV PCM 16-bit standard"""
        output_path = "/tmp/converted_audio.wav"
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Échec conversion : {result.stderr.decode()}")
            
        return output_path

    def transcribe(
        self, 
        file_path: str,
        language: Optional[str] = None,  # Auto-détection par défaut
        prompt: Optional[str] = None
    ) -> str:
        """
        Effectue la transcription audio avec gestion des formats
        """
        try:
            original_path = file_path
            needs_conversion = False
            
            # Vérification MIME type
            mime_type, _ = guess_type(file_path)
            if mime_type != 'audio/wav':
                needs_conversion = True
                file_path = self._convert_to_compatible_format(file_path)

            self._validate_file(file_path)
            
            with open(file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language=language,
                    prompt=prompt
                )

            return transcript.text
            
        except Exception as e:
            raise RuntimeError(f"Échec transcription : {str(e)}")
            
        finally:
            # Nettoyage fichier converti
            if needs_conversion and os.path.exists(file_path):
                os.remove(file_path)

def transcribe_audio(file_path: str) -> str:
    """Interface simplifiée pour Streamlit"""
    transcriber = AudioTranscriber()
    return transcriber.transcribe(file_path)
