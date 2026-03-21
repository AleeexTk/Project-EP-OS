// content.js - ChatGPT Bridge — Phase 1 Hardened
// Fixes: React input injection, real TOKEN_STREAM deltas, auth detection, error specificity

// ─── Z-Bus emitter ──────────────────────────────────────────────────────────
function emitToZBus(topic, payload, session_id, task_id, severity = "info") {
    chrome.runtime.sendMessage({
        type: "FORWARD_ZBUS",
        zbusMessage: {
            event_id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            topic,
            session_id,
            provider_id: "gpt",
            task_id,
            severity,
            payload
        }
    });
}

// ─── Auth check ──────────────────────────────────────────────────────────────
function isAuthenticated() {
    // ChatGPT login page has a specific heading or login button
    const loginBtn = document.querySelector('button[data-testid="login-button"]');
    const welcomeHeading = document.querySelector('h1.text-4xl'); // "Welcome back"
    const loginPage = window.location.pathname === '/auth/login' ||
                      window.location.pathname === '/';
    if (loginBtn || welcomeHeading) return false;
    if (loginPage && !document.querySelector('#prompt-textarea')) return false;
    return true;
}

// ─── React-compatible text injection ─────────────────────────────────────────
function injectTextReact(element, text) {
    element.focus();

    if (element.tagName === "TEXTAREA") {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(element, text);
        element.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
        // Simulate a real user paste event, which is the most reliable way 
        // to bypass modern React rich-text editors (Draft.js/Lexical)
        element.innerHTML = '';
        element.focus();
        
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text/plain', text);
        
        const pasteEvent = new ClipboardEvent('paste', {
            clipboardData: dataTransfer,
            bubbles: true,
            cancelable: true
        });
        
        element.dispatchEvent(pasteEvent);
        
        // Fallback if paste event was ignored
        if (!element.innerText.includes(text.substring(0, 10))) {
            document.execCommand('insertText', false, text);
        }
    }

    // Secondary event blast for good measure
    ['input', 'change', 'keydown', 'keyup'].forEach(evtType => {
        element.dispatchEvent(new Event(evtType, { bubbles: true, cancelable: true }));
    });
}

// ─── Find prompt area ────────────────────────────────────────────────────────
function findPromptArea() {
    // Primary: ChatGPT stable test IDs
    const byId = document.querySelector('#prompt-textarea');
    if (byId) return byId;

    // Secondary: contenteditable with data-testid
    const byTestId = document.querySelector('[data-testid="prompt-textarea"]');
    if (byTestId) return byTestId;

    // Tertiary: any focused contenteditable in main area
    const allEditable = [...document.querySelectorAll('div[contenteditable="true"]')];
    const mainArea = document.querySelector('main');
    if (mainArea) {
        const inMain = allEditable.find(el => mainArea.contains(el));
        if (inMain) return inMain;
    }

    // Fallback: any textarea
    return document.querySelector('textarea');
}

// ─── Message listener ────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "INJECT_PROMPT") {
        executeChatGPTFlow(message.prompt, message.session_id, message.task_id);
        sendResponse({ status: "received" });
    }
    if (message.action === "PING") {
        sendResponse({ status: "alive", authenticated: isAuthenticated() });
    }
    return true;
});

// ─── Main flow ───────────────────────────────────────────────────────────────
function executeChatGPTFlow(promptText, sessionId, taskId) {
    // 1. Auth check first
    if (!isAuthenticated()) {
        console.warn("[Bridge] AUTH_ERROR: User not authenticated.");
        emitToZBus("AUTH_ERROR", {
            detail: "ChatGPT not authenticated — please log in",
            url: window.location.href
        }, sessionId, taskId, "error");
        return;
    }

    // 2. Find prompt area
    const promptArea = findPromptArea();
    if (!promptArea) {
        console.error("[Bridge] DOM_ERROR: Prompt area not found.");
        emitToZBus("DOM_ERROR", {
            detail: "ChatGPT input area not found — UI may have changed",
            url: window.location.href,
            hint: "Try refreshing the ChatGPT page"
        }, sessionId, taskId, "error");
        return;
    }

    // 3. Inject text using React-compatible method
    console.log("[Bridge] Injecting prompt via React-compatible path:", promptArea.tagName);
    injectTextReact(promptArea, promptText);

    // 4. Wait for React to process, then click Send
    setTimeout(() => {
        const sendBtn = document.querySelector('button[data-testid="send-button"]') ||
                        document.querySelector('button[aria-label="Send prompt"]');

        const getLatest = () => {
            const msgs = document.querySelectorAll('div[data-message-author-role="assistant"]');
            return msgs.length > 0 ? msgs[msgs.length - 1] : null;
        };

        const triggerClick = (btn) => {
            btn.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
            btn.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
            btn.click();
        };

        if (sendBtn && !sendBtn.disabled) {
            const prevMsg = getLatest();
            triggerClick(sendBtn);
            console.log("[Bridge] Send clicked — starting response observer.");
            emitToZBus("PROMPT_ACCEPTED", { status: "dispatched" }, sessionId, taskId);
            startResponseObserver(sessionId, taskId, prevMsg);
        } else if (sendBtn && sendBtn.disabled) {
            // Text may not have registered — retry once after a longer wait
            setTimeout(() => {
                const retryBtn = document.querySelector('button[data-testid="send-button"]') ||
                                 document.querySelector('button[aria-label="Send prompt"]');
                if (retryBtn && !retryBtn.disabled) {
                    const prevMsg = getLatest();
                    triggerClick(retryBtn);
                    emitToZBus("PROMPT_ACCEPTED", { status: "dispatched_after_retry" }, sessionId, taskId);
                    startResponseObserver(sessionId, taskId, prevMsg);
                } else {
                    emitToZBus("DOM_ERROR", {
                        detail: "Send button disabled — prompt injection may have failed",
                        hint: "Check if ChatGPT is generating a previous response"
                    }, sessionId, taskId, "error");
                }
            }, 600);
        } else {
            emitToZBus("DOM_ERROR", {
                detail: "Send button not found — ChatGPT UI may have changed",
                url: window.location.href
            }, sessionId, taskId, "error");
        }
    }, 350);
}

