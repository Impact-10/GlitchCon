from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Initialize FastAPI app
app = FastAPI()

#  Enable CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Modify this for security in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

#  Set up Gemini API Key (Replace with your actual API key)
GENAI_API_KEY = "AIzaSyCFew-OOxPjDWG-6Sr93L5FyBLcfXfghao"  # 🔴 Replace this with your actual API key
genai.configure(api_key=GENAI_API_KEY)

#  Define request model
class ChatRequest(BaseModel):
    message: str

#  Chatbot API endpoint
@app.post("/api/chatbot")
async def chatbot(request: ChatRequest):
    try:
        # Load the Gemini AI model
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Modify prompt to ensure simple, easy-to-understand explanations
        prompt = (
            f"Every reply should be based on banking unless specified otherwise. "
            f"Explain in a very simple way, so even an elderly person with no financial knowledge can understand: {request.message}"
        )

        response = model.generate_content(prompt)

        return {"response": response.text}
    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}

# Run the FastAPI app using:
# uvicorn chatbotapi:app --reload

