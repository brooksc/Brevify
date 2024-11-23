// Debug logging function
function debugLog(message, data = null) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Background Script:`, message, data || '');
}

debugLog('Background script loaded');

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    try {
        debugLog('Received message', { message, sender });
        
        if (!message || !message.type) {
            throw new Error('Invalid message format');
        }
        
        if (message.type === 'BREVIFY_COMMAND') {
            const { command, params } = message;
            debugLog('Processing command', { command, params });
            
            if (!command || !params || !params.text) {
                throw new Error('Missing required command parameters');
            }
            
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
                    throw new Error(`Unknown command: ${command}`);
            }
            
            // Open the AI service tab
            chrome.tabs.create({ url }, (newTab) => {
                if (chrome.runtime.lastError) {
                    const error = chrome.runtime.lastError.message;
                    debugLog('Error opening new tab:', error);
                    sendResponse({ error });
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
                                    const error = chrome.runtime.lastError.message;
                                    debugLog('Error injecting script:', error);
                                    sendResponse({ error });
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
                    const error = chrome.runtime.lastError.message;
                    debugLog('Error opening new tab:', error);
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
                                    const error = chrome.runtime.lastError.message;
                                    debugLog('Error injecting script:', error);
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
    } catch (error) {
        debugLog('Error processing message:', error.message);
        sendResponse({ error: error.message });
    }
});
