from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
from datetime import datetime
import random
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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
    },
    'fr': {
        'name': 'Français',
        'app_title': '📜 Aujourd\'hui dans l\'Histoire',
        'subtitle': 'En ce jour',
        'date_label': '📅 Date',
        'go_btn': 'Aller',
        'today_btn': 'Aujourd\'hui',
        'random_fact': 'Cliquez pour un fait historique aléatoire !',
        'random_btn': '🎲 Fait aléatoire',
        'quiz_label': '📝 QUIZ',
        'quiz_ready': 'Prêt à tester vos connaissances en histoire ?',
        'quiz_new': '📚 Nouveau quiz',
        'quiz_not_enough': 'Pas assez d\'événements pour un quiz aujourd\'hui ! 😅',
        'quiz_question': '❓ Que s\'est-il passé en',
        'quiz_correct': '✅ Correct ! Bien joué ! 🎉',
        'quiz_wrong': '❌ Faux ! Correct :',
        'quiz_score': '🏆 Score :',
        'favorites_label': '⭐ Favoris',
        'events_label': '🔥 Événements historiques',
        'births_label': '🎂 Nés ce jour',
        'deaths_label': '🕊️ Décédés ce jour',
        'no_events': 'Aucun événement pour cette date',
        'error_loading': '❌ Erreur de chargement',
        'retry_btn': 'Réessayer',
        'share_all': '📤 Tout partager',
        'share_today': '📅 Partager aujourd\'hui',
        'refresh_btn': '⟳ Actualiser',
        'footer': 'Fait avec ❤️ • Wikipédia',
        'loading': 'Chargement de l\'histoire...',
        'no_facts': 'Aucun fait disponible pour cette date !'
    },
    'it': {
        'name': 'Italiano',
        'app_title': '📜 Oggi nella Storia',
        'subtitle': 'In questo giorno',
        'date_label': '📅 Data',
        'go_btn': 'Vai',
        'today_btn': 'Oggi',
        'random_fact': 'Clicca per un fatto storico casuale!',
        'random_btn': '🎲 Fatto casuale',
        'quiz_label': '📝 QUIZ',
        'quiz_ready': 'Pronto a testare le tue conoscenze storiche?',
        'quiz_new': '📚 Nuovo quiz',
        'quiz_not_enough': 'Non ci sono abbastanza eventi per un quiz oggi! 😅',
        'quiz_question': '❓ Cosa è successo nel',
        'quiz_correct': '✅ Corretto! Ben fatto! 🎉',
        'quiz_wrong': '❌ Sbagliato! Corretto:',
        'quiz_score': '🏆 Punteggio:',
        'favorites_label': '⭐ Preferiti',
        'events_label': '🔥 Eventi storici',
        'births_label': '🎂 Nati in questo giorno',
        'deaths_label': '🕊️ Morti in questo giorno',
        'no_events': 'Nessun evento per questa data',
        'error_loading': '❌ Errore nel caricamento',
        'retry_btn': 'Riprova',
        'share_all': '📤 Condividi tutto',
        'share_today': '📅 Condividi oggi',
        'refresh_btn': '⟳ Aggiorna',
        'footer': 'Fatto con ❤️ • Wikipedia',
        'loading': 'Caricamento della storia...',
        'no_facts': 'Nessun fatto disponibile per questa data!'
    },
    'pt': {
        'name': 'Português',
        'app_title': '📜 Hoje na História',
        'subtitle': 'Neste dia',
        'date_label': '📅 Data',
        'go_btn': 'Ir',
        'today_btn': 'Hoje',
        'random_fact': 'Clique para um fato histórico aleatório!',
        'random_btn': '🎲 Fato aleatório',
        'quiz_label': '📝 QUIZ',
        'quiz_ready': 'Pronto para testar seus conhecimentos históricos?',
        'quiz_new': '📚 Novo quiz',
        'quiz_not_enough': 'Não há eventos suficientes para um quiz hoje! 😅',
        'quiz_question': '❓ O que aconteceu em',
        'quiz_correct': '✅ Correto! Muito bem! 🎉',
        'quiz_wrong': '❌ Errado! Correto:',
        'quiz_score': '🏆 Pontuação:',
        'favorites_label': '⭐ Favoritos',
        'events_label': '🔥 Eventos históricos',
        'births_label': '🎂 Nascidos neste dia',
        'deaths_label': '🕊️ Mortos neste dia',
        'no_events': 'Nenhum evento para esta data',
        'error_loading': '❌ Erro ao carregar',
        'retry_btn': 'Tentar novamente',
        'share_all': '📤 Compartilhar tudo',
        'share_today': '📅 Compartilhar hoje',
        'refresh_btn': '⟳ Atualizar',
        'footer': 'Feito com ❤️ • Wikipedia',
        'loading': 'Carregando história...',
        'no_facts': 'Nenhum fato disponível para esta data!'
    },
    'ru': {
        'name': 'Русский',
        'app_title': '📜 Сегодня в истории',
        'subtitle': 'В этот день',
        'date_label': '📅 Дата',
        'go_btn': 'Перейти',
        'today_btn': 'Сегодня',
        'random_fact': 'Нажмите для случайного исторического факта!',
        'random_btn': '🎲 Случайный факт',
        'quiz_label': '📝 ВИКТОРИНА',
        'quiz_ready': 'Готовы проверить свои знания истории?',
        'quiz_new': '📚 Новая викторина',
        'quiz_not_enough': 'Недостаточно событий для викторины сегодня! 😅',
        'quiz_question': '❓ Что произошло в',
        'quiz_correct': '✅ Правильно! Отлично! 🎉',
        'quiz_wrong': '❌ Неправильно! Правильно:',
        'quiz_score': '🏆 Счет:',
        'favorites_label': '⭐ Избранное',
        'events_label': '🔥 Исторические события',
        'births_label': '🎂 Родились в этот день',
        'deaths_label': '🕊️ Умерли в этот день',
        'no_events': 'Нет событий для этой даты',
        'error_loading': '❌ Ошибка загрузки',
        'retry_btn': 'Повторить',
        'share_all': '📤 Поделиться всем',
        'share_today': '📅 Поделиться сегодня',
        'refresh_btn': '⟳ Обновить',
        'footer': 'Сделано с ❤️ • Wikipedia',
        'loading': 'Загрузка истории...',
        'no_facts': 'Нет фактов для этой даты!'
    },
    'ja': {
        'name': '日本語',
        'app_title': '📜 今日の歴史',
        'subtitle': 'この日',
        'date_label': '📅 日付',
        'go_btn': '表示',
        'today_btn': '今日',
        'random_fact': 'ランダムな歴史的事実をクリック！',
        'random_btn': '🎲 ランダムな事実',
        'quiz_label': '📝 クイズ',
        'quiz_ready': '歴史の知識を試す準備はできましたか？',
        'quiz_new': '📚 新しいクイズ',
        'quiz_not_enough': '今日はクイズに十分なイベントがありません！ 😅',
        'quiz_question': '❓ 何が起こったか',
        'quiz_correct': '✅ 正解！お見事！ 🎉',
        'quiz_wrong': '❌ 間違い！正解は：',
        'quiz_score': '🏆 スコア：',
        'favorites_label': '⭐ お気に入り',
        'events_label': '🔥 歴史的な出来事',
        'births_label': '🎂 この日に生まれた人',
        'deaths_label': '🕊️ この日に亡くなった人',
        'no_events': 'この日付のイベントはありません',
        'error_loading': '❌ 読み込みエラー',
        'retry_btn': '再試行',
        'share_all': '📤 すべて共有',
        'share_today': '📅 今日を共有',
        'refresh_btn': '⟳ 更新',
        'footer': '❤️ で作られた • Wikipedia',
        'loading': '履歴を読み込んでいます...',
        'no_facts': 'この日付の事実はありません！'
    },
    'zh': {
        'name': '中文',
        'app_title': '📜 历史上的今天',
        'subtitle': '在这一天',
        'date_label': '📅 日期',
        'go_btn': '前往',
        'today_btn': '今天',
        'random_fact': '点击获取随机历史事实！',
        'random_btn': '🎲 随机事实',
        'quiz_label': '📝 测验',
        'quiz_ready': '准备好测试你的历史知识了吗？',
        'quiz_new': '📚 新测验',
        'quiz_not_enough': '今天的活动不足以进行测验！ 😅',
        'quiz_question': '❓ 发生了什么',
        'quiz_correct': '✅ 正确！做得好！ 🎉',
        'quiz_wrong': '❌ 错误！正确：',
        'quiz_score': '🏆 分数：',
        'favorites_label': '⭐ 收藏',
        'events_label': '🔥 历史事件',
        'births_label': '🎂 今天出生',
        'deaths_label': '🕊️ 今天去世',
        'no_events': '此日期没有活动',
        'error_loading': '❌ 加载错误',
        'retry_btn': '重试',
        'share_all': '📤 分享全部',
        'share_today': '📅 分享今天',
        'refresh_btn': '⟳ 刷新',
        'footer': '用 ❤️ 制作 • Wikipedia',
        'loading': '正在加载历史...',
        'no_facts': '此日期没有可用的事实！'
    }
}# ===== NOTIFICATION SYSTEM =====
subscriptions = {}

