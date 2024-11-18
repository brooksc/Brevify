// Constants
const MAX_HISTORY_ITEMS = 20;
const CACHE_TIMEOUT = 3600000; // 1 hour in milliseconds
const DEBUG_MAX_LOGS = 100; // Maximum number of debug logs to keep

// App State Management
class AppState {
    static MAX_HISTORY_ITEMS = 10;
    static channelHistory = [];
    static channels = [];
    static theme = 'auto';
    static debug = false;
    static prompt = '';

    static initialize() {
        // Load settings from localStorage
        this.theme = localStorage.getItem('theme') || 'auto';
        this.debug = localStorage.getItem('debug') === 'true';
        this.prompt = localStorage.getItem('prompt') || '';
        
        // Load channels from localStorage
        const savedChannels = localStorage.getItem('channels');
        if (savedChannels) {
            this.channels = JSON.parse(savedChannels);
        }
        
        // Load channel history
        const savedHistory = localStorage.getItem('channelHistory');
        if (savedHistory) {
            this.channelHistory = JSON.parse(savedHistory);
            this.updateHistoryUI();
        }
        
        // Apply initial theme
        this.updateTheme();
    }

    static updateTheme(value = null) {
        // Update theme value if provided
        if (value !== null) {
            this.theme = value;
            localStorage.setItem('theme', value);
        }
        
        const html = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        // Remove existing theme classes
        html.classList.remove('dark', 'light');

        // Apply new theme
        const themeToApply = this.theme === 'auto' ? (prefersDark ? 'dark' : 'light') : this.theme;
        html.classList.add(themeToApply);
    }

    static addChannel(url, title) {
        const channel = { url, title };
        
        // Remove if already exists
        this.channels = this.channels.filter(ch => ch.url !== url);
        
        // Add to front
        this.channels.unshift(channel);
        
        // Limit size
        if (this.channels.length > this.MAX_HISTORY_ITEMS) {
            this.channels.pop();
        }
        
        // Save to localStorage
        localStorage.setItem('channels', JSON.stringify(this.channels));
        
        // Update UI
        this.updateChannelDropdown();
    }

    static updateChannelDropdown() {
        const select = document.getElementById('channel-history');
        if (!select) return;

        // Clear existing options except the first placeholder
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Add channels to dropdown
        this.channels.forEach(channel => {
            const option = document.createElement('option');
            option.value = channel.url;
            option.textContent = channel.title;
            select.appendChild(option);
        });
    }

    static addToHistory(url) {
        // Remove if already exists
        this.channelHistory = this.channelHistory.filter(c => c !== url);
        
        // Add to front
        this.channelHistory.unshift(url);
        
        // Limit size
        if (this.channelHistory.length > this.MAX_HISTORY_ITEMS) {
            this.channelHistory.pop();
        }
        
        // Save to localStorage
        localStorage.setItem('channelHistory', JSON.stringify(this.channelHistory));
        
        // Update UI
        this.updateHistoryUI();
    }

    static updateHistoryUI() {
        const select = document.getElementById('channel-history');
        if (!select) return;

        // Clear existing options except the first placeholder
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Add channel history
        this.channelHistory.forEach(url => {
            const option = document.createElement('option');
            option.value = url;
            option.textContent = url;
            select.appendChild(option);
        });
    }

    static onChannelSelect(event) {
        const url = event.target.value;
        if (url) {
            document.getElementById('channel-input').value = url;
        }
    }
}

// Logger for debugging
const Logger = {
    debugLogs: [],
    maxLogs: DEBUG_MAX_LOGS,

    initialize() {
        this.debugPanel = document.getElementById('debug-panel');
    },
    
    add(message, data = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            message,
            ...data
        };
        
        this.debugLogs.unshift(logEntry);
        
        // Trim logs if they exceed max size
        if (this.debugLogs.length > this.maxLogs) {
            this.debugLogs.pop();
        }
        
        // Update panel if debug mode is on
        if (AppState.debug) {
            this.updatePanel();
        }
    },
    
    clear() {
        this.debugLogs = [];
        if (this.debugPanel) {
            this.debugPanel.innerHTML = '';
        }
    },
    
    updatePanel() {
        if (!this.debugPanel) return;
        
        this.debugPanel.innerHTML = this.debugLogs.map(log => `
            <div class="p-2 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500">${new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span class="px-1 text-xs rounded ${this.getLevelClass(log.level)}">${log.level || 'INFO'}</span>
                </div>
                <div class="mt-1">${log.message}</div>
                ${this.formatDetails(log)}
            </div>
        `).join('');
    },
    
    getLevelClass(level) {
        switch (level?.toUpperCase()) {
            case 'ERROR': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            case 'WARN': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
            case 'DEBUG': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
            default: return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
        }
    },
    
    formatDetails(log) {
        const details = { ...log };
        delete details.timestamp;
        delete details.message;
        delete details.level;
        
        if (Object.keys(details).length === 0) return '';
        
        return `
            <pre class="mt-2 p-2 text-xs bg-gray-100 dark:bg-gray-800 rounded overflow-x-auto">
                ${JSON.stringify(details, null, 2)}
            </pre>
        `;
    }
};

