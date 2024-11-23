// Immediate console log to verify script loading
console.log('[Brevify] Content script loaded - timestamp:', new Date().toISOString());

// Constants
const BREVIFY_API = 'http://localhost:8888';

// Debug logging function
function debugLog(message, data = null) {
    // Log to console directly first
    console.log('[Brevify Debug]', message, data || '');
    
    const style = 'background: #0066cc; color: white; padding: 2px 5px; border-radius: 3px;';
    if (data) {
        console.log('%c[Brevify]%c ' + message, style, '', data);
    } else {
        console.log('%c[Brevify]%c ' + message, style, '');
    }
}

// Immediately log initialization
debugLog('Content script initializing on URL:', window.location.href);

// Function to handle commands
function handleCommand(command, params) {
    debugLog('Handling command', { command, params });
    
    // Debug the transcript data
    if (params && params.text) {
        debugLog('Transcript data received:', {
            length: params.text.length,
            preview: params.text.substring(0, 100) + '...',
            fullText: params.text
        });
    } else {
        debugLog('No transcript data in params:', params);
        return;
    }
    
    let url;
    switch (command) {
        case 'chatgpt':
            url = 'https://chat.openai.com/';
            break;
        case 'claude':
            url = 'https://claude.ai/';
            break;
        case 'gemini':
            url = 'https://gemini.google.com/';
            break;
        default:
            debugLog('Unknown command', command);
            return;
    }
    
    // Open the URL first
    const newWindow = window.open(url, '_blank');
    
    // Copy text to clipboard as backup
    navigator.clipboard.writeText(params.text)
        .then(() => {
            debugLog('Copied to clipboard as backup');
        })
        .catch(error => {
            debugLog('Error copying to clipboard:', error);
        });
        
    // Wait a bit for the window to load, then send the message
    setTimeout(() => {
        if (newWindow) {
            try {
                // Send message to the AI service tab
                chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                    if (tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, {
                            selectedText: params.text
                        }, function(response) {
                            debugLog('Message sent to AI service tab:', response);
                        });
                    }
                });
            } catch (error) {
                debugLog('Error sending message to AI service:', error);
            }
        }
    }, 2000); // Wait 2 seconds for the page to load
}

// Listen for messages from the page
window.addEventListener('message', event => {
    debugLog('Received window message', {
        origin: event.origin,
        data: event.data
    });

    // Verify origin and message format
    if (event.origin !== BREVIFY_API || !event.data || !event.data.type) {
        return;
    }

    const message = event.data;
    debugLog('Processing BREVIFY message', message);

    if (message.type === 'BREVIFY_ANALYZE') {
        // Forward the message to background script
        chrome.runtime.sendMessage(message, response => {
            debugLog('Background script response:', response);
            if (chrome.runtime.lastError) {
                debugLog('Error from background script:', chrome.runtime.lastError);
            }
            // Send response back to the page
            window.postMessage({
                type: 'BREVIFY_RESPONSE',
                success: !response.error,
                error: response.error
            }, BREVIFY_API);
        });
    } else if (message.type === 'BREVIFY_CHECK') {
        debugLog('Extension check received');
        window.postMessage({
            type: 'BREVIFY_RESPONSE',
            payload: { success: true }
        }, '*');
        return;
    } else if (!message?.type?.startsWith('BREVIFY_') || message.type === 'BREVIFY_RESPONSE') {
        return;
    }

    debugLog('Processing BREVIFY message', message);
    
    // For BREVIFY_COMMAND messages, handle them directly
    if (message.type === 'BREVIFY_COMMAND') {
        const { command, params } = message;
        handleCommand(command, params);
        return;
    }
});
