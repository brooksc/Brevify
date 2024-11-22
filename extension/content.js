// Constants
const BREVIFY_API = 'http://localhost:8888';

// State
let currentVideoId = null;

// Helper Functions
function getVideoId() {
    const url = new URL(window.location.href);
    return url.searchParams.get('v');
}

function createBrevifyButton() {
    const button = document.createElement('button');
    button.className = 'brevify-button';
    button.textContent = 'Brevify';
    button.title = 'Analyze with AI';
    return button;
}

function createAIToolsDropdown() {
    const dropdown = document.createElement('div');
    dropdown.className = 'brevify-dropdown';
    
    const services = [
        { id: 'chatgpt', name: 'ChatGPT', url: 'https://chat.openai.com/' },
        { id: 'claude', name: 'Claude', url: 'https://claude.ai/' },
        { id: 'gemini', name: 'Gemini', url: 'https://gemini.google.com/' }
    ];
    
    services.forEach(service => {
        const item = document.createElement('button');
        item.className = 'brevify-dropdown-item';
        item.textContent = `Analyze with ${service.name}`;
        item.dataset.service = service.id;
        dropdown.appendChild(item);
    });
    
    return dropdown;
}

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

// Main Functions
async function checkTranscript(videoId) {
    try {
        const response = await fetch(`${BREVIFY_API}/check/${videoId}`);
        const data = await response.json();
        return data.exists;
    } catch (error) {
        debugLog('Error checking transcript', error);
        return false;
    }
}

async function injectBrevifyButton() {
    try {
        // Wait for the menu container
        const menuContainer = await waitForElement('#above-the-fold #top-level-buttons-computed');
        if (!menuContainer) {
            debugLog('Menu container not found');
            return;
        }
        
        // Create button container
        const container = document.createElement('div');
        container.className = 'brevify-container';
        
        // Create main button
        const button = createBrevifyButton();
        container.appendChild(button);
        
        // Create dropdown
        const dropdown = createAIToolsDropdown();
        container.appendChild(dropdown);
        
        // Add click handlers
        dropdown.addEventListener('click', async (e) => {
            if (e.target.classList.contains('brevify-dropdown-item')) {
                const service = e.target.dataset.service;
                debugLog('Service selected', service);
                
                // Get video ID
                const videoId = getVideoId();
                if (!videoId) {
                    debugLog('No video ID found');
                    return;
                }
                
                // Send message to analyze
                sendMessageToBackground({
                    type: 'BREVIFY_ANALYZE',
                    payload: {
                        videoId,
                        service
                    }
                });
            }
        });
        
        // Insert into page
        menuContainer.appendChild(container);
        debugLog('Button injected successfully');
        
    } catch (error) {
        debugLog('Error injecting button', error);
    }
}

// Function to wait for an element using MutationObserver
function waitForElement(selector, timeout = 10000) {
    return new Promise((resolve) => {
        const element = document.querySelector(selector);
        if (element) {
            return resolve(element);
        }

        const observer = new MutationObserver((mutations, obs) => {
            const element = document.querySelector(selector);
            if (element) {
                obs.disconnect();
                resolve(element);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        setTimeout(() => {
            observer.disconnect();
            resolve(null);
        }, timeout);
    });
}

// Initialize
async function init() {
    debugLog('Initializing');
    
    const videoId = getVideoId();
    if (videoId && videoId !== currentVideoId) {
        currentVideoId = videoId;
        debugLog('New video detected', videoId);
        
        if (await checkTranscript(videoId)) {
            injectBrevifyButton();
        }
    }
}

// Function to send message to background script
function sendMessageToBackground(message, callback) {
    debugLog('Sending message to background', message);
    chrome.runtime.sendMessage(message, callback);
}

// Watch for navigation events
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        debugLog('URL changed', url);
        init();
    }
}).observe(document, { subtree: true, childList: true });

// Initial load
init();

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    debugLog('Received message from extension', { message, sender });
    
    if (message.type === 'BREVIFY_ANALYZE') {
        debugLog('Processing analyze request', message.payload);
        sendMessageToBackground(message, (response) => {
            debugLog('Received response from background', response);
            if (chrome.runtime.lastError) {
                debugLog('Error sending message', chrome.runtime.lastError);
                return;
            }
            // Forward response to page if needed
            if (message.type.startsWith('BREVIFY_')) {
                window.postMessage({
                    type: 'BREVIFY_RESPONSE',
                    payload: response
                }, '*');
            }
        });
        return true; // Keep the message channel open for async response
    }
});

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
    sendMessageToBackground(message, (response) => {
        debugLog('Sending response back to page');
        window.postMessage({
            type: 'BREVIFY_RESPONSE',
            payload: response
        }, '*');
    });
});
