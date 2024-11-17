// OAuth 2.0 configuration
const AUTH_CONFIG = {
    client_id: window.CONFIG?.oauth?.client_id || '', // Get client ID from config
    scope: 'https://www.googleapis.com/auth/youtube.force-ssl',
    discovery_docs: ['https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest']
};

let tokenClient;
let gapiInited = false;
let gisInited = false;

function gapiLoaded() {
    gapi.load('client', initializeGapiClient);
}

async function initializeGapiClient() {
    await gapi.client.init({
        discoveryDocs: AUTH_CONFIG.discovery_docs,
    });
    gapiInited = true;
    maybeEnableButtons();
}

function gisLoaded() {
    tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: AUTH_CONFIG.client_id,
        scope: AUTH_CONFIG.scope,
        callback: '', // defined later
    });
    gisInited = true;
    maybeEnableButtons();
}

function maybeEnableButtons() {
    if (gapiInited && gisInited) {
        document.getElementById('authorize-button')?.classList.remove('hidden');
    }
}

let accessToken = null;

async function handleAuthClick() {
    tokenClient.callback = async (resp) => {
        if (resp.error !== undefined) {
            throw resp;
        }
        accessToken = resp.access_token;
        document.getElementById('authorize-button')?.classList.add('hidden');
        document.getElementById('signout-button')?.classList.remove('hidden');
        
        // Store the token in AppState
        if (window.AppState) {
            window.AppState.accessToken = accessToken;
        }
    };

    if (accessToken === null) {
        // Prompt the user to select a Google Account and ask for consent to share their data
        tokenClient.requestAccessToken({prompt: 'consent'});
    } else {
        // Skip display of account chooser and consent dialog for an existing session
        tokenClient.requestAccessToken({prompt: ''});
    }
}

function handleSignoutClick() {
    const token = accessToken;
    accessToken = null;
    fetch(`https://oauth2.googleapis.com/revoke?token=${token}`, {
        method: 'POST',
    }).then(() => {
        document.getElementById('authorize-button')?.classList.remove('hidden');
        document.getElementById('signout-button')?.classList.add('hidden');
        if (window.AppState) {
            window.AppState.accessToken = null;
        }
    });
}

// Export functions for use in app.js
window.gapiLoaded = gapiLoaded;
window.gisLoaded = gisLoaded;
window.handleAuthClick = handleAuthClick;
window.handleSignoutClick = handleSignoutClick;