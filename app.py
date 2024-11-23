#!/usr/bin/env python3
"""
Brevify - Your Shortcut to YouTube Wisdom
Main application file using Flask framework
"""
from flask import Flask, render_template, request, jsonify
from app.db import init_db, save_url, get_saved_urls

app = Flask(__name__)

# Initialize the database
init_db()

@app.route("/")
def index():
    """Main page route"""
    urls = get_saved_urls()
    return render_template('index.html', saved_urls=urls)

@app.route("/save-url", methods=["POST"])
def save_channel_url():
    """Save a channel URL"""
    url = request.form.get('channel_url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    if save_url(url):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to save URL"}), 500

@app.route("/fetch-videos", methods=["POST"])
def fetch_videos():
    """Process YouTube URL and return results"""
    url = request.form.get('channel_url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Save the URL when fetching videos
    save_url(url)
    
    # Implementation coming soon
    return render_template('results.html', url=url)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