def send_daily_notification():
    today = datetime.now()
    month = today.month
    day = today.day
    
    events_list = []
    try:
        url = f"https://api.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for e in r.json().get('events', [])[:3]:
                events_list.append({
                    'year': str(e.get('year', '?')),
                    'text': re.sub(r'<[^>]+>', '', e.get('text', ''))[:100]
                })
    except:
        pass
    
    if not events_list:
        events_list = [
            {'year': '1914', 'text': 'World War I began'},
            {'year': '1945', 'text': 'Empire State Building crash'},
            {'year': '1976', 'text': 'Tangshan earthquake'}
        ]
    
    message = f"📜 Today in History ({today.strftime('%B %d')})\n\n"
    for e in events_list[:3]:
        message += f"• {e['year']}: {e['text']}\n"
    message += f"\n📱 Open app for more: {os.environ.get('APP_URL', 'https://history-app-z99b.onrender.com')}"
    
    print(f"📨 NOTIFICATION: {message}")
    return message

scheduler = BackgroundScheduler()
scheduler.add_job(func=send_daily_notification, trigger=CronTrigger(hour=8, minute=0))
scheduler.start()

# ===== ROUTES =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/languages')
def get_languages():
    return jsonify(LANGUAGES)

@app.route('/api/events')
def get_events():
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)
    
    if not month or not day:
        now = datetime.now()
        month = now.month
        day = now.day
    
    events_list, births_list, deaths_list = [], [], []
    
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

