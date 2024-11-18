import { Store } from './store.js';

class BrevifyApp {
    constructor() {
        this.channels = Store.getChannels();
        this.settings = Store.getSettings();
        this.videos = Store.getVideos();
        this.initializeUI();
        this.setupEventListeners();
    }

    initializeUI() {
        this.renderChannels();
        this.renderVideos();
        this.applyTheme();
    }

    setupEventListeners() {
        // Channel form submission
        document.getElementById('channel-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const urlInput = document.getElementById('channel-url');
            const url = urlInput.value.trim();
            
            try {
                const response = await fetch('/api/channel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                
                if (!response.ok) throw new Error('Failed to add channel');
                
                const channelData = await response.json();
                this.channels = Store.addChannel(channelData);
                this.renderChannels();
                urlInput.value = '';
            } catch (error) {
                console.error('Error adding channel:', error);
                this.showError('Failed to add channel. Please check the URL and try again.');
            }
        });

        // Settings form
        document.getElementById('settings-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const settings = {
                apiKey: formData.get('api-key'),
                defaultPrompt: formData.get('default-prompt'),
                selectedAIs: Array.from(formData.getAll('ai-services')),
                debugEnabled: formData.get('debug-enabled') === 'on',
                cacheTimeout: parseInt(formData.get('cache-timeout'), 10)
            };
            Store.saveSettings(settings);
            this.settings = settings;
            this.showSuccess('Settings saved successfully');
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.settings.theme = this.settings.theme === 'light' ? 'dark' : 'light';
            Store.saveSettings(this.settings);
            this.applyTheme();
        });

        // Channel actions
        document.getElementById('channel-list').addEventListener('click', async (e) => {
            const action = e.target.dataset.action;
            const channelId = e.target.closest('.channel-card')?.dataset.channelId;
            
            if (!channelId) return;
            
            switch (action) {
                case 'refresh':
                    await this.refreshChannel(channelId);
                    break;
                case 'toggle':
                    this.toggleChannel(channelId);
                    break;
                case 'remove':
                    this.removeChannel(channelId);
                    break;
                case 'copy':
                    this.copyChannelUrl(channelId);
                    break;
            }
        });

        // Video filters
        document.getElementById('video-filters').addEventListener('change', (e) => {
            const sortBy = document.getElementById('sort-by').value;
            const filterChannel = document.getElementById('filter-channel').value;
            const dateRange = document.getElementById('date-range').value;
            
            this.filterAndSortVideos({ sortBy, filterChannel, dateRange });
        });
    }

    async refreshChannel(channelId) {
        try {
            const response = await fetch(`/api/channel/${channelId}/videos`);
            if (!response.ok) throw new Error('Failed to refresh channel');
            
            const videos = await response.json();
            this.videos = Store.saveVideos([...videos, ...this.videos]);
            this.renderVideos();
            
            Store.updateChannel(channelId, { lastRefreshed: new Date().toISOString() });
            this.renderChannels();
        } catch (error) {
            this.showError('Failed to refresh channel videos');
        }
    }

    toggleChannel(channelId) {
        const channel = this.channels.find(c => c.id === channelId);
        if (channel) {
            Store.updateChannel(channelId, { isActive: !channel.isActive });
            this.channels = Store.getChannels();
            this.renderChannels();
            this.renderVideos();
        }
    }

    removeChannel(channelId) {
        if (confirm('Are you sure you want to remove this channel?')) {
            this.channels = Store.removeChannel(channelId);
            this.renderChannels();
            this.renderVideos();
        }
    }

    copyChannelUrl(channelId) {
        const channel = this.channels.find(c => c.id === channelId);
        if (channel?.url) {
            navigator.clipboard.writeText(channel.url);
            this.showSuccess('Channel URL copied to clipboard');
        }
    }

    renderChannels() {
        const channelList = document.getElementById('channel-list');
        channelList.innerHTML = this.channels.map(channel => `
            <div class="channel-card" data-channel-id="${channel.id}">
                <img src="${channel.thumbnail}" alt="${channel.name}" class="channel-thumbnail">
                <div class="channel-info">
                    <h3>${channel.name}</h3>
                    <p>${channel.subscriberCount} subscribers • ${channel.videoCount} videos</p>
                    <p>Last refreshed: ${new Date(channel.lastRefreshed).toLocaleString()}</p>
                </div>
                <div class="channel-actions">
                    <button data-action="refresh" class="btn-action">↻</button>
                    <button data-action="toggle" class="btn-action ${channel.isActive ? 'active' : ''}">${channel.isActive ? '✓' : '✗'}</button>
                    <button data-action="remove" class="btn-action">🗑</button>
                    <button data-action="copy" class="btn-action">📋</button>
                </div>
            </div>
        `).join('');
    }

    renderVideos() {
        const videoList = document.getElementById('video-list');
        const activeChannels = this.channels.filter(c => c.isActive).map(c => c.id);
        const filteredVideos = this.videos.filter(v => activeChannels.includes(v.channelId));
        
        videoList.innerHTML = filteredVideos.map(video => `
            <div class="video-card" data-video-id="${video.id}">
                <img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail">
                <div class="video-info">
                    <h3>${video.title}</h3>
                    <p>${new Date(video.publishedAt).toLocaleDateString()} • ${video.duration} • ${video.viewCount} views</p>
                    <p>${video.description}</p>
                </div>
                <div class="ai-services">
                    ${video.aiServices.map(service => `
                        <a href="/service/${service.serviceId}/${video.id}" 
                           class="ai-service-link ${service.status}"
                           title="${service.status}">
                            ${service.serviceId}
                        </a>
                    `).join('')}
                </div>
                <div class="video-status ${video.status}">${video.status}</div>
            </div>
        `).join('');
    }

    filterAndSortVideos({ sortBy, filterChannel, dateRange }) {
        let filtered = [...this.videos];
        
        // Apply channel filter
        if (filterChannel) {
            filtered = filtered.filter(v => v.channelId === filterChannel);
        }
        
        // Apply date filter
        if (dateRange) {
            const [start, end] = dateRange.split(',').map(d => new Date(d));
            filtered = filtered.filter(v => {
                const date = new Date(v.publishedAt);
                return date >= start && date <= end;
            });
        }
        
        // Apply sorting
        switch (sortBy) {
            case 'date-desc':
                filtered.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
                break;
            case 'date-asc':
                filtered.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));
                break;
            case 'views':
                filtered.sort((a, b) => b.viewCount - a.viewCount);
                break;
            case 'duration':
                filtered.sort((a, b) => this.parseDuration(b.duration) - this.parseDuration(a.duration));
                break;
            case 'channel':
                filtered.sort((a, b) => {
                    const channelA = this.channels.find(c => c.id === a.channelId)?.name || '';
                    const channelB = this.channels.find(c => c.id === b.channelId)?.name || '';
                    return channelA.localeCompare(channelB);
                });
                break;
        }
        
        this.videos = filtered;
        this.renderVideos();
    }

    parseDuration(duration) {
        const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
        if (!match) return 0;
        const [, hours = 0, minutes = 0, seconds = 0] = match;
        return hours * 3600 + minutes * 60 + seconds * 1;
    }

    applyTheme() {
        document.documentElement.classList.toggle('dark', this.settings.theme === 'dark');
    }

    showError(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = 'toast error';
        setTimeout(() => toast.className = 'toast', 3000);
    }

    showSuccess(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = 'toast success';
        setTimeout(() => toast.className = 'toast', 3000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BrevifyApp();
});
