from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import uuid
import os

app = FastAPI()

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
    speed: float = 1.0
    pitch: int = 0

@app.post("/api/generate")
async def generate_audio(request: TTSRequest):
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Convert speed (e.g., 1.5) to edge-tts rate format (e.g., "+50%")
        rate_val = int((request.speed - 1.0) * 100)
        rate_str = f"{rate_val:+d}%"
        
        # Convert pitch (e.g., 5) to edge-tts pitch format (e.g., "+5Hz")
        pitch_str = f"{request.pitch:+d}Hz"
        
        communicate = edge_tts.Communicate(
            request.text, 
            request.voice,
            rate=rate_str,
            pitch=pitch_str
        )
        await communicate.save(filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
