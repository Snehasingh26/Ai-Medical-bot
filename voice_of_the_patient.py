import logging
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Records audio from the microphone and saves it as an MP3 file.

    Args:
    - file_path (str): Path to save the recorded audio file.
    - timeout (int): Maximum time to wait for a phrase to start (in seconds).
    - phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            
            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            # Convert the recorded audio to an MP3 file
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred while recording: {e}")

def transcribe_with_groq(audio_filepath, GROQ_API_KEY, stt_model="whisper-large-v3"):
    """
    Transcribes an audio file using Groq's Whisper model.

    Args:
    - audio_filepath (str): Path to the recorded audio file.
    - GROQ_API_KEY (str): Your Groq API key.
    - stt_model (str): The speech-to-text model to use.

    Returns:
    - str: Transcribed text.
    """
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        logging.error(f"Error in transcribe_with_groq: {e}")
        return "Error in Speech to Text"
