import json
import logging
import os
import urllib.request

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma4:e2b")


def summarize_incident(incident) -> str:
    prompt = (
        "You are a workplace safety analyst. Summarize the following detected "
        "incident in 1-2 factual sentences. Do not invent causes or conclusions.\n\n"
        f"Type: {incident.type}\nSeverity: {incident.severity}\n"
        f"Status: {incident.status}\nDescription: {incident.description}\n"
        f"Camera ID: {incident.camera_id}\nTimestamp: {incident.timestamp}\n"
        f"Tracking ID: {incident.tracking_id}\nConfidence: {incident.confidence:.2f}\n"
    )
    try:
        body = json.dumps({
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        text = data.get("response", "").strip()
        if text:
            return text
    except Exception as exc:
        logger.warning("LLM summarization failed: %s", exc)
    return (
        f"Incident of type {incident.type} with {incident.severity} severity "
        f"was detected at {incident.timestamp}. {incident.description}"
    )
