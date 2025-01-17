from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.chatbot import MentalHealthChatbot
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

chatbot = MentalHealthChatbot(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    user_id = "user_123"  # Replace with a unique user ID in a real-world app
    response = chatbot.generate_response(user_message, user_id)
    return response