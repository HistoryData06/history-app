from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random
import os

app = Flask(__name__)
CORS(app)

# ===== LANGUAGE DICTIONARY =====
LANGUAGES = {
    'en': {
        'name': 'English',
        'app_title': '📜 Today in History',
        'subtitle': 'On This Day',
        'date_label': '📅 Date',
        'go_btn': 'Go',
        'today_btn': 'Today',
        'random_fact': 'Click for a random historical fact!',
        'random_btn': '🎲 Random Fact',
        'quiz_label': '📝 QUIZ TIME',
        'quiz_ready': 'Ready to test your history knowledge?',
        'quiz_new': '📚 New Quiz',
        'quiz_not_enough': 'Not enough events for a quiz today! 😅',
        'quiz_question': '❓ What happened in',
        'quiz_correct': '✅ Correct! Well done! 🎉',
        'quiz_wrong': '❌ Wrong! Correct:',
        'quiz_score': '🏆 Quiz Score:',
        'favorites_label': '⭐ Favorites',
        'events_label': '🔥 Historical Events',
        'births_label': '🎂 Born on This Day',
        'deaths_label': '🕊️ Died on This Day',
        'no_events': 'No events for this date',
        'error_loading': '❌ Error loading events',
        'retry_btn': 'Retry',
        'share_all': '📤 Share All',
        'share_today': '📅 Share Today',
        'refresh_btn': '⟳ Refresh',
        'footer': 'Built with ❤️ • Wikipedia',
        'loading': 'Loading history...',
        'no_facts': 'No facts available for this date!'
    },
    'hr': {
        'name': 'Hrvatski',
        'app_title': '📜 Povijest danas',
        'subtitle': 'Na današnji dan',
        'date_label': '📅 Datum',
        'go_btn': 'Idi',
        'today_btn': 'Danas',
        'random_fact': 'Klikni za nasumičnu povijesnu činjenicu!',
        'random_btn': '🎲 Nasumična činjenica',
        'quiz_label': '📝 QUIZ',
        'quiz_ready': 'Spremni testirati svoje povijesno znanje?',
        'quiz_new': '📚 Novi kviz',
        'quiz_not_enough': 'Nema dovoljno događaja za kviz danas! 😅',
        'quiz_question': '❓ Što se dogodilo',
        'quiz_correct': '✅ Točno! Odlično! 🎉',
        'quiz_wrong': '❌ Netočno! Točno je:',
        'quiz_score': '🏆 Rezultat:',
        'favorites_label': '⭐ Favoriti',
        'events_label': '🔥 Povijesni događaji',
        'births_label': '🎂 Rođeni na današnji dan',
        'deaths_label': '🕊️ Preminuli na današnji dan',
        'no_events': 'Nema događaja za ovaj datum',
        'error_loading': '❌ Greška pri učitavanju',
        'retry_btn': 'Pokušaj ponovno',
        'share_all': '📤 Podijeli sve',
        'share_today': '📅 Podijeli danas',
        'refresh_btn': '⟳ Osvježi',
        'footer': 'Napravljeno s ❤️ • Wikipedia',
        'loading': 'Učitavanje povijesti...',
        'no_facts': 'Nema činjenica za ovaj datum!'
    },
    'es': {
        'name': 'Español',
        'app_title': '📜 Hoy en la Historia',
        'subtitle': 'En este día',
        'date_label': '📅 Fecha',
        'go_btn': 'Ir',
        'today_btn': 'Hoy',
        'random_fact': '¡Haz clic para un hecho histórico aleatorio!',
        'random_btn': '🎲 Hecho aleatorio',
        'quiz_label': '📝 CUESTIONARIO',
        'quiz_ready': '¿Listo para probar tus conocimientos de historia?',
        'quiz_new': '📚 Nuevo cuestionario',
        'quiz_not_enough': '¡No hay suficientes eventos para un cuestionario hoy! 😅',
        'quiz_question': '❓ ¿Qué sucedió en',
        'quiz_correct': '✅ ¡Correcto! ¡Bien hecho! 🎉',
        'quiz_wrong': '❌ ¡Incorrecto! Correcto:',
        'quiz_score': '🏆 Puntuación:',
        'favorites_label': '⭐ Favoritos',
        'events_label': '🔥 Eventos históricos',
        'births_label': '🎂 Nacidos en este día',
        'deaths_label': '🕊️ Fallecidos en este día',
        'no_events': 'No hay eventos para esta fecha',
        'error_loading': '❌ Error al cargar eventos',
        'retry_btn': 'Reintentar',
        'share_all': '📤 Compartir todo',
        'share_today': '📅 Compartir hoy',
        'refresh_btn': '⟳ Actualizar',
        'footer': 'Hecho con ❤️ • Wikipedia',
        'loading': 'Cargando historia...',
        'no_facts': '¡No hay hechos disponibles para esta fecha!'
    },
    'de': {
        'name': 'Deutsch',
        'app_title': '📜 Heute in der Geschichte',
        'subtitle': 'An diesem Tag',
        'date_label': '📅 Datum',
        'go_btn': 'Los',
        'today_btn': 'Heute',
        'random_fact': 'Klicke für eine zufällige historische Tatsache!',
        'random_btn': '🎲 Zufällige Tatsache',
        'quiz_label': '📝 QUIZ',
        'quiz_ready': 'Bereit, dein Geschichtswissen zu testen?',
        'quiz_new': '📚 Neues Quiz',
        'quiz_not_enough': 'Nicht genug Ereignisse für ein Quiz heute! 😅',
        'quiz_question': '❓ Was geschah im',
        'quiz_correct': '✅ Richtig! Gut gemacht! 🎉',
        'quiz_wrong': '❌ Falsch! Richtig ist:',
        'quiz_score': '🏆 Punktestand:',
        'favorites_label': '⭐ Favoriten',
        'events_label': '🔥 Historische Ereignisse',
        'births_label': '🎂 Geboren an diesem Tag',
        'deaths_label': '🕊️ Gestorben an diesem Tag',
        'no_events': 'Keine Ereignisse für dieses Datum',
        'error_loading': '❌ Fehler beim Laden der Ereignisse',
        'retry_btn': 'Wiederholen',
        'share_all': '📤 Alle teilen',
        'share_today': '📅 Heute teilen',
        'refresh_btn': '⟳ Aktualisieren',
        'footer': 'Gemacht mit ❤️ • Wikipedia',
        'loading': 'Lade Geschichte...',
        'no_facts': 'Keine Fakten für dieses Datum verfügbar!'
    }
}

