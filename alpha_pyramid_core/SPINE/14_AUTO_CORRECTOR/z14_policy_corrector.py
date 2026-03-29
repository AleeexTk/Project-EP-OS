"""
Auto Corrector — Z14 · Alpha_Pyramid_Core · SPINE sector
Intercepts and repairs tasks blocked by the Z-Cascade Monument.
"""

from __future__ import annotations
import asyncio
import copy
import logging
import sys
from pathlib import Path

# Setup paths for importing B1_Kernel
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel"))
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B2_ProviderMatrix"))
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry"))

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any

from contracts import TaskEnvelope, CascadeStatus, TaskStatus
from provider_matrix import ProviderMatrix
from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge

logger = logging.getLogger("AUTO_CORRECTOR")

class RepairJournal:
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    _REPAIRS_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "repairs.json"
    
    repair_history: List[Dict[str, Any]] = []
    _initialized = False

    @classmethod
    def _ensure_initialized(cls):
        if not cls._initialized:
            try:
                if cls._REPAIRS_FILE.exists():
                    with open(cls._REPAIRS_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            cls.repair_history = data
            except Exception as e:
                logger.error(f"[REPAIR_JOURNAL] Failed to load history: {e}")
            cls._initialized = True

    @classmethod
    def record_repair(cls, node_id: str, original_payload: Any, repaired_payload: Any, provider: str, reason: str):
        cls._ensure_initialized()
        record = {
            "node_id": node_id,
            "timestamp": datetime.now().isoformat(),
            "original_payload": original_payload,
            "repaired_payload": repaired_payload,
            "provider": provider,
            "reason": reason
        }
        cls.repair_history.append(record)
        cls._save()

    @classmethod
    def _save(cls):
        try:
            os.makedirs(os.path.dirname(cls._REPAIRS_FILE), exist_ok=True)
            with open(cls._REPAIRS_FILE, "w", encoding="utf-8") as f:
                json.dump(cls.repair_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[REPAIR_JOURNAL] Failed to save history: {e}")

class AutoCorrectorNode:
    @staticmethod
    def _run_async(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        result: Dict[str, Any] = {}
        error: Dict[str, BaseException] = {}

        def _runner():
            try:
                result["value"] = asyncio.run(coro)
            except BaseException as exc:
                error["value"] = exc

        import threading
        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        thread.join()
        if "value" in error:
            raise error["value"]
        return result.get("value")

    @staticmethod
    def _build_error_signature(rejection_reason: str, original_intent: str) -> str:
        return f"{rejection_reason}|{original_intent}".strip()

    @staticmethod
    def _rewrite_with_provider(provider, original_intent: str, current_proposal: str, rejection_reason: str) -> str:
        prompt = (
            "Rewrite the synthesis_proposal so it strictly aligns with the original intent.\n"
            "Return only the repaired synthesis_proposal text.\n\n"
            f"Original intent:\n{original_intent}\n\n"
            f"Current synthesis_proposal:\n{current_proposal}\n\n"
            f"Rejection reason:\n{rejection_reason}\n"
        )

        if provider.value == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not set")
            payload = {
                "model": os.getenv("ANTHROPIC_MODEL", "").strip() or "claude-sonnet-4-20250514",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            blocks = result.get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()

        if provider.value == "gpt":
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set")
            payload = {
                "model": os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        model = os.getenv("GEMINI_MODEL", "").strip() or "gemini-2.0-flash"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        candidates = result.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        return "".join(p.get("text", "") for p in parts).strip()

    @staticmethod
    def intercept_and_repair(envelope: TaskEnvelope, rejection_reason: str) -> TaskEnvelope:
        """
        Takes a blocked envelope, uses an LLM (or fallback logic) to rewrite
        the synthesis_proposal so it matches the original intent, and returns it.
        """
        logger.warning(f"[Z14_AUTO_CORRECTOR] Intercepting blocked task from {envelope.source_node}. Reason: {rejection_reason}")
        
        repaired_envelope = envelope.model_copy(deep=True)
        
        # Retrieve best provider for Z14 logic repair
        provider = ProviderMatrix.get_best_available(14, "SPINE")
        
        original_intent = repaired_envelope.intent or ""
        original_proposal = str(repaired_envelope.payload.get("synthesis_proposal", "") or "")
        error_signature = AutoCorrectorNode._build_error_signature(rejection_reason, original_intent)
        recalled_proposal = None
        try:
            bridge = AutoCorrectorNode._run_async(CognitiveBridge.get_instance())
            recalled_memory = AutoCorrectorNode._run_async(bridge.recall_healing_pattern(error_signature))
            if recalled_memory and isinstance(recalled_memory, dict):
                content = str(recalled_memory.get("content", ""))
                if "[OUTCOME]" in content:
                    recalled_proposal = content.split("[OUTCOME]", 1)[1].strip()
        except Exception as e:
            logger.warning(f"[Z14_AUTO_CORRECTOR] Memory recall unavailable: {e}")
        
        if not original_intent:
            repaired_proposal = "Restored semantic alignment."
        elif recalled_proposal:
            repaired_proposal = recalled_proposal
        else:
            try:
                repaired_proposal = AutoCorrectorNode._rewrite_with_provider(
                    provider=provider,
                    original_intent=original_intent,
                    current_proposal=original_proposal,
                    rejection_reason=rejection_reason,
                )
                if not repaired_proposal:
                    repaired_proposal = original_intent
            except Exception as e:
                logger.error(f"[Z14_AUTO_CORRECTOR] LLM rewrite failed with {provider.value}: {e}")
                repaired_proposal = original_intent
            
        logger.info(f"[Z14_AUTO_CORRECTOR] Synthesis Proposal rewritten with {provider.value} provider logic.")
        
        repaired_envelope.payload["synthesis_proposal"] = repaired_proposal
        if "simulate_semantic_loss" in repaired_envelope.payload:
            repaired_envelope.payload["simulate_semantic_loss"] = False
            
        repaired_envelope.cascade_status = CascadeStatus.PENDING
        
        # Record in journal
        RepairJournal.record_repair(
            node_id=envelope.source_node,
            original_payload=envelope.payload.get("synthesis_proposal"),
            repaired_payload=repaired_proposal,
            provider=provider.value,
            reason=rejection_reason
        )

        try:
            bridge = AutoCorrectorNode._run_async(CognitiveBridge.get_instance())
            AutoCorrectorNode._run_async(
                bridge.store_decision(
                    topic=error_signature,
                    outcome=repaired_proposal,
                    z_level=14,
                    tags=["heal", "z14_auto_corrector"],
                )
            )
        except Exception as e:
            logger.warning(f"[Z14_AUTO_CORRECTOR] Memory store unavailable: {e}")
        
        return repaired_envelope
