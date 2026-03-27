# EP-OS Canonical Execution Model

EP-OS is not a monolithic application or a single website. It is a **Hybrid Architectural System** built upon three strictly separated layers. This document serves as the absolute canon defining their roles, boundaries, and the nature of the system's truth.

---

## 1. The Runtime Node (The Body)

The **Runtime Node** is where the project actually lives and breathes. It executes locally on the developer's machine or a dedicated self-hosted node.

**Responsibilities:**

- File system manipulation and local storage.
- Active memory and `pyramid_state.json` maintenance.
- Local agent instantiation and execution.
- Emitting the system heartbeat (`pulse`).
- Handling manifest generation and synchronization.
- **Role:** The executor.

## 2. The Shared Canon (The Law)

The **Shared Canon** is the conceptual and structural framework that binds the system together. It ensures that no matter where an operation takes place, the semantic integrity of the pyramid is preserved.

**Responsibilities:**

- Z-Architecture hierarchy (Levels 1 through 17).
- Definition of node types, sectors, and their allowed behaviors.
- The `TRINITY` protocols and role separation.
- Semantic contracts, routing rules, and graphical semantics.
- **Role:** The constitution.

## 3. The Global Control Plane (The Eye \& The Hand)

The **Global Control Plane** (formerly the "Web UI") is the remote orchestration layer. It is a dashboard and a mission console, not the operating system itself. It must never pretend to hold the local files or run the local agents.

**Responsibilities:**

- 3D visualization of the pyramid graph.
- Issuing remote commands (via Kernel Dispatch).
- Health monitoring and audit logging.
- Observer-level UX and macro-scale orchestration.
- **Role:** The bridge for the operator.

---

## 4. The Source of Truth (Hybrid Truth)

EP-OS operates on a **Hybrid Truth (Variant C)** paradigm:

- **Runtime Truth:** The definitive state of the project files, the real-time execution context, and the immediate agent memory reside strictly in the **Local Runtime Node**.
- **Orchestration Truth:** The dashboard views, remote telemetry, and managerial commands reside in the **Control Plane**.
The Truth is not located in one place; it is the correct alignment of local execution matching remote observation.

## 5. Synchronization Mechanism

The layers synchronize through the **Z-Bus** and the **Crystallized Spine (Kernel)**:

- The **Runtime Node** serves its state via REST/WebSocket (Ports 8000/11434).
- The **Control Plane** (Port 3000 or Cloud) connects to the Runtime's API.
- The Runtime pushes its pulse and state upward (Manifest Sync).
- The Control Plane pushes Mission Dispatches and Guard commands downward.
- If the Control Plane loses connection (e.g., *CORE OFFLINE*), the Runtime Node continues to live and execute locally, preserving the project's state until the observer reconnects.
