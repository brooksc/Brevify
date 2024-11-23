(function () {
    console.log("Content script injected.");

    // Wait for the textarea and button to be available
    function waitForElements() {
        return new Promise((resolve) => {
            function checkElements() {
                const textarea = document.querySelector("textarea");
                const sendButton = document.querySelector('button[data-testid="send-button"]');
                
                if (textarea && sendButton) {
                    return resolve({ textarea, sendButton });
                }

                // If elements not found, try again after a delay
                setTimeout(checkElements, 100);
            }

            checkElements();
        });
    }

    // Listen for the message from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.selectedText) {
            console.log("Received selected text:", message.selectedText);

            // Wait for both textarea and send button
            waitForElements().then(({ textarea, sendButton }) => {
                console.log("Elements found:", { textarea, sendButton });
                
                // Set the text value
                textarea.value = message.selectedText;

                // Dispatch events to notify React of the change
                textarea.dispatchEvent(new Event("input", { bubbles: true }));
                textarea.dispatchEvent(new Event("change", { bubbles: true }));

                // Create and dispatch an Enter keydown event at the document level
                const enterEvent = new KeyboardEvent("keydown", {
                    key: "Enter",
                    code: "Enter",
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    composed: true,
                    cancelable: true
                });

                // Wait a bit for React to process the change
                setTimeout(() => {
                    console.log("Dispatching Enter event");
                    document.dispatchEvent(enterEvent);
                    
                    // As a backup, also click the button directly
                    if (!enterEvent.defaultPrevented) {
                        console.log("Enter event not handled, clicking button directly");
                        sendButton.click();
                    }
                }, 500);
            }).catch((error) => {
                console.error("Error finding elements:", error);
            });
        }
    });

    // Add a global keydown listener for regular Enter key usage
    document.addEventListener('keydown', function(event) {
        if (event.keyCode === 13 && !event.shiftKey && !event.metaKey && !event.ctrlKey) {
            const sendButton = document.querySelector('button[data-testid="send-button"]');
            if (sendButton) {
                event.preventDefault();
                sendButton.click();
            }
        }
    });
})();
