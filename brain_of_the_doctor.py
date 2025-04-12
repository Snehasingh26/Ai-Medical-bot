# Step 1: Setup GROQ API Key
import os
import base64
from groq import Groq
from dotenv import load_dotenv  # ✅ Load environment variables

# Load environment variables from .env file
load_dotenv()

# ✅ Get API Key Correctly
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ Error: GROQ_API_KEY is missing. Check your .env file.")

# Step 2: Convert image to required format (Function from trainer's code)
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ Error: The file '{image_path}' was not found.")

# Step 3: Setup Multimodal LLM (Function from trainer's code)
def analyze_image_with_query(query, model, encoded_image):
    client = Groq(api_key=GROQ_API_KEY)  # ✅ Pass the API key correctly

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                },
            ],
        }
    ]
    
    try:
        chat_completion = client.chat.completions.create(
            model=model,
            messages=messages  # ✅ Fix: `messages` should come **before** `model`
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# Main Function to call image analysis (Updated for Gradio integration)
def analyze_and_display(image_path, query="Is there something wrong with my face?", model="llama-3.2-90b-vision-preview"):
    encoded_image = encode_image(image_path)
    result = analyze_image_with_query(query, model, encoded_image)
    return result

# For Testing (Before Integration with Gradio)
image_path = "skin.jpg"
result = analyze_and_display(image_path)
if result:
    print("🔍 Analysis Result:", result)
