# Service configuration (override on invocation)
# Example: make run MODEL=Qwen/Qwen2.5-VL-7B-Instruct HOST_HTTP_PORT=8000 HOST_WS_PORT=8001
MODEL ?= Qwen/Qwen2.5-VL-3B-Instruct
VLLM_TAG ?= latest
HOST_HTTP_PORT ?= 8000
HOST_WS_PORT ?= 8001

.PHONY: build up down logs logs-vllm logs-proxy restart clean

build:
	@echo "Building WebSocket proxy image..."
	MODEL=$(MODEL) VLLM_TAG=$(VLLM_TAG) HOST_HTTP_PORT=$(HOST_HTTP_PORT) HOST_WS_PORT=$(HOST_WS_PORT) \
	docker compose build

up:
	@echo "Starting vLLM server with WebSocket proxy..."
	@echo "HTTP API available at: http://localhost:$(HOST_HTTP_PORT)/v1"
	@echo "WebSocket API available at: ws://localhost:$(HOST_WS_PORT)"
	MODEL=$(MODEL) VLLM_TAG=$(VLLM_TAG) HOST_HTTP_PORT=$(HOST_HTTP_PORT) HOST_WS_PORT=$(HOST_WS_PORT) \
	docker compose up -d
	@echo "Services started. Use 'make logs' to see output."

# Legacy alias for 'up'
run: up

down:
	@echo "Stopping services..."
	docker compose down

logs:
	@echo "Following logs for all services..."
	docker compose logs -f

logs-vllm:
	@echo "Following logs for vLLM service..."
	docker compose logs -f vllm

logs-proxy:
	@echo "Following logs for WebSocket proxy..."
	docker compose logs -f websocket-proxy

restart: down up

clean: down
	@echo "Cleaning up..."
	docker compose down --rmi local --volumes --remove-orphans
	@echo "Cleanup complete."
