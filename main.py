#!/usr/bin/env python3
"""
Direct vLLM approach with FastAPI WebSocket
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from vllm import LLM, SamplingParams
import uvicorn
import json

# Configuration
MODEL = os.getenv("MODEL", "Qwen/Qwen2.5-VL-3B-Instruct")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize model on startup, cleanup on shutdown"""
    print(f"Loading model: {MODEL}")
    app.state.llm = LLM(
        model=MODEL,
        trust_remote_code=True,
        max_model_len=2048,
        gpu_memory_utilization=0.9,
    )
    print("Model loaded successfully")
    yield
    # Cleanup (if needed)


# Initialize FastAPI app with lifespan
app = FastAPI(title="vLLM WebSocket Server", version="1.0.0", lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat completions"""
    await websocket.accept()
    print(f"WebSocket client connected: {websocket.client}")

    llm = websocket.app.state.llm  # Get model from app state

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            try:
                # Extract messages and convert to prompt
                messages = data.get("messages", [])
                if messages:
                    # For chat models, use proper chat template
                    if hasattr(llm, "chat"):
                        # Use chat method for instruction-tuned models
                        outputs = llm.chat(
                            messages,
                            SamplingParams(
                                temperature=data.get("temperature", 0.8),
                                top_p=data.get("top_p", 0.95),
                                max_tokens=data.get("max_tokens", 100),
                            ),
                        )
                    else:
                        # Fallback to simple prompt construction
                        prompt = messages[-1].get("content", "")
                        sampling_params = SamplingParams(
                            temperature=data.get("temperature", 0.8),
                            top_p=data.get("top_p", 0.95),
                            max_tokens=data.get("max_tokens", 100),
                        )
                        outputs = llm.generate(prompt, sampling_params)
                else:
                    prompt = data.get("prompt", "")
                    sampling_params = SamplingParams(
                        temperature=data.get("temperature", 0.8),
                        top_p=data.get("top_p", 0.95),
                        max_tokens=data.get("max_tokens", 100),
                    )
                    outputs = llm.generate(prompt, sampling_params)

                # Extract generated text
                generated_text = outputs[0].outputs[0].text

                # Send response
                await websocket.send_json({"type": "token", "content": generated_text})
                await websocket.send_json({"type": "complete"})

            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        print("WebSocket client disconnected")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": MODEL}


@app.get("/")
async def root():
    """Root endpoint with usage info"""
    return {
        "message": "vLLM WebSocket Server",
        "websocket_url": f"ws://{HOST}:{PORT}/ws",
        "model": MODEL,
    }


if __name__ == "__main__":
    print(f"Starting vLLM FastAPI WebSocket server")
    print(f"Model: {MODEL}")
    print(f"WebSocket endpoint: ws://{HOST}:{PORT}/ws")

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
