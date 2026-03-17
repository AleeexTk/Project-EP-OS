from __future__ import annotations
try:
    from .contracts import TaskEnvelope, SystemPolicy, TaskStatus
except ImportError:
    from contracts import TaskEnvelope, SystemPolicy, TaskStatus
from typing import Dict, Any, List, Optional

class SystemPolicyManager:
    """
    Enforces architectural discipline and security policies.
    Part of the Iron Guardian (Provocateur) runtime layer.
    """
    
    def __init__(self, default_policy: Optional[SystemPolicy] = None):
        self.policy = default_policy or SystemPolicy()
        self.audit_log: List[Dict[str, Any]] = []

    def validate_action(self, envelope: TaskEnvelope) -> bool:
        """
        Validates if a TaskEnvelope complies with system policies.
        """
        # EP-Sandbox Isolation Logic
        is_sandbox = "sandbox" in envelope.source_node.lower() or "sandbox" in envelope.target_node.lower()
        
        if is_sandbox:
            # Sandbox nodes are heavily restricted by default
            restricted_actions = ["filesystem_write", "network_request", "system_reboot"]
            if envelope.action in restricted_actions:
                envelope.status = TaskStatus.FAILED
                envelope.metadata["error"] = f"SandboxViolation: Action '{envelope.action}' is forbidden in EP-Sandbox."
                self._log_violation(envelope)
                return False

        # Basic Security Checks
        if envelope.action == "filesystem_write" and not self.policy.allow_filesystem_write:
            envelope.status = TaskStatus.FAILED
            envelope.metadata["error"] = "PolicyViolation: Filesystem write denied."
            self._log_violation(envelope)
            return False

        if envelope.action == "network_request" and not self.policy.allow_network_access:
            envelope.status = TaskStatus.FAILED
            envelope.metadata["error"] = "PolicyViolation: Network access denied."
            self._log_violation(envelope)
            return False

        return True

    def _log_violation(self, envelope: TaskEnvelope):
        self.audit_log.append({
            "task_id": envelope.task_id,
            "action": envelope.action,
            "error": envelope.metadata.get("error"),
            "timestamp": envelope.timestamp.isoformat()
        })
