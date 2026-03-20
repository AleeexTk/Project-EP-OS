// background.js - Browser Bridge Orchestrator (Z-Bus Vertical Slice)
let ws = null;
let isConnected = false;
let messageQueue = [];

// Schema Factory
function createZBusMessage(topic, payload = {}, session_id = null, task_id = null, severity = "info") {
    return {
        event_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        topic: topic,
        session_id: session_id,
        provider_id: "gpt",
        task_id: task_id,
        severity: severity,
        payload: payload
    };
}

function connectWebSocket() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
    
    console.log("[EvoPyramid Bridge] Connecting to Z-Bus...");
    ws = new WebSocket('ws://127.0.0.1:8000/ws');
    
    ws.onopen = () => {
        console.log("[EvoPyramid Bridge] Z-Bus Connected.");
        isConnected = true;
        flushQueue();
    };
    
    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log("[Bridge] Received WS Message:", msg.type || "unknown");

            // Handle Z-Bus events wrapped by the worker
            if (msg.type === "zbus_event" && msg.data) {
                const zEvent = msg.data;
                console.log(`[Bridge] Unwrapped Z-Bus Event: ${zEvent.topic}`);
                if (zEvent.topic === "PROMPT_DISPATCH") {
                    handlePromptDispatch(zEvent);
                }
            } 
            // Handle direct messages
            else if (msg.topic === "PROMPT_DISPATCH") {
                handlePromptDispatch(msg);
            }
        } catch (e) {
            console.error("[Bridge] WS Message Parse Error:", e, event.data);
        }
    };
    
    ws.onclose = () => {
        isConnected = false;
        setTimeout(connectWebSocket, 3000);
    };
    ws.onerror = () => ws.close();
}

function sendToCore(zbusMessage) {
    if (isConnected && ws.readyState === WebSocket.OPEN) {
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

// Inbound Routing
function handlePromptDispatch(message) {
    const payload = message.payload;
    const targetUrl = payload.url || "https://chatgpt.com/";
    const promptText = payload.prompt;
    const taskId = message.task_id;
    const sessionId = message.session_id;

    // Strict ChatGPT target for this slice
    chrome.tabs.query({ url: "*://*.chatgpt.com/*" }, (tabs) => {
        if (tabs.length > 0) {
            const tabId = tabs[0].id;
            console.log("[Bridge] Dispatching to ChatGPT tab:", tabId);
            
            chrome.tabs.sendMessage(tabId, { 
                action: "INJECT_PROMPT", 
                prompt: promptText,
                task_id: taskId,
                session_id: sessionId
            }, (response) => {
                if (chrome.runtime.lastError) {
                    const errMsg = chrome.runtime.lastError.message;
                    console.warn("[Bridge] Message failed, attempting auto-injection:", errMsg);
                    
                    if (errMsg.includes("Receiving end does not exist")) {
                        chrome.scripting.executeScript({
                            target: { tabId: tabId },
                            files: ["content.js"]
                        }, () => {
                            if (chrome.runtime.lastError) {
                                console.error("[Bridge] Auto-injection failed:", chrome.runtime.lastError.message);
                                sendToCore(createZBusMessage("BRIDGE_ERROR", { detail: "Injection failed" }, sessionId, taskId, "error"));
                            } else {
                                console.log("[Bridge] Auto-injection success, retrying dispatch...");
                                // Retry once after injection
                                setTimeout(() => {
                                    chrome.tabs.sendMessage(tabId, { 
                                        action: "INJECT_PROMPT", 
                                        prompt: promptText,
                                        task_id: taskId,
                                        session_id: sessionId
                                    });
                                }, 500);
                                sendToCore(createZBusMessage("PROMPT_ACCEPTED", { status: "received_after_inject" }, sessionId, taskId));
                            }
                        });
                    } else {
                        sendToCore(createZBusMessage("BRIDGE_ERROR", { detail: errMsg }, sessionId, taskId, "error"));
                    }
                } else {
                    console.log("[Bridge] Content script ACK:", response);
                    sendToCore(createZBusMessage("PROMPT_ACCEPTED", { status: "received" }, sessionId, taskId));
                }
            });
        } else {
            console.warn("[Bridge] No ChatGPT tabs found for dispatch.");
            sendToCore(createZBusMessage("BRIDGE_ERROR", { detail: "No active ChatGPT tab found" }));
        }
    });
}

// Receive from content.js and forward to Z-Bus
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "FORWARD_ZBUS") {
        sendToCore(msg.zbusMessage);
    }
});

// Heartbeat
chrome.alarms.create("heartbeat", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "heartbeat") {
        sendToCore(createZBusMessage("BRIDGE_HEARTBEAT", { status: "alive", provider: "ChatGPT" }));
        connectWebSocket();
        
        // Scan for tabs to update UI state
        chrome.tabs.query({ url: "*://*.chatgpt.com/*" }, (tabs) => {
            if (tabs.length > 0) {
                sendToCore(createZBusMessage("TAB_DISCOVERED", { 
                    url: tabs[0].url, 
                    title: tabs[0].title,
                    tab_id: tabs[0].id
                }));
            }
        });
    }
});

connectWebSocket();
