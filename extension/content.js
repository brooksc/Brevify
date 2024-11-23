// Constants
const BREVIFY_API = 'http://localhost:8888';

// Debug logging function
function debugLog(message, data = null) {
    const style = 'background: #0066cc; color: white; padding: 2px 5px; border-radius: 3px;';
    if (data) {
        console.log('%c[Brevify]%c ' + message, style, '', data);
    } else {
        console.log('%c[Brevify]%c ' + message, style, '');
    }
}

// Log when content script loads
debugLog('Content script loaded');
debugLog('Initializing');

// Function to handle commands
function handleCommand(command, params) {
    debugLog('Handling command', { command, params });
    
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
    
    // Copy text to clipboard first
    navigator.clipboard.writeText(params.text)
        .then(() => {
            debugLog('Copied transcript to clipboard');
            // Only open the URL after successfully copying to clipboard
            window.open(url, '_blank');
        })
        .catch(error => {
            debugLog('Error copying to clipboard:', error);
            // Still open the URL even if clipboard fails
            window.open(url, '_blank');
        });
}

// Listen for messages from the page
window.addEventListener('message', event => {
    debugLog('Received window message', {
        origin: event.origin,
        data: event.data
    });
    
    // Only accept messages from our own window
    if (event.source !== window) {
        debugLog('Ignoring message from different source');
        return;
    }
    
    const message = event.data;
    
    // Handle extension check
    if (message.type === 'BREVIFY_CHECK') {
        debugLog('Extension check received');
        window.postMessage({
            type: 'BREVIFY_RESPONSE',
            payload: { success: true }
        }, '*');
        return;
    }
    
    // Ignore if not a BREVIFY message or if it's a response
    if (!message?.type?.startsWith('BREVIFY_') || message.type === 'BREVIFY_RESPONSE') {
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
