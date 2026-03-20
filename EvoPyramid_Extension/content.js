// content.js - ChatGPT Strict Flow (Z-Bus Vertical Slice)

// Send structured standard events back to background script
function emitToZBus(topic, payload, session_id, task_id, severity="info") {
    chrome.runtime.sendMessage({
        type: "FORWARD_ZBUS",
        zbusMessage: {
            event_id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            topic: topic,
            session_id: session_id,
            provider_id: "gpt",
            task_id: task_id,
            severity: severity,
            payload: payload
        }
    });
}

// Listen for injection commands
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "INJECT_PROMPT") {
        executeChatGPTFlow(message.prompt, message.session_id, message.task_id);
        sendResponse({status: "received"});
    }
    return true;
});

function executeChatGPTFlow(promptText, sessionId, taskId) {
    // 1. Detect prompt area (ChatGPT contenteditable div)
    let promptArea = document.querySelector('#prompt-textarea') || 
                     document.querySelector('div[contenteditable="true"]') ||
                     document.querySelector('textarea');

    if (!promptArea) {
        console.warn("[Bridge] Could not find prompt area via standard selectors, searching by placeholder...");
        const allDivs = document.querySelectorAll('div[contenteditable="true"]');
        for (let div of allDivs) {
            if (div.innerText.toLowerCase().includes("chat") || div.getAttribute('placeholder')) {
                promptArea = div;
                break;
            }
        }
    }

    if (!promptArea) {
        console.error("[Bridge] DOM_ERROR: Prompt area not found.");
        emitToZBus("DOM_ERROR", { detail: "Could not find prompt area" }, sessionId, taskId, "error");
        return;
    }

    // 2. Inject Prompt
    console.log("[Bridge] Injecting prompt into:", promptArea);
    if (promptArea.tagName === "TEXTAREA") {
        promptArea.value = promptText;
    } else {
        promptArea.innerHTML = `<p>${promptText}</p>`;
    }
    
    // Dispatch events to trigger React state updates
    const events = ['input', 'change', 'keydown', 'keyup', 'keypress'];
    events.forEach(type => {
        promptArea.dispatchEvent(new Event(type, { bubbles: true }));
    });

    // 3. Click Send
    setTimeout(() => {
        let sendBtn = document.querySelector('button[data-testid="send-button"]');
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            emitToZBus("PROMPT_ACCEPTED", { status: "dispatched" }, sessionId, taskId);
            
            // 4. Start Observers
            startResponseObserver(sessionId, taskId);
        } else {
            emitToZBus("DOM_ERROR", { detail: "Send button missing or disabled" }, sessionId, taskId, "error");
        }
    }, 300);
}

function startResponseObserver(sessionId, taskId) {
    let lastLength = 0;
    let observer = null;
    let finalCheckTimer = null;

    // We observe the main chat output area
    const chatObserverTarget = document.querySelector('main');
    if (!chatObserverTarget) {
        emitToZBus("DOM_ERROR", { detail: "Could not find ChatGPT main container for observer" }, sessionId, taskId, "error");
        return;
    }

    function checkCompletion() {
        // Stop button presence is the main indicator ChatGPT is thinking
        // Different UI versions have different stop buttons, commonly aria-label="Stop generating"
        const stopBtn = document.querySelector('button[aria-label="Stop generating"]');
        const sendBtn = document.querySelector('button[data-testid="send-button"]');
        
        // Find the latest assistant message
        const messages = document.querySelectorAll('div[data-message-author-role="assistant"]');
        const latestMsg = messages[messages.length - 1];
        
        if (latestMsg) {
            const currentText = latestMsg.innerText;
            if (currentText.length > lastLength) {
                // If we want actual streaming, we send TOKEN_STREAM delta here
                // For simplicity in the slice, we just send a status ping if needed, or wait for complete
                lastLength = currentText.length;
            }
        }

        // Logic for completion: Stop button disappeared AND Send button is back (and we actually captured a message)
        if (!stopBtn && sendBtn && latestMsg) {
            // Give it 1 second grace period to ensure DOM fully settled
            if (finalCheckTimer) clearTimeout(finalCheckTimer);
            finalCheckTimer = setTimeout(() => {
                const finalMsgText = latestMsg.innerText;
                emitToZBus("RESPONSE_COMPLETE", { 
                    content: finalMsgText, 
                    tokens: finalMsgText.length // Rough proxy for now
                }, sessionId, taskId);
                
                if (observer) observer.disconnect();
            }, 1000);
        } else if (stopBtn) {
           // still generating, clear final check if it accidentally triggered
           if (finalCheckTimer) clearTimeout(finalCheckTimer);
        }
    }

    // Observe changes inside the main tag
    observer = new MutationObserver((mutations) => {
        checkCompletion();
    });

    observer.observe(chatObserverTarget, { childList: true, subtree: true, characterData: true });

    // Initial check in case it responds instantly
    checkCompletion();
}
