#!/usr/bin/env python3
"""
Brevify - YouTube Learning Assistant
Main application file using Flask framework
"""
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    """Main page route"""
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def process():
    """Process YouTube URL and return results"""
    url = request.form.get('youtube_url')
    # Implementation coming soon
    return render_template('results.html', url=url)

if __name__ == "__main__":
    app.run(debug=True)
