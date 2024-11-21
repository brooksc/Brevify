// Constants
const BREVIFY_API = 'http://localhost:8888';

// DOM Elements
const statusEl = document.getElementById('status');
const actionsEl = document.getElementById('actions');
const analyzeBtn = document.getElementById('analyze');
const chatgptBtn = document.getElementById('chatgpt');
const claudeBtn = document.getElementById('claude');
const geminiBtn = document.getElementById('gemini');

// State
let currentVideo = null;
let hasTranscript = false;

// Initialize popup
async function init() {
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('youtube.com/watch')) {
      statusEl.innerHTML = '<p>Navigate to a YouTube video to use Brevify</p>';
      return;
    }

    // Extract video ID
    const videoId = new URLSearchParams(new URL(tab.url).search).get('v');
    if (!videoId) {
      statusEl.innerHTML = '<p>Could not find video ID</p>';
      return;
    }

    currentVideo = videoId;
    
    // Check for transcript
    const response = await fetch(`${BREVIFY_API}/check-transcript?video_id=${videoId}`);
    const data = await response.json();
    
    hasTranscript = data.has_transcript;
    
    if (hasTranscript) {
      statusEl.innerHTML = '<p>✅ Transcript available</p>';
      actionsEl.style.display = 'flex';
    } else {
      statusEl.innerHTML = '<p>❌ No transcript available for this video</p>';
    }
  } catch (error) {
    console.error('Error:', error);
    statusEl.innerHTML = `<p>Error: ${error.message}</p>`;
  }
}

// Event Handlers
analyzeBtn.addEventListener('click', async () => {
  if (!currentVideo || !hasTranscript) return;
  
  try {
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Loading...';
    
    const response = await fetch(`${BREVIFY_API}/fetch-transcript?video_id=${currentVideo}`);
    const data = await response.json();
    
    if (data.transcript) {
      chatgptBtn.disabled = false;
      claudeBtn.disabled = false;
      geminiBtn.disabled = false;
    }
  } catch (error) {
    console.error('Error:', error);
    statusEl.innerHTML = `<p>Error: ${error.message}</p>`;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Learn with AI';
  }
});

chatgptBtn.addEventListener('click', () => {
  window.open(`${BREVIFY_API}/analyze/chatgpt?video_id=${currentVideo}`, '_blank');
});

claudeBtn.addEventListener('click', () => {
  window.open(`${BREVIFY_API}/analyze/claude?video_id=${currentVideo}`, '_blank');
});

geminiBtn.addEventListener('click', () => {
  window.open(`${BREVIFY_API}/analyze/gemini?video_id=${currentVideo}`, '_blank');
});

// Initialize
document.addEventListener('DOMContentLoaded', init);
