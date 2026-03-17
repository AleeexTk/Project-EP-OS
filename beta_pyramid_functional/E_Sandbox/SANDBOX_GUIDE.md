# EP-OS Principle: The Sandbox Protocol

## Overview

All new integrations, experimental agents, and architectural changes MUST live in the `EP-Sandbox` sector until they are verified for stability and security. This ensures the Core Pyramid remains crystallized and unbreakable.

## The Sandbox Lifecycle

### 1. Incubation (`SANDBOX` Sector)

- **Location**: `β_Pyramid_Functional/E_Sandbox/`
- **Security**: **Zero-Trust Isolation**.
- **Permissions**: Sandbox nodes cannot write to the filesystem or access the network without explicit Architect (User) approval via `TaskEnvelope` overrides.
- **Monitoring**: Every action is logged in the `Kernel Audit Log`.

### 2. Crystallization (Testing)

- The module is tested for performance, latency, and compliance with the `Trinity Protocol`.
- The `Reality Monitor` performs a stress test (Phase 2 audit).

### 3. Release (Core Sector)

- Upon successful validation, the node is moved to its permanent sector (e.g., `GOLD`, `RED`, `GREEN`).
- It is granted "Resident Status" and its policies are formalized in the `SystemPolicyManager`.

## How to use

When creating a new node, set its `sector` metadata to `SANDBOX` in the `.node_manifest.json`. The `Spine-Kernel` will automatically detect and isolate it.

---
*Signed by the Iron Guardian (Provocateur)*
