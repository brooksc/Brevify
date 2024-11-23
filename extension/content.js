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
    
    // Debug the transcript data
    if (params && params.text) {
        debugLog('Transcript data received:', {
            length: params.text.length,
            preview: params.text.substring(0, 100) + '...',
            fullText: params.text
        });
    } else {
        debugLog('No transcript data in params:', params);
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
    
    // Copy text to clipboard with more detailed error handling
    if (params && params.text) {
        debugLog('Attempting to copy to clipboard, text length:', params.text.length);
        navigator.clipboard.writeText(params.text)
            .then(() => {
                debugLog('Successfully copied to clipboard');
                // Test clipboard content
                navigator.clipboard.readText().then(clipText => {
                    debugLog('Clipboard content verification:', {
                        length: clipText.length,
                        preview: clipText.substring(0, 100) + '...'
                    });
                }).catch(err => {
                    debugLog('Error reading clipboard:', err);
                });
                
                // Only open the URL after successfully copying to clipboard
                debugLog('Opening URL:', url);
                window.open(url, '_blank');
            })
            .catch(error => {
                debugLog('Error copying to clipboard:', {
                    error: error,
                    errorName: error.name,
                    errorMessage: error.message,
                    errorStack: error.stack
                });
                // Still open the URL even if clipboard fails
                debugLog('Opening URL despite clipboard error:', url);
                window.open(url, '_blank');
            });
    } else {
        debugLog('No text to copy to clipboard');
        window.open(url, '_blank');
    }
}

// Listen for messages from the page
window.addEventListener('message', event => {
    debugLog('Received window message', {
        origin: event.origin,
        data: event.data,
        type: event.data?.type,
        command: event.data?.command,
        paramsPreview: event.data?.params ? {
            hasText: !!event.data.params.text,
            textLength: event.data.params.text?.length
        } : null
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
        debugLog('Executing command', {
            command,
            paramsPreview: params ? {
                hasText: !!params.text,
                textLength: params.text?.length
            } : null
        });
        handleCommand(command, params);
        return;
    }
});
