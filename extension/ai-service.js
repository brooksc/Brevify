(function () {
    // Debug logging function with timestamp
    function debugLog(message, data = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] AI Service:`, message, data || '');
    }

    debugLog('Content script injected');
    debugLog('Current domain:', window.location.hostname);

    // Helper function to get the appropriate selector for the current domain
    function getSelectors() {
        const domain = window.location.hostname;
        debugLog('Getting selectors for domain:', domain);
        
        if (domain === 'chatgpt.com') {
            return {
                textarea: "textarea",
                sendButton: 'button[data-testid="send-button"]'
            };
        }
        debugLog('Domain not supported');
        return null;
    }

    // Wait for the textarea and button to be available
    function waitForElements() {
        return new Promise((resolve) => {
            const selectors = getSelectors();
            if (!selectors) {
                debugLog('Not on a supported chat site:', window.location.hostname);
                return resolve(null);
            }

            let attempts = 0;
            const maxAttempts = 50; // 5 seconds total (50 * 100ms)

            function checkElements() {
                const textarea = document.querySelector(selectors.textarea);
                const sendButton = document.querySelector(selectors.sendButton);
                
                debugLog('Checking for elements:', {
                    hasTextarea: !!textarea,
                    hasSendButton: !!sendButton,
                    attempt: attempts + 1
                });

                if (textarea && sendButton) {
                    debugLog('Found required elements');
                    return resolve({ textarea, sendButton });
                }

                attempts++;
                if (attempts >= maxAttempts) {
                    debugLog('Timed out waiting for elements');
                    return resolve(null);
                }

                setTimeout(checkElements, 100);
            }

            checkElements();
        });
    }

    // Listen for the message from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        try {
            debugLog('Received message:', message);

            if (!message || !message.selectedText) {
                throw new Error('Invalid message format: missing selectedText');
            }

            // Wait for both textarea and send button
            waitForElements().then((elements) => {
                if (!elements) {
                    throw new Error('Required elements not found on page');
                }

                const { textarea, sendButton } = elements;
                debugLog('Setting text value');
                
                try {
                    // Set the text value
                    textarea.value = message.selectedText;
                    textarea.dispatchEvent(new Event("input", { bubbles: true }));
                    textarea.dispatchEvent(new Event("change", { bubbles: true }));

                    debugLog('Text value set successfully');

                    // Create and dispatch an Enter keydown event
                    const enterEvent = new KeyboardEvent("keydown", {
                        key: "Enter",
                        code: "Enter",
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        composed: true,
                        cancelable: true
                    });

                    // Wait for React to process the change
                    setTimeout(() => {
                        debugLog('Dispatching Enter event');
                        document.dispatchEvent(enterEvent);
                        
                        // As a backup, also click the button directly
                        if (!enterEvent.defaultPrevented) {
                            debugLog('Enter event not handled, clicking button directly');
                            sendButton.click();
                        }
                    }, 500);
                } catch (error) {
                    debugLog('Error setting text or submitting:', error.message);
                    throw error;
                }
            }).catch((error) => {
                debugLog('Error in waitForElements:', error.message);
                throw error;
            });
        } catch (error) {
            debugLog('Error processing message:', error.message);
            if (sendResponse) {
                sendResponse({ error: error.message });
            }
        }
    });

    // Add a global keydown listener for regular Enter key usage
    document.addEventListener('keydown', function(event) {
        try {
            const selectors = getSelectors();
            if (!selectors) return;

            if (event.keyCode === 13 && !event.shiftKey && !event.metaKey && !event.ctrlKey) {
                const sendButton = document.querySelector(selectors.sendButton);
                if (sendButton) {
                    event.preventDefault();
                    debugLog('Enter key pressed, clicking send button');
                    sendButton.click();
                }
            }
        } catch (error) {
            debugLog('Error in keydown handler:', error.message);
        }
    });
})();
