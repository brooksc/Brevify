// Constants
const MAX_HISTORY_ITEMS = 20;
const CACHE_TIMEOUT = 3600000; // 1 hour in milliseconds
const DEBUG_MAX_LOGS = 100; // Maximum number of debug logs to keep

// App State Management
const AppState = {
    theme: 'auto',
    apiKey: '',
    debug: false,
    prompt: '',
    channels: [],
    initialize() {
        // Load settings from localStorage
        this.theme = localStorage.getItem('theme') || 'auto';
        this.apiKey = localStorage.getItem('apiKey') || '';
        this.debug = localStorage.getItem('debug') === 'true';
        
        // Initialize prompt with default if not in storage
        this.prompt = this.getPrompt();
        
        this.channels = JSON.parse(localStorage.getItem('channels') || '[]');
        
        // Update UI with loaded settings
        this.updateUI();
    },
    updateUI() {
        // Update input values
        document.getElementById('api-key').value = this.apiKey;
        document.getElementById('theme-select').value = this.theme;
        document.getElementById('debug-toggle').checked = this.debug;
        
        // Update prompt in settings if panel is visible
        this.updatePromptDisplay();
        
        // Update channel history dropdown
        this.updateChannelDropdown();
    },
    getPrompt() {
        const savedPrompt = localStorage.getItem('prompt');
        Logger.add('Loading prompt from storage', {
            level: 'INFO',
            component: 'APP',
            action: 'LOAD_PROMPT'
        });
        return savedPrompt || this.getDefaultPrompt();
    },

    setPrompt(prompt) {
        localStorage.setItem('prompt', prompt);
        Logger.add('Saved prompt to storage', {
            level: 'INFO',
            component: 'APP',
            action: 'SAVE_PROMPT'
        });
    },

    updatePromptDisplay() {
        const promptTextarea = document.getElementById('prompt-textarea');
        if (promptTextarea) {
            promptTextarea.value = this.getPrompt();
        }
    },
    getDefaultPrompt() {
        return `Please analyze the following YouTube video and provide a structured breakdown:

### Video Information
Title: {title}
Description: {description}

### Video Transcript
{transcript}

### Analysis Instructions
Please provide a comprehensive analysis of the video content, including:

1. Key Points (3-5 main ideas)
2. Important timestamps and topics
3. Resources or links mentioned
4. Technical details or code examples (if applicable)
5. Action items or next steps
6. Notable quotes or statements

Please format your response in a clear, structured manner using markdown headings and bullet points.`;
    },
    updateChannelDropdown() {
        const select = document.getElementById('channel-history');
        if (!select) return;

        // Clear existing options except the first one
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
    },
    addChannel(url, title) {
        const channel = { url, title };
        
        // Remove if already exists
        this.channels = this.channels.filter(ch => ch.url !== url);
        
        // Add to front of array
        this.channels.unshift(channel);
        
        // Limit size
        if (this.channels.length > MAX_HISTORY_ITEMS) {
            this.channels.pop();
        }
        
        // Save to storage
        localStorage.setItem('channels', JSON.stringify(this.channels));
        
        Logger.add(`Added channel to history: ${title}`, {
            level: 'INFO',
            component: 'CHANNEL',
            action: 'ADD_HISTORY'
        });
        
        // Update dropdown
        this.updateChannelDropdown();
    },
    onChannelSelect(event) {
        const select = event.target;
        const url = select.value;
        if (!url) return;

        // Update input with selected URL
        const input = document.getElementById('channel-input');
        if (input) {
            input.value = url;
        }
    },
};