@app.route('/api/notification/subscribe', methods=['POST'])
def subscribe_notification():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    time = data.get('time', '08:00')
    subscriptions[user_id] = {'time': time, 'active': True}
    return jsonify({'status': 'subscribed', 'message': 'You will receive daily notifications!'})

@app.route('/api/notification/unsubscribe', methods=['POST'])
def unsubscribe_notification():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    if user_id in subscriptions:
        subscriptions[user_id]['active'] = False
    return jsonify({'status': 'unsubscribed', 'message': 'You have unsubscribed from notifications.'})

@app.route('/api/notification/status')
def notification_status():
    user_id = request.args.get('user_id', 'anonymous')
    is_active = user_id in subscriptions and subscriptions[user_id].get('active', False)
    time = subscriptions.get(user_id, {}).get('time', '08:00') if is_active else None
    return jsonify({'active': is_active, 'time': time})

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'History API is running!'})# ===== ARTICLE ROUTE =====
@app.route('/api/article')
def get_article():
    """Get article about a historical event using AI"""
    query = request.args.get('title', '')
    if not query:
        return jsonify({'error': 'No title provided'}), 400
    
    # Extract year
    year_match = re.search(r'\b(\d{4})\b', query)
    year = year_match.group(1) if year_match else None
    
    # ===== SOURCE 1: Try DeepSeek AI =====
    try:
        # Get API key from environment
        deepseek_key = os.environ.get('sk-2d594d1ee9d44f5d89ba5e49427097db')
        
        if deepseek_key:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json"
            }
            
            # Clean the query for better AI results
            clean_query = re.sub(r'[^\w\s]', '', query)
            clean_query = ' '.join(clean_query.split())
            
            prompt = f"""Write a short, engaging article about {clean_query} for a "Today in History" mobile app.

The article should:
- Be 100-150 words long
- Include key historical facts
- Be written in a clear, engaging style
- End with an interesting fact

Write the article in English:"""

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful historian writing engaging articles for a mobile app."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 400
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                article = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                if article:
                    return jsonify({
                        'title': f"📜 {clean_query}",
                        'extract': article,
                        'full_text': article,
                        'url': '',
                        'thumbnail': '',
                        'source': 'deepseek_ai'
                    })
    except Exception as e:
        print(f"DeepSeek AI error: {e}")
    
    # ===== SOURCE 2: Fallback to Wikipedia Year =====
    if year:
        try:
            page_title = year
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
            summary_resp = requests.get(summary_url, timeout=5)
            
            if summary_resp.status_code == 200:
                summary_data = summary_resp.json()
                extract = summary_data.get('extract', '')
                
                keywords = query.replace(str(year), '').strip().split()
                matched_sentence = ''
                
                if extract:
                    sentences = extract.split('.')
                    for sentence in sentences[:10]:
                        for word in keywords[:3]:
                            if len(word) > 3 and word.lower() in sentence.lower():
                                matched_sentence = sentence.strip() + '.'
                                break
                        if matched_sentence:
                            break
                
                if matched_sentence:
                    display_text = f"📅 **In {year}:** {matched_sentence}\n\n📖 From the Wikipedia article about {year}."
                else:
                    display_text = f"📅 **{query}**\n\n📖 From the Wikipedia article about {year}:\n\n{extract[:500]}..."
                
                return jsonify({
                    'title': f'Year {year}',
                    'extract': display_text,
                    'full_text': extract,
                    'url': f'https://en.wikipedia.org/wiki/{year}',
                    'thumbnail': summary_data.get('thumbnail', {}).get('source', ''),
                    'source': 'wikipedia_year'
                })
        except:
            pass
    
    # ===== SOURCE 3: Final Fallback =====
    if year:
        return jsonify({
            'title': f'About {year}',
            'extract': f"📜 **{query}**\n\n🔗 Read more: https://en.wikipedia.org/wiki/{year}\n\n💡 This event happened in {year}. Click the link above for more details.",
            'full_text': query,
            'url': f'https://en.wikipedia.org/wiki/{year}',
            'thumbnail': '',
            'source': 'fallback'
        })
    
    return jsonify({
        'title': 'Historical Event',
        'extract': f"📜 **{query}**\n\n💡 Try searching on Wikipedia:\nhttps://en.wikipedia.org/w/index.php?search={query.replace(' ', '+')}",
        'full_text': query,
        'url': f"https://en.wikipedia.org/w/index.php?search={query.replace(' ', '+')}",
        'thumbnail': '',
        'source': 'fallback_final'
    })
# ===== START SERVER =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
