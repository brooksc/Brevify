(function () {
    console.log("Content script injected.");

    // Wait for the textarea to be available
    function waitForElement(selector) {
        return new Promise((resolve) => {
            const element = document.querySelector(selector);
            if (element) {
                return resolve(element);
            }

            const observer = new MutationObserver(() => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    observer.disconnect();
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
            });
        });
    }

    // Listen for the message from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.selectedText) {
            console.log("Received selected text:", message.selectedText);

            // Replace the text inside the textarea with the selected text
            waitForElement("textarea").then((textarea) => {
                console.log("Textarea found:", textarea);
                textarea.value = message.selectedText;

                // Dispatch events to notify React of the change
                textarea.dispatchEvent(new Event("input", { bubbles: true }));
                textarea.dispatchEvent(new Event("change", { bubbles: true }));

                // Simulate pressing Enter
                textarea.dispatchEvent(new KeyboardEvent("keydown", {
                    key: "Enter",
                    code: "Enter",
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                }));
            }).catch((error) => {
                console.error("Error finding textarea:", error);
            });
        }
    });
})();
