// Debug logging function with style
function debugLog(message, data = null) {
    const style = 'background: #0066cc; color: white; padding: 2px 5px; border-radius: 3px;';
    if (data) {
        console.log('%c[Brevify AI]%c ' + message, style, '', data);
    } else {
        console.log('%c[Brevify AI]%c ' + message, style, '');
    }
}

// Log when script loads
debugLog('AI service script loaded');

// Wait for the textarea to be available
function waitForElement(selector) {
    return new Promise((resolve) => {
        const element = document.querySelector(selector);
        if (element) {
            return resolve(element);
        }

        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    });
}

// Function to inject text
async function injectText(text) {
    try {
        debugLog('Starting text injection');
        const textarea = await waitForElement('textarea');
        debugLog('Textarea found');

        textarea.value = text;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.dispatchEvent(new Event('change', { bubbles: true }));
        debugLog('Text injected and events dispatched');

        // Try to find and click the submit button
        const submit = document.querySelector('button[data-testid="send-button"]');
        if (submit && !submit.disabled) {
            submit.click();
            debugLog('Submit button clicked');
        }

        return true;
    } catch (error) {
        debugLog('Error injecting text', error);
        return false;
    }
}

// Main initialization
async function init() {
    try {
        debugLog('Starting initialization');
        
        // Get the text to inject from storage
        const data = await chrome.storage.local.get(['textToInject', 'targetService']);
        debugLog('Storage contents', {
            hasText: !!data.textToInject,
            textLength: data.textToInject?.length,
            targetService: data.targetService
        });
        
        if (data.textToInject) {
            debugLog('Found text to inject');
            const success = await injectText(data.textToInject);
            
            if (success) {
                debugLog('Text injection successful');
                // Clear the storage
                await chrome.storage.local.remove(['textToInject', 'targetService']);
                debugLog('Cleared storage');
            }
        }
    } catch (error) {
        debugLog('Error in init', error);
        console.error(error);
    }
}

// Start the injection process when the page is interactive
if (document.readyState === 'complete') {
    init();
} else {
    document.addEventListener('DOMContentLoaded', init);
}
