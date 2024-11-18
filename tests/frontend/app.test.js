import '@testing-library/jest-dom';
import { fireEvent } from '@testing-library/dom';
import { jest } from '@jest/globals';

// Import app.js functionality
import { AppState, showError, hideError, toggleSettings, fetchVideos, displayVideos } from '../../static/js/app.js';

// Mock fetch globally
global.fetch = jest.fn();

describe('AppState Management', () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  test('initializes with default values', () => {
    localStorage.getItem.mockReturnValue(null);
    AppState.initialize();
    
    expect(AppState.theme).toBe('auto');
    expect(AppState.channels).toEqual([]);
    expect(localStorage.getItem).toHaveBeenCalledWith('theme');
  });

  test('loads saved theme from localStorage', () => {
    localStorage.getItem.mockImplementation((key) => {
      if (key === 'theme') return 'dark';
      return null;
    });
    
    AppState.initialize();
    expect(AppState.theme).toBe('dark');
  });

  test('saves channel to history', () => {
    const testChannel = {
      url: 'https://youtube.com/@test',
      title: 'Test Channel'
    };
    
    AppState.addChannel(testChannel.url, testChannel.title);
    
    expect(localStorage.setItem).toHaveBeenCalled();
    expect(AppState.channels).toContainEqual(testChannel);
  });

  test('limits channel history to maximum items', () => {
    // Add more than MAX_HISTORY_ITEMS channels
    for (let i = 0; i < 25; i++) {
      AppState.addChannel(`https://youtube.com/@test${i}`, `Test Channel ${i}`);
    }
    
    expect(AppState.channels.length).toBeLessThanOrEqual(20);
    expect(AppState.channels[0].title).toBe('Test Channel 24'); // Most recent should be first
  });

  test('prevents duplicate channels in history', () => {
    const channel = {
      url: 'https://youtube.com/@test',
      title: 'Test Channel'
    };
    
    AppState.addChannel(channel.url, channel.title);
    AppState.addChannel(channel.url, channel.title);
    
    const matches = AppState.channels.filter(c => c.url === channel.url);
    expect(matches.length).toBe(1);
  });
});

describe('UI Interactions', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="settings-panel" class="hidden"></div>
      <button onclick="toggleSettings()">Settings</button>
    `;
    jest.clearAllMocks();
  });

  test('toggleSettings shows and hides settings panel', () => {
    const button = document.querySelector('button');
    const panel = document.getElementById('settings-panel');
    
    toggleSettings();
    expect(panel).not.toHaveClass('hidden');
    
    toggleSettings();
    expect(panel).toHaveClass('hidden');
  });

  test('toggleSettings does nothing if panel not found', () => {
    document.body.innerHTML = ''; // Remove the panel
    expect(() => toggleSettings()).not.toThrow();
  });
});

describe('Theme Management', () => {
  beforeEach(() => {
    document.documentElement.className = '';
    localStorage.clear();
    jest.spyOn(localStorage, 'setItem');
    jest.spyOn(localStorage, 'getItem');
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn()
    }));
    jest.clearAllMocks();
  });

  test('updates theme class on html element', () => {
    AppState.updateTheme('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    
    AppState.updateTheme('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  test('persists theme choice to localStorage', () => {
    AppState.updateTheme('dark');
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
    
    AppState.updateTheme('light');
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  test('respects system dark mode preference', () => {
    // Mock system dark mode preference
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn()
    }));

    AppState.updateTheme('auto');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  test('respects system light mode preference', () => {
    // Mock system light mode preference
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn()
    }));

    AppState.updateTheme('auto');
    expect(document.documentElement.classList.contains('light')).toBe(true);
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="error-message" class="hidden">
        <span class="message"></span>
      </div>
    `;
    jest.clearAllMocks();
  });

  test('shows error message', () => {
    const message = 'Test error message';
    showError(message);
    
    const errorElement = document.getElementById('error-message');
    const messageElement = errorElement.querySelector('.message');
    
    expect(errorElement).not.toHaveClass('hidden');
    expect(messageElement.textContent).toBe(message);
  });

  test('hides error message', () => {
    const errorElement = document.getElementById('error-message');
    errorElement.classList.remove('hidden');
    
    hideError();
    expect(errorElement).toHaveClass('hidden');
  });

  test('handles HTML in error messages safely', () => {
    const messageWithHTML = '<script>alert("xss")</script>Test message';
    showError(messageWithHTML);
    
    const messageElement = document.querySelector('.message');
    expect(messageElement.innerHTML).not.toContain('<script>');
  });

  test('handles missing error element gracefully', () => {
    document.body.innerHTML = '';
    expect(() => showError('test')).not.toThrow();
    expect(() => hideError()).not.toThrow();
  });
});

