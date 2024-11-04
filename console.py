# console.py
import json
import os
from flask import Flask, render_template_string

app = Flask(__name__)
VIDEO_LINKS_FILE = "C:\\Users\\Ducky\\Documents\\visualstudio\\api\\video_links.json"

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uploaded Videos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        a {
            display: block;
            margin: 10px 0;
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Uploaded Videos</h1>
    <div>
        {% if video_links %}
            {% for link in video_links %}
                <a href="{{ link }}">{{ link }}</a>
            {% endfor %}
        {% else %}
            <p>No videos uploaded yet.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    video_links = []
    if os.path.exists(VIDEO_LINKS_FILE):
        with open(VIDEO_LINKS_FILE, 'r') as f:
            video_links = json.load(f).get('links', [])
    return render_template_string(HTML_TEMPLATE, video_links=video_links)

def start_console():
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    start_console()
