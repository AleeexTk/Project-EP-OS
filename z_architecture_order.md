# EvoPyramid OS — Архитектурный Порядок Z1–Z17

> Аудит: 2026-03-15 | Статус: РАБОТА В ПРОЦЕССЕ

---

## Принцип чётности

| Тип | Z-уровни | Назначение |
| --- | --- | --- |
| 🦴 **Structural** (Кости) | Z17, Z15, Z13, Z11, Z9, Z7, Z5, Z3, Z1 | Модули, агенты, сервисы — видимые узлы силы |
| 🩸 **Infra / Transit** (Кровь) | Z16, Z14, Z12, Z10, Z8, Z6, Z4, Z2 | Роутеры, шины, зависимости, стэк, связи |

**Радиус слоя:** `R = 17 - Z + 1`. При центре (9,9): узел на Z17 имеет R=1, на Z1 — R=17.

---

## ALPHA LAYER — α_Pyramid_Core (Z17–Z11)

### Z17 — SPINE · Вершина системы (Structural ✅)

| Node ID | Title | Sector | Файл/Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-nexus` | GLOBAL NEXUS | SPINE | `α_Pyramid_Core/SPINE/17_GLOBAL_NEXUS` | ✅ Есть |

**Z16 — INFRA** (между Z17 и Z15): ❌ **ОТСУТСТВУЕТ**
> Нужен: Nexus Router / Boot Orchestrator
> Файл: `α_Pyramid_Core/SPINE/16_NEXUS_ROUTER/` + `.node_manifest.json`
> Назначение: маршрутизация команд от Nexus вниз к Z15; `Nexus_Boot.py` де-факто уже живёт здесь

---

### Z15 — PURPLE / RED · Управляющие протоколы (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-meta` | EVO META | PURPLE | `α_Pyramid_Core/PURPLE/15_EVO_META` | ✅ Есть |
| `openai_docs_hub` | OpenAI Docs Hub | PURPLE | `α_Pyramid_Core/PURPLE/15_OPENAI_DOCS_HUB` | ✅ Есть |

**Z14 — INFRA** (между Z15 и Z13): ❌ **ОТСУТСТВУЕТ**
> Нужен: Policy Bus / Protocol Dispatcher
> Назначение: связь между EVO META и EVO BRIDGE; распределяет политики от Z15 вниз
> Файл: `α_Pyramid_Core/SPINE/14_POLICY_BUS/`

---

### Z13 — RED · Мост в AI-провайдеры (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-bridge` | EVO BRIDGE | RED | `α_Pyramid_Core/RED/13_EVO_BRIDGE` | ✅ Есть |

**Z12 — INFRA** (между Z13 и Z11): ❌ **ОТСУТСТВУЕТ**
> Нужен: Provider Router (Gemini / OpenAI / Replicate adapter layer)
> Назначение: детали подключения к провайдерам, API-ключи, retry-логика
> Файл: `α_Pyramid_Core/RED/12_PROVIDER_ROUTER/`

---

### Z11 — GOLD · Governance & CI (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-pear` | PEAR LOOP | GOLD | `α_Pyramid_Core/GOLD/11_PEAR_LOOP` | ✅ Есть |
| `gh_ci_guardian` | GH CI Guardian | RED | `α_Pyramid_Core/RED/11_GH_CI_GUARDIAN` | ✅ Есть |

**Z10 — INFRA** (граница Alpha/Beta): ❌ **ОТСУТСТВУЕТ**
> Нужен: CR Gateway / Alpha→Beta Transit
> Назначение: контрактная передача задач из Alpha в Beta; здесь живёт `cr_gateway_z10.py` (файл есть, папки нет!)
> Файл: `α_Pyramid_Core/SPINE/10_CR_GATEWAY/` + перенести `cr_gateway_z10.py`

---

## BETA LAYER — β_Pyramid_Functional (Z9–Z5)

### Z9 — GREEN · Агенты и раннеры (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-async-jobs` | ASYNC JOB RUNNER | GREEN | `β_Pyramid_Functional/GREEN/9_ASYNC_JOB_RUNNER` | ✅ Есть |
| `gh_pr_resolver` | GH PR Resolver | GREEN | `β_Pyramid_Functional/GREEN/9_GH_PR_RESOLVER` | ✅ Есть |

**Z8 — INFRA** (между Z9 и Z7): ❌ **ОТСУТСТВУЕТ**
> Нужен: Agent Bus / Z-Bus (файл `agent_bus_z8.py` существует в бета-слое! — папки нет)
> Назначение: inter-agent шина, маршрут задач между агентами; Z-Bus уже написан
> Файл: `β_Pyramid_Functional/SPINE/8_AGENT_BUS/` + перенести `agent_bus_z8.py`

