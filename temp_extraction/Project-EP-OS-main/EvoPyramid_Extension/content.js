// content.js — Universal LLM Bridge v2.0
// Providers: ChatGPT · Claude · Gemini · Grok
// Architecture: provider config registry → single universal flow

// ─── Provider Registry ────────────────────────────────────────────────────────
const PROVIDERS = {
    chatgpt: {
        id: "gpt",
        match: () => location.hostname.includes("chatgpt.com"),
        isAuthenticated() {
            if (document.querySelector('button[data-testid="login-button"]')) return false;
            if (["/auth/login", "/"].includes(location.pathname) &&
                !document.querySelector("#prompt-textarea")) return false;
            return true;
        },
        findInput() {
            return document.querySelector("#prompt-textarea") ||
                   document.querySelector('[data-testid="prompt-textarea"]') ||
                   [...document.querySelectorAll('div[contenteditable="true"]')]
                       .find(el => document.querySelector("main")?.contains(el)) ||
                   document.querySelector("textarea");
        },
        findSendBtn() {
            return document.querySelector('button[data-testid="send-button"]') ||
                   document.querySelector('button[aria-label="Send prompt"]');
        },
        findChatRoot() {
            return document.querySelector("main") ||
                   document.querySelector('[class*="conversation"]');
        },
        getLatestResponse() {
            const msgs = document.querySelectorAll('div[data-message-author-role="assistant"]');
            return msgs.length ? msgs[msgs.length - 1] : null;
        },
        isGenerating() {
            return !!(
                document.querySelector('button[aria-label="Stop generating"]') ||
                document.querySelector('button[data-testid="stop-button"]') ||
                document.querySelector(".result-streaming")
            );
        }
    },

    claude: {
        id: "claude",
        match: () => location.hostname.includes("claude.ai"),
        isAuthenticated() {
            if (location.pathname.startsWith("/login")) return false;
            return !!this.findInput();
        },
        findInput() {
            return document.querySelector('div[contenteditable="true"].ProseMirror') ||
                   document.querySelector('fieldset div[contenteditable="true"]') ||
                   document.querySelector('[data-testid="composer-input"]') ||
                   [...document.querySelectorAll('div[contenteditable="true"]')]
                       .find(el => el.closest("fieldset") || el.closest("form"));
        },
        findSendBtn() {
            return document.querySelector('button[aria-label="Send Message"]') ||
                   document.querySelector('button[type="submit"]') ||
                   [...document.querySelectorAll("button")]
                       .find(b => b.ariaLabel?.toLowerCase().includes("send"));
        },
        findChatRoot() {
            return document.querySelector('[data-testid="conversation"]') ||
                   document.querySelector("main") ||
                   document.querySelector('[class*="conversation"]');
        },
        getLatestResponse() {
            const msgs = document.querySelectorAll(
                '[data-testid="assistant-message"], ' +
                '.font-claude-message, ' +
                '[data-is-streaming], ' +
                '[data-message-author="assistant"]'
            );
            if (msgs.length) return msgs[msgs.length - 1];
            const main = document.querySelector("main");
            if (!main) return null;
            const divs = [...main.querySelectorAll("div.prose, div[class*='message']")];
            return divs.length ? divs[divs.length - 1] : null;
        },
        isGenerating() {
            return !!(
                document.querySelector('[data-is-streaming="true"]') ||
                document.querySelector('button[aria-label="Stop"]') ||
                document.querySelector('[class*="streaming"]')
            );
        }
    },

    gemini: {
        id: "gemini",
        match: () =>
            location.hostname.includes("gemini.google.com") ||
            location.hostname.includes("aistudio.google.com"),
        isAuthenticated() {
            return !document.querySelector('a[href*="accounts.google.com"]');
        },
        findInput() {
            return document.querySelector(".input-area-container textarea") ||
                   document.querySelector("ms-prompt-input-wrapper textarea") ||
                   document.querySelector('div[contenteditable="true"][class*="input"]') ||
                   document.querySelector("rich-textarea div[contenteditable='true']") ||
                   document.querySelector("textarea");
        },
        findSendBtn() {
            return document.querySelector('button[aria-label="Send message"]') ||
                   document.querySelector('button.send-button') ||
                   document.querySelector('button[mattooltip="Run"]') ||
                   [...document.querySelectorAll("button")]
                       .find(b => b.ariaLabel?.toLowerCase().includes("send") ||
                                  b.ariaLabel?.toLowerCase() === "run");
        },
        findChatRoot() {
            return document.querySelector("chat-window") ||
                   document.querySelector("ms-chat-turn-container") ||
                   document.querySelector("main");
        },
        getLatestResponse() {
            const msgs = document.querySelectorAll(
                "message-content, .model-response-text, " +
                "ms-chat-turn:last-child .response-container, " +
                "[data-message-type='model']"
            );
            return msgs.length ? msgs[msgs.length - 1] : null;
        },
        isGenerating() {
            return !!(
                document.querySelector(".loading-bar") ||
                document.querySelector('[aria-label="Stop response"]') ||
                document.querySelector(".response-loading")
            );
        }
    },

    grok: {
        id: "grok",
        match: () => location.hostname.includes("grok.com"),
        isAuthenticated() {
            return !document.querySelector('a[href*="/i/flow/login"]') && !!this.findInput();
        },
        findInput() {
            return document.querySelector('textarea[placeholder*="Message"]') ||
                   document.querySelector('div[contenteditable="true"][data-lexical-editor]') ||
                   document.querySelector("textarea");
        },
        findSendBtn() {
            return document.querySelector('button[aria-label="Send"]') ||
                   document.querySelector('button[type="submit"]') ||
                   [...document.querySelectorAll("button")]
                       .find(b => b.ariaLabel?.toLowerCase().includes("send"));
        },
        findChatRoot() {
            return document.querySelector('[class*="message-list"]') ||
                   document.querySelector("main");
        },
        getLatestResponse() {
            const msgs = document.querySelectorAll(
                '[class*="AssistantMessage"], [data-message-author="grok"], ' +
                '[class*="response-content"]'
            );
            return msgs.length ? msgs[msgs.length - 1] : null;
        },
        isGenerating() {
            return !!(
                document.querySelector('[class*="isStreaming"]') ||
                document.querySelector('button[aria-label="Stop"]')
            );
        }
    }
};

