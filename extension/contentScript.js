(function () {
    console.log("Content script injected for ChatGPT.");

    // Function to wait for an element to be present in the DOM
    function waitForElement(selector, timeout = 10000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();

            const findElement = () => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }

                if (Date.now() - startTime > timeout) {
                    reject(new Error(`Timeout waiting for element: ${selector}`));
                    return;
                }

                requestAnimationFrame(findElement);
            };

            findElement();
        });
    }

    // Listen for the message from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.selectedText) {
            console.log("Received selected text:", message.selectedText);

            // ChatGPT uses a textarea
            waitForElement('textarea')
                .then((textarea) => {
                    console.log("Found ChatGPT textarea");
                    
                    // Set the value and trigger input events
                    textarea.value = message.selectedText;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Focus the textarea
                    textarea.focus();
                })
                .catch((error) => {
                    console.error("Error finding ChatGPT textarea:", error);
                });
        }
    });
})();