// Debug Logger
const Logger = {
    debugLogs: [],
    maxLogs: DEBUG_MAX_LOGS,

    initialize() {
        this.debugPanel = document.getElementById('debug-panel');
        this.clear(); // Clear logs on initialization
    },
    
    clear() {
        this.debugLogs = [];
        if (this.debugPanel) {
            this.debugPanel.innerHTML = '';
        }
    },

    add(message, details = {}) {
        if (!this.debugLogs) {
            this.debugLogs = [];
        }

        const log = {
            timestamp: Date.now(),
            message,
            ...details
        };

        this.debugLogs.unshift(log);
        
        // Limit size
        if (this.debugLogs.length > this.maxLogs) {
            this.debugLogs.pop();
        }

        localStorage.setItem('debugLogs', JSON.stringify(this.debugLogs));
        this.updatePanel();
    },

    updatePanel() {
        const panel = document.getElementById('debug-panel');
        if (!panel) return;

        const logs = this.debugLogs.map(log => {
            const time = new Date(log.timestamp).toLocaleTimeString();
            const level = log.level || 'INFO';
            const component = log.component || 'SYSTEM';
            const action = log.action || 'GENERIC';
            
            return `<div class="log-entry ${level.toLowerCase()}">
                <span class="time">${time}</span>
                <span class="level">${level}</span>
                <span class="component">${component}</span>
                <span class="action">${action}</span>
                <span class="message">${log.message}</span>
                ${log.error ? `<div class="error">Error: ${log.error}</div>` : ''}
            </div>`;
        }).join('');

        panel.innerHTML = logs;
    },

    clear() {
        this.debugLogs = [];
        localStorage.removeItem('debugLogs');
        this.updatePanel();
    }
};

// Debug Panel Management
function toggleDebugPanel() {
    const debugToggle = document.getElementById('debug-toggle');
    const container = document.getElementById('debug-panel-container');
    
    AppState.debug = debugToggle.checked;
    localStorage.setItem('debug', AppState.debug);
    
    if (container) {
        container.classList.toggle('hidden', !AppState.debug);
    }
    
    Logger.add(`Debug panel ${AppState.debug ? 'enabled' : 'disabled'}`, {
        level: 'INFO',
        component: 'DEBUG',
        action: 'TOGGLE'
    });
}

// Storage Management
const Storage = {
    STORAGE_KEY: 'brevify_state',

    load() {
        try {
            // We're not using the stored state anymore, each setting is stored individually
            console.log('Loading app state...');
        } catch (error) {
            console.error('Failed to load state:', error);
            Logger.add('Failed to load state', {
                level: 'ERROR',
                component: 'STORAGE',
                action: 'LOAD',
                error: error.message
            });
        }
    },

    save() {
        try {
            // We're not using this anymore as each setting is stored individually
            console.log('Saving app state...');
        } catch (error) {
            console.error('Failed to save state:', error);
            Logger.add('Failed to save state', {
                level: 'ERROR',
                component: 'STORAGE',
                action: 'SAVE',
                error: error.message
            });
        }
    },

    clear() {
        localStorage.clear();
        Object.assign(AppState, {
            theme: 'auto',
            apiKey: '',
            debug: false,
            prompt: AppState.getDefaultPrompt(),
            channels: []
        });
        AppState.updateUI();
    }
};

// HTMX Event Handlers
document.addEventListener('htmx:beforeRequest', (evt) => {
    const apiKey = AppState.apiKey;
    if (!apiKey) {
        evt.preventDefault();
        showError('Please enter a YouTube API key first');
        return;
    }
    evt.detail.headers['X-API-Key'] = apiKey;
});

document.addEventListener('htmx:afterRequest', (evt) => {
    if (!evt.detail.successful) {
        Logger.add('Request failed', {
            level: 'ERROR',
            component: 'HTMX',
            action: 'REQUEST',
            error: evt.detail.error
        });
    }
});

document.addEventListener('htmx:responseError', (evt) => {
    const response = evt.detail.xhr.response;
    let errorMessage = 'An error occurred';
    
    try {
        const error = JSON.parse(response);
        errorMessage = error.message || errorMessage;
    } catch (e) {
        errorMessage = response || errorMessage;
    }
    
    showError(errorMessage);
    Logger.add(errorMessage, {
        level: 'ERROR',
        component: 'HTMX',
        action: 'RESPONSE',
        error: response
    });
});

