// content.js - DOM interaction layer

// Injector function for robust UI interactions
function setNativeValue(element, value) {
  const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
  const prototype = Object.getPrototypeOf(element);
  const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
  
  if (valueSetter && valueSetter !== prototypeValueSetter) {
    prototypeValueSetter.call(element, value);
  } else {
    valueSetter.call(element, value);
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "RUN_PROMPT") {
        console.log(`[EvoPyramid Nexus] Injecting task from Z-Node: ${message.node_id}`);
        // Robust selector logic - this is typical Grok / ChatGPT prompt textarea search
        let promptArea = document.querySelector('textarea, [contenteditable="true"]');
        
        if (!promptArea) {
            // Self-healing: Warn the core that DOM changed
            chrome.runtime.sendMessage({
                type: "NODE_STATUS",
                node_id: message.node_id,
                status: "UI_BROKEN_MANUAL_INTERVENTION_REQUIRED",
                message: "No prompt area found. Site layout may have changed."
            });
            return;
        }

        // Fill text
        if (promptArea.tagName === 'TEXTAREA') {
            setNativeValue(promptArea, message.prompt);
            promptArea.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            promptArea.textContent = message.prompt;
            promptArea.dispatchEvent(new Event('input', { bubbles: true }));
        }

        // Find the submit button (ChatGPT: Send, Gemini: Specific path or text)
        let submitBtn = document.querySelector('button[aria-label="Send"], button[data-testid="send-button"], button.send-button, [aria-label="Submit"]');
        
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
            // Start the polling observer to wait for the bot's response
            observeResponseCompletion(message.node_id);
        } else {
            // Fallback: hit enter
            promptArea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
            observeResponseCompletion(message.node_id);
        }
    }
});

function observeResponseCompletion(node_id) {
    // This is a placeholder for a MutationObserver that waits until the LLM stops streaming "generating"
    // When done, it will extract the latest assistant bubble
    
    // For now, simulate delay and read
    setTimeout(() => {
        let responses = document.querySelectorAll('.agent-message, .result-text, [data-message-author-role="assistant"], .model-response, .conversation-content');
        let latestResponse = responses[responses.length - 1];
        
        if (latestResponse) {
            chrome.runtime.sendMessage({
                type: "LLM_RESPONSE",
                node_id: node_id,
                response_text: latestResponse.innerText,
                status: "SUCCESS"
            });
        }
    }, 15000); // Dumb wait for demo purposes. Real prod uses robust MutationObserver.
}
