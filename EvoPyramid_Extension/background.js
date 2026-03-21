// background.js - Browser Bridge Orchestrator — Phase 1 Hardened
// Fixes: session→tab binding map, PING health check, error routing, PROMPT_ACCEPTED timing

let ws = null;
let isConnected = false;
let messageQueue = [];

// ─── Session → Tab Binding Map ───────────────────────────────────────────────
// Maps session_id → { tabId, url, boundAt }
const sessionTabMap = {};

function bindSessionToTab(sessionId, tabId, url) {
    sessionTabMap[sessionId] = { tabId, url, boundAt: Date.now() };
    console.log(`[Bridge] Session ${sessionId} bound to tab ${tabId} (${url})`);
}

async function resolveTabForSession(sessionId, fallbackUrl) {
    // 1. Try existing binding
    const binding = sessionTabMap[sessionId];
    if (binding) {
        try {
            const tab = await chrome.tabs.get(binding.tabId);
            if (tab && tab.url && tab.url.includes("chatgpt.com")) {
                return { tabId: tab.id, source: "bound" };
            }
        } catch (_) {
            // Tab was closed — remove stale binding
            delete sessionTabMap[sessionId];
        }
    }

    // 2. Try matching by URL if we have one
    if (fallbackUrl && fallbackUrl.includes("chatgpt.com")) {
        const tabs = await chrome.tabs.query({ url: "*://*.chatgpt.com/*" });
        const match = tabs.find(t => t.url && (
            fallbackUrl.startsWith(t.url) || t.url.startsWith(fallbackUrl.split('?')[0])
        ));
        if (match) {
            bindSessionToTab(sessionId, match.id, match.url);
            return { tabId: match.id, source: "url_matched" };
        }
    }

    // 3. Fallback: first available ChatGPT tab
    const fallbackTabs = await chrome.tabs.query({ url: "*://*.chatgpt.com/*" });
    if (fallbackTabs.length > 0) {
        bindSessionToTab(sessionId, fallbackTabs[0].id, fallbackTabs[0].url);
        return { tabId: fallbackTabs[0].id, source: "fallback" };
    }

    return null;
}

// ─── Z-Bus message factory ────────────────────────────────────────────────────
function createZBusMessage(topic, payload = {}, session_id = null, task_id = null, severity = "info") {
    return {
        event_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        topic,
        session_id,
        provider_id: "gpt",
        task_id,
        severity,
        payload
    };
}

// ─── WebSocket connection ─────────────────────────────────────────────────────
function connectWebSocket() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

    console.log("[EvoPyramid Bridge] Connecting to Z-Bus...");
    ws = new WebSocket('ws://127.0.0.1:8000/ws');

    ws.onopen = () => {
        console.log("[EvoPyramid Bridge] Z-Bus Connected.");
        isConnected = true;
        flushQueue();
        sendToCore(createZBusMessage("BRIDGE_CONNECTED", { status: "connected", provider: "ChatGPT" }));
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log("[Bridge] Received WS Message:", msg.type || msg.topic || "unknown");

            // Unwrap Z-Bus envelope
            const zEvent = (msg.type === "zbus_event" && msg.data) ? msg.data : msg;

            if (zEvent.topic === "PROMPT_DISPATCH") {
                handlePromptDispatch(zEvent);
            } else if (zEvent.topic === "SESSION_BIND_TAB") {
                // Explicit bind command: { session_id, tab_url }
                const { session_id, tab_url } = zEvent.payload || {};
                if (session_id && tab_url) {
                    chrome.tabs.query({ url: "*://*.chatgpt.com/*" }, (tabs) => {
                        const match = tabs.find(t => t.url && t.url.includes(tab_url));
                        if (match) bindSessionToTab(session_id, match.id, match.url);
                    });
                }
            }
        } catch (e) {
            console.error("[Bridge] WS Message Parse Error:", e, event.data);
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
    if (isConnected && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(zbusMessage));
    } else {
        messageQueue.push(zbusMessage);
    }
}

function flushQueue() {
    while (messageQueue.length > 0) {
        ws.send(JSON.stringify(messageQueue.shift()));
    }
}

