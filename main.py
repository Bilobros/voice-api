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
    rate: str = "+0%"
    pitch: str = "+0Hz"

@app.post("/api/generate")
async def generate_audio(request: TTSRequest):
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Now passing rate and pitch to the TTS engine
        communicate = edge_tts.Communicate(
            request.text, 
            request.voice,
            rate=request.rate,
            pitch=request.pitch
        )
        await communicate.save(filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
