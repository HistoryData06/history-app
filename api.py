from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Sample data as fallback
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
                births_list.append
