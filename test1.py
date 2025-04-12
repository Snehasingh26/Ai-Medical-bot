import os 
import gradio as gr
import asyncio
import uuid

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

# System prompt for AI Doctor
system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
What's in this image?. Do you find anything wrong with it medically? 
If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
Donot say 'In the image I see' but say 'With what I see, I think you have ....'
Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
Keep your answer concise (max 2 sentences). No preamble, start your answer right away please."""

async def process_inputs(audio_filepath, image_filepath):
    # Clear outputs if no input is provided
    if not audio_filepath and not image_filepath:
        return "", "", None

    speech_to_text_output = ""
    doctor_response = "No image provided for me to analyze"

    # Transcribe audio if provided
    if audio_filepath:
        speech_to_text_output = await asyncio.to_thread(
            transcribe_with_groq,
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )

    # Analyze image if provided
    if image_filepath:
        doctor_response = await asyncio.to_thread(
            analyze_image_with_query,
            query=system_prompt + speech_to_text_output,
            encoded_image=encode_image(image_filepath),
            model="llama-3.2-11b-vision-preview"
        )

    # Generate unique filename for each session
    unique_filename = f"temp_audio_{uuid.uuid4().hex}.mp3"

    # Convert doctor's response to speech
    await asyncio.to_thread(
        text_to_speech_with_gtts,
        input_text=doctor_response,
        output_filepath=unique_filename
    )

    return speech_to_text_output, doctor_response, unique_filename

# Gradio Interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Record Your Question"),
        gr.Image(type="filepath", label="Upload an Image")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio(autoplay=True, label="Doctor's Voice Response")
    ],
    title="AI Doctor with Vision and Voice"
)

iface.launch(debug=True)
#http://127.0.0.1:7860/