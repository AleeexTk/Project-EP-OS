import logging
from typing import Optional
try:
    from .contracts import TaskEnvelope, CascadeStatus, TaskStatus
except ImportError:
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
        if envelope.payload.get("simulate_semantic_loss", False):
            Monument.block(envelope, "Semantic Integrity Lost. Original intent distorted.")
            return False
            
        # 2. Inter-level Consistency (Такт 2. Межуровневая согласованность)
        if envelope.payload.get("simulate_inconsistency", False):
            ChaosEngine.register_friction(envelope, "Inter-level capability mismatch.")
            Monument.block(envelope, "Consistency Failed. Target level cannot structurally accept this state.")
            return False

        # 3. Crystallization (Такт 3. Кристаллизация перехода)
        if Monument.crystallize(envelope):
            envelope.cascade_status = CascadeStatus.PASSED
            Observer.log_status(envelope, "Cascade Successful. Meaning preserved.")
            return True
        else:
            Monument.block(envelope, "Crystallization Failed. Invariant broken.")
            return False
