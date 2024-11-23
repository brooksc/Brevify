// YouTube content script for Brevify extension
console.log('Brevify: YouTube content script loaded');

// Track video URLs and send them to the background script
function handleVideoNavigation() {
    const videoId = new URLSearchParams(window.location.search).get('v');
    if (videoId) {
        const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        const videoTitle = document.title.replace(' - YouTube', '');
        
        // Send video info to background script
        chrome.runtime.sendMessage({
            type: 'VIDEO_VISITED',
            data: {
                url: videoUrl,
                title: videoTitle,
                source: 'youtube'
            }
        });
    }
}

// Listen for page navigation events
window.addEventListener('yt-navigate-finish', handleVideoNavigation);

// Initial check when script loads
handleVideoNavigation();

// Add Brevify button to YouTube interface
function addBrevifyButton() {
    const menuContainer = document.querySelector('#top-level-buttons-computed');
    if (!menuContainer || document.querySelector('#brevify-button')) return;

    const brevifyButton = document.createElement('button');
    brevifyButton.id = 'brevify-button';
    brevifyButton.className = 'yt-spec-button-shape-next';
    brevifyButton.innerHTML = `
        <div class="yt-spec-button-shape-next__button-text-content">
            <span>Brevify</span>
        </div>
    `;

    brevifyButton.addEventListener('click', () => {
        const videoId = new URLSearchParams(window.location.search).get('v');
        if (videoId) {
            chrome.runtime.sendMessage({
                type: 'BREVIFY_VIDEO',
                data: {
                    videoId: videoId,
                    url: window.location.href,
                    title: document.title.replace(' - YouTube', '')
                }
            });
        }
    });

    menuContainer.appendChild(brevifyButton);
}

// Watch for DOM changes to add the Brevify button
const observer = new MutationObserver(() => {
    addBrevifyButton();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Initial attempt to add button
addBrevifyButton();
