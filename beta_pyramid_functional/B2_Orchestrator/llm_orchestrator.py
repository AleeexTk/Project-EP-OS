import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, List, Optional, Dict
from urllib import error as urlerror
from urllib import request as urlrequest

import google.generativeai as genai

from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
from beta_pyramid_functional.B3_SessionRegistry.session_models import AgentSession, Provider

logger = logging.getLogger("llm_orchestrator")

_GEMINI_MODEL_CACHE: Optional[str] = None
_GEMINI_MODEL_LOCK = asyncio.Lock()
_GEMINI_QUOTA_BLOCK_UNTIL = 0.0
_GEMINI_QUOTA_BLOCK_REASON = ""
_PREFERRED_GEMINI_MODELS = (
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)
_OLLAMA_MODEL_CACHE: Optional[str] = None
_OLLAMA_MODEL_LOCK = asyncio.Lock()
_PREFERRED_OLLAMA_MODELS = (
    "qwen2.5:7b",
    "llama3.2:3b",
    "llama3.1:8b",
    "mistral:7b",
    "gemma3:4b",
)

def _normalize_model_name(raw_name: Any) -> Optional[str]:
    if raw_name is None:
        return None
    value = str(raw_name).strip()
    if not value:
        return None
    if "/" in value:
        value = value.split("/")[-1]
    return value


def _supports_generate_content(model: Any) -> bool:
    methods = getattr(model, "supported_generation_methods", None)
    if not methods:
        return True
    return any("generatecontent" in str(method).lower() for method in methods)


def _model_names_from_registry(models: List[Any]) -> List[str]:
    names: List[str] = []
    for model in models:
        if not _supports_generate_content(model):
            continue
        raw_name = getattr(model, "name", None) or getattr(model, "model_name", None)
        normalized = _normalize_model_name(raw_name)
        if normalized and normalized not in names:
            names.append(normalized)
    return names


async def _resolve_gemini_model(model_hint: Optional[str], force_refresh: bool = False) -> str:
    global _GEMINI_MODEL_CACHE

    hinted = _normalize_model_name(model_hint)
    if hinted:
        return hinted

    env_model = _normalize_model_name(os.getenv("GEMINI_MODEL"))
    if env_model:
        return env_model

    if _GEMINI_MODEL_CACHE and not force_refresh:
        return _GEMINI_MODEL_CACHE

    async with _GEMINI_MODEL_LOCK:
        if _GEMINI_MODEL_CACHE and not force_refresh:
            return _GEMINI_MODEL_CACHE

        available: List[str] = []
        try:
            registry = await asyncio.to_thread(lambda: list(genai.list_models()))
            available = _model_names_from_registry(registry)
        except Exception as exc:
            logger.warning("Gemini model discovery failed: %s", exc)

        for candidate in _PREFERRED_GEMINI_MODELS:
            if candidate in available:
                _GEMINI_MODEL_CACHE = candidate
                return candidate

        for name in available:
            if "flash" in name.lower():
                _GEMINI_MODEL_CACHE = name
                return name

        if available:
            _GEMINI_MODEL_CACHE = available[0]
        else:
            _GEMINI_MODEL_CACHE = _PREFERRED_GEMINI_MODELS[0]

        return _GEMINI_MODEL_CACHE

def _normalize_ollama_model_name(raw_name: Any) -> Optional[str]:
    if raw_name is None:
        return None
    value = str(raw_name).strip()
    return value or None


def _ollama_api_base() -> str:
    return os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434").rstrip("/")


