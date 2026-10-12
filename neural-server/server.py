"""Optional neural French TTS backend for Voice Studio. Deploy separately from GitHub Pages."""
import asyncio
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
import edge_tts

app = FastAPI()
origin = os.environ.get("ALLOWED_ORIGIN", "").strip()
if not origin:
    raise RuntimeError("Set ALLOWED_ORIGIN to your exact GitHub Pages origin")
app.add_middleware(CORSMiddleware, allow_origins=[origin], allow_methods=["POST"], allow_headers=["Content-Type"])

class Segment(BaseModel):
    speaker: str = Field(max_length=50)
    text: str = Field(min_length=1, max_length=3000)

class Request(BaseModel):
    items: list[Segment] = Field(min_length=1, max_length=50)
    lang: str = "fr-FR"
    rate: float = Field(default=0.9, ge=0.6, le=1.4)

@app.post("/api/tts")
async def tts(req: Request):
    if req.lang not in ("fr-FR", "fr-CA", "en-US"):
        raise HTTPException(400, "Unsupported language")
    if sum(len(x.text) for x in req.items) > 12000:
        raise HTTPException(413, "Text too long")
    speakers = list(dict.fromkeys(x.speaker for x in req.items))
    voice_pair = {"fr-FR": ("fr-FR-DeniseNeural", "fr-FR-HenriNeural"),
                  "fr-CA": ("fr-CA-SylvieNeural", "fr-CA-AntoineNeural"),
                  "en-US": ("en-US-JennyNeural", "en-US-GuyNeural")}[req.lang]
    rate = round((req.rate - 1) * 100)
    with tempfile.TemporaryDirectory() as tmp:
        chunks = []
        for i, item in enumerate(req.items):
            voice = voice_pair[speakers.index(item.speaker) % 2]
            path = Path(tmp) / f"{i:03d}.mp3"
            try:
                await edge_tts.Communicate(item.text, voice, rate=f"{rate:+d}%").save(str(path))
            except Exception:
                raise HTTPException(502, "Neural speech service unavailable")
            chunks.append(path.read_bytes())
        # MP3 frame streams can be concatenated for basic playback; for gapless audio use FFmpeg.
        return Response(content=b"".join(chunks), media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=french-voice.mp3"})