// Video Management
async function fetchVideos() {
    try {
        setLoading(true);
        hideError();

        const input = document.getElementById('channel-input');
        if (!input || !input.value.trim()) {
            throw new Error('Please enter a YouTube channel URL');
        }

        const url = input.value.trim();
        
        try {
            const response = await fetch(`/api/videos?url=${encodeURIComponent(url)}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Channel not found');
            }
            
            if (!data || !Array.isArray(data.videos)) {
                throw new Error('Invalid video data received from server');
            }
            
            if (data.channel_title) {
                AppState.addChannel(url, data.channel_title);
            }
            displayVideos(data.videos);
        } catch (error) {
            // Handle network errors
            if (error.message === 'Network error' || error.message === 'Failed to fetch') {
                throw new Error('Failed to fetch videos. Please try again.');
            }
            // Handle JSON parsing errors
            if (error instanceof SyntaxError) {
                throw new Error('Invalid video data received from server');
            }
            // Pass through other errors
            throw error;
        }
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

// Video Display
function displayVideos(videos) {
    const template = document.getElementById('video-card-template');
    const container = document.getElementById('video-container');
    
    if (!template || !container) return;
    
    container.innerHTML = '';
    
    // Handle invalid input
    if (!videos || !Array.isArray(videos)) {
        showError('Invalid video data received');
        return;
    }
    
    // Handle empty array
    if (videos.length === 0) {
        container.innerHTML = '<p>No videos found</p>';
        return;
    }

    videos.forEach(video => {
        // Skip invalid videos
        if (!video || typeof video !== 'object' || !video.id || !video.title || !video.thumbnail) {
            return;
        }
        
        const card = template.content.cloneNode(true);
        const videoCard = card.querySelector('.video-card');
        if (!videoCard) return;
        
        try {
            const img = videoCard.querySelector('img');
            if (img) {
                img.src = video.thumbnail;
                img.alt = video.title;
            }

            const link = videoCard.querySelector('a');
            if (link) {
                link.href = `https://youtube.com/watch?v=${video.id}`;
                link.textContent = video.title;
            }

            const description = videoCard.querySelector('p.description');
            if (description) {
                description.textContent = video.description || '';
            }

            container.appendChild(card);
        } catch (error) {
            console.error('Error creating video card:', error);
        }
    });
}

// Error handling
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (!errorElement) return;
    
    const messageElement = errorElement.querySelector('.message');
    if (messageElement) {
        messageElement.textContent = message;
    }
    errorElement.classList.remove('hidden');
}

function hideError() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.classList.add('hidden');
    }
}

