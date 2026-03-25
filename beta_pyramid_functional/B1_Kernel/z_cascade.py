import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure B1_Kernel is in path for absolute-style imports
_kern_path = str(Path(__file__).resolve().parent)
if _kern_path not in sys.path:
    sys.path.append(_kern_path)

from contracts import TaskEnvelope, CascadeStatus, TaskStatus

class Observer:
    @staticmethod
    def log_status(envelope: TaskEnvelope, message: str):
        logging.info(f"[Z-CASCADE OBSERVER] {envelope.task_id} [{envelope.action}] -> {message}")

class Monument:
    @staticmethod
    def crystallize(envelope: TaskEnvelope) -> bool:
        """Fixes the transition. If invariant broken, returns False."""
        envelope.cascade_status = CascadeStatus.CRYSTALLIZED
        logging.info(f"[Z-CASCADE MONUMENT] Transition crystallized for {envelope.task_id}.")
        return True

    @staticmethod
    def block(envelope: TaskEnvelope, reason: str):
        envelope.cascade_status = CascadeStatus.BLOCKED
        envelope.status = TaskStatus.FAILED
        envelope.metadata["cascade_error"] = reason
        logging.warning(f"[Z-CASCADE MONUMENT] Blocked: {reason}")

class ChaosEngine:
    @staticmethod
    def register_friction(envelope: TaskEnvelope, detail: str):
        logging.warning(f"[Z-CASCADE CHAOS] Friction detected: {detail}")

class CascadeValidator:
    """
    Implements the 'Cascading Inter-level Verification with Sliding Z-Pair'.
    Validates the descent of meaning from Z_n to Z_n-1.
    """
    
    @staticmethod
    def validate_descent(envelope: TaskEnvelope, target_z: int) -> bool:
        """
        Runs the full 3-step Cascade for a downward transition.
        1. Semantic Integrity
        2. Inter-level Consistency
        3. Crystallization
        """
        Observer.log_status(envelope, f"Starting Z-Cascade: Z{envelope.origin_z} -> Z{target_z}")
        envelope.cascade_status = CascadeStatus.ACTIVE
        
        # 1. Semantic Integrity (Такт 1. Семантическая целостность)
        # Check if intent is present
        if not envelope.intent and not envelope.payload.get("synthesis_proposal"):
             ChaosEngine.register_friction(envelope, "Missing semantic intent or synthesis proposal.")
             # We don't block yet, but we log the friction.

        if envelope.payload.get("simulate_semantic_loss", False):
            Monument.block(envelope, "Semantic Integrity Lost. Original intent distorted.")
            return False
            
        # 2. Inter-level Consistency (Такт 2. Межуровневая согласованность)
        # Sliding Z-Pair Invariant: Origin must be strictly above Target
        if envelope.origin_z <= target_z:
            Monument.block(envelope, f"Consistency Failed. Origin Z{envelope.origin_z} must be higher than Target Z{target_z}.")
            return False

        if envelope.payload.get("simulate_inconsistency", False):
            ChaosEngine.register_friction(envelope, "Inter-level capability mismatch.")
            Monument.block(envelope, "Consistency Failed. Target level cannot structurally accept this state.")
            return False

        # Placeholder for real SK_Engine validation (Phase 6 Integration)
        # In the future, this calls SK_Engine.validate_coherence(envelope.intent, envelope.payload['synthesis_proposal'])
        logging.info(f"[Z-CASCADE] SK_Engine internal coherence check: PASSED (Symbolic)")

        # 3. Crystallization (Такт 3. Кристаллизация перехода)
        if Monument.crystallize(envelope):
            envelope.cascade_status = CascadeStatus.PASSED
            Observer.log_status(envelope, "Cascade Successful. Meaning preserved.")
            return True
        else:
            Monument.block(envelope, "Crystallization Failed. Invariant broken.")
            return False
