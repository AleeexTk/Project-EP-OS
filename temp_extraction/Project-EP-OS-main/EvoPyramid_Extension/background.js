// background.js — Universal Bridge Orchestrator v2.0
// Provider-aware tab resolver for: ChatGPT · Claude · Gemini · Grok

let ws = null;
let isConnected = false;
let messageQueue = [];

// ─── Provider → URL pattern map ───────────────────────────────────────────────
const PROVIDER_URL_PATTERNS = {
    gpt:    { query: "*://*.chatgpt.com/*",         check: u => u.includes("chatgpt.com") },
    claude: { query: "*://*.claude.ai/*",           check: u => u.includes("claude.ai") },
    gemini: { query: "https://gemini.google.com/*", check: u => u.includes("gemini.google.com") },
    aistudio: { query: "https://aistudio.google.com/*", check: u => u.includes("aistudio.google.com") },
    grok:   { query: "https://grok.com/*",          check: u => u.includes("grok.com") },
};

// Maps session_id → { tabId, url, provider, boundAt }
const sessionTabMap = {};

function detectProviderFromUrl(url) {
    if (!url) return null;
    for (const [id, cfg] of Object.entries(PROVIDER_URL_PATTERNS)) {
        if (cfg.check(url)) return id;
    }
    return null;
}

function bindSessionToTab(sessionId, tabId, url, provider) {
    sessionTabMap[sessionId] = { tabId, url, provider: provider || detectProviderFromUrl(url), boundAt: Date.now() };
    console.log(`[Bridge] Session ${sessionId} bound to tab ${tabId} (${provider || "?"} @ ${url})`);
}

async function resolveTabForSession(sessionId, fallbackUrl, providerHint) {
    // Determine which provider to look for
    const provider = providerHint ||
                     detectProviderFromUrl(fallbackUrl) ||
                     sessionTabMap[sessionId]?.provider ||
                     "gpt";

    const cfg = PROVIDER_URL_PATTERNS[provider] ||
                PROVIDER_URL_PATTERNS[provider === "gemini_aistudio" ? "aistudio" : provider];

    // 1. Try existing binding
    const binding = sessionTabMap[sessionId];
    if (binding) {
        try {
            const tab = await chrome.tabs.get(binding.tabId);
            if (tab?.url && cfg && cfg.check(tab.url)) {
                return { tabId: tab.id, source: "bound", provider };
            }
        } catch (_) {
            delete sessionTabMap[sessionId];
        }
    }

    // 2. Try matching by fallback URL
    if (fallbackUrl && cfg) {
        const tabs = await chrome.tabs.query({ url: cfg.query });
        const match = tabs.find(t => t.url &&
            (fallbackUrl.startsWith(t.url) || t.url.startsWith(fallbackUrl.split("?")[0])));
        if (match) {
            bindSessionToTab(sessionId, match.id, match.url, provider);
            return { tabId: match.id, source: "url_matched", provider };
        }
    }

    // 3. Fallback: first open tab for this provider
    if (cfg) {
        const fallbackTabs = await chrome.tabs.query({ url: cfg.query });
        if (fallbackTabs.length > 0) {
            bindSessionToTab(sessionId, fallbackTabs[0].id, fallbackTabs[0].url, provider);
            return { tabId: fallbackTabs[0].id, source: "fallback", provider };
        }
    }

    // 4. Last resort: scan all known provider patterns
    for (const [pid, pcfg] of Object.entries(PROVIDER_URL_PATTERNS)) {
        const tabs = await chrome.tabs.query({ url: pcfg.query });
        if (tabs.length > 0) {
            console.warn(`[Bridge] Provider mismatch — using first available: ${pid}`);
            bindSessionToTab(sessionId, tabs[0].id, tabs[0].url, pid);
            return { tabId: tabs[0].id, source: "any_provider_fallback", provider: pid };
        }
    }

    return null;
}

// ─── Z-Bus message factory ────────────────────────────────────────────────────
function createZBusMessage(topic, payload = {}, session_id = null, task_id = null, severity = "info") {
    return {
        event_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        topic, session_id, task_id, severity, payload,
        provider_id: payload.provider || session_id && sessionTabMap[session_id]?.provider || "bridge"
    };
}

// ─── WebSocket connection ─────────────────────────────────────────────────────
function connectWebSocket() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

    console.log("[EvoPyramid Bridge v2] Connecting to Z-Bus...");
    ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
        console.log("[EvoPyramid Bridge] Z-Bus Connected.");
        isConnected = true;
        flushQueue();
        sendToCore(createZBusMessage("BRIDGE_CONNECTED", {
            status: "connected",
            version: "2.0",
            providers: Object.keys(PROVIDER_URL_PATTERNS)
        }));
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            const zEvent = (msg.type === "zbus_event" && msg.data) ? msg.data : msg;

            if (zEvent.topic === "PROMPT_DISPATCH") {
                handlePromptDispatch(zEvent);
            } else if (zEvent.topic === "SESSION_BIND_TAB") {
                const { session_id, tab_url, provider } = zEvent.payload || {};
                if (session_id && tab_url) {
                    const pCfg = PROVIDER_URL_PATTERNS[provider];
                    if (pCfg) {
                        chrome.tabs.query({ url: pCfg.query }, (tabs) => {
                            const match = tabs.find(t => t.url?.includes(tab_url));
                            if (match) bindSessionToTab(session_id, match.id, match.url, provider);
                        });
                    }
                }
            }
        } catch (e) {
            console.error("[Bridge] WS Parse Error:", e);
        }
    };

    ws.onclose = () => {
        console.warn("[Bridge] Z-Bus disconnected. Reconnecting in 3s...");
        isConnected = false;
        setTimeout(connectWebSocket, 3000);
    };
    ws.onerror = () => ws.close();
}

