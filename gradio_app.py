import os
import gradio as gr
import asyncio
import pydub  # For audio duration extraction

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

# System prompt
system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

async def process_inputs(audio_filepath, image_filepath):
    if audio_filepath is None and image_filepath is None:
        yield "", "", None
        return

    yield "", "Analyzing, please wait...", None

    speech_to_text_output = ""
    doctor_response = "No image provided to analyze."

    if audio_filepath:
        # Convert to WAV if the file format is problematic or unclear
        if not audio_filepath.endswith('.wav'):
            converted_audio_filepath = "converted_audio.wav"
            audio = pydub.AudioSegment.from_file(audio_filepath)
            audio.export("converted_audio.wav", format="wav", codec="pcm_s16le")
            audio_filepath = converted_audio_filepath  # Use the converted file for processing

        # Extract audio duration using pydub
        audio = pydub.AudioSegment.from_file(audio_filepath)
        audio_duration = len(audio) / 1000  # duration in seconds
        print(f"Audio Duration: {audio_duration} seconds")  # Debugging purpose

        speech_to_text_output = await asyncio.to_thread(
            transcribe_with_groq,
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )

    if image_filepath:
        doctor_response = await asyncio.to_thread(
            analyze_image_with_query,
            query=system_prompt + speech_to_text_output,
            encoded_image=encode_image(image_filepath),
            model="llama-3.2-11b-vision-preview"
        )

    await asyncio.to_thread(
        text_to_speech_with_gtts,
        input_text=doctor_response,
        output_filepath="final.mp3"
    )

    yield speech_to_text_output, doctor_response, "final.mp3"

# ✨ CSS with improved description styling
css = """
body {
    background: linear-gradient(135deg, #d4fc79, #96e6a1);
    font-family: 'Segoe UI', sans-serif;
    animation: fadein 1s ease-in;
    margin: 0;
}

h1 {
    text-align: center;
    color: #2b6777;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
    animation: slidein 1s ease;
}

.gradio-container {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    animation: fadein 1.5s ease-in;
}

.gr-button {
    background-color: #52ab98;
    color: white;
    font-weight: 600;
    font-size: 18px;
    padding: 12px 24px;
    border-radius: 25px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0px 5px 15px rgba(82, 171, 152, 0.4);
}

.gr-button:hover {
    background-color: #2b6777;
    transform: scale(1.05);
}

.gr-textbox, .gr-audio {
    border-radius: 16px;
    background-color: #f4f9f9;
    border: 1px solid #d3e0ea;
    padding: 10px;
    font-size: 16px;
}

.gr-textbox:focus {
    border-color: #52ab98;
    outline: none;
}

audio {
    width: 100%;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slidein {
    from { transform: translateX(-30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* ✅ Proper fix: darker description */
.prose > p {
    color: #2b2b2b !important;
    font-weight: 500;
    font-size: 18px;
}
"""

# Gradio UI
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎤 Speak Your Question"),
        gr.Image(type="filepath", label="🖼️ Upload a Medical Image")
    ],
    outputs=[
        gr.Textbox(label="📝 Transcribed Text"),
        gr.Textbox(label="🧠 Doctor's Insight"),
        gr.Audio(label="🔈 Audio Response", autoplay=True)
    ],
    title="🧑‍⚕️ AI Medical Doctor Bot",
    description="Ask your skin health query and upload a medical image. The AI Doctor will analyze and provide a human-like response!",
    css=css,
    flagging_mode="never"

)

iface.launch(debug=True)
#http://127.0.0.1:7860/