def _ollama_request(method: str, path: str, payload: Optional[dict] = None, timeout: int = 30) -> dict:
    base = _ollama_api_base()
    url = f"{base}{path}"
    body = None
    headers = {"Accept": "application/json"}
    auth_header = os.getenv("OLLAMA_AUTH_HEADER", "").strip()
    api_key = os.getenv("OLLAMA_API_KEY", "").strip()
    if auth_header:
        headers["Authorization"] = auth_header
    elif api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urlrequest.Request(url=url, data=body, headers=headers, method=method)

    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urlerror.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        if len(detail) > 220:
            detail = detail[:220] + "..."
        raise RuntimeError(f"Ollama HTTP {exc.code} on {path}: {detail}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(
            f"Ollama is not reachable at {_ollama_api_base()}. Start 'ollama serve'."
        ) from exc

    if not raw.strip():
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned non-JSON payload from {path}.") from exc

    if isinstance(parsed, dict):
        return parsed
    return {}


def _ollama_list_models() -> List[str]:
    data = _ollama_request("GET", "/api/tags", timeout=12)
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list):
        return []

    names: List[str] = []
    for item in models:
        if not isinstance(item, dict):
            continue
        model_name = _normalize_ollama_model_name(item.get("name"))
        if model_name and model_name not in names:
            names.append(model_name)
    return names


async def _resolve_ollama_model(model_hint: Optional[str], force_refresh: bool = False) -> str:
    global _OLLAMA_MODEL_CACHE

    hinted = _normalize_ollama_model_name(model_hint)
    
    # Try to get what's actually on the machine
    available: List[str] = []
    try:
        available = await asyncio.to_thread(_ollama_list_models)
    except Exception as exc:
        logger.warning("Ollama model discovery failed: %s", exc)

    # 1. If user hinted a specific model, check if it exists locally
    if hinted:
        if hinted in available:
            return hinted
        # If hint not found, we'll continue to find a better one but log hint failure
        logger.warning("Hinted model '%s' not found in Ollama. Looking for alternatives...", hinted)

    # 2. Check environment variable
    env_model = _normalize_ollama_model_name(os.getenv("OLLAMA_MODEL"))
    if env_model and env_model in available:
        return env_model

    # 3. Use cache if valid
    if _OLLAMA_MODEL_CACHE and not force_refresh and _OLLAMA_MODEL_CACHE in available:
        return _OLLAMA_MODEL_CACHE

    async with _OLLAMA_MODEL_LOCK:
        # Re-check after lock
        if _OLLAMA_MODEL_CACHE and not force_refresh and _OLLAMA_MODEL_CACHE in available:
            return _OLLAMA_MODEL_CACHE

        # 4. Filter preferred models that actually exist
        for candidate in _PREFERRED_OLLAMA_MODELS:
            if candidate in available:
                _OLLAMA_MODEL_CACHE = candidate
                return candidate

        # 5. ABSOLUTE FALLBACK: Just take the first one that exists!
        if available:
            _OLLAMA_MODEL_CACHE = available[0]
            logger.info("Auto-selected fallback Ollama model: %s", _OLLAMA_MODEL_CACHE)
            return _OLLAMA_MODEL_CACHE
        else:
            # Nothing at all? Use a sane default but it might 404
            _OLLAMA_MODEL_CACHE = "llama3.2:3b"
            return _OLLAMA_MODEL_CACHE

def _is_quota_error(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "quota exceeded",
        "resource_exhausted",
        "rate limit",
        "429",
    )
    return any(marker in lowered for marker in markers)


def _is_hard_quota_lock(text: str) -> bool:
    lowered = text.lower()
    return bool(re.search(r"limit:\s*0\b", lowered))


