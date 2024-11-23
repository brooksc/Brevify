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
    // Immediate console log for debugging
    console.log('[Brevify] Handling command:', command, 'params:', params);
    
    debugLog('Handling command', { command, params });
    
    // Debug the transcript data
    if (params && params.text) {
        console.log('[Brevify] Transcript data:', params.text.substring(0, 100) + '...');
        debugLog('Transcript data received:', {
            length: params.text.length,
            preview: params.text.substring(0, 100) + '...',
            fullText: params.text
        });
    } else {
        console.log('[Brevify] No transcript data in params');
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
            console.log('[Brevify] Unknown command:', command);
            debugLog('Unknown command', command);
            return;
    }
    
    // Copy text to clipboard with more detailed error handling
    if (params && params.text) {
        console.log('[Brevify] Attempting to copy text to clipboard, length:', params.text.length);
        debugLog('Attempting to copy to clipboard, text length:', params.text.length);
        
        navigator.clipboard.writeText(params.text)
            .then(() => {
                console.log('[Brevify] Successfully copied to clipboard');
                debugLog('Successfully copied to clipboard');
                
                // Test clipboard content
                return navigator.clipboard.readText();
            })
            .then(clipText => {
                console.log('[Brevify] Clipboard verification:', clipText.substring(0, 100) + '...');
                debugLog('Clipboard content verification:', {
                    length: clipText.length,
                    preview: clipText.substring(0, 100) + '...'
                });
                
                // Only open the URL after successfully copying to clipboard
                console.log('[Brevify] Opening URL:', url);
                debugLog('Opening URL:', url);
                window.open(url, '_blank');
            })
            .catch(error => {
                console.error('[Brevify] Clipboard error:', error);
                debugLog('Error with clipboard:', {
                    error: error,
                    errorName: error.name,
                    errorMessage: error.message,
                    errorStack: error.stack
                });
                // Still open the URL even if clipboard fails
                console.log('[Brevify] Opening URL despite clipboard error:', url);
                debugLog('Opening URL despite clipboard error:', url);
                window.open(url, '_blank');
            });
    } else {
        console.log('[Brevify] No text to copy, opening URL:', url);
        debugLog('No text to copy to clipboard');
        window.open(url, '_blank');
    }
}

// Listen for messages from the page
window.addEventListener('message', event => {
    // Immediate console log
    console.log('[Brevify] Received message:', event.data);
    
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
        console.log('[Brevify] Ignoring message from different source');
        debugLog('Ignoring message from different source');
        return;
    }
    
    const message = event.data;
    
    // Handle extension check
    if (message.type === 'BREVIFY_CHECK') {
        console.log('[Brevify] Extension check received');
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

    console.log('[Brevify] Processing message:', message);
    debugLog('Processing BREVIFY message', message);
    
    // For BREVIFY_COMMAND messages, handle them directly
    if (message.type === 'BREVIFY_COMMAND') {
        const { command, params } = message;
        console.log('[Brevify] Executing command:', command, 'params:', params);
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
