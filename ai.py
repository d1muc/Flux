import os
import json
import platform
import urllib.request
import urllib.error

def get_os_info():
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
    except Exception:
        pass
    return f"{platform.system()} {platform.release()}"

def get_ollama_models():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            return [model['name'] for model in data.get('models', [])]
    except Exception:
        return []

def generate_ai_command(prompt, model, history):
    os_info = get_os_info()
    hist_str = " | ".join(history[-10:]) if history else "None"
    
    system_prompt = (
        "You are a strict CLI assistant for a Unix-like terminal. "
        f"CRITICAL SYSTEM CONTEXT: Working directory: {os.getcwd()}. System: {os_info}. "
        f"Their recent terminal history (last 10 commands): {hist_str}. "
        "Based on the user's natural language request, generate ONLY the raw shell command. "
        "Do not use Markdown formatting. Do not output backticks. Do not explain the command. Just the command."
    )
    
    data = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
            cmd = result.get('response', '').strip()
            if cmd.startswith('```'):
                lines = cmd.split('\n')
                if len(lines) >= 2:
                    cmd = '\n'.join(lines[1:-1]).strip() if lines[-1].strip() == '```' else '\n'.join(lines[1:]).strip()
            return cmd
    except Exception as e:
        return f"echo 'AI Error: {e}'"