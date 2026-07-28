from flask import Flask, request, jsonify, render_template_string
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

# ===== HTML TEMPLATE (with Multi-Language!) =====
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

        .lang-selector {
            background: #0a0a0a;
            border-radius: 12px;
            padding: 12px 20px;
            margin-bottom: 22px;
            border: 1px solid rgba(255, 215, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        .lang-selector label {
            color: #FFD700;
            font-weight: 700;
            font-size: 0.85em;
            letter-spacing: 2px;
        }
        .lang-selector select {
            flex: 1;
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid rgba(255, 215, 0, 0.2);
            background: #1a1a1a;
            color: #ffffff;
            font-size: 0.95em;
            cursor: pointer;
            min-width: 120px;
        }
        .lang-selector select:focus {
            outline: none;
            border-color: #FFD700;
        }
        .lang-selector .lang-flag {
            font-size: 1.4em;
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
            flex: 1;
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

        .quiz-container {
            margin-top: 16px;
            border-top: 1px solid rgba(255,215,0,0.1);
            padding-top: 16px;
        }
        .quiz-container .quiz-label {
            color: #FFD700;
            font-weight: 700;
            font-size: 0.85em;
            display: block;
            margin-bottom: 10px;
        }
        .quiz-container .quiz-question {
            font-size: 1em;
            color: #ffffff;
            margin-bottom: 10px;
        }
        .quiz-container .quiz-options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .quiz-container .quiz-options button {
            padding: 10px 12px;
            background: rgba(255,215,0,0.05);
            border: 1px solid rgba(255,215,0,0.15);
            border-radius: 8px;
            color: #ffffff;
            font-size: 0.8em;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            font-family: inherit;
        }
        .quiz-container .quiz-options button:hover {
            background: rgba(255,215,0,0.15);
        }
        .quiz-container .quiz-options button.correct {
            background: rgba(0,255,0,0.2);
            border-color: #00ff00;
        }
        .quiz-container .quiz-options button.wrong {
            background: rgba(255,0,0,0.2);
            border-color: #ff0000;
        }
        .quiz-container .quiz-result {
            margin-top: 10px;
            font-weight: 600;
            font-size: 0.95em;
            min-height: 1.5em;
        }
        .quiz-container .quiz-result.correct { color: #00ff00; }
        .quiz-container .quiz-result.wrong { color: #ff6b6b; }
        .quiz-container .quiz-stats {
            margin-top: 10px;
            font-size: 0.85em;
            color: #FFD700;
            text-align: center;
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

        .share-section {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        .share-btn {
            flex: 1;
            padding: 12px;
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.15);
            border-radius: 8px;
            color: #FFD700;
            font-size: 0.85em;
            cursor: pointer;
            text-align: center;
            font-weight: 600;
        }
        .share-btn:hover { background: rgba(255, 215, 0, 0.15); }

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
            .quiz-container .quiz-options {
                grid-template-columns: 1fr 1fr;
            }
            .lang-selector { flex-direction: column; align-items: stretch; }
        }
        @media (max-width: 380px) {
            .quiz-container .quiz-options {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="lang-selector">
            <span class="lang-flag">🌍</span>
            <label for="langSelect">Language</label>
            <select id="langSelect" onchange="changeLanguage(this.value)">
                <option value="en">🇬🇧 English</option>
                <option value="hr">🇭🇷 Hrvatski</option>
                <option value="es">🇪🇸 Español</option>
                <option value="de">🇩🇪 Deutsch</option>
            </select>
        </div>

        <div class="header">
            <h1 id="appTitle">📜 Today in History</h1>
            <div class="date" id="headerDate">Loading...</div>
        </div>

        <div class="date-picker">
            <label id="dateLabel">📅 Date</label>
            <input type="date" id="dateInput">
            <button class="go-btn" id="goBtn" onclick="goToDate()">Go</button>
            <button class="today-btn" id="todayBtn" onclick="goToday()">Today</button>
        </div>

        <div class="fact-card">
            <div class="fact-text" id="factText">Click for a random fact!</div>
            <button class="fact-btn" id="randomBtn" onclick="getRandomFact()">🎲 Random Fact</button>
            
            <div class="quiz-container">
                <span class="quiz-label" id="quizLabel">📝 QUIZ TIME</span>
                <div class="quiz-question" id="quizQuestion">Ready to test your history knowledge?</div>
                <div class="quiz-options" id="quizOptions"></div>
                <div class="quiz-result" id="quizResult"></div>
                <div class="quiz-stats" id="quizStats">🏆 Quiz Score: 0</div>
                <button class="fact-btn" id="quizNewBtn" onclick="generateQuiz()" style="margin-top:8px;">📚 New Quiz</button>
            </div>
        </div>

        <div class="card" id="favoritesCard" style="display:none;">
            <div class="card-header">
                <h2 id="favoritesLabel">⭐ Favorites</h2>
                <span class="badge" id="favCount">0</span>
            </div>
            <div id="favoritesList"></div>
        </div>

        <div id="content">
            <div class="loading-state">
                <div class="spinner"></div>
                <p id="loadingText">Loading history...</p>
            </div>
        </div>

        <div class="share-section">
            <button class="share-btn" id="shareAllBtn" onclick="shareAll()">📤 Share All</button>
            <button class="share-btn" id="shareTodayBtn" onclick="shareToday()">📅 Share Today</button>
        </div>

        <button class="refresh-btn" id="refreshBtn" onclick="loadEvents()">⟳ Refresh</button>

        <div class="footer" id="footerText">Built with ❤️ • Wikipedia</div>
    </div>

    <script>
        // ===== LANGUAGE SUPPORT =====
        let currentLang = localStorage.getItem('historyLang') || 'en';
        let translations = {};

        async function loadTranslations() {
            try {
                const response = await fetch('/api/languages');
                const data = await response.json();
                translations = data;
                return data;
            } catch (e) {
                console.error('Error loading translations:', e);
                return {};
            }
        }

        function changeLanguage(lang) {
            currentLang = lang;
            localStorage.setItem('historyLang', lang);
            document.getElementById('langSelect').value = lang;
            updateUI();
            loadEvents();
        }

        function getText(key) {
            if (translations[currentLang] && translations[currentLang][key]) {
                return translations[currentLang][key];
            }
            if (translations['en'] && translations['en'][key]) {
                return translations['en'][key];
            }
            return key;
        }

        function updateUI() {
            document.querySelectorAll('[data-lang]').forEach(el => {
                const key = el.getAttribute('data-lang');
                el.textContent = getText(key);
            });
            
            document.getElementById('appTitle').textContent = getText('app_title');
            document.getElementById('dateLabel').textContent = getText('date_label');
            document.getElementById('goBtn').textContent = getText('go_btn');
            document.getElementById('todayBtn').textContent = getText('today_btn');
            document.getElementById('randomBtn').innerHTML = getText('random_btn');
            document.getElementById('quizLabel').textContent = getText('quiz_label');
            document.getElementById('quizNewBtn').textContent = getText('quiz_new');
            document.getElementById('favoritesLabel').textContent = getText('favorites_label');
            document.getElementById('shareAllBtn').textContent = getText('share_all');
            document.getElementById('shareTodayBtn').textContent = getText('share_today');
            document.getElementById('refreshBtn').textContent = getText('refresh_btn');
            document.getElementById('footerText').textContent = getText('footer');
            document.getElementById('loadingText').textContent = getText('loading');
        }

        // ===== STATE =====
        let currentEvents = [];
        let currentQuiz = null;
        let quizAnswered = false;
        let favorites = JSON.parse(localStorage.getItem('historyFavorites') || '[]');

        // ===== UTILITY =====
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

        function isFavorited(year, text) {
            return favorites.some(f => f.year === year && f.text === text);
        }

        function toggleFavorite(year, text, type) {
            const index = favorites.findIndex(f => f.year === year && f.text === text);
            if (index > -1) {
                favorites.splice(index, 1);
            } else {
                favorites.push({ year, text, type, date: new Date().toISOString() });
            }
            localStorage.setItem('historyFavorites', JSON.stringify(favorites));
            renderFavorites();
            loadEvents();
        }

        function renderFavorites() {
            const card = document.getElementById('favoritesCard');
            const list = document.getElementById('favoritesList');
            const count = document.getElementById('favCount');
            
            if (favorites.length === 0) {
                card.style.display = 'none';
                return;
            }
            card.style.display = 'block';
            count.textContent = favorites.length;
            
            let html = '';
            favorites.forEach(f => {
                html += `
                    <div class="event-item">
                        <span class="event-year">${f.year}</span>
                        <span class="event-text">${f.text}</span>
                        <button onclick="removeFavorite('${f.year}', '${f.text.replace(/'/g, "\\\\'")}')" 
                                style="background:none;border:none;color:#ff6b6b;font-size:1.2em;cursor:pointer;padding:0 8px;">✕</button>
                    </div>
                `;
            });
            list.innerHTML = html;
        }

        function removeFavorite(year, text) {
            favorites = favorites.filter(f => !(f.year === year && f.text === text));
            localStorage.setItem('historyFavorites', JSON.stringify(favorites));
            renderFavorites();
            loadEvents();
        }

        // ===== LOAD EVENTS =====
        async function loadEvents() {
            const date = getDateFromInput();
            const month = date.getMonth() + 1;
            const day = date.getDate();
            
            document.getElementById('headerDate').innerHTML = formatDate(date);
            
            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>${getText('loading')}</p>
                </div>
            `;

            try {
                const response = await fetch(`/api/events?month=${month}&day=${day}`);
                const data = await response.json();
                currentEvents = data;
                let html = '';

                if (data.events && data.events.length > 0) {
                    html += `
                        <div class="card">
                            <div class="card-header">
                                <h2>${getText('events_label')}</h2>
                                <span class="badge">${data.events.length}</span>
                            </div>
                    `;
                    data.events.forEach(e => {
                        const fav = isFavorited(e.year, e.text);
                        html += `
                            <div class="event-item">
                                <span class="event-year">${e.year}</span>
                                <span class="event-text">${e.text}</span>
                                <button onclick="toggleFavorite('${e.year}', '${e.text.replace(/'/g, "\\\\'")}', 'event')"
                                        style="background:none;border:none;color:${fav ? '#FFD700' : '#555'};font-size:1.2em;cursor:pointer;padding:0 8px;">
                                    ${fav ? '⭐' : '☆'}
                                </button>
                            </div>
                        `;
                    });
                    html += `</div>`;
                }

                if (data.births && data.births.length > 0) {
                    html += `
                        <div class="card">
                            <div class="card-header">
                                <h2>${getText('births_label')}</h2>
                                <span class="badge">${data.births.length}</span>
                            </div>
                    `;
                    data.births.forEach(e => {
                        const fav = isFavorited(e.year, e.text);
                        html += `
                            <div class="event-item">
                                <span class="event-year">${e.year}</span>
                                <span class="event-text">${e.text}</span>
                                <button onclick="toggleFavorite('${e.year}', '${e.text.replace(/'/g, "\\\\'")}', 'birth')"
                                        style="background:none;border:none;color:${fav ? '#FFD700' : '#555'};font-size:1.2em;cursor:pointer;padding:0 8px;">
                                    ${fav ? '⭐' : '☆'}
                                </button>
                            </div>
                        `;
                    });
                    html += `</div>`;
                }

                if (data.deaths && data.deaths.length > 0) {
                    html += `
                        <div class="card">
                            <div class="card-header">
                                <h2>${getText('deaths_label')}</h2>
                                <span class="badge">${data.deaths.length}</span>
                            </div>
                    `;
                    data.deaths.forEach(e => {
                        const fav = isFavorited(e.year, e.text);
                        html += `
                            <div class="event-item">
                                <span class="event-year">${e.year}</span>
                                <span class="event-text">${e.text}</span>
                                <button onclick="toggleFavorite('${e.year}', '${e.text.replace(/'/g, "\\\\'")}', 'death')"
                                        style="background:none;border:none;color:${fav ? '#FFD700' : '#555'};font-size:1.2em;cursor:pointer;padding:0 8px;">
                                    ${fav ? '⭐' : '☆'}
                                </button>
                            </div>
                        `;
                    });
                    html += `</div>`;
                }

                if (!html) {
                    html = `
                        <div class="card" style="text-align:center;padding:40px 20px;">
                            <p style="color:#888888;">${getText('no_events')}</p>
                        </div>
                    `;
                }

                content.innerHTML = html;
                renderFavorites();
                setTimeout(generateQuiz, 500);
            } catch (err) {
                content.innerHTML = `
                    <div class="card" style="text-align:center;padding:40px 20px;">
                        <p style="color:#ff6b6b;">${getText('error_loading')}</p>
                        <p style="color:#666;font-size:0.8em;">${err.message}</p>
                        <button onclick="loadEvents()" style="margin-top:12px;padding:8px 20px;background:#FFD700;border:none;border-radius:6px;color:#000;font-weight:bold;cursor:pointer;">${getText('retry_btn')}</button>
                    </div>
                `;
            }
        }

        // ===== DATE FUNCTIONS =====
        function goToDate() {
            loadEvents();
        }

        function goToday() {
            const today = new Date();
            document.getElementById('dateInput').value = today.toISOString().split('T')[0];
            loadEvents();
        }

        // ===== RANDOM FACT =====
        function getRandomFact() {
            const allEvents = [];
            if (currentEvents.events) allEvents.push(...currentEvents.events.map(e => ({...e, type: 'event'})));
            if (currentEvents.births) allEvents.push(...currentEvents.births.map(e => ({...e, type: 'birth'})));
            if (currentEvents.deaths) allEvents.push(...currentEvents.deaths.map(e => ({...e, type: 'death'})));
            
            if (allEvents.length === 0) {
                document.getElementById('factText').innerHTML = getText('no_facts');
                return;
            }
            
            const random = allEvents[Math.floor(Math.random() * allEvents.length)];
            const emojis = { event: '🔥', birth: '🎂', death: '🕊️' };
            document.getElementById('factText').innerHTML = 
                `${emojis[random.type] || '📜'} <span style="color:#FFD700;">${random.year}</span> — ${random.text}`;
        }

        // ===== QUIZ FEATURE =====
        function generateQuiz() {
            const allEvents = [];
            if (currentEvents.events) allEvents.push(...currentEvents.events.map(e => ({...e, type: 'event'})));
            if (currentEvents.births) allEvents.push(...currentEvents.births.map(e => ({...e, type: 'birth'})));
            if (currentEvents.deaths) allEvents.push(...currentEvents.deaths.map(e => ({...e, type: 'death'})));
            
            if (allEvents.length < 4) {
                document.getElementById('quizQuestion').innerHTML = getText('quiz_not_enough');
                document.getElementById('quizOptions').innerHTML = '';
                document.getElementById('quizResult').innerHTML = '';
                return;
            }

            const correct = allEvents[Math.floor(Math.random() * allEvents.length)];
            const wrongs = allEvents.filter(e => e.year !== correct.year);
            const shuffledWrongs = wrongs.sort(() => Math.random() - 0.5).slice(0, 3);
            
            while (shuffledWrongs.length < 3) {
                const sampleYears = ['1776', '1865', '1941', '1969', '1492', '1789'];
                const sampleTexts = ['Declaration of Independence', 'Civil War ended', 'Pearl Harbor attack', 'Moon landing', 'Columbus arrived', 'French Revolution'];
                const idx = shuffledWrongs.length;
                shuffledWrongs.push({
                    year: sampleYears[idx % sampleYears.length],
                    text: sampleTexts[idx % sampleTexts.length],
                    type: 'event'
                });
            }
            
            const options = [correct, ...shuffledWrongs].sort(() => Math.random() - 0.5);
            currentQuiz = { correct, options };
            quizAnswered = false;
            
            document.getElementById('quizQuestion').innerHTML = 
                `${getText('quiz_question')} <strong>${correct.year}</strong>?`;
            
            const optionsContainer = document.getElementById('quizOptions');
            optionsContainer.innerHTML = '';
            options.forEach((option) => {
                const btn = document.createElement('button');
                btn.text
