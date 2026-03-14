// background.js - The Robust Orchestrator
let ws = null;
let isConnected = false;
let messageQueue = []; // The Offline Queue

// Establish unkillable connection loop
function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

  console.log("[EvoPyramid Nexus] Attempting connection to os kernel...");
  ws = new WebSocket('ws://127.0.0.1:8000/ws');

  ws.onopen = () => {
    console.log("[EvoPyramid Nexus] Linked to Core.");
    isConnected = true;
    flushQueue(); // Send all stacked messages
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleIncomingCommand(data);
  };

  ws.onclose = () => {
    console.warn("[EvoPyramid Nexus] Connection lost. Falling back to offline queue.");
    isConnected = false;
    setTimeout(connectWebSocket, 5000); // Exponential backoff in production
  };

  ws.onerror = (err) => {
    console.error("[EvoPyramid Nexus] Socket error.", err);
    ws.close();
  };
}

// Queue system for Offline safety
function sendToCore(payload) {
  if (isConnected && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload));
  } else {
    console.log("[EvoPyramid Nexus] Offline. Queuing payload for sync.", payload);
    messageQueue.push(payload);
    // Persist queue to local storage in case browser closes
    chrome.storage.local.set({ offlineQueue: messageQueue });
  }
}

function flushQueue() {
  chrome.storage.local.get(['offlineQueue'], (result) => {
    let q = result.offlineQueue || messageQueue;
    while (q.length > 0) {
      let msg = q.shift();
      ws.send(JSON.stringify(msg));
    }
    messageQueue = [];
    chrome.storage.local.set({ offlineQueue: [] });
  });
}

function handleIncomingCommand(command) {
    if (command.type === "LLM_INJECT_PROMPT") {
        injectPromptIntoTab(command.url, command.prompt, command.node_id);
    }
}

// Find existing tab or create new isolated one
function injectPromptIntoTab(targetUrl, promptText, callingNodeId) {
    chrome.tabs.query({ url: targetUrl + "*" }, (tabs) => {
        let tabId;
        if (tabs.length > 0) {
            tabId = tabs[0].id; // Reuse existing session
            chrome.tabs.sendMessage(tabId, { action: "RUN_PROMPT", prompt: promptText, node_id: callingNodeId });
        } else {
            // Create a pinned background tab
            chrome.tabs.create({ url: targetUrl, active: false, pinned: true }, (newTab) => {
                // Wait for map load and inject
                setTimeout(() => {
                    chrome.tabs.sendMessage(newTab.id, { action: "RUN_PROMPT", prompt: promptText, node_id: callingNodeId });
                }, 5000); // Temporary dumb wait, robust version uses tab update listener
            });
        }
    });
}

// Kickstart the heartbeat
chrome.alarms.create("heartbeat", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "heartbeat") connectWebSocket();
});

connectWebSocket();
