import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()


# ==============================
# ROOT
# ==============================
@app.get("/")
async def root():
    return {"status": "Server running successfully"}


# ==============================
# TEST LLM (Groq)
# ==============================
@app.get("/test-llm")
async def test_llm():
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    try:
        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Say hello in one sentence"}
            ]
        )

        return {
            "llm_response": response.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# TEST TTS (Cartesia Play)
# ==============================
@app.get("/test-tts")
async def test_tts():
    api_key = os.getenv("CARTESIA_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="CARTESIA_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Cartesia-Version": "2025-04-16",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": "sonic",
        "voice": {
            "mode": "id",
            "id": "79a125e8-cd45-4c13-8a67-188112f4dd22"
        },
        "transcript": "Hello, your AI voice system is now fully operational.",
        "output_format": {
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": 16000
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.cartesia.ai/v1/tts",
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return Response(
            content=response.content,
            media_type="audio/wav"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))