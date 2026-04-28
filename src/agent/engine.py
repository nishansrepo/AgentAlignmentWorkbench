"""
agent/engine.py - Local LLM agent using Ollama.
Model: Qwen3 8B. Pull with: ollama pull qwen3:8b
"""
from __future__ import annotations
import json, logging, time

logger = logging.getLogger(__name__)
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_TEMPERATURE = 0.7
OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_status():
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return {"running": True, "models": [m["name"] for m in data.get("models", [])], "error": ""}
    except Exception as e:
        return {"running": False, "models": [], "error": f"Ollama not running. Start with: ollama serve"}

def call_ollama(model, system_prompt, messages, temperature=DEFAULT_TEMPERATURE):
    import urllib.request, urllib.error
    full = [{"role": "system", "content": system_prompt}] + messages
    payload = json.dumps({"model": model, "messages": full, "stream": False,
                          "options": {"temperature": temperature}}).encode()
    req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/chat", data=payload,
                                headers={"Content-Type": "application/json"}, method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode())
            content = data.get("message", {}).get("content", "")
            if "<think>" in content and "</think>" in content:
                content = content[content.index("</think>") + len("</think>"):].strip()
            return {"status": "OK", "content": content, "model": model,
                    "latency_s": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "ERROR", "content": f"Error: {e}", "model": model,
                "latency_s": round(time.time() - start, 2)}

class CorporateAgent:
    def __init__(self, org_config, document_store=None, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
        self.org_config = org_config
        self.document_store = document_store
        self.model = model
        self.temperature = temperature
        self.conversation_history = []
        self._system_prompt = org_config.build_system_prompt()

    def respond(self, user_message, speaker_name, speaker_role, speaker_relationship):
        speaker_ctx = f"[{speaker_name}, {speaker_role} ({speaker_relationship} to you), is speaking to you.]"
        retrieved_chunks = []
        retrieved_context = ""
        if self.document_store and self.document_store.count > 0:
            chunks = self.document_store.query(user_message, n_results=3)
            if chunks:
                retrieved_chunks = chunks
                parts = [f"[Reference from {c.get('filename','')}]\n{c['text']}" for c in chunks]
                retrieved_context = "\n\nRelevant information from your briefing documents:\n" + "\n\n".join(parts)
        full_system = self._system_prompt + (("\n\n" + retrieved_context) if retrieved_context else "")
        formatted = f"{speaker_ctx}\n\n{user_message}"
        self.conversation_history.append({"role": "user", "content": formatted})
        result = call_ollama(self.model, full_system, self.conversation_history, self.temperature)
        if result["status"] == "OK":
            self.conversation_history.append({"role": "assistant", "content": result["content"]})
        return {"content": result.get("content", ""), "status": result.get("status", "ERROR"),
                "latency_s": result.get("latency_s", 0), "model": self.model,
                "retrieved_chunks": retrieved_chunks, "full_system_prompt": full_system,
                "speaker_info": {"name": speaker_name, "role": speaker_role, "relationship": speaker_relationship}}

    def reset_conversation(self):
        self.conversation_history = []

    def get_conversation_length(self):
        return len(self.conversation_history) // 2
