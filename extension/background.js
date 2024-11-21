// Debug logging function
function debugLog(message, data = null) {
    console.log(`Background Script:`, message, data || '');
}

debugLog('Background script loaded');

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    debugLog('Received message', { message, sender });
    
    if (message.type === 'BREVIFY_ANALYZE') {
        handleAnalyzeRequest(message.payload, sender.tab?.id)
            .then(result => {
                debugLog('Analysis completed', result);
                sendResponse(result);
            })
            .catch(error => {
                debugLog('Analysis failed', error);
                sendResponse({ success: false, error: error.message });
            });
        return true; // Keep the message channel open for async response
    }
});

// Handle analyze requests
async function handleAnalyzeRequest(payload, sourceTabId) {
    try {
        debugLog('Processing analyze request', { payload, sourceTabId });
        
        // Store the text to inject
        debugLog('Storing text for injection', {
            textLength: payload.text.length,
            service: payload.service,
            textPreview: payload.text.substring(0, 50) + '...'
        });
        
        await chrome.storage.local.set({
            textToInject: payload.text,
            targetService: payload.service
        });
        
        // Get the target URL based on the service
        const targetUrl = getServiceUrl(payload.service);
        debugLog('Target URL determined', targetUrl);
        
        // Create new tab
        debugLog('Creating new tab');
        const targetTab = await chrome.tabs.create({ url: targetUrl });
        
        // Wait for the tab to finish loading then inject our script
        chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo, tab) {
            if (tabId === targetTab.id && changeInfo.status === 'complete' && 
                (tab.url.includes('chat.openai.com') || tab.url.includes('chatgpt.com') || tab.url.includes('claude.ai'))) {
                // Remove the listener to prevent future calls
                chrome.tabs.onUpdated.removeListener(listener);
                
                debugLog('Target tab loaded, injecting script');
                // Inject the content script
                chrome.scripting.executeScript({
                    target: { tabId: targetTab.id },
                    files: ['ai-service.js']
                }).then(() => {
                    debugLog('Script injected successfully');
                }).catch((err) => {
                    debugLog('Error injecting script', err);
                });
            }
        });
        
        return { success: true };
    } catch (error) {
        debugLog('Error in handleAnalyzeRequest', error);
        throw error;
    }
}

// Get service URL
function getServiceUrl(service) {
    const urls = {
        chatgpt: 'https://chatgpt.com/',
        claude: 'https://claude.ai/',
        gemini: 'https://gemini.google.com/'
    };
    return urls[service] || null;
}
