from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
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

# Database Setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            status TEXT DEFAULT 'inactive'
        )
    """)
    conn.commit()
    conn.close()

init_db()

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TTSRequest(BaseModel):
    text: str
    voice: str
    speed: float = 1.0
    pitch: int = 0

@app.post("/api/signup")
def signup(user: SignupRequest):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password, status) VALUES (?, ?, 'inactive')", (user.email, user.password))
        conn.commit()
        return {"message": "Account created successfully! Please pay 1499 PKR and contact on WhatsApp for activation."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered!")
    finally:
        conn.close()

@app.post("/api/login")
def login(user: LoginRequest):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE email = ? AND password = ?", (user.email, user.password))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=400, detail="Invalid email or password!")
    
    status = row[0]
    if status != 'active':
        raise HTTPException(status_code=403, detail="Account is inactive! Please complete payment on WhatsApp.")
    
    return {"message": "Login successful", "status": "active"}

# Simple Admin route to activate users directly from browser/API
@app.get("/api/admin/activate/{email}")
def activate_user(email: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'active' WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return {"message": f"User {email} activated successfully!"}

@app.post("/api/generate")
async def generate_audio(request: TTSRequest):
    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        rate_val = int((request.speed - 1.0) * 100)
        rate_str = f"{rate_val:+d}%"
        pitch_str = f"{request.pitch:+d}Hz"
        
        communicate = edge_tts.Communicate(request.text, request.voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(filepath)
        
        return FileResponse(filepath, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