// ─── Detect active provider ───────────────────────────────────────────────────
const PROVIDER = Object.values(PROVIDERS).find(p => p.match()) || null;

// ─── Z-Bus emitter ────────────────────────────────────────────────────────────
function emitToZBus(topic, payload, session_id, task_id, severity = "info") {
    chrome.runtime.sendMessage({
        type: "FORWARD_ZBUS",
        zbusMessage: {
            event_id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            topic, session_id, task_id, severity, payload,
            provider_id: PROVIDER?.id ?? "unknown"
        }
    });
}

// ─── Universal text injection (textarea / ProseMirror / Lexical / Draft.js) ──
function injectText(element, text) {
    element.focus();

    if (element.tagName === "TEXTAREA") {
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, "value"
        )?.set;
        setter ? setter.call(element, text) : (element.value = text);
        ["input", "change"].forEach(t =>
            element.dispatchEvent(new Event(t, { bubbles: true })));
    } else if (element.isContentEditable) {
        element.innerHTML = "";
        element.focus();
        const dt = new DataTransfer();
        dt.setData("text/plain", text);
        element.dispatchEvent(new ClipboardEvent("paste", {
            clipboardData: dt, bubbles: true, cancelable: true
        }));
        // Fallback if paste was swallowed
        setTimeout(() => {
            const cur = element.innerText || element.textContent || "";
            if (!cur.includes(text.substring(0, 15))) {
                document.execCommand("insertText", false, text);
            }
        }, 50);
    }

    ["input", "change", "keydown", "keyup"].forEach(t =>
        element.dispatchEvent(new Event(t, { bubbles: true, cancelable: true })));
}

// ─── Message listener ─────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "INJECT_PROMPT") {
        if (!PROVIDER) {
            sendResponse({ status: "error", detail: "Provider not detected on this page" });
            return true;
        }
        executeProviderFlow(message.prompt, message.session_id, message.task_id);
        sendResponse({ status: "received", provider: PROVIDER.id });
    }
    if (message.action === "PING") {
        sendResponse({
            status: "alive",
            provider: PROVIDER?.id ?? "unknown",
            authenticated: PROVIDER ? PROVIDER.isAuthenticated() : false
        });
    }
    return true;
});

