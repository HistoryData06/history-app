from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random
import os

app = Flask(__name__)
CORS(app)

# Your sample data
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

@app.route('/api/events')
def get_events():
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)
    
    if not month or not day:
        now = datetime.now()
        month = now.month
        day = now.day
    
    events_list, births_list, deaths_list = [], [], []
    
    # Try Wikipedia
    try:
        r = requests.get(f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}", timeout=5)
        if r.status_code == 200:
            for e in r.json().get('events', [])[:10]:
                events_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:150]
                })
    except:
        pass
    
    try:
        r = requests.get(f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}", timeout=5)
        if r.status_code == 200:
            for e in r.json().get('births', [])[:6]:
                births_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:120]
                })
    except:
        pass
    
    try:
        r = requests.get(f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}", timeout=5)
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

@app.route('/api/random')
def random_event():
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)
    
    if not month or not day:
        now = datetime.now()
        month = now.month
        day = now.day
    
    events = []
    try:
        r = requests.get(f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}", timeout=5)
        if r.status_code == 200:
            for e in r.json().get('events', [])[:10]:
                events.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:150]
                })
    except:
        pass
    
    if not events:
        events = SAMPLE_EVENTS
    
    return jsonify(random.choice(events) if events else {'year': '?', 'text': 'No events found'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'History API is running!'})

# 👇 THIS IS IMPORTANT FOR RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
