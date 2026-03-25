"""
SEC Guardian — Z12 · Alpha_Pyramid_Core · SPINE sector

Security proxy gateway positioned between Z13 (EVO BRIDGE / AI providers)
and Z11 (PEAR LOOP / Governance). Audits every cross-layer request for:
  - Origin legitimacy (anti-spoofing)
  - Token / API key abuse (rate-limit awareness)
  - Z-boundary enforcement at the Alpha boundary
"""

from __future__ import annotations
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Resolve project root: sec_guardian.py -> 12_SEC_GUARDIAN -> SPINE -> alpha_pyramid_core -> PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel"))
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry"))

from contracts import TaskEnvelope, TaskStatus, CascadeStatus

logger = logging.getLogger("SEC_GUARDIAN")

# ---------------------------------------------------------------------------
#  Rate-limit / Abuse Tracker
# ---------------------------------------------------------------------------

@dataclass
class _NodeRecord:
    request_times: list = field(default_factory=list)
    blocked_until: float = 0.0


class RateLimiter:
    """Sliding-window rate limiter: max N requests per window_seconds."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._records: dict[str, _NodeRecord] = defaultdict(_NodeRecord)

    def is_allowed(self, node_id: str) -> bool:
        now = time.time()
        rec = self._records[node_id]

        if now < rec.blocked_until:
            return False  # still in cooldown

        # Evict timestamps outside the window
        rec.request_times = [t for t in rec.request_times if now - t <= self.window_seconds]

        if len(rec.request_times) >= self.max_requests:
            rec.blocked_until = now + self.window_seconds
            logger.warning(f"[SEC_GUARDIAN] Rate limit triggered for '{node_id}'. Blocked for {self.window_seconds}s.")
            return False

        rec.request_times.append(now)
        return True


# ---------------------------------------------------------------------------
#  Anti-Spoofing Checker
# ---------------------------------------------------------------------------

# Trusted origin map: nodes that are allowed to claim a given z_level origin.
# Unlisted nodes must not claim Alpha (Z11+) origins.
TRUSTED_ALPHA_NODES = {"gen-nexus", "gen-meta", "gen-bridge", "gh_ci_guardian", "gen-pear"}


class OriginVerifier:
    @staticmethod
    def verify(envelope: TaskEnvelope) -> tuple[bool, str]:
        """Returns (pass, reason)."""
        # Rule: only trusted nodes may originate from Z11+
        if envelope.origin_z >= 11 and envelope.source_node not in TRUSTED_ALPHA_NODES:
            return False, f"SpoofingAttempt: '{envelope.source_node}' claims Z{envelope.origin_z} origin but is not a trusted Alpha node."
        return True, "OK"


# ---------------------------------------------------------------------------
#  SEC Guardian — Public Interface
# ---------------------------------------------------------------------------

class SecGuardian:
    """
    Z12 Security Proxy. Call `audit()` on every envelope descending from
    Z13 (EVO_BRIDGE) toward Z11 (PEAR_LOOP / Governance).
    """

    def __init__(self, max_rps: int = 10, window: int = 60):
        self._limiter = RateLimiter(max_requests=max_rps, window_seconds=window)
        self._verifier = OriginVerifier()

    def audit(self, envelope: TaskEnvelope) -> bool:
        """
        Returns True if the envelope passes all security checks.
        Mutates `envelope.status` and `envelope.metadata['error']` on failure.
        """
        # 1. Origin verification
        ok, reason = self._verifier.verify(envelope)
        if not ok:
            self._block(envelope, reason)
            return False

        # 2. Rate-limit check
        if not self._limiter.is_allowed(envelope.source_node):
            self._block(envelope, f"RateLimitViolation: '{envelope.source_node}' exceeded request quota.")
            return False

        logger.info(f"[SEC_GUARDIAN] ✅ Envelope {envelope.task_id} from '{envelope.source_node}' cleared security audit.")
        return True

    @staticmethod
    def _block(envelope: TaskEnvelope, reason: str):
        envelope.status = TaskStatus.FAILED
        envelope.metadata["error"] = reason
        logger.warning(f"[SEC_GUARDIAN] 🚫 BLOCKED — {reason}")
