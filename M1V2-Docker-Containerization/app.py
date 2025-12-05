#!/usr/bin/env python3
"""
LLM Inference API Wrapper
Connects to Ollama running on host machine
"""
from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# Connect to Ollama on host machine
# host.docker.internal works on Mac/Windows Docker Desktop
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'llama3.2')

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        resp = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
        models = [m['name'] for m in resp.json().get('models', [])]
        return jsonify({
            "status": "healthy",
            "ollama_connected": True,
            "available_models": models
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "ollama_connected": False,
            "error": str(e)
        }), 503

@app.route('/v1/completions', methods=['POST'])
def completions():
    """OpenAI-compatible completions endpoint"""
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', DEFAULT_MODEL)
    max_tokens = data.get('max_tokens', 100)
    
    start_time = time.time()
    
    response = requests.post(
        f'{OLLAMA_HOST}/api/generate',
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {'num_predict': max_tokens}
        },
        timeout=60
    )
    
    result = response.json()
    latency = time.time() - start_time
    
    return jsonify({
        "id": f"cmpl-{int(time.time())}",
        "object": "text_completion",
        "model": model,
        "choices": [{
            "text": result.get('response', ''),
            "index": 0,
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": result.get('prompt_eval_count', 0),
            "completion_tokens": result.get('eval_count', 0),
            "total_tokens": result.get('prompt_eval_count', 0) + result.get('eval_count', 0)
        },
        "latency_seconds": round(latency, 2)
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available models"""
    resp = requests.get(f'{OLLAMA_HOST}/api/tags')
    models = resp.json().get('models', [])
    
    return jsonify({
        "object": "list",
        "data": [{"id": m['name'], "object": "model"} for m in models]
    })

if __name__ == '__main__':
    print(f"🚀 Starting LLM API server...")
    print(f"📡 Connecting to Ollama at: {OLLAMA_HOST}")
    app.run(host='0.0.0.0', port=8000, debug=False)

# Version 2.0 - 04:04:16
