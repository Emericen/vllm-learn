#!/usr/bin/env python3
"""
FastAPI WebSocket proxy for vLLM:
- Connects to external vLLM service via HTTP API
- Provides WebSocket interface for streaming completions
"""

import os
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from openai import AsyncOpenAI

# Configuration via env vars
MODEL = os.getenv("MODEL", "Qwen/Qwen2.5-VL-3B-Instruct")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://vllm:8000/v1")
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8001"))

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.websocket("/")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = AsyncOpenAI(base_url=VLLM_BASE_URL, api_key="EMPTY")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            stream = None
            try:
                stream = await client.chat.completions.create(
                    model=data.get("model", MODEL),
                    messages=data.get("messages", []),
                    max_tokens=data.get("max_tokens", 100),
                    stream=True,
                )

                async for chunk in stream:
                    try:
                        content = chunk.choices[0].delta.content  # type: ignore[attr-defined]
                    except Exception:
                        content = None
                    if content:
                        await websocket.send_text(
                            json.dumps({"type": "token", "content": content})
                        )

                await websocket.send_text(json.dumps({"type": "complete"}))

            except Exception as e:
                # Clean up stream if it exists
                if stream:
                    try:
                        await stream.aclose()
                    except:
                        pass
                
                await websocket.send_text(
                    json.dumps({"type": "error", "message": str(e)})
                )

    except WebSocketDisconnect:
        # Clean up stream on disconnect
        if 'stream' in locals() and stream:
            try:
                await stream.aclose()
            except:
                pass


if __name__ == "__main__":
    uvicorn.run("main:app", host=WS_HOST, port=WS_PORT, log_level="info")
