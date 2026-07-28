from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random
import os

app = Flask(__name__)
CORS(app)

# ===== HTML TEMPLATE (everything in one file) =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>📅 Today in History</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Arial', sans-serif;
            background: #000000;
            min-height: 100vh;
            padding: 20px;
            color: #ffffff;
        }
        .container { max-width: 580px; margin: 0 auto; padding: 10px 0 30px; }

        .header {
            text-align: center;
            padding: 30px 20px 25px;
            margin-bottom: 30px;
            border-bottom: 3px solid #FFD700;
        }
        .header h1 {
            font-size: 2.2em;
            font-weight: 900;
            letter-spacing: 6px;
            color: #FFD700;
            text-transform: uppercase;
        }
        .header .date {
            font-size: 1.1em;
            color: #ffffff;
            margin-top: 14px;
            letter-spacing: 3px;
        }

        .date-picker {
            background: #0a0a0a;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 22px;
            border: 1px solid rgba(255, 215, 0, 0.15);
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .date-picker input {
            flex: 1;
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid rgba(255, 215, 0, 0.2);
            background: #1a1a1a;
            color: #ffffff;
            font-size: 1em;
            min-width: 150px;
        }
        .date-picker .go-btn {
            padding: 10px 24px;
            background: #FFD700;
            border: none;
            border-radius: 8px;
            color: #000000;
            font-weight: 900;
            cursor: pointer;
        }
        .date-picker .today-btn {
            padding: 10px 16px;
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 8px;
            color: #FFD700;
            cursor: pointer;
        }

        .card {
            background: #0a0a0a;
            border-radius: 12px;
            padding: 24px 22px;
            margin-bottom: 22px;
            border: 1px solid rgba(255, 215, 0, 0.15);
        }
        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(255, 215, 0, 0.08);
        }
        .card-header h2 {
            font-size: 0.85em;
            color: #FFD700;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        .card-header .badge {
            margin-left: auto;
            background: rgba(255, 215, 0, 0.10);
            padding: 2px 12px;
            border-radius: 20px;
            color: #FFD700;
            font-size: 0.65em;
        }
        .event-item {
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 215, 0, 0.04);
            display: flex;
            gap: 14px;
            align-items: flex-start;
        }
        .event-item:last-child { border-bottom: none; }
        .event-year {
            flex-shrink: 0;
            color: #FFD700;
            font-weight: 900;
            min-width: 58px;
            padding: 2px 10px;
            background: rgba(255, 215, 0, 0.06);
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255, 215, 0, 0.08);
        }
        .event-text {
            color: #ffffff;
            font-size: 0.95em;
            line-height: 1.6;
            font-weight: 300;
        }

        .fact-card {
            background: #0a0a0a;
            border-radius: 12px;
            padding: 20px 22px;
            margin-bottom: 22px;
            border: 1px solid rgba(255, 215, 0, 0.15);
            text-align: center;
        }
        .fact-card .fact-text {
            color: #ffffff;
            font-size: 0.95em;
            line-height: 1.6;
            font-weight: 300;
        }
        .fact-btn {
            margin-top: 12px;
            padding: 8px 20px;
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 20px;
            color: #FFD700;
            cursor: pointer;
            font-size: 0.8em;
        }

        .refresh-btn {
            display: block;
            width: 100%;
            padding: 18px;
            background: #FFD700;
            border: none;
            border-radius: 50px;
            color: #000000;
            font-weight: 900;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-top: 8px;
        }

        .loading-state {
            text-align: center;
            padding: 50px 20px;
            color: #666666;
        }
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255, 215, 0, 0.08);
            border-top: 3px solid #FFD700;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 16px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .footer {
            text-align: center;
            color: #333333;
            font-size: 0.7em;
            padding: 30px 0 10px;
            border-top: 1px solid rgba(255, 215, 0, 0.04);
            margin-top: 10px;
        }

        @media (max-width: 480px) {
            body { padding: 12px; }
            .header h1 { font-size: 1.6em; }
            .date-picker { flex-direction: column; }
            .date-picker input { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📜 Today in History</h1>
            <div class="date" id="headerDate">Loading...</div>
        </div>

        <div class="date-picker">
            <input type="date" id="dateInput">
            <button class="go-btn" onclick="goToDate()">Go</button>
            <button class="today-btn" onclick="goToday()">Today</button>
        </div>

        <div class="fact-card">
            <div class="fact-text" id="factText">Click for a random fact!</div>
            <button class="fact-btn" onclick="getRandomFact()">🎲 Random Fact</button>
        </div>

        <div id="content">
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading history...</p>
            </div>
        </div>

        <button class="refresh-btn" onclick="loadEvents()">⟳ Refresh</button>

        <div class="footer">
            Built with ❤️ • Wikipedia
        </div>
    </div>

    <script>
        let currentEvents = [];

        function formatDate(date) {
            return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
        }

        function getDateFromInput() {
            const val = document.getElementById('dateInput').value;
            if (val) {
                const parts = val.split('-');
                return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
            }
            return new Date();
        }

        function loadEvents() {
            const date = getDateFromInput();
            const month = date.getMonth() + 1;
            const day = date.getDate();
            
            document.getElementById('headerDate').innerHTML = formatDate(date);
            
            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Loading history...</p>
                </div>
            `;

            // Use the API endpoint
            fetch(`/api/events?month=${month}&day=${day}`)
                .then(response => response.json())
                .then(data => {
                    currentEvents = data;
                    let html = '';

                    if (data.events && data.events.length > 0) {
                        html += `
                            <div class="card">
                                <div class="card-header">
                                    <h2>🔥 Historical Events</h2>
                                    <span class="badge">${data.events.length}</span>
                                </div>
                        `;
                        data.events.forEach(e => {
                            html += `
                                <div class="event-item">
                                    <span class="event-year">${e.year}</span>
                                    <span class="event-text">${e.text}</span>
                                </div>
                            `;
                        });
                        html += `</div>`;
                    }

                    if (data.births && data.births.length > 0) {
                        html += `
                            <div class="card">
                                <div class="card-header">
                                    <h2>🎂 Born on This Day</h2>
                                    <span class="badge">${data.births.length}</span>
                                </div>
                        `;
                        data.births.forEach(e => {
                            html += `
                                <div class="event-item">
                                    <span class="event-year">${e.year}</span>
                                    <span class="event-text">${e.text}</span>
                                </div>
                            `;
                        });
                        html += `</div>`;
                    }

                    if (data.deaths && data.deaths.length > 0) {
                        html += `
                            <div class="card">
                                <div class="card-header">
                                    <h2>🕊️ Died on This Day</h2>
                                    <span class="badge">${data.deaths.length}</span>
                                </div>
                        `;
                        data.deaths.forEach(e => {
                            html += `
                                <div class="event-item">
                                    <span class="event-year">${e.year}</span>
                                    <span class="event-text">${e.text}</span>
                                </div>
                            `;
                        });
                        html += `</div>`;
                    }

                    if (!html) {
                        html = `
                            <div class="card" style="text-align:center;padding:40px 20px;">
                                <p style="color:#888888;">No events for this date</p>
                            </div>
                        `;
                    }

                    content.innerHTML = html;
                })
                .catch(err => {
                    content.innerHTML = `
                        <div class="card" style="text-align:center;padding:40px 20px;">
                            <p style="color:#ff6b6b;">❌ Error loading events</p>
                            <p style="color:#666;font-size:0.8em;">${err.message}</p>
                            <button onclick="loadEvents()" style="margin-top:12px;padding:8px 20px;background:#FFD700;border:none;border-radius:6px;color:#000;font-weight:bold;cursor:pointer;">Retry</button>
                        </div>
                    `;
                });
        }

        function goToDate() {
            loadEvents();
        }

        function goToday() {
            const today = new Date();
            document.getElementById('dateInput').value = today.toISOString().split('T')[0];
            loadEvents();
        }

        function getRandomFact() {
            const allEvents = [];
            if (currentEvents.events) allEvents.push(...currentEvents.events);
            if (currentEvents.births) allEvents.push(...currentEvents.births);
            if (currentEvents.deaths) allEvents.push(...currentEvents.deaths);
            
            if (allEvents.length === 0) {
                document.getElementById('factText').innerHTML = 'No facts available!';
                return;
            }
            
            const random = allEvents[Math.floor(Math.random() * allEvents.length)];
            document.getElementById('factText').innerHTML = 
                `<span style="color:#FFD700;">${random.year}</span> — ${random.text}`;
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date();
            document.getElementById('dateInput').value = today.toISOString().split('T')[0];
            loadEvents();
        });
    </script>
</body>
</html>
"""

# ===== SAMPLE DATA =====
SAMPLE_EVENTS = [
    {'year': '1914', 'text': 'World War I began when Austria-Hungary declared war on Serbia'},
    {'year': '1945', 'text': 'A US Army bomber crashed into the Empire State Building'},
    {'year': '1976', 'text': 'The Tangshan earthquake in China killed over 240,000 people'},
    {'year': '1996', 'text': 'The remains of a woolly mammoth were discovered in Siberia'}
]

SAMPLE_BIRTHS = [
    {'year': '1804', 'text': 'Ludwig Feuerbach, German philosopher'},
    {'year': '1929', 'text': 'Jacqueline Kennedy Onassis, First Lady of the United States'},
    {'year': '1938', 'text': 'Alberto Fujimori, President of Peru'},
    {'year': '1954', 'text': 'Hugo Chávez, President of Venezuela'}
]

SAMPLE_DEATHS = [
    {'year': '1750', 'text': 'Johann Sebastian Bach, German composer'},
    {'year': '2004', 'text': 'Francis Crick, co-discoverer of DNA structure'},
    {'year': '2015', 'text': 'Edward Natapei, Prime Minister of Vanuatu'}
]

# ===== ROUTES =====
@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/events')
def get_events():
    """Get historical events for a specific date"""
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)
    
    if not month or not day:
        now = datetime.now()
        month = now.month
        day = now.day
    
    events_list, births_list, deaths_list = [], [], []
    
    # Try Wikipedia
    try:
        url = f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for e in r.json().get('events', [])[:10]:
                events_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:150]
                })
    except:
        pass
    
    try:
        url = f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for e in r.json().get('births', [])[:6]:
                births_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:120]
                })
    except:
        pass
    
    try:
        url = f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for e in r.json().get('deaths', [])[:6]:
                deaths_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:120]
                })
    except:
        pass
    
    # Use sample data if Wikipedia failed
    if not events_list and not births_list and not deaths_list:
        events_list = SAMPLE_EVENTS
        births_list = SAMPLE_BIRTHS
        deaths_list = SAMPLE_DEATHS
    
    return jsonify({
        'events': events_list,
        'births': births_list,
        'deaths': deaths_list
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'History API is running!'})

# ===== START SERVER =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