// ─── Prompt dispatch ──────────────────────────────────────────────────────────
async function handlePromptDispatch(message) {
    const payload = message.payload || {};
    const promptText = payload.prompt;
    const taskId = message.task_id;
    const sessionId = message.session_id;
    const externalUrl = payload.external_url || payload.url || null;

    if (!promptText) {
        sendToCore(createZBusMessage("BRIDGE_ERROR", {
            detail: "PROMPT_DISPATCH received with no prompt text"
        }, sessionId, taskId, "error"));
        return;
    }

    const resolved = await resolveTabForSession(sessionId, externalUrl);

    if (!resolved) {
        console.warn("[Bridge] No ChatGPT tab found for session:", sessionId);
        sendToCore(createZBusMessage("SESSION_TAB_MISSING", {
            detail: "No open ChatGPT tab found. Please open ChatGPT in your browser.",
            session_id: sessionId
        }, sessionId, taskId, "error"));
        return;
    }

    const { tabId, source } = resolved;
    console.log(`[Bridge] Dispatching to tab ${tabId} (${source}) for session ${sessionId}`);

    // PING content script first to confirm it's alive
    pingThenDispatch(tabId, promptText, sessionId, taskId);
}

function pingThenDispatch(tabId, promptText, sessionId, taskId) {
    chrome.tabs.sendMessage(tabId, { action: "PING" }, (pingResponse) => {
        if (chrome.runtime.lastError || !pingResponse) {
            // Content script not running — inject it first
            console.log("[Bridge] Content script not responding, injecting...");
            chrome.scripting.executeScript({
                target: { tabId },
                files: ["content.js"]
            }, () => {
                if (chrome.runtime.lastError) {
                    sendToCore(createZBusMessage("BRIDGE_ERROR", {
                        detail: `Failed to inject content script: ${chrome.runtime.lastError.message}`,
                        hint: "Check if extension has permission for this tab"
                    }, sessionId, taskId, "error"));
                    return;
                }
                // Wait for script to initialise then dispatch
                setTimeout(() => dispatchPrompt(tabId, promptText, sessionId, taskId), 500);
            });
        } else if (!pingResponse.authenticated) {
            // Script alive but user not logged in
            sendToCore(createZBusMessage("AUTH_ERROR", {
                detail: "ChatGPT not authenticated — user must log in",
                tab_id: tabId
            }, sessionId, taskId, "error"));
        } else {
            // All good — dispatch
            dispatchPrompt(tabId, promptText, sessionId, taskId);
        }
    });
}

function dispatchPrompt(tabId, promptText, sessionId, taskId) {
    chrome.tabs.sendMessage(tabId, {
        action: "INJECT_PROMPT",
        prompt: promptText,
        task_id: taskId,
        session_id: sessionId
    }, (response) => {
        if (chrome.runtime.lastError) {
            sendToCore(createZBusMessage("BRIDGE_ERROR", {
                detail: chrome.runtime.lastError.message
            }, sessionId, taskId, "error"));
        } else {
            console.log("[Bridge] Content script ACK:", response);
            // PROMPT_ACCEPTED is emitted by content.js AFTER the send-button click
            // so we do NOT send it here — content.js owns that signal
        }
    });
}

// ─── Messages from content.js → Z-Bus ────────────────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "FORWARD_ZBUS") {
        sendToCore(msg.zbusMessage);
        // Update tab binding on any content.js message
        if (sender.tab && msg.zbusMessage.session_id) {
            const sid = msg.zbusMessage.session_id;
            if (!sessionTabMap[sid] || sessionTabMap[sid].tabId !== sender.tab.id) {
                bindSessionToTab(sid, sender.tab.id, sender.tab.url);
            }
        }
    }
    return false;
});

// ─── Heartbeat ────────────────────────────────────────────────────────────────
chrome.alarms.create("heartbeat", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "heartbeat") {
        connectWebSocket();
        sendToCore(createZBusMessage("BRIDGE_HEARTBEAT", {
            status: "alive",
            provider: "ChatGPT",
            sessions_bound: Object.keys(sessionTabMap).length
        }));

        // Scan for ChatGPT tabs and report
        chrome.tabs.query({ url: "*://*.chatgpt.com/*" }, (tabs) => {
            if (tabs.length > 0) {
                sendToCore(createZBusMessage("TAB_DISCOVERED", {
                    count: tabs.length,
                    url: tabs[0].url,
                    title: tabs[0].title,
                    tab_id: tabs[0].id
                }));
            }
        });
    }
});

connectWebSocket();
