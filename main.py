from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import uuid
import os
import tempfile

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

# Yeh function aapki index.html file ko direct website par open karega
@app.get("/")
def serve_home():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Error: index.html file nahi mili. Kripya GitHub mein file ka naam check karein.</h1>", status_code=404)

@app.post("/api/generate")
async def generate_audio(request: TTSRequest, background_tasks: BackgroundTasks):
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        rate_val = int((request.speed - 1.0) * 100)
        rate_str = f"{rate_val:+d}%"
        pitch_str = f"{request.pitch:+d}Hz"
        
        communicate = edge_tts.Communicate(request.text, request.voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(filepath)
        
        background_tasks.add_task(os.remove, filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
def test_audio():
    return {"status": "Success", "message": "Vercel Backend is Live!"}
