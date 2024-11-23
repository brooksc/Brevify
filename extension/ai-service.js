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

                // Wait a bit for React to process the change, then click the send button
                setTimeout(() => {
                    console.log("Clicking send button");
                    sendButton.click();
                }, 500);
            }).catch((error) => {
                console.error("Error finding elements:", error);
            });
        }
    });
})();
