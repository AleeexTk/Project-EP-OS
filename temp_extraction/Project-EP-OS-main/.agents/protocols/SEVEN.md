# SEVEN — Universal Decision Stress Test for AI Agents

**Purpose:** To force any decision, idea, or architectural choice through seven mandatory stress vectors before action is taken.

---

## [1] PLACE

**Question:** Where does this live in the structure of the system?

* A decision must have a real place (file, layer, module, service, policy, etc.).
* What to answer: exact location, owner, scope, and system boundary.

## [2] BREAK

**Question:** What breaks first, and what happens next?

* Name one concrete first break and describe the chain of failure.
* What to answer: first failure point, immediate consequence, system reaction, recovery behavior.

## [3] CORE

**Question:** What cannot be removed without destroying the meaning?

* The irreducible essence in one line.
* Everything else is implementation or decoration.

## [4] HUMAN

**Question:** What does a real human actually do?

* Grounding vector: "I open → I see → I do → I get".
* Avoid vague abstractions like "it improves usability".

## [5] SIGNAL

**Question:** What message does the system send forward?

* Format: **origin / target / content / status**.
* Tests whether the decision has a clean handoff.

## [6] FORWARD

**Question:** What does this lead to after two iterations?

* Trajectory check: step 1 (logical next step) → step 2 (compounding effect).
* Reveals scaling value or technical debt.

## [7] AGAINST

**Question:** What is the strongest honest argument against this decision?

* Anti-self-deception vector. State the strongest objection and check if the decision can answer it.

---

## RESULT & SCORING archetypes

* **7/7 — PROCEED:** Structurally strong.
* **5–6/7 — REVISE:** Promising but unstable.
* **0–4/7 — REJECT:** Not ready for implementation.

**Hard-Fail Vectors (Non-optional):**

* **PLACE** (existence)
* **BREAK** (reality)
* **CORE** (meaning)
