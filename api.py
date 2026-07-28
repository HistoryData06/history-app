from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random

# 👇 The application object MUST be named 'app' for Vercel
app = Flask(__name__)
CORS(app)

# ... (your existing SAMPLE_EVENTS, SAMPLE_BIRTHS, SAMPLE_DEATHS data here) ...

# --- Your Routes ---
# All your @app.route decorators remain the same
@app.route('/api/events')
def get_events():
    # ... (your existing code for this route) ...
    return jsonify({'events': events_list, 'births': births_list, 'deaths': deaths_list})

@app.route('/api/random')
def random_event():
    # ... (your existing code for this route) ...
    return jsonify(random_event_data)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'History API is running!'})

# This block is only needed if you run the file directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