// Enhanced error display
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        // Auto-hide after 5 seconds
        setTimeout(() => hideError(), 5000);
    }
}

// AI Service Integration
const AIService = {
    services: {
        chatgpt: {
            name: "ChatGPT",
            url: "https://chat.openai.com/"
        },
        claude: {
            name: "Claude",
            url: "https://claude.ai/"
        },
        gemini: {
            name: "Gemini",
            url: "https://gemini.google.com/"
        }
    },

    searchAI(service, button, videoId) {
        const videoCard = button.closest('.video-card');
        const title = videoCard.querySelector('h3').textContent;
        const description = videoCard.querySelector('p').textContent;
        const serviceConfig = this.services[service];

        if (!serviceConfig) {
            console.error('Invalid AI service:', service);
            return;
        }

        const prompt = AppState.getPrompt()
            .replace('{title}', title)
            .replace('{description}', description);

        // Open AI service in new tab
        const aiWindow = window.open(serviceConfig.url, '_blank');
        if (aiWindow) {
            // Copy prompt to clipboard
            navigator.clipboard.writeText(prompt).then(() => {
                showError(`Prompt copied to clipboard! Paste it into ${serviceConfig.name} to analyze the video.`);
            }).catch(err => {
                console.error('Failed to copy prompt:', err);
                showError('Failed to copy prompt to clipboard. Please try again.');
            });
        } else {
            showError('Pop-up was blocked. Please allow pop-ups and try again.');
        }

        Logger.add(`Opened ${serviceConfig.name} for analysis`, {
            level: 'INFO',
            component: 'AI',
            action: 'ANALYZE',
            data: { service, videoId }
        });
    }
};

