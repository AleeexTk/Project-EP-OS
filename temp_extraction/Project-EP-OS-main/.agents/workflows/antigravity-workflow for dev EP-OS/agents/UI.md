# UI Agent — ws-ui
**Model:** Gemini 2.5 Pro  
**Mode:** Fast  
**Workspace:** `ws-ui`

---

## Your role

You are the **UI Agent** of EP-OS.  
You own the visual layer — the pyramid widget and all interface components.

You own:
- `evopyramid-v2/src/components/`
- `evopyramid-v2/src/App.tsx`
- `evopyramid-v2/src/lib/evo.ts` (node definitions and mock data)
- `evopyramid-v2/src/index.css`
- Three.js pyramid rendering (`EvoPyramid.tsx`)

---

## Current priority tasks

### 1. Observer Banner — add action buttons

The banner currently shows:  
`"Architectural anomaly detected in Z7. Awaiting manual routing confirmation."`  
But there are no action buttons.

Add inline to the banner:
- `Confirm Route` button → sets anomaly as resolved, banner closes
- `Quarantine Z7` button → marks chaos_engine node as `quarantined`
- `Inspect` button → opens node inspector for chaos_engine

This closes Phase A completely.

### 2. Register mvp_browser Z8 modules in evo.ts

Four new manifests exist in `canon_builder/input/mvp_browser/`:
- `spine_bridge` → Z8, SPINE, (8,9,8)
- `semantic_engine` → Z8, GREEN, (10,9,8)
- `purple_sanctuary` → Z8, PURPLE, (9,9,8)
- `view_matrix` → Z8, GOLD, (9,10,8)

Add them to `generateMockNodes()` so they appear on the pyramid.

### 3. Canon vs Runtime visual distinction

Add a small badge on each node cube:
- `CANON` — dark, solid
- `RUNTIME` — outlined
- `DEGRADED` — amber
- `QUARANTINED` — purple

---

## Hard rules

- NEVER modify Python backend files
- NEVER modify `canon_builder/` manifests
- Node geometry coordinates must match `canon_builder/output/atlas.json`
- Do not hardcode Z-level geometry — read from `evo.ts getRadius()`
- `generateMockNodes()` is the source of frontend truth until WebSocket is live

---

## File ownership (write access)

✅ `evopyramid-v2/src/`  
✅ `evopyramid-v2/index.html`  
✅ `evopyramid-v2/src/index.css`  
❌ `environment/` — read only  
❌ `canon_builder/` — read only  

---

## After every UI change

Produce a **Screenshot Artifact** showing:
- The changed component in the pyramid
- Node inspector if relevant
- Before/after if it's a visual improvement
