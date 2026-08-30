"""
Model Adapter Module for ModelLoop.
Provides a unified, model-agnostic execution interface across multiple LLM providers:
1. Google GenAI (Native Gemini SDK)
2. Anthropic (Claude models via API/SDK)
3. OpenAI-Compatible Gateways (OpenCode Zen, OpenRouter, Custom Endpoints)
"""

import os
import json
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# Registry of supported/configurable providers and expanded model catalog
PROVIDER_CONFIGS = {
    "google": {
        "name": "Google GenAI",
        "type": "native_google",
        "env_key": "GEMINI_API_KEY",
        "default_model": "gemini-3.6-flash",
        "models": [
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-3.1-pro",
            "gemini-2.5-flash",
            "gemini-1.5-flash"
        ],
        "model_display_names": {
            "gemini-3.6-flash": "Gemini 3.6 Flash",
            "gemini-3.7-flash": "Gemini 3.7 Flash",
            "gemini-3.5-flash": "Gemini 3.5 Flash",
            "gemini-3.1-pro": "Gemini 3.1 Pro",
            "gemini-2.5-flash": "Gemini 2.5 Flash",
            "gemini-1.5-flash": "Gemini 1.5 Flash"
        }
    },
    "anthropic": {
        "name": "Anthropic",
        "type": "native_anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "model_display_names": {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
            "claude-3-5-haiku-20241022": "Claude 3.5 Haiku"
        }
    },
    "opencode_zen": {
        "name": "OpenCode Zen / OpenAI Gateway",
        "type": "openai_compatible",
        "env_key": "OPENCODE_API_KEY",
        "base_url": os.getenv("OPENCODE_BASE_URL", "https://api.opencode.zen/v1"),
        "default_model": "zai-org/glm-5.2-maas",
        "models": [
            "zai-org/glm-5.2-maas",
            "zen-pro",
            "zen-flash",
            "zen-coder"
        ],
        "model_display_names": {
            "zai-org/glm-5.2-maas": "GLM 5.2 MAAS (zai-org/glm-5.2-maas)",
            "zen-pro": "Zen Pro",
            "zen-flash": "Zen Flash",
            "zen-coder": "Zen Coder"
        }
    },
    "openai_compatible": {
        "name": "Custom OpenAI-Compatible Endpoint",
        "type": "openai_compatible",
        "env_key": "CUSTOM_PROVIDER_API_KEY",
        "base_url": os.getenv("CUSTOM_PROVIDER_BASE_URL", "http://localhost:8000/v1"),
        "default_model": os.getenv("CUSTOM_PROVIDER_MODEL", "custom-model"),
        "models": [os.getenv("CUSTOM_PROVIDER_MODEL", "custom-model")],
        "model_display_names": {
            os.getenv("CUSTOM_PROVIDER_MODEL", "custom-model"): os.getenv("CUSTOM_PROVIDER_MODEL", "Custom OpenAI-Compatible Model")
        }
    }
}

def get_provider_status(provider_id):
    """Checks if API key for a provider is configured in environment."""
    config = PROVIDER_CONFIGS.get(provider_id)
    if not config:
        return {"configured": False, "reason": "Unknown provider", "key_name": "N/A"}
    
    key_name = config["env_key"]
    api_key = os.getenv(key_name)
    
    if api_key and api_key != "your_dummy_key_here" and len(api_key.strip()) > 5:
        return {"configured": True, "key_name": key_name}
    return {"configured": False, "key_name": key_name, "reason": f"{key_name} not set in environment"}

def call_model_adapter(prompt, provider_id="google", model_name=None):
    """
    Unified entry point for sending prompts to LLM providers.
    Returns normalized response dict:
    {
        "text": str,
        "provider": str,
        "model": str,
        "status": "live" | "fallback" | "error",
        "error": str or None
    }
    """
    config = PROVIDER_CONFIGS.get(provider_id, PROVIDER_CONFIGS["google"])
    selected_model = model_name or config["default_model"]
    status_info = get_provider_status(provider_id)
    
    # Provider 1: Google GenAI (Native Gemini SDK)
    if config["type"] == "native_google":
        return _call_google_genai(prompt, selected_model, status_info)
        
    # Provider 2: Anthropic (Claude)
    elif config["type"] == "native_anthropic":
        return _call_anthropic(prompt, selected_model, status_info)
        
    # Provider 3: OpenAI-Compatible Gateway (OpenCode Zen / Custom)
    elif config["type"] == "openai_compatible":
        return _call_openai_compatible(prompt, config, selected_model, status_info)
        
    return {
        "text": "Error: Unsupported provider type",
        "provider": config["name"],
        "model": selected_model,
        "status": "error",
        "error": "Unsupported provider type"
    }