// Channel Management
async function addChannel(url) {
    try {
        setLoading(true);
        hideError();

        // Extract channel ID from URL
        const channelId = extractChannelId(url);
        if (!channelId) {
            throw new Error('Invalid YouTube channel URL');
        }

        // Fetch channel info from API
        const response = await fetch(`/api/channel/${channelId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch channel information');
        }

        const channelData = await response.json();
        
        // Add channel to store
        Store.addChannel({
            id: channelId,
            title: channelData.title,
            thumbnail: channelData.thumbnail,
            subscriberCount: channelData.subscriberCount,
            url: url
        });

        // Update UI
        updateChannelList();
        
        // Clear input
        document.getElementById('channel-input').value = '';
        
        // Fetch videos for the new channel
        await fetchChannelVideos(channelId);
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function updateChannelList() {
    const channels = Store.getChannels();
    const channelList = document.getElementById('channel-list');
    const template = document.getElementById('channel-card-template');
    
    // Clear existing channels
    channelList.innerHTML = '';
    
    // Add channel cards
    channels.forEach(channel => {
        const card = template.content.cloneNode(true);
        
        // Set channel info
        card.querySelector('img').src = channel.thumbnail;
        card.querySelector('img').alt = channel.title;
        card.querySelector('h3').textContent = channel.title;
        card.querySelector('p').textContent = `${formatNumber(channel.subscriberCount)} subscribers`;
        
        // Set data attributes
        const cardElement = card.querySelector('.channel-card');
        cardElement.dataset.channelId = channel.id;
        cardElement.dataset.active = channel.isActive;
        
        // Add event listeners
        card.querySelector('.refresh-button').addEventListener('click', () => refreshChannel(channel.id));
        card.querySelector('.toggle-button').addEventListener('click', () => toggleChannel(channel.id));
        card.querySelector('.remove-button').addEventListener('click', () => removeChannel(channel.id));
        
        // Add to list
        channelList.appendChild(card);
    });
}

async function refreshChannel(channelId) {
    try {
        setLoading(true);
        hideError();
        
        // Update last refreshed timestamp
        Store.updateChannel(channelId, {
            lastRefreshed: new Date().toISOString()
        });
        
        // Fetch new videos
        await fetchChannelVideos(channelId);
        
        // Update UI
        updateChannelList();
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function toggleChannel(channelId) {
    const channels = Store.getChannels();
    const channel = channels.find(c => c.id === channelId);
    if (channel) {
        Store.updateChannel(channelId, {
            isActive: !channel.isActive
        });
        updateChannelList();
    }
}

function removeChannel(channelId) {
    if (confirm('Are you sure you want to remove this channel?')) {
        Store.removeChannel(channelId);
        updateChannelList();
    }
}

// Helper function to format numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Helper function to extract channel ID from URL
function extractChannelId(url) {
    try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname;
        
        // Handle different URL formats
        if (pathname.startsWith('/channel/')) {
            return pathname.split('/')[2];
        }
        if (pathname.startsWith('/c/')) {
            return pathname.split('/')[2];
        }
        if (pathname.startsWith('/user/')) {
            return pathname.split('/')[2];
        }
        
        return null;
    } catch (error) {
        return null;
    }
}

// Helper function to format video duration
function formatDuration(duration) {
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return '0:00';
    
    const [, hours = 0, minutes = 0, seconds = 0] = match;
    if (hours > 0) {
        return `${hours}:${minutes.padStart(2, '0')}:${seconds.padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.padStart(2, '0')}`;
}

// Helper function to format view count
function formatViews(views) {
    if (views >= 1000000) {
        return `${(views / 1000000).toFixed(1)}M`;
    }
    if (views >= 1000) {
        return `${(views / 1000).toFixed(1)}K`;
    }
    return views.toString();
}

// UI Functions
function setLoading(loading) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.classList.toggle('hidden', !loading);
    }
}

function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    if (panel) {
        panel.classList.toggle('hidden');
    }
}

// Video Card Interactions
function toggleDescription(button) {
    const description = button.previousElementSibling;
    const isExpanded = description.style.webkitLineClamp !== '2';
    
    if (isExpanded) {
        description.style.webkitLineClamp = '2';
        button.textContent = 'Show More';
    } else {
        description.style.webkitLineClamp = 'unset';
        button.textContent = 'Show Less';
    }
}

// Debug Panel Management
function toggleDebugPanel() {
    const panel = document.getElementById('debug-panel');
    if (!panel) return;
    
    const isHidden = panel.classList.contains('hidden');
    
    if (isHidden) {
        panel.classList.remove('hidden');
        Logger.updatePanel();
    } else {
        panel.classList.add('hidden');
    }
    
    // Save debug state
    AppState.debug = !isHidden;
    localStorage.setItem('debug', AppState.debug);
}

// Helper function to decode HTML entities
function decodeHTMLEntities(text) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    return textarea.value;
}

// Export all functions and classes
export {
    AppState,
    displayVideos,
    showError,
    hideError,
    toggleDescription,
    toggleDebugPanel,
    setLoading,
    decodeHTMLEntities,
    fetchVideos,
    toggleSettings,
    addChannel,
    updateChannelList,
    refreshChannel,
    toggleChannel,
    removeChannel
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Logger.clear();
    Logger.add('Initializing app...', {
        level: 'INFO',
        component: 'SYSTEM',
        action: 'INIT'
    });

    // Initialize Logger first
    Logger.initialize();
    
    // Initialize AppState
    AppState.initialize();
    
    // Set up debug panel
    const debugToggle = document.getElementById('debug-toggle-nav');
    if (debugToggle) {
        debugToggle.checked = AppState.debug;
        const container = document.getElementById('debug-panel-container');
        if (container) {
            container.classList.toggle('hidden', !AppState.debug);
        }
    }
    
    Logger.add('App initialized', {
        level: 'INFO',
        component: 'APP',
        action: 'INIT'
    });
});
