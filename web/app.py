# web/app.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, jsonify, send_file
import numpy as np
import io
import wave as wave_module

from core.interval_calculator import Note
from core.constants import NoteName
from language.primitives import SemanticPrimitives
from language.descriptors import DescriptorGrammar

app = Flask(__name__)
primitives = SemanticPrimitives()
descriptors = DescriptorGrammar()

SAMPLE_RATE = 44100


def generate_wave(frequency, duration_ms, volume=0.3):
    num_samples = int(SAMPLE_RATE * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms / 1000.0, num_samples, False)
    wave_data = (
            np.sin(2 * np.pi * frequency * t) * 1.0 +
            np.sin(2 * np.pi * frequency * 2 * t) * 0.5 +
            np.sin(2 * np.pi * frequency * 3 * t) * 0.25 +
            np.sin(2 * np.pi * frequency * 4 * t) * 0.125
    )
    decay = np.exp(-3.0 * t / (duration_ms / 1000.0))
    wave_data *= decay
    attack = int(num_samples * 0.01)
    release = int(num_samples * 0.05)
    envelope = np.ones(num_samples)
    if attack > 1:
        envelope[:attack] = np.linspace(0, 1, attack)
    if release > 1:
        envelope[-release:] = np.linspace(1, 0, release)
    return (wave_data * envelope * volume).astype(np.float32)


def generate_word_wav(notes, speed=1.0):
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, note in enumerate(notes):
        dur = base_duration if i < len(notes) - 1 else int(600 / speed)
        w = generate_wave(note.to_frequency(), dur)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