describe('Video Management', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="video-container"></div>
      <div id="loading-spinner" class="hidden"></div>
      <div id="error-message" class="hidden">
        <span class="message"></span>
      </div>
      <input id="channel-input" type="text" value="" />
    `;
    jest.clearAllMocks();
  });

  test('fetchVideos handles empty input', async () => {
    await fetchVideos();
    
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
    expect(errorElement.querySelector('.message').textContent).toBe('Please enter a YouTube channel URL');
    expect(fetch).not.toHaveBeenCalled();
  });

  test('fetchVideos shows loading state', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    global.fetch.mockImplementationOnce(() => new Promise(resolve => setTimeout(() => resolve({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        channel_title: 'Test Channel',
        videos: []
      })
    }), 100)));

    const fetchPromise = fetchVideos();
    
    // Loading state should be visible immediately
    const spinner = document.getElementById('loading-spinner');
    expect(spinner).not.toHaveClass('hidden');
    
    await fetchPromise;
    
    // Loading state should be hidden after fetch completes
    expect(spinner).toHaveClass('hidden');
  });

  test('fetchVideos handles successful response', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    const mockResponse = {
      success: true,
      channel_title: 'Test Channel',
      videos: [
        {
          id: '123',
          title: 'Test Video',
          description: 'Test Description',
          thumbnail: 'test.jpg'
        }
      ]
    };

    global.fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    }));

    await fetchVideos();
    
    // Should have called fetch with the correct URL
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/videos?url='));
    
    // Should have added channel to history
    expect(AppState.channels).toContainEqual({
      url: 'https://youtube.com/@test',
      title: 'Test Channel'
    });
    
    // Error message should be hidden
    const errorElement = document.getElementById('error-message');
    expect(errorElement).toHaveClass('hidden');
  });

  test('fetchVideos handles API error response', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    global.fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        success: false,
        error: 'Channel not found'
      })
    }));

    await fetchVideos();
    
    // Should show error message
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
    expect(errorElement.querySelector('.message').textContent).toBe('Channel not found');
  });

  test('fetchVideos handles network error', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    global.fetch.mockImplementationOnce(() => Promise.reject(new Error('Network error')));

    await fetchVideos();
    
    // Should show error message
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
    expect(errorElement.querySelector('.message').textContent).toBe('Failed to fetch videos. Please try again.');
  });
});

describe('Video Display', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="video-container"></div>
      <template id="video-card-template">
        <div class="video-card">
          <img src="" alt="">
          <a href=""></a>
          <p class="description"></p>
        </div>
      </template>
      <div id="error-message" class="hidden">
        <span class="message"></span>
      </div>
      <div id="loading-spinner" class="hidden"></div>
      <input id="channel-input" type="text">
    `;
    jest.clearAllMocks();
  });

  test('displayVideos handles non-array input', () => {
    displayVideos('not an array');
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
    expect(errorElement.querySelector('.message').textContent).toBe('Invalid video data received');
  });

  test('displayVideos handles null/undefined input', () => {
    displayVideos(null);
    displayVideos(undefined);
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
  });

  test('displayVideos handles empty array', () => {
    displayVideos([]);
    const container = document.getElementById('video-container');
    expect(container.innerHTML).toContain('No videos found');
  });

  test('displayVideos handles invalid video objects', () => {
    const invalidVideos = [
      null,
      undefined,
      'string instead of object',
      {},
      { id: '123' }, // missing required fields
    ];
    displayVideos(invalidVideos);
    const container = document.getElementById('video-container');
    const cards = container.querySelectorAll('.video-card');
    expect(cards.length).toBe(0); // Should skip invalid videos
  });

  test('displayVideos handles missing template', () => {
    document.getElementById('video-card-template').remove();
    displayVideos([{ id: '123', title: 'Test', description: 'Test', thumbnail: 'test.jpg' }]);
    const container = document.getElementById('video-container');
    expect(container.children.length).toBe(0);
  });

  test('displayVideos handles missing container', () => {
    document.getElementById('video-container').remove();
    expect(() => {
      displayVideos([{ id: '123', title: 'Test', description: 'Test', thumbnail: 'test.jpg' }]);
    }).not.toThrow();
  });

  test('displayVideos creates correct video cards', () => {
    const videos = [
      {
        id: '123',
        title: 'Test Video',
        description: 'Test Description',
        thumbnail: 'test.jpg'
      }
    ];
    
    displayVideos(videos);
    const container = document.getElementById('video-container');
    const card = container.querySelector('.video-card');
    
    expect(card).toBeTruthy();
    expect(card.querySelector('img').src).toContain('test.jpg');
    expect(card.querySelector('img').alt).toBe('Test Video');
    expect(card.querySelector('a').href).toContain('watch?v=123');
    expect(card.querySelector('a').textContent).toBe('Test Video');
    expect(card.querySelector('p').textContent).toBe('Test Description');
  });
});

describe('API Integration', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="video-container"></div>
      <template id="video-card-template">
        <div class="video-card">
          <img src="" alt="">
          <a href=""></a>
          <p class="description"></p>
        </div>
      </template>
      <div id="error-message" class="hidden">
        <span class="message"></span>
      </div>
      <div id="loading-spinner" class="hidden"></div>
      <input id="channel-input" type="text">
    `;
    jest.clearAllMocks();
  });

  test('fetchVideos handles malformed API response', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    global.fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        success: true,
        videos: 'not an array'  // Malformed response
      })
    }));

    await fetchVideos();
    
    // Should show error message
    const errorElement = document.getElementById('error-message');
    expect(errorElement).not.toHaveClass('hidden');
    expect(errorElement.querySelector('.message').textContent).toBe('Invalid video data received from server');
  });

  test('fetchVideos handles missing channel_title gracefully', async () => {
    const channelInput = document.getElementById('channel-input');
    channelInput.value = 'https://youtube.com/@test';
    
    const response = {
      success: true,
      videos: [{
        id: '123',
        title: 'Test Video',
        description: 'Test Description',
        thumbnail: 'test.jpg'
      }]
      // Intentionally missing channel_title
    };

    global.fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve(response)
    }));

    await fetchVideos();
    
    // Should still display videos even without channel_title
    const container = document.getElementById('video-container');
    expect(container.querySelector('.video-card')).toBeTruthy();
  });
});
