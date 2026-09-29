import os
import io
import json
import time
from typing import Optional
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from snapflow.core.whisper_engine import SnapWhisperEngine
from snapflow.core.refiner import EdgeRefiner
from snapflow.core.injector import TextInjector
from snapflow.core.audio import AudioRingBuffer

app = FastAPI(title="SnapFlow AI", description="Ultra-Low Latency Ambient Dictation for Snapdragon HP PCs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper_engine = SnapWhisperEngine()
edge_refiner = EdgeRefiner(is_enabled=False, default_style="clean_verbatim")
text_injector = TextInjector()

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SnapFlow AI</h1><p>Dashboard UI loading...</p>"


@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "provider": whisper_engine.provider_display_name,
        "is_npu": whisper_engine.is_npu_accelerated,
        "model": whisper_engine.model_name,
        "polish_enabled": edge_refiner.is_enabled,
        "default_style": edge_refiner.default_style,
        "target_soc": "Snapdragon X Elite / Plus (HP OmniBook Ultra)",
    }


@app.post("/api/refine")
async def api_refine(payload: dict):
    text = payload.get("text", "")
    style = payload.get("style", edge_refiner.default_style)
    result = edge_refiner.refine(text, style=style)
    return result


@app.post("/api/inject")
async def api_inject(payload: dict):
    text = payload.get("text", "")
    success = text_injector.type_text(text)
    return {"success": success, "length": len(text)}


@app.post("/api/transcribe-file")
async def api_transcribe_file(file: UploadFile = File(...)):
    content = await file.read()
    tmp_path = f"/tmp/{file.filename}"
    try:
        with open(tmp_path, "wb") as f:
            f.write(content)
        result = whisper_engine.transcribe_file(tmp_path)
        return result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.websocket("/ws/dictate")
async def websocket_dictate(websocket: WebSocket):
    await websocket.accept()
    client_ring_buffer = AudioRingBuffer(capacity_seconds=10.0, sample_rate=16000)

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data and data["bytes"]:
                raw_bytes = data["bytes"]
                audio_samples = np.frombuffer(raw_bytes, dtype=np.float32)
                client_ring_buffer.write(audio_samples)

                chunk = client_ring_buffer.get_last_n_seconds(2.0)
                if len(chunk) >= 8000:
                    transcription = whisper_engine.transcribe_chunk(chunk)
                    raw_text = transcription["text"]

                    if raw_text and edge_refiner.is_enabled:
                        refine_res = edge_refiner.refine(raw_text)
                        final_text = refine_res["refined"]
                        refine_latency = refine_res["latency_ms"]
                    else:
                        final_text = raw_text
                        refine_latency = 0.0

                    payload = {
                        "raw_text": raw_text,
                        "final_text": final_text,
                        "latency_ms": transcription["latency_ms"] + refine_latency,
                        "rtf": transcription["rtf"],
                        "provider": transcription["provider"],
                        "is_npu": transcription["is_npu"],
                        "joules_saved": transcription["joules_saved"],
                    }
                    await websocket.send_text(json.dumps(payload))

            elif "text" in data and data["text"]:
                msg = json.loads(data["text"])
                action = msg.get("action")
                if action == "update_settings":
                    edge_refiner.set_enabled(msg.get("polish_enabled", edge_refiner.is_enabled))
                    if "style" in msg:
                        edge_refiner.default_style = msg["style"]
                    await websocket.send_text(json.dumps({"status": "settings_updated"}))
                elif action == "inject":
                    text = msg.get("text", "")
                    text_injector.type_text(text)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