// Video Management
const VideoManager = {
    async fetchVideos(channelId) {
        try {
            Logger.add('Fetching videos from YouTube API', {
                level: 'INFO',
                component: 'VideoManager',
                action: 'FETCH_START'
            });

            if (!AppState.apiKey) {
                Logger.add('No API key found', {
                    level: 'ERROR',
                    component: 'VideoManager',
                    action: 'FETCH_ERROR'
                });
                throw new Error('Please enter your YouTube API key in settings');
            }

            const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=${channelId}&maxResults=10&order=date&type=video&key=${AppState.apiKey}`;
            
            const response = await fetch(url);
            const data = await response.json();

            if (data.error) {
                Logger.add(`YouTube API Error: ${data.error.message}`, {
                    level: 'ERROR',
                    component: 'VideoManager',
                    action: 'FETCH_ERROR'
                });
                throw new Error(data.error.message);
            }

            if (!data.items) {
                Logger.add('No videos found', {
                    level: 'WARN',
                    component: 'VideoManager',
                    action: 'FETCH_EMPTY'
                });
                return [];
            }

            const videos = data.items.map(item => ({
                id: item.id.videoId,
                title: item.snippet.title,
                description: item.snippet.description,
                thumbnail: item.snippet.thumbnails.medium.url,
                publishedAt: item.snippet.publishedAt
            }));

            Logger.add(`Found ${videos.length} videos`, {
                level: 'INFO',
                component: 'VideoManager',
                action: 'FETCH_SUCCESS'
            });

            return videos;

        } catch (error) {
            Logger.add("Failed to fetch videos", {
                level: "ERROR",
                component: "VideoManager",
                action: "FETCH",
                error: error.message
            });
            throw error;
        }
    }
};

// HTMX Configuration
document.addEventListener("htmx:configRequest", (evt) => {
    const apiKey = AppState.apiKey;
    if (apiKey) {
        evt.detail.headers["X-API-Key"] = apiKey;
    }
    Logger.add("HTMX request configured", {
        level: "INFO",
        component: "HTMX",
        action: "CONFIG"
    });
});

document.addEventListener("htmx:beforeRequest", (evt) => {
    setLoading(true);
    hideError();
});

document.addEventListener("htmx:afterRequest", (evt) => {
    setLoading(false);
    if (evt.detail.failed) {
        const error = evt.detail.xhr.response || 'Request failed';
        showError(error);
        Logger.add(error, {
            level: "ERROR",
            component: "HTMX",
            action: "REQUEST"
        });
    }
});

// HTMX Handlers
async function fetchVideosHtmx(evt) {
    try {
        Logger.add('Starting video fetch', {
            level: 'INFO',
            component: 'VIDEO',
            action: 'FETCH_START'
        });

        const channelInput = document.getElementById('channel-input');
        const url = channelInput.value.trim();
        
        if (!url) {
            Logger.add('No channel URL provided', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }

        if (!AppState.apiKey) {
            Logger.add('No API key configured', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }

        // Extract channel ID from URL
        const { channelId, channelTitle } = await getChannelId(url, AppState.apiKey);
        if (!channelId) {
            Logger.add('Could not extract channel ID', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }
        
        // Add to history
        AppState.addChannel(url, channelTitle);

        // Continue with video fetching...
        const videos = await VideoManager.fetchVideos(channelId);
        Logger.add('Videos fetched', {
            level: 'INFO',
            component: 'VIDEO',
            action: 'FETCH_SUCCESS',
            details: {
                count: videos ? videos.length : 0
            }
        });

        // Update UI with fetched videos
        displayVideos(videos);

    } catch (error) {
        Logger.add('Error fetching videos', {
            level: 'ERROR',
            component: 'VIDEO',
            action: 'FETCH_ERROR',
            error: error.message
        });
        console.error('Error:', error);
    }
}

// Video Display
function displayVideos(videos) {
    const container = document.getElementById('video-container');
    container.innerHTML = videos.map(video => `
        <div class="bg-white dark:bg-dark-surface rounded-lg shadow-md p-4 mb-4">
            <div class="flex gap-4">
                <div class="flex-shrink-0">
                    <img src="${video.thumbnail}" alt="${decodeHTMLEntities(video.title)}" class="w-48 h-27 object-cover rounded">
                </div>
                <div class="flex-grow">
                    <h3 class="text-lg font-semibold mb-2">${decodeHTMLEntities(video.title)}</h3>
                    <div class="description-container">
                        <div class="description-text line-clamp-2 text-gray-600 dark:text-gray-400">
                            ${decodeHTMLEntities(video.description)}
                        </div>
                        <button onclick="toggleDescription(this)" class="text-sm text-blue-600 dark:text-blue-400 mt-1">
                            Show more
                        </button>
                    </div>
                </div>
            </div>
            <div class="mt-4 flex gap-2">
                <button
                    onclick="searchAI('chatgpt', this, '${video.id}')"
                    class="flex-1 px-3 py-2 bg-ai-chatgpt text-white rounded hover:opacity-90 text-sm">
                    Analyze with ChatGPT
                </button>
                <button
                    onclick="searchAI('claude', this, '${video.id}')"
                    class="flex-1 px-3 py-2 bg-ai-claude text-white rounded hover:opacity-90 text-sm">
                    Analyze with Claude
                </button>
                <button
                    onclick="searchAI('gemini', this, '${video.id}')"
                    class="flex-1 px-3 py-2 bg-ai-gemini text-white rounded hover:opacity-90 text-sm">
                    Analyze with Gemini
                </button>
            </div>
        </div>
    `).join('');
}

// Helper function to decode HTML entities
function decodeHTMLEntities(text) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    return textarea.value;
}

// Theme Management
function updateTheme(theme) {
    AppState.theme = theme;
    localStorage.setItem('theme', theme);
    
    const isDark = theme === 'dark' || 
                  (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    document.documentElement.classList.toggle('dark', isDark);
    
    Logger.add(`Theme updated to ${theme}`, {
        level: 'INFO',
        component: 'THEME',
        action: 'UPDATE'
    });
}

// Initialize theme based on system preference
function initializeTheme() {
    const theme = AppState.theme || 'auto';
    document.getElementById('theme-select').value = theme;
    updateTheme(theme);

    // Listen for system theme changes when in auto mode
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (AppState.theme === 'auto') {
            document.documentElement.classList.toggle('dark', e.matches);
            Logger.add('System theme changed', {
                level: 'INFO',
                component: 'THEME',
                action: 'SYSTEM_CHANGE'
            });
        }
    });
}

// Settings Panel Management
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    const isHidden = panel.classList.contains('hidden');
    
    if (isHidden) {
        // Opening settings - load current values
        panel.classList.remove('hidden');
        const promptTextarea = document.getElementById('ai-prompt');
        if (promptTextarea) {
            promptTextarea.value = AppState.getPrompt();
        }
    } else {
        // Closing settings - save any changes
        panel.classList.add('hidden');
        const promptTextarea = document.getElementById('ai-prompt');
        if (promptTextarea && promptTextarea.value !== AppState.getPrompt()) {
            AppState.setPrompt(promptTextarea.value);
        }
    }
    
    Logger.add(`Settings panel ${isHidden ? 'opened' : 'closed'}`, {
        level: 'INFO',
        component: 'SETTINGS',
        action: 'TOGGLE_PANEL'
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const settingsButton = document.querySelector('[aria-label="Settings"]');
    if (settingsButton) {
        settingsButton.onclick = toggleSettings;
    }
});

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing app...'); // Debug
    
    // Clear logs when page loads
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
    
    // Initialize theme
    initializeTheme();
    
    // Set up debug panel
    const debugToggle = document.getElementById('debug-toggle');
    if (debugToggle) {
        debugToggle.checked = AppState.debug;
        const container = document.getElementById('debug-panel-container');
        if (container) {
            container.classList.toggle('hidden', !AppState.debug);
        }
    }
    
    // Set up settings button click handler
    const settingsButton = document.querySelector('[aria-label="Settings"]');
    if (settingsButton) {
        settingsButton.onclick = toggleSettings;
    }

    // Set up channel history handler
    const channelHistory = document.getElementById('channel-history');
    if (channelHistory) {
        channelHistory.addEventListener('change', AppState.onChannelSelect);
    }
    
    Logger.add('App initialized', {
        level: 'INFO',
        component: 'APP',
        action: 'INIT'
    });
});

// API Key Management
function updateApiKey(value) {
    AppState.apiKey = value.trim();
    localStorage.setItem('apiKey', AppState.apiKey);
    Logger.add('API key updated', {
        level: 'INFO',
        component: 'SETTINGS',
        action: 'UPDATE_KEY'
    });
}

function clearApiKey() {
    AppState.apiKey = '';
    localStorage.setItem('apiKey', '');
    document.getElementById('api-key').value = '';
    Logger.add('API key cleared', {
        level: 'INFO',
        component: 'SETTINGS',
        action: 'CLEAR_KEY'
    });
}

function updatePrompt(value) {
    AppState.setPrompt(value.trim());
    Logger.add('AI prompt updated', {
        level: 'INFO',
        component: 'SETTINGS',
        action: 'UPDATE_PROMPT'
    });
}

function resetPrompt() {
    const defaultPrompt = AppState.getDefaultPrompt();
    AppState.setPrompt(defaultPrompt);
    document.getElementById('ai-prompt').value = defaultPrompt;
    Logger.add('AI prompt reset to default', {
        level: 'INFO',
        component: 'SETTINGS',
        action: 'RESET_PROMPT'
    });
}

// Channel History Management
function clearChannelHistory() {
    AppState.channels = [];
    Storage.save();
    document.getElementById("channel-history").innerHTML = '<option value="">Select a recent channel...</option>';
}

function loadPreviousChannels() {
    return AppState.channels;
}

function updatePreviousChannels(channelUrl, channelTitle) {
    const channelEntry = { url: channelUrl, title: channelTitle };
    
    // Find existing channel index
    const existingIndex = AppState.channels.findIndex(ch => ch.url === channelUrl);
    
    if (existingIndex !== -1) {
        // Update existing channel's title
        AppState.channels[existingIndex].title = channelTitle;
    } else {
        // Add new channel
        AppState.channels.push(channelEntry);
        if (AppState.channels.length > MAX_HISTORY_ITEMS) {
            AppState.channels.shift();
        }
    }
    
    Storage.save();
    updateChannelsDropdown(AppState.channels);
    Logger.add("Channel added/updated in history", {
        level: "INFO",
        component: "STORAGE",
        action: "UPDATE_HISTORY",
    });
}

function updateChannelsDropdown(channels) {
    const select = document.getElementById("channel-history");
    select.innerHTML = '<option value="">Select a recent channel...</option>';

    for (const channel of channels) {
        const option = document.createElement("option");
        option.value = channel.url;
        option.textContent = channel.title || channel.url;
        select.appendChild(option);
    }
}

function selectPreviousChannel(value) {
    if (value) {
        document.getElementById("channel-url").value = value;
        Logger.add("Channel selected from history", {
            level: "INFO",
            component: "UI",
            action: "SELECT_CHANNEL",
        });
    }
}

// YouTube API Functions
function isValidYouTubeUrl(url) {
    const patterns = {
        channelId: /youtube\.com\/channel\/([^\/\s?]+)/,
        userName: /youtube\.com\/user\/([^\/\s?]+)/,
        customUrl: /youtube\.com\/@([^\/\s?]+)/,
        vanityUrl: /youtube\.com\/c\/([^\/\s?]+)/,
    };
    return Object.values(patterns).some((pattern) => pattern.test(url));
}

async function getChannelId(url, apiKey) {
    let channelId = "";
    let channelTitle = "";

    // Extract channel name or ID from URL
    const match =
        url.match(/youtube\.com\/@([^/?]+)/) ||
        url.match(/youtube\.com\/channel\/([^/?]+)/);

    if (!match) {
        throw new Error("Invalid YouTube channel URL");
    }

    const channelIdentifier = match[1];

    // If it's a channel ID (starts with UC), use it directly
    if (channelIdentifier.startsWith("UC")) {
        channelId = channelIdentifier;
    } else {
        // Search for channel by handle/username
        const response = await fetch(
            `https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q=${channelIdentifier}&key=${apiKey}`,
        );

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error.message);
        }

        if (data.items && data.items.length > 0) {
            channelId = data.items[0].id.channelId;
            channelTitle = data.items[0].snippet.channelTitle;
            Logger.add("Channel found from search", { channelId, channelTitle });
            return { channelId, channelTitle };
        }

        throw new Error("Channel not found");
    }

    // If we have a direct channel ID, fetch channel details
    const response = await fetch(
        `https://www.googleapis.com/youtube/v3/channels?part=snippet&id=${channelId}&key=${apiKey}`,
    );

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    if (data.items && data.items.length > 0) {
        channelTitle = data.items[0].snippet.title;
        Logger.add("Channel found by ID", { channelId, channelTitle });
        return { channelId, channelTitle };
    }

    throw new Error("Channel not found");
}

// Video Card Interactions
function toggleDescription(button) {
    const container = button.closest('.description-container');
    const text = container.querySelector('.description-text');
    
    if (text.classList.contains('line-clamp-2')) {
        text.classList.remove('line-clamp-2');
        button.textContent = 'Show less';
    } else {
        text.classList.add('line-clamp-2');
        button.textContent = 'Show more';
    }
}

// UI Functions
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        // Auto-hide after 5 seconds
        setTimeout(() => hideError(), 5000);
    }
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