HTML = r"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolRes — Universal Musical Language</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #020210;
            --accent: #ff6a00;
            --accent2: #ff9500;
            --accent-glow: rgba(255,106,0,0.4);
            --surface: rgba(12,12,32,0.85);
            --surface2: rgba(20,20,50,0.9);
            --green: #00e676;
            --text: #d0d0e0;
            --muted: #707090;
            --red: #ff4757;
            --radius: 16px;
            --transition: 0.2s ease;
        }
        .light-theme {
            --bg: #f5f0e8;
            --accent: #7c3aed;
            --accent2: #a78bfa;
            --accent-glow: rgba(124,58,237,0.3);
            --surface: rgba(255,255,255,0.85);
            --surface2: rgba(240,235,225,0.9);
            --text: #1a1a2e;
            --muted: #6a6a7a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
            transition: background 0.5s ease, color 0.5s ease;
        }
        #starfield { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
        .container { max-width: 800px; margin: 0 auto; position: relative; z-index: 1; }
        header { text-align: center; margin-bottom: 24px; }
        .logo {
            font-size: 2.8em; font-weight: 700; letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent2), var(--accent));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .subtitle { color: var(--muted); font-size: 0.9em; font-weight: 300; margin-top: 4px; }
        .top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
        .stats { display: flex; gap: 20px; font-size: 0.8em; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
        .stats span { color: var(--accent); font-weight: 600; font-size: 1.1em; }
        .theme-toggle {
            background: var(--surface2); border: 1px solid rgba(255,255,255,0.08);
            color: var(--text); padding: 8px 16px; border-radius: 20px;
            cursor: pointer; font-size: 0.85em; font-family: inherit;
        }
        .tabs { display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap; }
        .tab {
            padding: 10px 18px; border-radius: 12px 12px 0 0;
            background: var(--surface2); color: var(--muted);
            cursor: pointer; font-size: 0.9em; font-weight: 500;
            border: none; font-family: inherit; transition: all var(--transition);
        }
        .tab.active { background: var(--surface); color: var(--accent); font-weight: 600; }
        .tab:hover { color: var(--text); }
        .card {
            background: var(--surface); border: 1px solid rgba(255,255,255,0.04);
            border-radius: 0 0 var(--radius) var(--radius); padding: 24px;
            backdrop-filter: blur(10px);
        }
        .search-row { display: flex; gap: 10px; margin-bottom: 16px; }
        input, select {
            padding: 10px 14px; font-size: 14px; border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.06);
            background: var(--surface2); color: var(--text); font-family: inherit;
        }
        .light-theme input, .light-theme select { border-color: rgba(0,0,0,0.1); }
        input:focus, select:focus { border-color: var(--accent); outline: none; }
        input::placeholder { color: #505070; }
        select { cursor: pointer; max-height: 200px; }
        .btn {
            padding: 10px 18px; font-size: 14px; border-radius: 8px;
            border: none; cursor: pointer; font-weight: 600; font-family: inherit;
        }
        .btn-primary { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #000; }
        .btn-primary:hover { box-shadow: 0 6px 20px var(--accent-glow); }
        .btn-sm {
            padding: 5px 10px; font-size: 0.75em; border-radius: 6px;
            background: var(--surface2); color: var(--accent);
            border: 1px solid rgba(255,255,255,0.05); cursor: pointer; font-family: inherit;
        }
        .btn-sm:hover { border-color: var(--accent); }
        .notes-display {
            font-size: 1.4em; font-weight: 600; letter-spacing: 2px; text-align: center;
            padding: 12px; background: var(--surface2); border-radius: 10px;
            color: var(--accent2); word-break: break-all; font-family: 'Courier New', monospace;
            margin-top: 10px;
        }
        .desc-row { font-size: 0.85em; color: var(--muted); text-align: center; margin-top: 10px; }
        .desc-row span { display: inline-block; background: var(--surface2); padding: 3px 8px; border-radius: 14px; margin: 2px; }
        .meaning { text-align: center; margin-top: 8px; color: var(--green); font-weight: 500; }
        .speed-row { display: flex; align-items: center; gap: 10px; justify-content: center; margin-top: 14px; color: var(--muted); font-size: 0.85em; }
        .speed-row input[type=range] { width: 100px; accent-color: var(--accent); }
        audio { width: 100%; margin-top: 10px; border-radius: 8px; }
        .error-msg {
            background: rgba(255,71,87,0.1); border: 1px solid rgba(255,71,87,0.3);
            color: var(--red); padding: 12px; border-radius: 10px; font-size: 0.85em;
            margin-top: 12px; text-align: center;
        }
        .compose-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 16px;
        }
        .compose-row {
            display: flex; align-items: center; gap: 8px;
            padding: 6px 0;
        }
        .compose-row .cat-label {
            width: 90px; font-size: 0.7em; color: var(--muted);
            text-transform: uppercase; letter-spacing: 0.5px; text-align: right;
        }
        .compose-row select {
            flex: 1; min-width: 120px;
        }
        .compose-row.invalid select {
            border-color: var(--red) !important;
        }
        .compose-buttons {
            display: flex; gap: 10px; margin-top: 16px; justify-content: center;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.85em; margin-top: 10px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.04); }
        th { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75em; letter-spacing: 1px; }
        .table-wrap { max-height: 400px; overflow-y: auto; border-radius: 10px; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; background: var(--accent-glow); color: var(--accent2); }
        .rules-list { list-style: none; padding: 0; }
        .rules-list li { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); line-height: 1.6; }
        .rules-list li:last-child { border-bottom: none; }
        .rules-list strong { color: var(--accent); }
        .rules-list em { color: var(--muted); font-style: normal; font-size: 0.9em; }
        @media (max-width: 600px) {
            .logo { font-size: 2em; }
            .compose-grid { grid-template-columns: 1fr; }
            .search-row { flex-direction: column; }
            .btn { width: 100%; }
            .tabs { flex-wrap: wrap; }
            .tab { font-size: 0.75em; padding: 8px 10px; }
        }
    </style>