def test_provider_connection(provider_id, model_name=None):
    """Executes a 1-token light test request to verify API connection."""
    config = PROVIDER_CONFIGS.get(provider_id, PROVIDER_CONFIGS["google"])
    status_info = get_provider_status(provider_id)
    if not status_info["configured"]:
        return {
            "status": "not_configured",
            "message": f"Cannot test connection: {status_info['key_name']} is missing in environment.",
            "provider": config["name"]
        }
    
    res = call_model_adapter("Ping", provider_id=provider_id, model_name=model_name)
    if res["status"] == "live":
        return {"status": "live", "message": f"Connection verified successfully for {config['name']} ({res['model']}).", "provider": config["name"]}
    elif res["status"] == "fallback":
        return {"status": "fallback", "message": f"Rate-limit or error hit. Operating in fallback execution mode.", "provider": config["name"]}
    else:
        return {"status": "error", "message": f"Connection failed: {res['error']}", "provider": config["name"]}

def _call_google_genai(prompt, model_name, status_info):
    """Call Google GenAI via SDK, falling back to simulation if rate-limited or unconfigured."""
    if not status_info["configured"]:
        from main import get_simulated_gemini_response
        return {
            "text": get_simulated_gemini_response(prompt),
            "provider": "Google GenAI",
            "model": model_name,
            "status": "fallback",
            "error": "GEMINI_API_KEY unconfigured; running in fallback mode"
        }
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        time.sleep(0.3)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if not response or not response.text:
            raise Exception("Empty response from Google GenAI API")
        return {
            "text": response.text,
            "provider": "Google GenAI",
            "model": model_name,
            "status": "live",
            "error": None
        }
    except Exception as e:
        from main import get_simulated_gemini_response
        return {
            "text": get_simulated_gemini_response(prompt),
            "provider": "Google GenAI",
            "model": model_name,
            "status": "fallback",
            "error": f"API note: {str(e)[:100]}"
        }

def _call_anthropic(prompt, model_name, status_info):
    """Call Anthropic API if key is set, else return unconfigured error."""
    if not status_info["configured"]:
        return {
            "text": f"Error: ANTHROPIC_API_KEY not configured in environment.",
            "provider": "Anthropic",
            "model": model_name,
            "status": "error",
            "error": "ANTHROPIC_API_KEY missing"
        }
    api_key = os.getenv("ANTHROPIC_API_KEY")
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": model_name,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            text = res_json.get("content", [{}])[0].get("text", "")
            return {
                "text": text,
                "provider": "Anthropic",
                "model": model_name,
                "status": "live",
                "error": None
            }
    except Exception as e:
        return {
            "text": f"Anthropic API Error: {str(e)}",
            "provider": "Anthropic",
            "model": model_name,
            "status": "error",
            "error": str(e)
        }

def _call_openai_compatible(prompt, config, model_name, status_info):
    """Call generic OpenAI-compatible chat completions endpoint."""
    key_name = config["env_key"]
    if not status_info["configured"]:
        return {
            "text": f"Error: {key_name} not configured in environment.",
            "provider": config["name"],
            "model": model_name,
            "status": "error",
            "error": f"{key_name} missing"
        }
    api_key = os.getenv(key_name)
    base_url = config.get("base_url", "").rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    try:
        req = urllib.request.Request(endpoint, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            text = res_json["choices"][0]["message"]["content"]
            return {
                "text": text,
                "provider": config["name"],
                "model": model_name,
                "status": "live",
                "error": None
            }
    except Exception as e:
        return {
            "text": f"API Error ({config['name']}): {str(e)}",
            "provider": config["name"],
            "model": model_name,
            "status": "error",
            "error": str(e)
        }