---

### Z7 — GREEN / SPINE · Runtime Engine (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-webmcp` | WEB MCP CORE | GREEN | `β_Pyramid_Functional/GREEN/7_WEB_MCP_CORE` | ✅ Есть |
| `chatgpt_apps_bridge` | ChatGPT Apps Bridge | SPINE | `β_Pyramid_Functional/SPINE/7_CHATGPT_APPS_BRIDGE` | ✅ Есть |

> ⚠️ `chaos_bus_z7.py` существует в корне β но не имеет папки-узла!
> Нужен узел: `β_Pyramid_Functional/SPINE/7_CHAOS_ENGINE/`

**Z6 — INFRA** (между Z7 и Z5): ❌ **ОТСУТСТВУЕТ**
> Нужен: Resolution Stream / Chaos→Dashboard bridge
> Файл `resolution_stream_z6.py` существует! — папки нет
> Файл: `β_Pyramid_Functional/SPINE/6_RESOLUTION_STREAM/`

---

### Z5 — SPINE · Dashboard / Action (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `gen-dashboard` | EVO DASHBOARD | SPINE | `β_Pyramid_Functional/SPINE/5_EVO_DASHBOARD` | ✅ Есть |
| `test_stress_node` | Stress Test Node | GREEN | `β_Pyramid_Functional/GREEN/5_Stress_Test_Node` | ⚠️ Тестовый — удалить |

**Z4 — INFRA** (граница Beta/Gamma): ❌ **ОТСУТСТВУЕТ**
> Нужен: Observer Relay (файл `observer_relay_z4.py` в γ-слое уже пустой)
> Назначение: передача событий из Beta в Gamma (логи, пульс)
> Файл: `β_Pyramid_Functional/SPINE/4_OBSERVER_RELAY/`

---

## GAMMA LAYER — γ_Pyramid_Reflective (Z3–Z1)

### Z3 — GOLD · Reflective Checkpoints (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `netlify_deploy_beacon` | Netlify Deploy Beacon | GOLD | `γ_Pyramid_Reflective/GOLD/3_NETLIFY_DEPLOY_BEACON` | ✅ Есть |

**Z2 — INFRA** (между Z3 и Z1): ❌ **ОТСУТСТВУЕТ**
> Нужен: Audit Bridge / Reflection Relay
> Назначение: связь Netlify Beacon → Deploy Audit Ledger
> Файл: `γ_Pyramid_Reflective/SPINE/2_AUDIT_BRIDGE/`

---

### Z1 — SPINE · База памяти (Structural ✅)

| Node ID | Title | Sector | Папка | Статус |
| --- | --- | --- | --- | --- |
| `deploy_audit_ledger` | Deploy Audit Ledger | SPINE | `γ_Pyramid_Reflective/SPINE/1_DEPLOY_AUDIT_LEDGER` | ✅ Есть |

---

## Сводный аудит: что нужно создать

### Фазы работ

#### 🔴 ФАЗА 1 — Регистрация "сирот" (файлы без папок-узлов)

Эти `.py` файлы живут без соответствующих директорий-узлов.
Задача: создать папки + `.node_manifest.json` для каждого.

| Файл | Текущее место | Нужная папка-узел | Z | Sector |
| --- | --- | --- | --- | --- |
| `cr_gateway_z10.py` | `β_Pyramid_Functional/` | `α_Pyramid_Core/SPINE/10_CR_GATEWAY/` | Z10 | SPINE |
| `agent_bus_z8.py` | `β_Pyramid_Functional/` | `β_Pyramid_Functional/SPINE/8_AGENT_BUS/` | Z8 | SPINE |
| `chaos_bus_z7.py` | `β_Pyramid_Functional/` | `β_Pyramid_Functional/SPINE/7_CHAOS_ENGINE/` | Z7 | SPINE |
| `resolution_stream_z6.py` | `β_Pyramid_Functional/` | `β_Pyramid_Functional/SPINE/6_RESOLUTION_STREAM/` | Z6 | SPINE |
| `observer_relay_z4.py` | `γ_Pyramid_Reflective/` | `γ_Pyramid_Reflective/SPINE/4_OBSERVER_RELAY/` | Z4 | SPINE |
| `joint_sync_z1.py` | `γ_Pyramid_Reflective/` | `γ_Pyramid_Reflective/SPINE/1_DEPLOY_AUDIT_LEDGER/` | Z1 | SPINE |

