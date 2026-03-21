
/**
 * EvoPyramid OS - Vertical Slice Audit Script
 * Copy and paste this into the browser console on chatgpt.com to verify DOM selectors.
 */
(function() {
    console.log("%c EvoPyramid OS: Selector Audit Starting...", "color: #10b981; font-weight: bold; font-size: 14px;");
    
    const audit = {
        "Prompt Area (#prompt-textarea)": !!document.querySelector('#prompt-textarea'),
        "Send Button (button[data-testid='send-button'])": !!document.querySelector('button[data-testid="send-button"]'),
        "Main Container (main)": !!document.querySelector('main'),
        "Assistant Msg (div[data-message-author-role='assistant'])": !!document.querySelector('div[data-message-author-role="assistant"]'),
        "Stop Button (button[aria-label='Stop generating'])": !!document.querySelector('button[aria-label="Stop generating"]')
    };

    console.table(audit);

    const missing = Object.keys(audit).filter(k => !audit[k]);
    if (missing.length === 0) {
        console.log("%c ALL SELECTORS FOUND. Vertical Slice should work.", "color: #10b981; font-weight: bold;");
    } else {
        console.warn("%c SELECTORS MISSING: " + missing.join(", "), "color: #f43f5e; font-weight: bold;");
        console.log("Note: Stop Button and Assistant Msg might only appear during active generation.");
    }
})();
