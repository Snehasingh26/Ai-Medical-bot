import os
from gtts import gTTS
import requests
from playsound import playsound  # ✅ Import playsound
import platform
import subprocess

# Function to check for internet connection
def check_internet():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except:
        return False

# Function to convert text to speech with gTTS
def text_to_speech_with_gtts(input_text, output_filepath):
    # Check internet connection
    if not check_internet():
        print("Error: No internet connection - gTTS requires internet")
        return False

    try:
        # Generate speech
        language = "en"
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(output_filepath)
        print(f"Successfully saved audio to {output_filepath}")

        # Verify file was created
        if not os.path.exists(output_filepath):
            raise FileNotFoundError("Output file was not created")
        
        return output_filepath

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Function to automatically play the audio after conversion
def play_audio(output_filepath):
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")

# Main program execution
if __name__ == "__main__":
    input_text = "Hi this is AI with Sneha!"
    output_file = "gtts_testing.mp3"
    
    if text_to_speech_with_gtts(input_text, output_file):
        print("Conversion successful, now playing audio...")
        play_audio(output_file)  # ✅ Play the sound automatically
    else:
        print("Process failed")