// ─── Main universal flow ──────────────────────────────────────────────────────
function executeProviderFlow(promptText, sessionId, taskId) {
    if (!PROVIDER) {
        emitToZBus("BRIDGE_ERROR", {
            detail: "No supported LLM provider detected on this page",
            url: location.href
        }, sessionId, taskId, "error");
        return;
    }

    if (!PROVIDER.isAuthenticated()) {
        emitToZBus("AUTH_ERROR", {
            detail: `${PROVIDER.id} — user not authenticated`,
            url: location.href, provider: PROVIDER.id
        }, sessionId, taskId, "error");
        return;
    }

    const input = PROVIDER.findInput();
    if (!input) {
        emitToZBus("DOM_ERROR", {
            detail: `${PROVIDER.id} — input area not found`,
            url: location.href, provider: PROVIDER.id,
            hint: "Try refreshing the page"
        }, sessionId, taskId, "error");
        return;
    }

    const prevMsg = PROVIDER.getLatestResponse();
    injectText(input, promptText);

    const tryDispatch = (attempt = 1) => {
        const sendBtn = PROVIDER.findSendBtn();
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
            sendBtn.dispatchEvent(new PointerEvent("pointerup", { bubbles: true }));
            sendBtn.click();
            emitToZBus("PROMPT_ACCEPTED", {
                status: attempt === 1 ? "dispatched" : "dispatched_after_retry",
                provider: PROVIDER.id
            }, sessionId, taskId);
            startResponseObserver(sessionId, taskId, prevMsg);
        } else if (attempt < 3) {
            setTimeout(() => tryDispatch(attempt + 1), 500 * attempt);
        } else {
            emitToZBus("BRIDGE_ERROR", {
                detail: `${PROVIDER.id} — send button not ready after 3 attempts`,
                provider: PROVIDER.id
            }, sessionId, taskId, "error");
        }
    };

    setTimeout(() => tryDispatch(), 200);
}

// ─── Response observer ────────────────────────────────────────────────────────
function startResponseObserver(sessionId, taskId, previousMsgNode) {
    const chatRoot = PROVIDER.findChatRoot();
    if (!chatRoot) {
        emitToZBus("BRIDGE_ERROR", {
            detail: `${PROVIDER.id} — chat container not found`,
            provider: PROVIDER.id
        }, sessionId, taskId, "error");
        return;
    }

    const STREAM_THROTTLE_MS = 250;
    let observer = null;
    let lastKnownLength = 0;
    let lastEmittedLength = 0;
    let lastStreamEmit = 0;
    let streamStarted = false;
    let idleTimer = null;

    function finalizeResponse(finalText) {
        if (!streamStarted) return;
        streamStarted = false;
        if (observer) { observer.disconnect(); observer = null; }

        if (finalText.length > lastEmittedLength) {
            emitToZBus("TOKEN_STREAM", {
                delta: finalText.slice(lastEmittedLength),
                content: finalText, length: finalText.length, provider: PROVIDER.id
            }, sessionId, taskId);
        }
        emitToZBus("RESPONSE_COMPLETE", {
            content: finalText, length: finalText.length,
            tokens_approx: Math.ceil(finalText.length / 4),
            provider: PROVIDER.id
        }, sessionId, taskId);
    }

    function checkAndStream() {
        const latestMsg = PROVIDER.getLatestResponse();
        if (!latestMsg || latestMsg === previousMsgNode) return;

        const currentText = latestMsg.innerText || latestMsg.textContent || "";
        const now = Date.now();

        if (currentText.length > lastKnownLength) {
            streamStarted = true;
            lastKnownLength = currentText.length;

            if ((now - lastStreamEmit) >= STREAM_THROTTLE_MS) {
                emitToZBus("TOKEN_STREAM", {
                    delta: currentText.slice(lastEmittedLength),
                    content: currentText, length: currentText.length, provider: PROVIDER.id
                }, sessionId, taskId);
                lastEmittedLength = currentText.length;
                lastStreamEmit = now;
            }

            if (idleTimer) clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                const t = PROVIDER.getLatestResponse();
                finalizeResponse(t?.innerText || t?.textContent || "");
            }, 3000);

        } else if (streamStarted && !PROVIDER.isGenerating()) {
            if (idleTimer) clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                const t = PROVIDER.getLatestResponse();
                finalizeResponse(t?.innerText || t?.textContent || "");
            }, 800);
        }
    }

    observer = new MutationObserver(checkAndStream);
    observer.observe(chatRoot, { childList: true, subtree: true, characterData: true });

    setTimeout(() => {
        if (observer) {
            observer.disconnect();
            emitToZBus("BRIDGE_ERROR", {
                detail: "Response observation timeout (5 min)", provider: PROVIDER.id
            }, sessionId, taskId, "error");
        }
    }, 5 * 60 * 1000);

    checkAndStream();
}