</head>
<body>
    <canvas id="starfield"></canvas>

    <div class="container">
        <header>
            <div class="logo">🎵 SolRes</div>
            <p class="subtitle">Universal musical language — describe the world with sound</p>
        </header>

        <div class="top-row">
            <div class="stats">
                <div>Primitives <span>{{ primitives_count }}</span></div>
                <div>Words <span>{{ descriptions_count }}</span></div>
            </div>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀️ Light</button>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('translate')">🔍 Translate</button>
            <button class="tab" onclick="switchTab('compose')">🧩 Compose</button>
            <button class="tab" onclick="switchTab('dictionary')">📖 Dictionary</button>
            <button class="tab" onclick="switchTab('rules')">📋 Rules</button>
        </div>

        <!-- TAB: Translate -->
        <div class="card" id="tab-translate">
            <div class="search-row">
                <input type="text" id="wordInput" placeholder="Enter a word: sun, вода, love, кошка..." 
                       onkeypress="if(event.key==='Enter') translateWord()" />
                <button class="btn btn-primary" onclick="translateWord()">🔍 Translate</button>
            </div>
            <div id="result">
                <div style="text-align:center;color:var(--muted);opacity:0.5;">Type a word to see its description and hear its melody</div>
            </div>
            <div class="speed-row">
                <span>🐢</span>
                <input type="range" id="speedSlider" min="0.5" max="2.5" step="0.1" value="1.0" 
                       oninput="updateSpeed(); playAudio()">
                <span>🐇</span>
                <span id="speedLabel" style="color:var(--accent);font-weight:600;">1.0x</span>
            </div>
            <audio id="audioPlayer" controls style="display:none"></audio>
        </div>

        <!-- TAB: Compose -->
        <div class="card" id="tab-compose" style="display:none;">
            <div class="compose-grid" id="composeGrid"></div>
            <div class="compose-buttons">
                <button class="btn btn-primary" onclick="composePlay()">▶ Play</button>
                <button class="btn btn-sm" onclick="composeRandom()">✨ Random</button>
                <button class="btn btn-sm" onclick="composeClear()">✕ Clear</button>
            </div>
            <div id="composeError"></div>
            <div id="composeResult"></div>
            <audio id="composeAudio" controls style="display:none;width:100%;margin-top:10px;"></audio>
        </div>

        <!-- TAB: Dictionary -->
        <div class="card" id="tab-dictionary" style="display:none;">
            <div class="search-row">
                <input type="text" id="dictSearch" placeholder="Search primitives & words..." oninput="filterDict()" />
            </div>
            <h3 style="margin:12px 0 8px;color:var(--accent);">🔤 Primitives <span style="color:var(--muted);font-weight:400;">({{ primitives_count }})</span></h3>
            <div class="table-wrap">
                <table id="primitivesTable">
                    <thead><tr><th>Category</th><th>RU</th><th>EN</th><th>Pattern</th></tr></thead>
                    <tbody>{{ primitives_rows | safe }}</tbody>
                </table>
            </div>
            <h3 style="margin:16px 0 8px;color:var(--accent);">📝 Words <span style="color:var(--muted);font-weight:400;">({{ descriptions_count }})</span></h3>
            <div class="table-wrap">
                <table id="wordsTable">
                    <thead><tr><th>Word</th><th>EN</th><th>Description</th><th style="width:24px;"></th></tr></thead>
                    <tbody>{{ words_rows | safe }}</tbody>
                </table>
            </div>
        </div>

        <!-- TAB: Rules -->
        <div class="card" id="tab-rules" style="display:none;">
            <h3 style="color:var(--accent);margin-bottom:12px;">📋 Rules of SolRes</h3>
            <ol class="rules-list">
                <li><strong>Alphabet:</strong> 7 notes — <em>Do, Re, Mi, Fa, Sol, La, Si</em></li>
                <li><strong>Words = intervals</strong> between notes. <em>Major third (4 semitones) = nature, Perfect fifth (7) = created objects</em></li>
                <li><strong>Direction = grammar.</strong> Up = light/good/active. Down = darkness/passive. Static = identity.</li>
                <li><strong>Primitives:</strong> 135+ basic meanings in <em>12 fixed categories</em></li>
                <li><strong>Category order</strong> (strict):<br>
                    <em>Existence → Size → Physics → Material → Shape → Color → Action → Relation → Value → Quantity → Space → Time</em></li>
                <li><strong>Flexible length:</strong> 2–12 primitives per word. Unused categories are skipped.</li>
                <li><strong>Example:</strong> "sun" = <em>big + hot + bright + rise + above + good + day</em> → DO MI SOL DO RE SOL LA DO</li>
                <li><strong>Everyone can propose</strong> new words/primitives/rules on <a href="https://github.com/tihon0392-boop/solres_language/discussions" target="_blank" style="color:var(--accent);">GitHub Discussions</a></li>
            </ol>
        </div>
    </div>

    <script>
        // === STARFIELD ===
        const canvas = document.getElementById('starfield');
        const ctx = canvas.getContext('2d');
        let theme = 'dark';
        let bodies = [];
        const BODY_COUNT = 200;
        function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        window.addEventListener('resize', () => { resizeCanvas(); createBodies(); });
        function random(min, max) { return Math.random() * (max - min) + min; }
        function createBodies() {
            bodies = [];
            for (let i = 0; i < BODY_COUNT; i++) {
                bodies.push({
                    x: random(0, canvas.width), y: random(0, canvas.height),
                    r: random(0.8, 4.5), baseOpacity: random(0.15, 1.0),
                    phase: random(0, Math.PI * 2), period: random(300, 2000),
                    alive: true, respawnTime: 0
                });
            }
        }
        function drawBodies() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const isLight = theme === 'light';
            const now = Date.now();
            bodies.forEach(b => {
                if (!b.alive) { if (now > b.respawnTime) { b.alive = true; b.baseOpacity = random(0.15, 1.0); b.r = random(0.8, 4.5); } return; }
                const twinkle = Math.sin(now / 1000 * (2 * Math.PI) / (b.period / 1000) + b.phase) * 0.3 + 0.7;
                const alpha = b.baseOpacity * twinkle;
                if (isLight) {
                    ctx.fillStyle = `rgba(${Math.floor(alpha*30)},${Math.floor(alpha*30)},${Math.floor(alpha*30)},${alpha})`;
                    ctx.shadowColor = `rgba(0,0,0,${alpha*0.95})`;
                } else {
                    const br = Math.floor(180 + alpha * 75);
                    ctx.fillStyle = `rgba(${br},${br},${Math.floor(br*0.85)},${alpha})`;
                    ctx.shadowColor = `rgba(255,240,220,${alpha*0.7})`;
                }
                ctx.shadowBlur = b.r * 3;
                ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2); ctx.fill();
            });
            ctx.shadowBlur = 0;
            requestAnimationFrame(drawBodies);
        }
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left, my = e.clientY - rect.top;
            for (let b of bodies) {
                if (!b.alive) continue;
                if (Math.sqrt((b.x-mx)**2 + (b.y-my)**2) < b.r + 10) {
                    b.alive = false; b.respawnTime = Date.now() + 10000; break;
                }
            }
        });
        resizeCanvas(); createBodies(); drawBodies();
        function toggleTheme() {
            const btn = document.getElementById('themeBtn');
            if (theme === 'dark') { theme = 'light'; document.body.classList.add('light-theme'); btn.textContent = '🌙 Dark'; }
            else { theme = 'dark'; document.body.classList.remove('light-theme'); btn.textContent = '☀️ Light'; }
        }

        // === TABS ===
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.card').forEach(c => c.style.display = 'none');
            document.getElementById('tab-' + tab).style.display = 'block';
            event.target.classList.add('active');
        }

        // === TRANSLATE ===
        let currentWord = '';
        function updateSpeed() { document.getElementById('speedLabel').textContent = document.getElementById('speedSlider').value + 'x'; }
        function quickSearch(word) { document.getElementById('wordInput').value = word; translateWord(); }
        async function translateWord() {
            const word = document.getElementById('wordInput').value.trim();
            if (!word) return;
            currentWord = word;
            const res = await fetch('/translate?word=' + encodeURIComponent(word));
            const data = await res.json();
            let html = '';
            if (data.error) { html = '<div class="error-msg">' + data.error + '</div>'; }
            else {
                if (data.description) { html += '<div class="desc-row">'; data.description.forEach(d => { html += '<span>' + d + '</span> '; }); html += '</div>'; }
                html += '<div class="notes-display">' + data.notes + '</div>';
                if (data.meaning && data.meaning !== 'not found') { html += '<div class="meaning">' + data.meaning + '</div>'; }
            }
            document.getElementById('result').innerHTML = html;
            if (!data.error) playAudio();
        }
        async function playAudio() {
            if (!currentWord) return;
            const speed = document.getElementById('speedSlider').value;
            const audioRes = await fetch('/play?word=' + encodeURIComponent(currentWord) + '&speed=' + speed);
            const audioBlob = await audioRes.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const player = document.getElementById('audioPlayer');
            player.style.display = 'block'; player.src = audioUrl; player.play();
        }

        // === DICTIONARY ===
        function filterDict() {
            const q = document.getElementById('dictSearch').value.toLowerCase();
            document.querySelectorAll('#primitivesTable tbody tr, #wordsTable tbody tr').forEach(tr => {
                tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
            });
        }
        function playDictWord(word) {
            document.getElementById('wordInput').value = word;
            switchTab('translate');
            translateWord();
        }

        // === COMPOSE ===
        const CATEGORIES = {{ categories_json | safe }};
        const CATEGORY_ORDER = {{ category_order_json | safe }};

        function buildComposeGrid() {
            const grid = document.getElementById('composeGrid');
            grid.innerHTML = '';
            CATEGORY_ORDER.forEach((cat, i) => {
                const words = CATEGORIES[cat] || [];
                const row = document.createElement('div');
                row.className = 'compose-row';
                row.id = 'compose-row-' + i;
                row.innerHTML = `
                    <span class="cat-label">${cat.split(':').pop()}</span>
                    <select id="compose-select-${i}" onchange="validateCompose()">
                        <option value="">—</option>
                        ${words.map(w => `<option value="${w}">${w}</option>`).join('')}
                    </select>
                `;
                grid.appendChild(row);
            });
        }

        function getSelectedPrimitives() {
            const selected = [];
            CATEGORY_ORDER.forEach((cat, i) => {
                const sel = document.getElementById('compose-select-' + i);
                if (sel && sel.value) {
                    selected.push({word: sel.value, category: cat, index: i});
                }
            });
            return selected;
        }

        function validateCompose() {
            const selected = getSelectedPrimitives();
            let lastIdx = -1;
            let valid = true;

            // Сбрасываем все
            CATEGORY_ORDER.forEach((_, i) => {
                const row = document.getElementById('compose-row-' + i);
                if (row) row.classList.remove('invalid');
            });

            for (const s of selected) {
                const catIdx = CATEGORY_ORDER.indexOf(s.category);
                if (catIdx < lastIdx) {
                    valid = false;
                    document.getElementById('compose-row-' + s.index).classList.add('invalid');
                }
                lastIdx = catIdx;
            }

            document.getElementById('composeError').innerHTML = '';
            return {valid, selected};
        }

        async function composePlay() {
            const {valid, selected} = validateCompose();
            if (selected.length < 2) {
                document.getElementById('composeError').innerHTML = '<div class="error-msg">Select at least 2 primitives</div>';
                return;
            }
            if (!valid) {
                document.getElementById('composeError').innerHTML = '<div class="error-msg">Category order violated! Red borders show the problem.</div>';
                return;
            }

            const words = selected.map(s => s.word);
            const res = await fetch('/compose?words=' + encodeURIComponent(words.join(',')));
            const data = await res.json();

            document.getElementById('composeResult').innerHTML = `
                <div class="desc-row">${words.map(w => '<span>' + w + '</span>').join(' ')}</div>
                <div class="notes-display">${data.notes}</div>
            `;

            const audioRes = await fetch('/compose_play?words=' + encodeURIComponent(words.join(',')));
            const audioBlob = await audioRes.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const player = document.getElementById('composeAudio');
            player.style.display = 'block'; player.src = audioUrl; player.play();
        }

        function composeRandom() {
            const {valid, selected} = validateCompose();
            // Заполняем случайными там, где пусто
            CATEGORY_ORDER.forEach((cat, i) => {
                const sel = document.getElementById('compose-select-' + i);
                if (!sel.value) {
                    const words = CATEGORIES[cat] || [];
                    if (words.length > 0 && Math.random() > 0.6) {
                        sel.value = words[Math.floor(Math.random() * words.length)];
                    }
                }
            });
            validateCompose();
        }

        function composeClear() {
            CATEGORY_ORDER.forEach((_, i) => {
                const sel = document.getElementById('compose-select-' + i);
                if (sel) sel.value = '';
            });
            document.getElementById('composeResult').innerHTML = '';
            document.getElementById('composeError').innerHTML = '';
            document.getElementById('composeAudio').style.display = 'none';
            validateCompose();
        }

        // Init
        buildComposeGrid();
    </script>
