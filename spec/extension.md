# Chrome Extension MVP Specification: AI Service Text Injector

## 1. Core Functionality
- Receive text content from a website
- Open specified AI service (ChatGPT, Claude, etc.) in a new tab
- Inject received text into the AI service's input field
- Trigger the submit action

## 2. Manifest (manifest.json)
```json
{
  "manifest_version": 3,
  "name": "AI Text Injector",
  "version": "1.0",
  "description": "Injects text into AI services",
  "permissions": [
    "activeTab",
    "scripting",
    "storage"
  ],
  "host_permissions": [
    "https://chat.openai.com/*",
    "https://claude.ai/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

## 3. Components

### Background Script (background.js)
```javascript
// Listen for messages from websites
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'inject') {
    // Store the text and target service
    chrome.storage.local.set({
      textToInject: request.text,
      targetService: request.service
    }, () => {
      // Open the target service
      const urls = {
        'chatgpt': 'https://chat.openai.com',
        'claude': 'https://claude.ai/chat'
      };
      chrome.tabs.create({ url: urls[request.service] });
    });
  }
});
```

### Content Script (content.js)
```javascript
// Check if we're on an AI service page and have text to inject
chrome.storage.local.get(['textToInject', 'targetService'], (data) => {
  if (!data.textToInject) return;

  // Selectors for different services
  const selectors = {
    'chatgpt': 'textarea[data-id="root"]',
    'claude': 'textarea[placeholder="Type a message"]'
  };

  const service = window.location.host.includes('openai') ? 'chatgpt' : 'claude';
  const selector = selectors[service];

  // Try to find and fill the input field
  const interval = setInterval(() => {
    const input = document.querySelector(selector);
    if (input) {
      clearInterval(interval);
      input.value = data.textToInject;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      
      // Trigger submit
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        bubbles: true
      });
      input.dispatchEvent(enterEvent);

      // Clear the stored text
      chrome.storage.local.remove(['textToInject', 'targetService']);
    }
  }, 500);
});
```

## 4. Website Integration
Websites can trigger the extension using:
```javascript
// Send text to the extension
chrome.runtime.sendMessage(extensionId, {
  action: 'inject',
  text: 'Your text here',
  service: 'chatgpt' // or 'claude'
});
```

## 5. Security Considerations
- Extension ID must be whitelisted by the website
- Text size should be limited (e.g., 20,000 characters)
- No sensitive data should be stored persistently

## 6. Installation & Setup
1. Load as unpacked extension in Chrome
2. Get extension ID from chrome://extensions
3. Provide extension ID to websites that need to use it

## 7. Limitations
- Requires user to be logged into AI services
- May break if AI services change their UI
- Limited error handling in MVP
- No guarantee of successful injection