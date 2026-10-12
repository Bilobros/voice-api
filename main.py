from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import uuid
import os
import tempfile

app = FastAPI()

# Vercel ko browser se connect karne ke liye CORS
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
async def generate_audio(request: TTSRequest, background_tasks: BackgroundTasks):
    try:
        # Vercel par temporary folder mein file save karna
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        rate_val = int((request.speed - 1.0) * 100)
        rate_str = f"{rate_val:+d}%"
        pitch_str = f"{request.pitch:+d}Hz"
        
        communicate = edge_tts.Communicate(request.text, request.voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(filepath)
        
        # Audio send hote hi server se mp3 kachra saaf kar do
        background_tasks.add_task(os.remove, filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Vercel Backend is Live!"}