</body>
</html>
"""


def _build_primitives_rows():
    rows = []
    for entry in primitives.primitives.values():
        rows.append(
            f"<tr><td><span class='badge'>{entry['category']}</span></td><td>{entry['ru']}</td><td>{entry['en']}</td><td style='font-family:monospace;font-size:0.8em;color:var(--muted);'>{entry['pattern']}</td></tr>")
    return '\n'.join(rows)


def _build_words_rows():
    rows = []
    for word, data in sorted(descriptors.descriptions.items()):
        desc = ' + '.join(data['ru'])
        rows.append(
            f"<tr><td>{word}</td><td>{data['en']}</td><td style='font-size:0.85em;'>{desc}</td><td><button class='btn-sm' onclick='playDictWord(\"{word}\")'>▶</button></td></tr>")
    return '\n'.join(rows)


def _build_categories_json():
    import json
    cats = {}
    for entry in primitives.primitives.values():
        cat = entry['category']
        if cat not in cats:
            cats[cat] = []
        cats[cat].append(entry['ru'])
    return json.dumps(cats, ensure_ascii=False)


def _build_category_order_json():
    import json
    return json.dumps(DescriptorGrammar.CATEGORY_ORDER, ensure_ascii=False)


@app.route('/')
def home():
    return render_template_string(
        HTML,
        primitives_count=primitives.total_count(),
        descriptions_count=len(descriptors.descriptions),
        primitives_rows=_build_primitives_rows(),
        words_rows=_build_words_rows(),
        categories_json=_build_categories_json(),
        category_order_json=_build_category_order_json()
    )


@app.route('/translate')
def translate():
    word = request.args.get('word', '').strip()
    tonic = Note(NoteName.DO, 4)

    description = descriptors.get_description(word)
    if not description:
        description = descriptors.get_description_en(word)

    if description:
        notes, _ = descriptors.describe_to_notes(word, tonic)
        meaning = word
    else:
        prim = primitives.get_by_ru(word) or primitives.get_by_en(word)
        if prim:
            notes = descriptors.describe_to_notes(word, tonic)[0]
            meaning = prim["ru"] + " / " + prim["en"]
            description = [prim["ru"]]
        else:
            return jsonify({
                'notes': '—',
                'meaning': 'not found',
                'description': [],
                'error': 'Слово не найдено. Попробуйте: солнце, water, любовь, cat'
            })

    SHARP_SEMITONES = {1, 3, 6, 8, 10}
    note_names = []
    for n in notes:
        midi = n.to_midi()
        semitone = midi % 12
        sharp = "♯" if semitone in SHARP_SEMITONES else ""
        note_names.append(f"{n.name.name}{sharp}{n.octave}")

    return jsonify({
        'notes': ' → '.join(note_names),
        'meaning': meaning,
        'description': description
    })


@app.route('/play')
def play():
    word = request.args.get('word', '').strip()
    speed = float(request.args.get('speed', '1.0'))
    tonic = Note(NoteName.DO, 4)

    notes, _ = descriptors.describe_to_notes(word, tonic)
    wav_buf = generate_word_wav(notes, speed)
    return send_file(wav_buf, mimetype='audio/wav')


@app.route('/compose')
def compose():
    words_str = request.args.get('words', '')
    words = [w.strip() for w in words_str.split(',') if w.strip()]
    tonic = Note(NoteName.DO, 4)

    # Валидация порядка
    result = descriptors.validate_order(words)
    if not result["valid"]:
        return jsonify({'error': '; '.join(result["errors"])})

    # Строим ноты
    notes = [tonic]
    current_midi = tonic.to_midi()
    base_octave = 4

    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            movements = descriptors._pattern_to_movements(prim["pattern"])
            if movements:
                semitones, direction = movements[0]
                current_midi += direction * semitones
                current_octave = (current_midi // 12) - 1
                if current_octave > base_octave + 1:
                    current_midi -= 12
                elif current_octave < base_octave - 1:
                    current_midi += 12
                notes.append(descriptors._midi_to_note(current_midi))

    SHARP_SEMITONES = {1, 3, 6, 8, 10}
    note_names = []
    for n in notes:
        midi = n.to_midi()
        semitone = midi % 12
        sharp = "♯" if semitone in SHARP_SEMITONES else ""
        note_names.append(f"{n.name.name}{sharp}{n.octave}")

    return jsonify({'notes': ' → '.join(note_names), 'words': result["correct_order"]})


@app.route('/compose_play')
def compose_play():
    words_str = request.args.get('words', '')
    words = [w.strip() for w in words_str.split(',') if w.strip()]
    tonic = Note(NoteName.DO, 4)

    result = descriptors.validate_order(words)
    notes = [tonic]
    current_midi = tonic.to_midi()
    base_octave = 4

    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            movements = descriptors._pattern_to_movements(prim["pattern"])
            if movements:
                semitones, direction = movements[0]
                current_midi += direction * semitones
                current_octave = (current_midi // 12) - 1
                if current_octave > base_octave + 1:
                    current_midi -= 12
                elif current_octave < base_octave - 1:
                    current_midi += 12
                notes.append(descriptors._midi_to_note(current_midi))

    wav_buf = generate_word_wav(notes, 1.0)
    return send_file(wav_buf, mimetype='audio/wav')


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 SolRes Web App")
    print(f"   Primitives: {primitives.total_count()}")
    print(f"   Descriptions: {len(descriptors.descriptions)}")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)