// ─── Response observer with real streaming ───────────────────────────────────
function startResponseObserver(sessionId, taskId, previousMsgNode) {
    const chatRoot = document.querySelector('main');
    if (!chatRoot) {
        emitToZBus("DOM_ERROR", {
            detail: "Cannot find main chat container for response observation"
        }, sessionId, taskId, "error");
        return;
    }

    let observer = null;
    let idleTimer = null;
    let streamStarted = false;
    let lastKnownLength = 0;
    
    // Throttle streaming updates: emit at most every 300ms
    let lastEmittedLength = 0;
    let lastStreamEmit = 0;
    const STREAM_THROTTLE_MS = 300;

    function getLatestAssistantMessage() {
        const msgs = document.querySelectorAll('div[data-message-author-role="assistant"]');
        return msgs.length > 0 ? msgs[msgs.length - 1] : null;
    }

    function isGenerating() {
        // ChatGPT shows a stop button while generating
        return !!(
            document.querySelector('button[aria-label="Stop generating"]') ||
            document.querySelector('button[data-testid="stop-button"]') ||
            document.querySelector('.result-streaming')
        );
    }

    function finalizeResponse(finalText) {
        if (!streamStarted) return;
        streamStarted = false; // Prevent double-firing
        
        if (observer) {
            observer.disconnect();
            observer = null;
        }

        // Flush any trailing delta before completion
        if (finalText.length > lastEmittedLength) {
            emitToZBus("TOKEN_STREAM", {
                delta: finalText.slice(lastEmittedLength),
                content: finalText,
                length: finalText.length
            }, sessionId, taskId);
        }

        console.log(`[Bridge] Response complete. Length: ${finalText.length}`);
        emitToZBus("RESPONSE_COMPLETE", {
            content: finalText,
            length: finalText.length,
            tokens_approx: Math.ceil(finalText.length / 4)
        }, sessionId, taskId);
    }

    function checkAndStream() {
        const latestMsg = getLatestAssistantMessage();
        
        // Wait until ChatGPT creates a strictly NEW assistant message node
        if (!latestMsg || latestMsg === previousMsgNode) return;

        const currentText = latestMsg.innerText || latestMsg.textContent || '';
        const now = Date.now();

        if (currentText.length > lastKnownLength) {
            // Text is actively growing
            streamStarted = true;
            lastKnownLength = currentText.length;

            // Emit throttled STREAM events
            if ((now - lastStreamEmit) >= STREAM_THROTTLE_MS) {
                const delta = currentText.slice(lastEmittedLength);
                lastEmittedLength = currentText.length;
                lastStreamEmit = now;

                emitToZBus("TOKEN_STREAM", {
                    delta,
                    content: currentText,
                    length: currentText.length
                }, sessionId, taskId);
            }

            // Reset idle completion timer: If 3 seconds pass with NO text growth, assume completion.
            if (idleTimer) clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                const latestText = latestMsg.innerText || latestMsg.textContent || '';
                finalizeResponse(latestText);
            }, 3000);

        } else if (streamStarted) {
            // Text didn't grow, but DOM mutated.
            // Fast completion optimization: if the stop button vanished, finish quickly
            if (!isGenerating()) {
                if (idleTimer) clearTimeout(idleTimer);
                idleTimer = setTimeout(() => {
                    const latestText = latestMsg.innerText || latestMsg.textContent || '';
                    finalizeResponse(latestText);
                }, 800); // Only an 800ms grace period if stop button is gone
            }
        }
    }

    observer = new MutationObserver(() => checkAndStream());
    observer.observe(chatRoot, {
        childList: true,
        subtree: true,
        characterData: true
    });

    // Safety timeout: 5 minutes max — disconnect and report if still waiting
    setTimeout(() => {
        if (observer) {
            observer.disconnect();
            emitToZBus("BRIDGE_ERROR", {
                detail: "Response observation timeout (5 min). No completion signal received."
            }, sessionId, taskId, "error");
        }
    }, 5 * 60 * 1000);

    // Initial check
    checkAndStream();
}
