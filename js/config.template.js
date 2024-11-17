// OAuth 2.0 configuration
const CONFIG = {
    oauth: {
        client_id: "YOUR_CLIENT_ID",
        project_id: "YOUR_PROJECT_ID",
        auth_uri: "https://accounts.google.com/o/oauth2/auth",
        token_uri: "https://oauth2.googleapis.com/token",
        auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
        client_secret: "YOUR_CLIENT_SECRET"
    }
};

// Make config available globally
window.CONFIG = CONFIG;