def _extract_retry_seconds(text: str, default_seconds: int = 60) -> int:
    patterns = (
        r"please retry in\s+([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay\s*\{\s*seconds:\s*([0-9]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        try:
            return max(1, int(float(match.group(1))))
        except Exception:
            continue
    return default_seconds


def _quota_cooldown_message(
    session: AgentSession, retry_seconds: int, block_reason: str = ""
) -> str:
    if block_reason == "limit_zero":
        return (
            "[SYSTEM QUOTA] Gemini API quota is disabled for this project (limit=0). "
            f"Session moved to WAITING for {retry_seconds}s. "
            "Enable billing/quota in Google AI Studio for this key/project, then retry. "
            f"Use 'Open' to continue externally ({session.provider.upper()})."
        )

    return (
        "[SYSTEM QUOTA] Gemini API quota is exhausted for this project. "
        f"Session moved to WAITING for {retry_seconds}s. "
        f"Use 'Open' to continue externally ({session.provider.upper()}) "
        "or retry after cooldown."
    )



def _session_routing_policy(session: AgentSession) -> dict:
    linked_external = bool(str(session.external_url or "").strip())
    
    # Check for global Gemini quota block
    now = time.time()
    gemini_blocked = _GEMINI_QUOTA_BLOCK_UNTIL > now

    if session.provider == Provider.OLLAMA:
        return {
            "mode": "local_ollama",
            "reason": "provider_ollama",
            "linked_external": linked_external,
            "provider": session.provider,
        }

    if gemini_blocked and session.provider == Provider.GEMINI:
        return {
            "mode": "local_ollama",
            "reason": "gemini_quota_fallback",
            "linked_external": linked_external,
            "provider": Provider.OLLAMA, # Force Ollama for fallback
        }

    if linked_external:
        return {
            "mode": "local_ollama",
            "reason": "external_url_attached",
            "linked_external": True,
            "provider": session.provider,
        }

    if session.provider in (Provider.GPT, Provider.CLAUDE, Provider.COPILOT):
        return {
            "mode": "local_ollama",
            "reason": "browser_provider_bridge",
            "linked_external": False,
            "provider": session.provider,
        }

    return {
        "mode": "gemini_api",
        "reason": "gemini_cloud",
        "linked_external": linked_external,
        "provider": session.provider,
    }


class OllamaSupervisor:
    """
    Local supervisor that analyzes tasks and evaluates responses.
    Component of the Hybrid Supervised Agent Mesh.
    """
    @staticmethod
    async def analyze_task(session: AgentSession) -> dict:
        """
        [SUPERVISOR MESH] Pre-processes the task using local Ollama.
        Determines the technical goal and prepares a structured plan.
        """
        try:
            prompt = (
                f"You are the EvoPyramid Supervisor. Analyze this task for a {session.provider} session.\n"
                f"NODE: {session.node_id} (Z{session.node_z})\n"
                f"GOAL: {session.task_title}\n"
                f"CONTEXT: {session.task_context or 'None'}\n\n"
                "Return a 1-sentence summary of the architectural goal."
            )
            messages = [{"role": "user", "content": prompt}]
            
            # Use the orchestrator's internal helper to call Ollama
            model_name = await _resolve_ollama_model("llama3.2:3b")
            analysis_text = await asyncio.to_thread(AgentOrchestrator._send_ollama_sync, model_name, messages)
            
            return {
                "task_goal": session.task_title,
                "prepared_prompt": analysis_text.strip(),
                "supervised": True
            }
        except Exception as e:
            logger.warning(f"Ollama Supervisor pre-processing failed: {e}")
            return {
                "task_goal": session.task_title,
                "prepared_prompt": f"Architecture context: {session.task_context or 'General assistance.'}",
                "supervised": False
            }

    @staticmethod
    async def evaluate_response(response_text: str) -> dict:
        """
        [SUPERVISOR MESH] Evaluates the response quality using local Ollama.
        """
        try:
            prompt = (
                "You are the EvoPyramid Evaluator. Rate this AI response for technical accuracy and depth.\n\n"
                f"RESPONSE: {response_text[:1000]}\n\n"
                "Return exactly 1 OR 0 (1 for valid/deep, 0 for failed/shallow)."
            )
            messages = [{"role": "user", "content": prompt}]
            model_name = await _resolve_ollama_model("llama3.2:3b")
            score_text = await asyncio.to_thread(AgentOrchestrator._send_ollama_sync, model_name, messages)
            
            is_valid = "1" in score_text
            return {
                "quality_score": 1.0 if is_valid else 0.1,
                "valid": is_valid,
                "actions": ["LOG_INVENTORY"] if "node" in response_text.lower() else []
            }
        except Exception as e:
            logger.warning(f"Ollama Supervisor evaluation failed: {e}")
            return {"quality_score": 0.5, "valid": len(response_text) > 20, "actions": []}

class SupervisedTaskRouter:
    """
    Business logic for routing tasks between providers based on Z-level and quota status.
    """
    @staticmethod
    def resolve_provider(session: AgentSession, policy: dict) -> Provider:
        # Priority 1: Manual Override
        if session.provider == Provider.OLLAMA:
            return Provider.OLLAMA
            
        # Priority 2: Quota Fallback
        if policy.get("reason") == "gemini_quota_fallback":
            return Provider.OLLAMA
            
        # Priority 3: External URL Bridge (if attached, we prefer Gemini/External)
        if policy.get("linked_external"):
            return Provider.GEMINI
            
        return Provider.GEMINI

class AgentOrchestrator:
    """
    Handles internal LLM logic for sessions.
    Connects nodes to local/cloud providers (Ollama/Gemini).
    """
    @staticmethod
    async def _system_context(session: AgentSession) -> str:
        # Load real-time state insight
        state_summary = "State context unavailable."
        memory_context = "No relevant project memories found."
        
        try:
            root_dir = Path(__file__).resolve().parents[2]
            state_path = root_dir / "state" / "pyramid_state.json"
            pulse_path = root_dir / "state" / "pulse.json"
            
            # 1. State metrics (from UI/V11)
            sys_health = "UNKNOWN"
            sys_eng = "UNKNOWN"
            total_nodes = 0
            active_nodes = []
            idle_nodes = []
            
            if state_path.exists():
                with open(state_path, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    metrics = state_data.get("system_metrics", {})
                    sys_health = metrics.get("health_pct", "UNKNOWN")
                    sys_eng = metrics.get("cognitive_memory_size", "UNKNOWN")
                    
                    nodes = state_data.get("nodes", {})
                    total_nodes = len(nodes)
                    active_nodes = [n["title"] for n in nodes.values() if n.get("state") == "active"]
                    idle_nodes = [n["title"] for n in nodes.values() if n.get("state") == "idle"]

            # 2. Pulse metrics (ObserverRelay)
            pulse_msg = "No pulse data."
            if pulse_path.exists():
                with open(pulse_path, "r", encoding="utf-8") as f:
                    pulse_data = json.load(f)
                    obs = pulse_data.get("observer_report", {})
                    if obs:
                        nodes_online = len(obs.get("active_nodes", []))
                        last_updated = obs.get("last_updated", "UNKNOWN")
                        pulse_msg = f"Last heartbeat at {last_updated}. Observer saw {nodes_online} nodes online."

            # 3. Session Registry
            from beta_pyramid_functional.B3_SessionRegistry.session_models import SessionRegistry, SessionStatus
            sessions = SessionRegistry.list_all()
            active_sessions = sum(1 for s in sessions if s.status == SessionStatus.ACTIVE)
            
            state_summary = (
                f"--- LIVE TELEMETRY ---\n"
                f"Health: {sys_health}% | Cognitive Cortex: {sys_eng} ENG blocks\n"
                f"Nodes: {total_nodes} registered. "
                f"ACTIVE sample: {', '.join(active_nodes[:5])}. IDLE sample: {', '.join(idle_nodes[:5])}.\n"
                f"Swarm Terminals: {active_sessions} active sessions out of {len(sessions)} total.\n"
                f"Pulse: {pulse_msg}\n"
                f"----------------------\n"
            )
            
            # --- SEMANTIC MEMORY INJECTION ---
            try:
                cortex = await ProjectCortex.get_instance()
                # Query based on task context or last message
                query_text = session.task_context or ""
                if session.messages:
                    query_text += f" | {session.messages[-1].content}"
                
                similar_blocks = await cortex.find_similar(query_text, threshold=0.01)
                if similar_blocks:
                    mem_strings = [f"[{b.id}] {b.content[:200]}..." for b in similar_blocks[:2]]
                    memory_context = " | ".join(mem_strings)
            except Exception as e:
                logger.warning(f"ProjectCortex retrieval failed: {e}")

        except Exception as e:
            state_summary = f"State insight error: {e}"
        
        workspace_info = "Workspace explorer active. Use 'REQUEST_FILE: <path>' if you need code context."
        ctx = ""
        is_genesis = session.node_id and session.node_id.startswith("gen-")
        if is_genesis:
            ctx = (
                "You are an EvoGenesis Architect Agent. You operate under the GLOBAL NEXUS master-orchestration layer. "
                "Principles: PEAR loop (Perception, Evolution, Action, Reflection). "
                f"Binding: NODE '{session.node_id}' (EvoGenesis Child Pyramid). "
                f"ACTUAL SYSTEM STATE: {state_summary} "
                f"PROJECT RECOLLECTION: {memory_context} "
                "Current Goal: Develop a professional architecture for an asynchronous GCP-hosted backend. "
                "Provide highly technical, structured advice aligned with evopyramid-ai."
            )
        else:
            ctx = (
                f"You are the Truth-Channel Assistant of EvoPyramid OS. Role: {session.provider.upper()}. "
                f"You are bound to NODE: '{session.node_id}' at Z-LEVEL: {session.node_z}. "
                f"ACTUAL SYSTEM STATE:\n{state_summary}\n"
                f"PROJECT RECOLLECTION: {memory_context}\n"
                f"Task Context: {session.task_context or 'General assistance.'}.\n"
                f"WORKSPACE TOOLS: {workspace_info}\n"
                "CRITICAL DIRECTIVES:\n"
                "1. If asked about system health, memory size, or connected nodes, respond EXCLUSIVELY using the LIVE TELEMETRY numbers provided above.\n"
                "2. Do NOT invent capabilities or guess statuses. If a metric says UNKNOWN, state that it is unknown.\n"
                "3. If you need to see a file, conclude your thought with 'REQUEST_FILE: <path>'. The system will provide it in the next cycle.\n"
                "4. Keep responses professional, factual, and deeply rooted in the actual state."
            )
        
        # Log context for debugging
        print(f"\n[ORCHESTRATOR DEBUG] Generated System Context for {session.node_id}:\n{ctx}\n")
        return ctx

    @staticmethod
    def _history(session: AgentSession) -> List[dict]:
        history: List[dict] = []
        for msg in session.messages[-11:-1]:
            history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content],
            })
        return history

    @staticmethod
    async def _send(model_name: str, system_ctx: str, history: List[dict], user_message: str) -> str:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=history)
        response = await asyncio.to_thread(chat.send_message, f"{system_ctx}\n\nUSER: {user_message}")
        return response.text

    @staticmethod
    def _build_ollama_messages(session: AgentSession, system_ctx: str) -> List[dict]:
        messages: List[dict] = [{"role": "system", "content": system_ctx}]
        for msg in session.messages[-12:]:
            content = str(msg.content or "").strip()
            if not content:
                continue
            role = "assistant" if msg.role == "assistant" else "user" if msg.role == "user" else "system"
            messages.append({"role": role, "content": content})
        return messages

    @staticmethod
    def _ollama_messages_to_prompt(messages: List[dict]) -> str:
        lines: List[str] = []
        for message in messages:
            role = str(message.get("role", "user")).upper()
            content = str(message.get("content", "")).strip()
            if content:
                lines.append(f"{role}: {content}")
        lines.append("ASSISTANT:")
        return "\n\n".join(lines)

    @staticmethod
    def _send_ollama_sync(model_name: str, messages: List[dict]) -> str:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }

        try:
            chat_data = _ollama_request("POST", "/api/chat", payload=payload, timeout=180)
            message = chat_data.get("message") if isinstance(chat_data, dict) else None
            text = str((message or {}).get("content", "")).strip()
            if text:
                return text
        except RuntimeError as exc:
            text = str(exc)
            if "not reachable" in text.lower():
                raise
            if "HTTP 404" not in text and "HTTP 405" not in text:
                logger.warning("Ollama /api/chat failed, fallback to /api/generate: %s", text)

        prompt = AgentOrchestrator._ollama_messages_to_prompt(messages)
        generate_data = _ollama_request(
            "POST",
            "/api/generate",
            payload={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        generated_text = str(generate_data.get("response", "")).strip()
        if generated_text:
            return generated_text
        raise RuntimeError("Ollama returned an empty response.")

    @staticmethod
    async def _send_ollama(model_name: str, messages: List[dict]) -> str:
        return await asyncio.to_thread(AgentOrchestrator._send_ollama_sync, model_name, messages)

    @staticmethod
    async def _send_anthropic(session: AgentSession, system_ctx: str) -> str:
        """Direct Anthropic API. Requires ANTHROPIC_API_KEY env var."""
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Add it to your .env or environment variables."
            )

        model_name = (
            os.getenv("ANTHROPIC_MODEL", "").strip() or
            getattr(session, "model_hint", None) or
            "claude-sonnet-4-20250514"
        )

        history_messages: List[dict] = []
        for msg in session.messages[:-1]:
            if msg.role.value in ("user", "assistant"):
                history_messages.append({"role": msg.role.value, "content": msg.content})

        last_content = session.messages[-1].content if session.messages else ""

        payload = {
            "model": model_name,
            "max_tokens": 4096,
            "system": system_ctx,
            "messages": history_messages + [{"role": "user", "content": last_content}]
        }

        def _call():
            import urllib.request, urllib.error
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    blocks = result.get("content", [])
                    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Anthropic API HTTP {e.code}: {body}")

        response = await asyncio.to_thread(_call)
        logger.info(f"[Anthropic] {model_name} → {len(response)} chars for session {session.id}")
        return response

    @staticmethod
    async def get_response(session: AgentSession) -> Optional[str]:
        global _GEMINI_QUOTA_BLOCK_UNTIL, _GEMINI_QUOTA_BLOCK_REASON

        if not session.messages:
            return "[SYSTEM DEBUG] Session has no user message yet."

        system_ctx = await AgentOrchestrator._system_context(session)

        policy = _session_routing_policy(session)
        provider = SupervisedTaskRouter.resolve_provider(session, policy)

        try:
            # All paths now go through Supervisor Pre-analysis
            analysis = await OllamaSupervisor.analyze_task(session)
            logger.info(f"Ollama Supervisor (Z{session.node_z}) analysis: {analysis.get('prepared_prompt', 'None')[:50]}...")

            response_text = ""

            if provider == Provider.CLAUDE or session.provider == Provider.CLAUDE:
                # ─── DIRECT ANTHROPIC API PATH ────────────────────────────
                response_text = await AgentOrchestrator._send_anthropic(session, system_ctx)

            elif provider == Provider.OLLAMA:
                # LOCAL OLLAMA PATH
                model_hint = session.model_hint if session.provider == Provider.OLLAMA else "llama3.2:3b"
                model_name = await _resolve_ollama_model(model_hint)
                messages = AgentOrchestrator._build_ollama_messages(session, system_ctx)
                response_text = await AgentOrchestrator._send_ollama(model_name, messages)
            else:
                # CLOUD GEMINI PATH (w/ Potential Bridge fallback handled in UI)
                api_key = os.getenv("GEMINI_API_KEY", "").strip()
                if not api_key:
                    logger.warning(f"GEMINI_API_KEY not found for node {session.node_id}. Falling back to OLLAMA.")
                    # Force local execution
                    model_name = await _resolve_ollama_model("llama3.2:3b")
                    messages = AgentOrchestrator._build_ollama_messages(session, system_ctx)
                    response_text = await AgentOrchestrator._send_ollama(model_name, messages)
                else:
                    now = time.time()
                    if _GEMINI_QUOTA_BLOCK_UNTIL > now:
                        # Logic should have routed to OLLAMA, but in case of race:
                        retry_seconds = max(1, int(_GEMINI_QUOTA_BLOCK_UNTIL - now))
                        return _quota_cooldown_message(session, retry_seconds, _GEMINI_QUOTA_BLOCK_REASON)

                    genai.configure(api_key=api_key)
                    history = AgentOrchestrator._history(session)
                    last_msg = session.messages[-1].content
                    model_name = await _resolve_gemini_model(session.model_hint)
                    response_text = await AgentOrchestrator._send(model_name, system_ctx, history, last_msg)

            # Unified Post-processing Evaluation
            evaluation = await OllamaSupervisor.evaluate_response(response_text)
            if not evaluation["valid"]:
                return f"[SUPERVISOR CAUTION] Response rejected by local mesh for low quality. Detail: {response_text}"
            
            return response_text

        except Exception as exc:
            error_text = str(exc)
            
            # Handle Quota Block Globally if it happened during the call
            if _is_quota_error(error_text):
                _GEMINI_QUOTA_BLOCK_UNTIL = time.time() + 60 # Cooldown
                _GEMINI_QUOTA_BLOCK_REASON = "unexpected_quota_hit"
                return f"[SYSTEM FALLBACK] Gemini quota exhausted. Please try again (Ollama will take over)."

            if policy.get("reason") == "external_url_attached":
                 return (
                    "[SYSTEM LINKED] Session attached to external browser chat. "
                    "Use 'Open' to continue. "
                    f"Bridge status: {error_text}"
                )
            return f"⚠ AI Orchestration Error: {error_text}"

    @staticmethod
    async def plan_mission(objective: str) -> List[Dict[str, Any]]:
        """
        [STRATEGIC MESH] Decomposes a global objective into a multi-agent plan.
        Returns a list of task definitions: [{"role": str, "z_level": int, "intent": str}]
        """
        prompt = (
            "You are the EvoPyramid Architect (Z17). Decompose the following objective into a structured, multi-agent mission plan. "
            "For each task, specify a specialized role (e.g., Auditor, Engineer, Researcher, SecurityGuardian), "
            "a target Z-Level (1-17), and a specific task intent.\n\n"
            f"OBJECTIVE: {objective}\n\n"
            "Return EXCLUSIVELY a JSON array of objects. Example:\n"
            '[{"role": "Auditor", "z_level": 7, "intent": "Analyze code for vulnerabilities"}, {"role": "Engineer", "z_level": 5, "intent": "Fix identified issues"}]\n'
            "Ensure the plan is logical, specialized, and follows EvoPyramid standards."
        )
        
        # Create a dummy session for the planning call
        session = AgentSession(
            node_id="strategic-planner",
            node_z=17,
            task_title="Strategic Mission Planning",
            provider=Provider.GEMINI, # Prefer cloud for complex planning
            task_context="Architecture Mode"
        )
        session.add_user_message(prompt)
        
        response = await AgentOrchestrator.get_response(session)
        
        # Parse JSON from response (robust cleaning)
        try:
            # Strip markdown fences if present
            clean_response = re.sub(r"```json|```", "", response).strip()
            # Find the first '[' and last ']' to isolate the array
            json_match = re.search(r"(\[.*\])", clean_response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group(1))
                if isinstance(plan, list):
                    return plan
        except Exception as e:
            logger.warning(f"Failed to parse LLM mission plan: {e}. Raw response: {response}")
            
        # Fallback to a single-agent plan if parsing fails
        return [{"role": "Generalist", "z_level": 5, "intent": objective}]