# ===== ROUTES =====
@app.route('/')
def index():
    """Serve the main page from templates/index.html"""
    return render_template('index.html')

@app.route('/api/languages')
def get_languages():
    """Return the language dictionary for the frontend"""
    return jsonify(LANGUAGES)

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
        events_list = [
            {'year': '1914', 'text': 'World War I began when Austria-Hungary declared war on Serbia'},
            {'year': '1945', 'text': 'A US Army bomber crashed into the Empire State Building'},
            {'year': '1976', 'text': 'The Tangshan earthquake in China killed over 240,000 people'},
            {'year': '1996', 'text': 'The remains of a woolly mammoth were discovered in Siberia'}
        ]
        births_list = [
            {'year': '1804', 'text': 'Ludwig Feuerbach, German philosopher'},
            {'year': '1929', 'text': 'Jacqueline Kennedy Onassis, First Lady of the United States'},
            {'year': '1938', 'text': 'Alberto Fujimori, President of Peru'},
            {'year': '1954', 'text': 'Hugo Chávez, President of Venezuela'}
        ]
        deaths_list = [
            {'year': '1750', 'text': 'Johann Sebastian Bach, German composer'},
            {'year': '2004', 'text': 'Francis Crick, co-discoverer of DNA structure'},
            {'year': '2015', 'text': 'Edward Natapei, Prime Minister of Vanuatu'}
        ]
    
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
