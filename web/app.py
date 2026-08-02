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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            transition: background 0.5s ease, color 0.5s ease;
        }
        #starfield {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0;
        }
        .container {
            max-width: 720px;
            width: 100%;
            position: relative;
            z-index: 1;
        }
        header { text-align: center; margin-bottom: 28px; }
        .logo {
            font-size: 3em;
            font-weight: 700;
            letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent2), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 4px;
        }
        .subtitle { color: var(--muted); font-size: 0.95em; font-weight: 300; }
        .top-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .stats {
            display: flex;
            gap: 20px;
            font-size: 0.8em;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stats span { color: var(--accent); font-weight: 600; font-size: 1.1em; }
        .theme-toggle {
            background: var(--surface2);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--text);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85em;
            font-family: inherit;
            transition: all var(--transition);
        }
        .theme-toggle:hover { border-color: var(--accent); }
        .card {
            background: var(--surface);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: var(--radius);
            padding: 28px;
            margin-bottom: 16px;
            backdrop-filter: blur(10px);
        }
        .card:focus-within { border-color: var(--accent-glow); }
        .search-row { display: flex; gap: 10px; }
        input {
            flex: 1;
            padding: 14px 18px;
            font-size: 16px;
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.06);
            background: var(--surface2);
            color: var(--text);
            font-family: inherit;
            transition: all var(--transition);
        }
        .light-theme input { border-color: rgba(0,0,0,0.1); }
        input:focus { border-color: var(--accent); outline: none; box-shadow: 0 0 0 3px var(--accent-glow); }
        input::placeholder { color: #505070; }
        .btn {
            padding: 14px 24px;
            font-size: 16px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            font-family: inherit;
            transition: all var(--transition);
            white-space: nowrap;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: #000;
        }
        .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 25px var(--accent-glow); }
        .btn-primary:active { transform: scale(0.97); }
        .result-area { margin-top: 20px; min-height: 40px; }
        .desc-row {
            font-size: 0.85em;
            color: var(--muted);
            text-align: center;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        .desc-row span {
            display: inline-block;
            background: var(--surface2);
            padding: 4px 10px;
            border-radius: 20px;
            margin: 2px;
            font-size: 0.9em;
        }
        .notes-display {
            font-size: 1.6em;
            font-weight: 600;
            letter-spacing: 2px;
            text-align: center;
            padding: 16px;
            background: var(--surface2);
            border-radius: 12px;
            color: var(--accent2);
            word-break: break-all;
            font-family: 'Courier New', monospace;
        }
        .meaning {
            text-align: center;
            margin-top: 10px;
            font-size: 1em;
            color: var(--green);
            font-weight: 500;
        }
        .speed-row {
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: center;
            margin-top: 16px;
            color: var(--muted);
            font-size: 0.85em;
        }
        .speed-row input[type=range] { width: 120px; accent-color: var(--accent); }
        .speed-row .speed-val { color: var(--accent); font-weight: 600; min-width: 36px; text-align: center; }
        audio { width: 100%; margin-top: 12px; border-radius: 8px; }
        .examples {
            color: var(--muted);
            font-size: 0.85em;
            line-height: 2.2;
            text-align: center;
        }
        .examples span {
            color: var(--text);
            cursor: pointer;
            padding: 3px 6px;
            border-radius: 6px;
            transition: all var(--transition);
            opacity: 0.8;
        }
        .examples span:hover { color: var(--accent2); opacity: 1; background: var(--accent-glow); }
        .error-msg {
            background: rgba(255,71,87,0.1);
            border: 1px solid rgba(255,71,87,0.3);
            color: var(--red);
            padding: 12px;
            border-radius: 10px;
            font-size: 0.85em;
            margin-top: 12px;
            text-align: center;
        }
        @media (max-width: 500px) {
            .logo { font-size: 2.2em; }
            .search-row { flex-direction: column; }
            .btn { width: 100%; }
            .notes-display { font-size: 1.2em; }
            .stats { gap: 12px; }
            .top-row { flex-direction: column; gap: 8px; }
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

        <div class="card">
            <div class="search-row">
                <input type="text" id="wordInput" 
                       placeholder="Enter a word: sun, вода, love, кошка..." 
                       onkeypress="if(event.key==='Enter') translateWord()" />
                <button class="btn btn-primary" onclick="translateWord()">🔍 Translate</button>
            </div>

            <div class="result-area" id="result">
                <div class="desc-row" style="opacity:0.5;">Type a word to see its description and hear its melody</div>
                <div class="notes-display" style="background:transparent;opacity:0.3;">—</div>
            </div>

            <div class="speed-row">
                <span>🐢</span>
                <input type="range" id="speedSlider" min="0.5" max="2.5" step="0.1" value="1.0" 
                       oninput="updateSpeed(); playAudio()">
                <span>🐇</span>
                <span class="speed-val" id="speedLabel">1.0x</span>
            </div>

            <audio id="audioPlayer" controls style="display:none"></audio>
        </div>

        <div class="card">
            <p class="examples">
                <span onclick="quickSearch('солнце')">солнце</span>
                <span onclick="quickSearch('sun')">sun</span>
                <span onclick="quickSearch('луна')">луна</span>
                <span onclick="quickSearch('moon')">moon</span>
                <span onclick="quickSearch('вода')">вода</span>
                <span onclick="quickSearch('water')">water</span>
                <span onclick="quickSearch('любовь')">любовь</span>
                <span onclick="quickSearch('love')">love</span>
                <span onclick="quickSearch('кошка')">кошка</span>
                <span onclick="quickSearch('cat')">cat</span>
                <span onclick="quickSearch('зима')">зима</span>
                <span onclick="quickSearch('winter')">winter</span>
                <span onclick="quickSearch('огонь')">огонь</span>
                <span onclick="quickSearch('fire')">fire</span>
                <span onclick="quickSearch('звезда')">звезда</span>
                <span onclick="quickSearch('star')">star</span>
            </p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('starfield');
        const ctx = canvas.getContext('2d');
        let theme = 'dark';
        let bodies = [];
        const BODY_COUNT = 200;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', () => { resizeCanvas(); createBodies(); });

        function random(min, max) { return Math.random() * (max - min) + min; }

        function createBodies() {
            bodies = [];
            for (let i = 0; i < BODY_COUNT; i++) {
                bodies.push({
                    x: random(0, canvas.width),
                    y: random(0, canvas.height),
                    r: random(0.8, 4.5),
                    baseOpacity: random(0.15, 1.0),
                    phase: random(0, Math.PI * 2),
                    period: random(300, 2000),
                    alive: true,
                    respawnTime: 0
                });
            }
        }

        function drawBodies() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const isLight = theme === 'light';
            const now = Date.now();

            bodies.forEach(b => {
                if (!b.alive) {
                    if (now > b.respawnTime) {
                        b.alive = true;
                        b.baseOpacity = random(0.15, 1.0);
                        b.r = random(0.8, 4.5);
                    }
                    return;
                }

                const twinkle = Math.sin(now / 1000 * (2 * Math.PI) / (b.period / 1000) + b.phase) * 0.3 + 0.7;
                const alpha = b.baseOpacity * twinkle;

                if (isLight) {
                    const darkness = Math.floor(alpha * 30);
                    ctx.fillStyle = `rgba(${darkness},${darkness},${darkness},${alpha})`;
                    ctx.shadowColor = `rgba(0,0,0,${alpha * 0.95})`;
                } else {
                    const brightness = Math.floor(180 + alpha * 75);
                    ctx.fillStyle = `rgba(${brightness},${brightness},${Math.floor(brightness * 0.85)},${alpha})`;
                    ctx.shadowColor = `rgba(255,240,220,${alpha * 0.7})`;
                }
                ctx.shadowBlur = b.r * 3;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.shadowBlur = 0;
            requestAnimationFrame(drawBodies);
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            for (let b of bodies) {
                if (!b.alive) continue;
                const dx = b.x - mx;
                const dy = b.y - my;
                if (Math.sqrt(dx*dx + dy*dy) < b.r + 10) {
                    b.alive = false;
                    b.respawnTime = Date.now() + 10000;
                    break;
                }
            }
        });

        resizeCanvas();
        createBodies();
        drawBodies();

        function toggleTheme() {
            const btn = document.getElementById('themeBtn');
            if (theme === 'dark') {
                theme = 'light';
                document.body.classList.add('light-theme');
                btn.textContent = '🌙 Dark';
            } else {
                theme = 'dark';
                document.body.classList.remove('light-theme');
                btn.textContent = '☀️ Light';
            }
        }

        let currentWord = '';

        function updateSpeed() {
            document.getElementById('speedLabel').textContent = 
                document.getElementById('speedSlider').value + 'x';
        }

        function quickSearch(word) {
            document.getElementById('wordInput').value = word;
            translateWord();
        }

        async function translateWord() {
            const word = document.getElementById('wordInput').value.trim();
            if (!word) return;
            currentWord = word;

            const res = await fetch('/translate?word=' + encodeURIComponent(word));
            const data = await res.json();

            let html = '';
            if (data.error) {
                html = '<div class="error-msg">' + data.error + '</div>';
            } else {
                if (data.description) {
                    html += '<div class="desc-row">';
                    data.description.forEach(d => { html += '<span>' + d + '</span> '; });
                    html += '</div>';
                }
                html += '<div class="notes-display">' + data.notes + '</div>';
                if (data.meaning && data.meaning !== 'not found') {
                    html += '<div class="meaning">' + data.meaning + '</div>';
                }
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
            player.style.display = 'block';
            player.src = audioUrl;
            player.play();
        }
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(
        HTML,
        primitives_count=primitives.total_count(),
        descriptions_count=len(descriptors.descriptions)
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


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 SolRes Web App")
    print(f"   Primitives: {primitives.total_count()}")
    print(f"   Descriptions: {len(descriptors.descriptions)}")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)