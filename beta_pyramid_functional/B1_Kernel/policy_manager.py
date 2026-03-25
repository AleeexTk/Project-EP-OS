import sys
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Add current directory to path for absolute-style imports
_kern_path = str(Path(__file__).resolve().parent)
if _kern_path not in sys.path:
    sys.path.insert(0, _kern_path)

from contracts import TaskEnvelope, SystemPolicy, TaskStatus, CascadeStatus

class SystemPolicyManager:
    """
    Enforces architectural discipline and security policies.
    Part of the Iron Guardian (Provocateur) runtime layer.
    """
    
    # Filesystem paths for persistence
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    _LOG_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "violations.json"
    _QUARANTINE_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "quarantine.json"

    # Persistent class-level storage
    audit_log: List[Dict[str, Any]] = []
    quarantine_list: set[str] = set()
    
    _initialized = False

    def __init__(self, default_policy: Optional[SystemPolicy] = None):
        self.policy = default_policy or SystemPolicy()
        self.reporting_hooks: List[Callable[[Dict[str, Any]], None]] = []
        SystemPolicyManager._ensure_initialized()

    @classmethod
    def _ensure_initialized(cls):
        """Loads existing audit logs and quarantine list from disk if not already done."""
        if not cls._initialized:
            try:
                # Load Violations
                if cls._LOG_FILE.exists():
                    with open(cls._LOG_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            cls.audit_log = data
                
                # Load Quarantine
                if cls._QUARANTINE_FILE.exists():
                    with open(cls._QUARANTINE_FILE, "r", encoding="utf-8") as f:
                        q_data = json.load(f)
                        if isinstance(q_data, list):
                            cls.quarantine_list = set(q_data)
            except Exception as e:
                logging.error(f"[POLICY_MANAGER] Failed to load persistent data: {e}")
            cls._initialized = True

    def quarantine_node(self, node_id: str):
        """Places a node into quarantine, blocking all of its actions."""
        if node_id not in self.quarantine_list:
            self.quarantine_list.add(node_id)
            self._save_quarantine()
            logging.info(f"[POLICY_MANAGER] Node '{node_id}' placed in QUARANTINE.")

    def _save_quarantine(self):
        """Saves the current quarantine list to disk."""
        try:
            os.makedirs(os.path.dirname(self._QUARANTINE_FILE), exist_ok=True)
            with open(self._QUARANTINE_FILE, "w", encoding="utf-8") as f:
                json.dump(list(self.quarantine_list), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[POLICY_MANAGER] Failed to save quarantine list: {e}")

    def model_copy(self, deep=True):
        """Pydantic v2 compatibility for manual copies if needed."""
        return super().model_copy(deep=deep)

    def register_reporter(self, hook: Callable[[Dict[str, Any]], None]):
        """Registers a callback for security/architectural violations."""
        self.reporting_hooks.append(hook)

    def validate_action(self, envelope: TaskEnvelope) -> bool:
        """
        Validates if a TaskEnvelope complies with system policies.
        Enforces Trinity Protocol: Autonomy + Security.
        """
        # -1. SEC_GUARDIAN: Rate-limit + Anti-Spoof (Z12 Security Proxy)
        if not self._sec_audit(envelope):
            return False

        # 0. Quarantine Check (Automated Discipline)
        if envelope.source_node in self.quarantine_list:
            envelope.status = TaskStatus.FAILED
            envelope.metadata["error"] = f"QuarantineViolation: Node '{envelope.source_node}' is in quarantine and cannot perform actions."
            self._log_violation(envelope)
            return False

        # 1. Z-Level Hierarchy Check (The 'Iron Guardian' constraint)
        if not self._validate_z_access(envelope):
            return False

        # 2. EP-Sandbox Isolation Logic
        is_sandbox = "sandbox" in envelope.source_node.lower() or "sandbox" in envelope.target_node.lower()
        
        if is_sandbox:
            restricted_actions = ["filesystem_write", "network_request", "system_reboot", "manifest_node"]
            if envelope.action in restricted_actions:
                envelope.status = TaskStatus.FAILED
                envelope.metadata["error"] = f"SandboxViolation: Action '{envelope.action}' is forbidden in EP-Sandbox."
                self._log_violation(envelope)
                return False

        # 3. Action-Specific Security Checks
        if envelope.action == "filesystem_write" and not self.policy.allow_filesystem_write:
            envelope.status = TaskStatus.FAILED
            envelope.metadata["error"] = "PolicyViolation: Filesystem write denied by global policy."
            self._log_violation(envelope)
            return False

        # 4. Z-Cascade Protocol (Descending Meaning Check)
        if envelope.action in ["manifest_node", "sync_structure", "execute_mission"] and envelope.origin_z > 5:
            target_z = envelope.payload.get("target_z", envelope.payload.get("z_level", envelope.origin_z - 1))
            if envelope.origin_z > target_z:
                from z_cascade import CascadeValidator

                cascade_success = CascadeValidator.validate_descent(envelope, target_z)
                if not cascade_success:
                    if envelope.cascade_status == CascadeStatus.BLOCKED:
                        logging.warning(f"[POLICY_MANAGER] Task blocked by Monument. Handing over to Z14_AUTO_CORRECTOR...")
                        try:
                            import sys
                            from pathlib import Path
                            # policy_manager.py -> B1_Kernel -> beta_pyramid_functional -> PROJECT_ROOT
                            PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
                            z14_path = str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "14_AUTO_CORRECTOR")
                            if z14_path not in sys.path:
                                sys.path.insert(0, z14_path)
                            from auto_corrector import AutoCorrectorNode
                            
                            repaired_envelope = AutoCorrectorNode.intercept_and_repair(envelope, envelope.metadata.get("error", "Semantic Integrity Lost"))
                            
                            # Second pass validation on repaired envelope
                            if CascadeValidator.validate_descent(repaired_envelope, target_z):
                                # Success! Mutate original envelope to match repaired logic
                                envelope.payload["synthesis_proposal"] = repaired_envelope.payload.get("synthesis_proposal")
                                envelope.cascade_status = CascadeStatus.CRYSTALLIZED
                                envelope.status = TaskStatus.PENDING
                                if "error" in envelope.metadata:
                                    del envelope.metadata["error"]
                                logging.info(f"[POLICY_MANAGER] Z14 Auto-Corrector resurrected the task successfully.")
                                return True
                        except Exception as e:
                            logging.error(f"[POLICY_MANAGER] Auto-Corrector bypass failed: {e}")

                    self._log_violation(envelope)
                    return False

        return True

    def _sec_audit(self, envelope: TaskEnvelope) -> bool:
        """SEC_GUARDIAN (Z12): Rate-limit and anti-spoof check before any other validation."""
        try:
            if not hasattr(self, "_sec_guardian"):
                from pathlib import Path as _Path
                _PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
                import sys as _sys
                _z12_path = str(_PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "12_SEC_GUARDIAN")
                _b3_path = str(_PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry")
                if _z12_path not in _sys.path:
                    _sys.path.insert(0, _z12_path)
                if _b3_path not in _sys.path:
                    _sys.path.insert(0, _b3_path)
                from sec_guardian import SecGuardian
                self._sec_guardian = SecGuardian()
            return self._sec_guardian.audit(envelope)
        except Exception as e:
            logging.error(f"[POLICY_MANAGER] CRITICAL: SEC_GUARDIAN initialization failed: {e}")
            envelope.status = TaskStatus.FAILED
            envelope.metadata["error"] = f"SecurityServiceUnavailable: {e}"
            return False  # Fail-closed: block actions if guardian is broken

    def _validate_z_access(self, envelope: TaskEnvelope) -> bool:
        """
        Prevent low-level nodes from triggering high-level mutations.
        A node can only manifest or sync nodes at or below its own Z-level + 1 (limited growth).
        """
        if envelope.action in ["manifest_node", "sync_structure"]:
            target_z = envelope.payload.get("z_level", 0)
            if envelope.origin_z < 10 and target_z >= 10:
                envelope.status = TaskStatus.FAILED
                envelope.metadata["error"] = f"Z-Violation: Node at Z{envelope.origin_z} cannot manifest Z{target_z} (High-Pyramid)."
                self._log_violation(envelope)
                return False
        return True

    def _log_violation(self, envelope: TaskEnvelope):
        violation_event = {
            "task_id": envelope.task_id,
            "action": envelope.action,
            "error": envelope.metadata.get("error"),
            "timestamp": envelope.timestamp.isoformat(),
            "source": envelope.source_node,
            "target": envelope.target_node,
            "origin_z": envelope.origin_z
        }
        self.audit_log.append(violation_event)
        
        # Persistent save to disk
        try:
            os.makedirs(os.path.dirname(self._LOG_FILE), exist_ok=True)
            with open(self._LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.audit_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[POLICY_MANAGER] Failed to save audit log: {e}")
            
        # Trigger external reporters (Reflective Layer)
        for hook in self.reporting_hooks:
            try:
                hook(violation_event)
            except Exception as e:
                logging.error(f"[POLICY_MANAGER] Error in reporting hook: {e}")

# Auto-initialize on module load to ensure persistent data is available to all components
SystemPolicyManager._ensure_initialized()
