// Debug logging function
function debugLog(message, data = null) {
    console.log(`Background Script:`, message, data || '');
}

debugLog('Background script loaded');

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    debugLog('Received message', { message, sender });
    
    if (message.type === 'BREVIFY_COMMAND') {
        const { command, params } = message;
        debugLog('Processing command', { command, params });
        
        let url;
        switch (command) {
            case 'chatgpt':
                url = 'https://chatgpt.com/';
                break;
            case 'claude':
                url = 'https://claude.ai/';
                break;
            case 'gemini':
                url = 'https://gemini.google.com/';
                break;
            default:
                debugLog('Unknown command', command);
                sendResponse({ error: 'Unknown command' });
                return;
        }
        
        // Open the AI service tab
        chrome.tabs.create({ url }, (newTab) => {
            if (chrome.runtime.lastError) {
                debugLog('Error opening new tab:', chrome.runtime.lastError);
                sendResponse({ error: chrome.runtime.lastError.message });
                return;
            }
            
            debugLog('New tab opened with ID:', newTab.id);
            
            // Wait for the tab to finish loading
            chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo, updatedTab) {
                if (tabId === newTab.id && changeInfo.status === "complete") {
                    // Remove the listener to prevent future calls
                    chrome.tabs.onUpdated.removeListener(listener);
                    
                    // Inject the content script file
                    chrome.scripting.executeScript(
                        {
                            target: { tabId: newTab.id },
                            files: ["ai-service.js"]
                        },
                        () => {
                            if (chrome.runtime.lastError) {
                                debugLog('Error injecting script:', chrome.runtime.lastError);
                                sendResponse({ error: chrome.runtime.lastError.message });
                            } else {
                                debugLog('Script injected successfully');
                                chrome.tabs.sendMessage(newTab.id, { 
                                    selectedText: params.text
                                });
                                sendResponse({ success: true });
                            }
                        }
                    );
                }
            });
        });
        
        return true; // Keep the message channel open for async response
    } else if (message.type === 'BREVIFY_ANALYZE') {
        const openaiChatUrl = 'https://chat.openai.com/';
        
        // Open the ChatGPT tab
        chrome.tabs.create({ url: openaiChatUrl }, (newTab) => {
            if (chrome.runtime.lastError) {
                debugLog('Error opening new tab:', chrome.runtime.lastError);
                return;
            }
            
            debugLog('New tab opened with ID:', newTab.id);
            
            // Wait for the tab to finish loading
            chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo, updatedTab) {
                if (tabId === newTab.id && changeInfo.status === "complete") {
                    // Remove the listener to prevent future calls
                    chrome.tabs.onUpdated.removeListener(listener);
                    
                    // Inject the content script file
                    chrome.scripting.executeScript(
                        {
                            target: { tabId: newTab.id },
                            files: ["ai-service.js"]
                        },
                        () => {
                            if (chrome.runtime.lastError) {
                                debugLog('Error injecting script:', chrome.runtime.lastError);
                            } else {
                                debugLog('Script injected successfully');
                                chrome.tabs.sendMessage(newTab.id, { 
                                    selectedText: message.payload.text 
                                });
                            }
                        }
                    );
                }
            });
        });
        
        sendResponse({ success: true });
        return true;
    }
});