#### 🟡 ФАЗА 2 — Создание инфра-узлов (Z-чётные)

Новые папки + манифесты для инфраструктурных Z-уровней:

| Папка | Z | Назначение |
| --- | --- | --- |
| `α_Pyramid_Core/SPINE/16_NEXUS_ROUTER/` | Z16 | Boot routing, Nexus_Boot.py wrapper |
| `α_Pyramid_Core/SPINE/14_POLICY_BUS/` | Z14 | Policy dispatching Alpha→Beta |
| `α_Pyramid_Core/RED/12_PROVIDER_ROUTER/` | Z12 | AI provider adapters (Gemini/OpenAI/Replicate) |
| `β_Pyramid_Functional/SPINE/6_RESOLUTION_STREAM/` | Z6 | Resolution stream Beta→observability |
| `β_Pyramid_Functional/SPINE/4_OBSERVER_RELAY/` | Z4 | Event relay Beta→Gamma |
| `γ_Pyramid_Reflective/SPINE/2_AUDIT_BRIDGE/` | Z2 | Audit relay Gamma Z3→Z1 |

#### 🟢 ФАЗА 3 — Связи (links)

Добавить в `pyramid_state.json` и `.node_manifest.json` ссылки `links: []`:

| От | К | Через |
| --- | --- | --- |
| `gen-nexus` (Z17) | `gen-meta` (Z15) | Z16 nexus_router |
| `gen-meta` (Z15) | `gen-bridge` (Z13) | Z14 policy_bus |
| `gen-bridge` (Z13) | `gh_ci_guardian` (Z11) | Z12 provider_router |
| `gen-pear` (Z11) | `gen-async-jobs` (Z9) | Z10 cr_gateway |
| `gen-async-jobs` (Z9) | `gen-webmcp` (Z7) | Z8 agent_bus |
| `gen-webmcp` (Z7) | `gen-dashboard` (Z5) | Z6 resolution_stream |
| `gen-dashboard` (Z5) | `netlify_deploy_beacon` (Z3) | Z4 observer_relay |
| `netlify_deploy_beacon` (Z3) | `deploy_audit_ledger` (Z1) | Z2 audit_bridge |

#### 🔵 ФАЗА 4 — Cleanup

- Удалить `test_stress_node` из `pyramid_state.json` и его папку
- Добавить `runtime_canon_flag` в `models.py` → `Node`
- `PATCH /nodes/{id}/status` endpoint в `evo_api.py`
- Observer Banner в `App.tsx`
- После всего: `POST /canon/guard/apply?update_existing=true&prune_missing=true`

---

## Карта Z-Spine (вертикаль)

```text
Z17  SPINE  gen-nexus          [GLOBAL NEXUS]        ← вершина
Z16  SPINE  nexus_router       [BOOT ROUTER]         ← INFRA ❌
Z15  PURPLE gen-meta           [EVO META]
Z14  SPINE  policy_bus         [POLICY BUS]          ← INFRA ❌
Z13  RED    gen-bridge         [EVO BRIDGE]
Z12  RED    provider_router    [PROVIDER ROUTER]     ← INFRA ❌
Z11  GOLD   gen-pear           [PEAR LOOP]
Z10  SPINE  cr_gateway         [CR GATEWAY]          ← INFRA ❌ (файл есть)
─────────── Alpha / Beta boundary ───────────────────
Z9   GREEN  gen-async-jobs     [ASYNC JOB RUNNER]
Z8   SPINE  agent_bus          [AGENT BUS]           ← INFRA ❌ (файл есть)
Z7   GREEN  gen-webmcp         [WEB MCP CORE]
Z7   SPINE  chaos_bus          [CHAOS ENGINE]        ← ❌ нет узла
Z6   SPINE  resolution_stream  [RESOLUTION STREAM]   ← INFRA ❌ (файл есть)
Z5   SPINE  gen-dashboard      [EVO DASHBOARD]
Z4   SPINE  observer_relay     [OBSERVER RELAY]      ← INFRA ❌ (файл есть)
─────────── Beta / Gamma boundary ───────────────────
Z3   GOLD   netlify_beacon     [NETLIFY DEPLOY BEACON]
Z2   SPINE  audit_bridge       [AUDIT BRIDGE]        ← INFRA ❌
Z1   SPINE  deploy_audit       [DEPLOY AUDIT LEDGER] ← основание
```

---

## Следующий шаг

**ФАЗА 1 начинается сейчас**: создаём папки-узлы для файлов-сирот + их `.node_manifest.json` → затем запускаем `/sync/discover-modules?update_existing=true`.
