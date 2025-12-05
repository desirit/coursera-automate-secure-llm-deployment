from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    response = requests.post(
        f'{OLLAMA_HOST}/api/generate',
        json={'model': 'llama3.2', 'prompt': data.get('prompt', 'Hi'), 'stream': False},
        timeout=60
    )
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
# v2
# v2