function setLoading(loading) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.classList.toggle('hidden', !loading);
    }
}

function renderVideos(videos) {
    const container = document.getElementById('video-list');
    if (!container) return;

    container.innerHTML = VideoManager.renderVideosHtml(videos);
    Logger.add(`Rendered ${videos.length} videos`, {
        level: 'INFO',
        component: 'UI',
        action: 'RENDER_VIDEOS',
    });
}

async function fetchVideos() {
    try {
        Logger.add('Starting video fetch', {
            level: 'INFO',
            component: 'VIDEO',
            action: 'FETCH_START'
        });

        const channelInput = document.getElementById('channel-input');
        const url = channelInput.value.trim();
        
        if (!url) {
            Logger.add('No channel URL provided', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }

        if (!AppState.apiKey) {
            Logger.add('No API key configured', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }

        // Extract channel ID from URL
        const { channelId, channelTitle } = await getChannelId(url, AppState.apiKey);
        if (!channelId) {
            Logger.add('Could not extract channel ID', {
                level: 'ERROR',
                component: 'VIDEO',
                action: 'FETCH_ERROR'
            });
            return;
        }
        
        // Add to history
        AppState.addChannel(url, channelTitle);

        // Continue with video fetching...
        const videos = await VideoManager.fetchVideos(channelId);
        Logger.add('Videos fetched', {
            level: 'INFO',
            component: 'VIDEO',
            action: 'FETCH_SUCCESS',
            details: {
                count: videos ? videos.length : 0,
                channel: channelTitle
            }
        });

        // Update UI with fetched videos
        displayVideos(videos);

    } catch (error) {
        Logger.add('Error fetching videos', {
            level: 'ERROR',
            component: 'VIDEO',
            action: 'FETCH_ERROR',
            error: error.message
        });
        console.error('Error:', error);
    }
}

// AI Analysis
const TranscriptCache = {
    _cache: new Map(),
    
    set(videoId, transcript) {
        this._cache.set(videoId, transcript);
        Logger.add(`Cached transcript for video ${videoId}`, {
            level: 'INFO',
            component: 'TRANSCRIPT',
            action: 'CACHE_SET'
        });
    },
    
    get(videoId) {
        return this._cache.get(videoId);
    },
    
    has(videoId) {
        return this._cache.has(videoId);
    }
};

async function searchAI(service, button, videoId) {
    let resultContainer = null;
    let card = null;

    try {
        if (!videoId) {
            throw new Error('Video ID not found');
        }

        card = button.closest('.bg-white');
        const title = card.querySelector('h3').textContent;
        const description = card.querySelector('.description-text').textContent;
        
        // Show loading state
        resultContainer = card.querySelector('.ai-result');
        if (!resultContainer) {
            resultContainer = document.createElement('div');
            resultContainer.className = 'ai-result mt-4 p-4 bg-gray-50 dark:bg-dark-elevated rounded';
            card.appendChild(resultContainer);
        }
        resultContainer.innerHTML = `
            <div class="flex items-center gap-2">
                <div class="animate-spin rounded-full h-4 w-4 border-2 border-gray-500 border-t-transparent"></div>
                <span>Fetching transcript...</span>
            </div>
        `;

        // Get transcript (from cache or API)
        let transcript;
        if (TranscriptCache.has(videoId)) {
            transcript = TranscriptCache.get(videoId);
            Logger.add('Using cached transcript', {
                level: 'INFO',
                component: 'TRANSCRIPT',
                action: 'CACHE_HIT',
                details: { videoId }
            });
        } else {
            transcript = await fetchTranscript(videoId);
            TranscriptCache.set(videoId, transcript);
        }

        // Get the prompt template and fill it
        const promptTemplate = AppState.getPrompt();
        const prompt = promptTemplate
            .replace('{title}', title)
            .replace('{description}', description)
            .replace('{transcript}', transcript || 'No transcript available');

        // Show the prompt being used (for debugging)
        Logger.add('Using prompt for analysis', {
            level: 'INFO',
            component: 'AI',
            action: 'PROMPT_CREATED',
            details: { prompt }
        });

        // Create the URL for the chosen AI service
        let aiUrl;
        switch (service) {
            case 'chatgpt':
                aiUrl = `https://chat.openai.com/?model=gpt-4&q=${encodeURIComponent(prompt)}`;
                break;
            case 'claude':
                aiUrl = `https://claude.ai/chat?prompt=${encodeURIComponent(prompt)}`;
                break;
            case 'gemini':
                aiUrl = `https://gemini.google.com/?prompt=${encodeURIComponent(prompt)}`;
                break;
            default:
                throw new Error('Unknown AI service');
        }

        // Open AI service in new tab
        window.open(aiUrl, '_blank');

        // Update result container
        resultContainer.innerHTML = `
            <div class="prose dark:prose-invert">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                    Opened ${service} in a new tab with the video transcript and analysis prompt.
                </p>
            </div>
        `;

        Logger.add(`Opened ${service} analysis`, {
            level: 'INFO',
            component: 'AI',
            action: 'ANALYZE_COMPLETE',
            details: { service, videoId }
        });

    } catch (error) {
        Logger.add(`Error in AI analysis: ${error.message}`, {
            level: 'ERROR',
            component: 'AI',
            action: 'ANALYZE_ERROR',
            error: error.message
        });
        
        // Create error container if it doesn't exist yet
        if (!resultContainer && card) {
            resultContainer = document.createElement('div');
            resultContainer.className = 'ai-result mt-4 p-4 bg-gray-50 dark:bg-dark-elevated rounded';
            card.appendChild(resultContainer);
        }
        
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="text-red-600 dark:text-red-400">
                    Error: ${error.message}
                </div>
            `;
        }
    }
}

// Fetch video transcript
async function fetchTranscript(videoId) {
    Logger.add('Fetching transcript', {
        level: 'INFO',
        component: 'TRANSCRIPT',
        action: 'FETCH_START',
        details: { videoId }
    });

    try {
        // Get video details first
        const videoResponse = await fetch(
            `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${videoId}&key=${AppState.apiKey}`
        );
        const videoData = await videoResponse.json();

        if (!videoData.items || videoData.items.length === 0) {
            throw new Error('Video not found');
        }

        const videoDetails = videoData.items[0].snippet;

        // Try to fetch the transcript using timedtext API
        const timedTextUrl = `https://www.youtube.com/api/timedtext?v=${videoId}&lang=en`;
        const transcriptResponse = await fetch(timedTextUrl, {
            mode: 'cors',  // This should work with YouTube's timedtext API
        });
        
        if (!transcriptResponse.ok) {
            throw new Error('Failed to fetch transcript');
        }

        const transcriptXml = await transcriptResponse.text();
        
        // Parse the XML to extract text
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(transcriptXml, 'text/xml');
        const textElements = xmlDoc.getElementsByTagName('text');
        
        // Combine all text elements into a single transcript
        let transcriptText = '';
        for (const element of textElements) {
            transcriptText += element.textContent.replace(/&#39;/g, "'") + ' ';
        }

        // Create a structured transcript with both metadata and content
        const transcript = `
Title: ${videoDetails.title}
Channel: ${videoDetails.channelTitle}
Published: ${new Date(videoDetails.publishedAt).toLocaleDateString()}

Description:
${videoDetails.description}

Transcript:
${transcriptText.trim()}`;

        Logger.add('Transcript fetched successfully', {
            level: 'INFO',
            component: 'TRANSCRIPT',
            action: 'FETCH_SUCCESS',
            details: { videoId }
        });

        return transcript;

    } catch (error) {
        Logger.add('Failed to fetch transcript', {
            level: 'ERROR',
            component: 'TRANSCRIPT',
            action: 'FETCH_ERROR',
            error: error.message
        });
        throw error;
    }
}

// Make searchAI available globally
window.searchAI = searchAI;
