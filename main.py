from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import uuid
import os

app = FastAPI()

# CORS settings - iski wajah se aapka frontend asani se connect ho jayega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str

@app.post("/api/generate")
async def generate_audio(request: TTSRequest):
    try:
        # Generate a unique audio file name
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Connect to Edge TTS and generate speech
        communicate = edge_tts.Communicate(request.text, request.voice)
        await communicate.save(filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
