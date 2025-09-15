# vLLM WebSocket Server

Docker Compose setup with separate vLLM and WebSocket proxy containers. 

## Quick Start

```bash
make run                                           # Default model
make run MODEL=Qwen/Qwen2.5-VL-7B-Instruct       # Custom model
make logs                                          # All service logs
make logs-vllm                                     # vLLM only
make logs-proxy                                    # WebSocket proxy only
make stop                                          # Stop services
```

## Services

- **vLLM**: Official `vllm/vllm-openai` image with GPU access
- **WebSocket Proxy**: Lightweight FastAPI service that streams completions

## Endpoints

- HTTP API: `http://localhost:8000/v1`
- WebSocket: `ws://localhost:8001`

## Configuration

Override defaults:
```bash
make run MODEL=meta-llama/Llama-3.2-3B-Instruct HOST_HTTP_PORT=9000 HOST_WS_PORT=9001
```

## Requirements

- Docker with GPU support (`gpus: all`)
- NVIDIA drivers + CUDA toolkit