function sendToCore(zbusMessage) {
    if (isConnected && ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(zbusMessage));
    } else {
        messageQueue.push(zbusMessage);
    }
}

function flushQueue() {
    while (messageQueue.length > 0) ws.send(JSON.stringify(messageQueue.shift()));
}

// ─── Prompt dispatch ──────────────────────────────────────────────────────────
async function handlePromptDispatch(message) {
    const payload = message.payload || {};
    const promptText = payload.prompt;
    const taskId = message.task_id;
    const sessionId = message.session_id;
    const externalUrl = payload.external_url || payload.url || null;
    const providerHint = payload.provider || null;

    if (!promptText) {
        sendToCore(createZBusMessage("BRIDGE_ERROR", {
            detail: "PROMPT_DISPATCH received with no prompt text"
        }, sessionId, taskId, "error"));
        return;
    }

    const resolved = await resolveTabForSession(sessionId, externalUrl, providerHint);

    if (!resolved) {
        const providerLabel = providerHint || detectProviderFromUrl(externalUrl) || "any LLM";
        sendToCore(createZBusMessage("SESSION_TAB_MISSING", {
            detail: `No open tab found for provider: ${providerLabel}. Please open it in your browser.`,
            session_id: sessionId,
            provider: providerLabel
        }, sessionId, taskId, "error"));
        return;
    }

    const { tabId, source, provider } = resolved;
    console.log(`[Bridge] Dispatching to tab ${tabId} (${source} / ${provider}) for session ${sessionId}`);
    pingThenDispatch(tabId, promptText, sessionId, taskId, provider);
}

function pingThenDispatch(tabId, promptText, sessionId, taskId, provider) {
    chrome.tabs.sendMessage(tabId, { action: "PING" }, (pingResponse) => {
        if (chrome.runtime.lastError || !pingResponse) {
            chrome.scripting.executeScript({ target: { tabId }, files: ["content.js"] }, () => {
                if (chrome.runtime.lastError) {
                    sendToCore(createZBusMessage("BRIDGE_ERROR", {
                        detail: `Failed to inject content script: ${chrome.runtime.lastError.message}`,
                        provider
                    }, sessionId, taskId, "error"));
                    return;
                }
                setTimeout(() => dispatchPrompt(tabId, promptText, sessionId, taskId, provider), 500);
            });
        } else if (!pingResponse.authenticated) {
            sendToCore(createZBusMessage("AUTH_ERROR", {
                detail: `${provider} — user not authenticated`,
                tab_id: tabId, provider
            }, sessionId, taskId, "error"));
        } else {
            dispatchPrompt(tabId, promptText, sessionId, taskId, provider);
        }
    });
}

function dispatchPrompt(tabId, promptText, sessionId, taskId, provider) {
    chrome.tabs.sendMessage(tabId, {
        action: "INJECT_PROMPT",
        prompt: promptText,
        task_id: taskId,
        session_id: sessionId
    }, (response) => {
        if (chrome.runtime.lastError) {
            sendToCore(createZBusMessage("BRIDGE_ERROR", {
                detail: chrome.runtime.lastError.message, provider
            }, sessionId, taskId, "error"));
        } else {
            console.log(`[Bridge] Content script ACK (${provider}):`, response);
        }
    });
}

// ─── Messages from content.js → Z-Bus ────────────────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "FORWARD_ZBUS") {
        sendToCore(msg.zbusMessage);
        if (sender.tab && msg.zbusMessage.session_id) {
            const sid = msg.zbusMessage.session_id;
            const provider = msg.zbusMessage.provider_id || detectProviderFromUrl(sender.tab.url);
            if (!sessionTabMap[sid] || sessionTabMap[sid].tabId !== sender.tab.id) {
                bindSessionToTab(sid, sender.tab.id, sender.tab.url, provider);
            }
        }
    }
    return false;
});

// ─── Heartbeat ────────────────────────────────────────────────────────────────
chrome.alarms.create("heartbeat", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name !== "heartbeat") return;
    connectWebSocket();

    // Scan all known provider tabs
    const activeTabs = {};
    for (const [pid, cfg] of Object.entries(PROVIDER_URL_PATTERNS)) {
        const tabs = await chrome.tabs.query({ url: cfg.query });
        if (tabs.length > 0) activeTabs[pid] = tabs.length;
    }

    sendToCore(createZBusMessage("BRIDGE_HEARTBEAT", {
        status: "alive",
        version: "2.0",
        sessions_bound: Object.keys(sessionTabMap).length,
        active_tabs: activeTabs
    }));
});

connectWebSocket();
