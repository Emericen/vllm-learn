#!/usr/bin/env python3
"""Simple test for vLLM inference server"""
import base64
import time
import os
import asyncio
import json
import websockets
from openai import OpenAI


MODEL = os.getenv("MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
HTTP_PORT = int(os.getenv("PORT", "8000"))
WS_PORT = int(os.getenv("WS_PORT", "8001"))


def test_http_api():
    # Initialize client
    client = OpenAI(base_url=f"http://192.222.55.38:{HTTP_PORT}/v1", api_key="EMPTY")

    # Read and encode image
    with open("data/test-img.png", "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    # Test vision chat
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What food do you see in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=1024,
        stream=True,
    )

    response = ""
    start_time = time.time()
    first_token = False
    for chunk in stream:
        if chunk.choices[0].delta.content:
            if not first_token:
                first_token = True
                ttft = time.time() - start_time
                print(f"TTFT: {ttft:.2f}s")
            response += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="", flush=True)

    print()


async def test_websocket():
    """Test WebSocket functionality"""
    uri = f"ws://192.222.55.38:8001"

    try:
        print("\n=== WebSocket Test ===")
        async with websockets.connect(uri) as websocket:
            # Read and encode image for WebSocket test
            with open("data/test-img.png", "rb") as f:
                base64_image = base64.b64encode(f.read()).decode("utf-8")

            # Send a test message with image
            message = {
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "What food do you see in this image?"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                        ]
                    }
                ],
                "max_tokens": 100,
            }

            await websocket.send(json.dumps(message))
            print("Message sent. Waiting for response...")

            # Listen for response tokens
            full_response = ""
            start_time = time.time()
            first_token = False

            async for response in websocket:
                data = json.loads(response)

                if data["type"] == "token":
                    if not first_token:
                        first_token = True
                        ttft = time.time() - start_time
                        print(f"TTFT: {ttft:.2f}s")
                    content = data["content"]
                    full_response += content
                    print(content, end="", flush=True)

                elif data["type"] == "complete":
                    print()
                    break

                elif data["type"] == "error":
                    print(f"\nError: {data['message']}")
                    break

    except Exception as e:
        print(f"WebSocket connection error: {e}")
        print("Make sure the vLLM server is running with WebSocket support")


def main():
    # print("=== HTTP API Test ===")
    # test_http_api()

    print("\nStarting WebSocket test...")
    asyncio.run(test_websocket())


if __name__ == "__main__":
    main()
