// Local Storage Management
export const StorageKeys = {
    CHANNELS: 'brevify_channels',
    SETTINGS: 'brevify_settings',
    VIDEOS: 'brevify_videos'
};

export const defaultSettings = {
    apiKey: '',
    defaultPrompt: '',
    selectedAIs: ['summary', 'transcript'],
    debugEnabled: false,
    cacheTimeout: 300,
    theme: 'light'
};

export class Store {
    static getChannels() {
        const stored = localStorage.getItem(StorageKeys.CHANNELS);
        return stored ? JSON.parse(stored) : [];
    }

    static saveChannels(channels) {
        localStorage.setItem(StorageKeys.CHANNELS, JSON.stringify(channels));
    }

    static getSettings() {
        const stored = localStorage.getItem(StorageKeys.SETTINGS);
        return stored ? JSON.parse(stored) : { ...defaultSettings };
    }

    static saveSettings(settings) {
        localStorage.setItem(StorageKeys.SETTINGS, JSON.stringify({
            ...defaultSettings,
            ...settings
        }));
    }

    static getVideos() {
        const stored = localStorage.getItem(StorageKeys.VIDEOS);
        return stored ? JSON.parse(stored) : [];
    }

    static saveVideos(videos) {
        localStorage.setItem(StorageKeys.VIDEOS, JSON.stringify(videos));
    }

    static addChannel(channel) {
        const channels = this.getChannels();
        const exists = channels.find(c => c.id === channel.id);
        if (!exists) {
            channels.push({
                ...channel,
                lastRefreshed: new Date().toISOString(),
                isActive: true
            });
            this.saveChannels(channels);
        }
        return channels;
    }

    static removeChannel(channelId) {
        const channels = this.getChannels();
        const filtered = channels.filter(c => c.id !== channelId);
        this.saveChannels(filtered);
        return filtered;
    }

    static updateChannel(channelId, updates) {
        const channels = this.getChannels();
        const updated = channels.map(channel => 
            channel.id === channelId ? { ...channel, ...updates } : channel
        );
        this.saveChannels(updated);
        return updated;
    }
}
