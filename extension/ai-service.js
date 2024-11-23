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

                // Try multiple ways to trigger submit
                setTimeout(() => {
                    // 1. Try Enter keydown event
                    textarea.dispatchEvent(new KeyboardEvent("keydown", {
                        key: "Enter",
                        code: "Enter",
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        composed: true
                    }));

                    // 2. Try Enter keypress event
                    textarea.dispatchEvent(new KeyboardEvent("keypress", {
                        key: "Enter",
                        code: "Enter",
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        composed: true
                    }));

                    // 3. Look for submit button and click it
                    const submitButton = textarea.form?.querySelector('button[type="submit"]') || 
                                      document.querySelector('button[type="submit"]') ||
                                      Array.from(document.querySelectorAll('button')).find(b => 
                                          b.textContent.toLowerCase().includes('send') || 
                                          b.textContent.toLowerCase().includes('submit'));
                    
                    if (submitButton) {
                        console.log("Found submit button:", submitButton);
                        submitButton.click();
                    } else {
                        console.log("No submit button found");
                    }
                }, 100); // Small delay to ensure text is properly set
            }).catch((error) => {
                console.error("Error finding textarea:", error);
            });
        }
    });
})();
