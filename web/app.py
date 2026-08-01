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
from chords.chords import ChordLexicon

app = Flask(__name__)
primitives = SemanticPrimitives()
descriptors = DescriptorGrammar()
chord_lex = ChordLexicon()

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


HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolRes — Universal Musical Language</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 750px; margin: 20px auto; 
               padding: 15px; background: #0a0a1a; color: #e0e0e0; font-size: 16px; }
        h1 { color: #ffd700; text-align: center; font-size: 2em; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 20px; font-size: 0.95em; }
        .box { background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 12px 0; }
        .search-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        input { flex: 1; min-width: 180px; padding: 12px; font-size: 16px; border-radius: 8px; 
                border: 2px solid #2a2a3e; background: #0d0d1a; color: #fff; }
        input:focus { border-color: #ffd700; outline: none; }
        button { padding: 12px 18px; font-size: 16px; border-radius: 8px; border: none; 
                 cursor: pointer; font-weight: bold; }
        .btn-translate { background: #ffd700; color: #000; }
        .btn-translate:hover { background: #ffed4a; }
        .mode { margin-bottom: 12px; }
        .mode span { color: #ffd700; font-weight: bold; }
        .result { margin-top: 18px; }
        .notes-display { font-size: 20px; color: #ffd700; font-weight: bold; text-align: center; 
                          margin: 10px 0; word-break: break-all; }
        .desc-display { font-size: 14px; color: #aaa; text-align: center; margin-bottom: 8px; }
        .meaning-display { font-size: 17px; color: #00ff88; text-align: center; }
        .examples { color: #888; font-size: 14px; line-height: 2; }
        .examples span { color: #ffd700; cursor: pointer; }
        .examples span:hover { text-decoration: underline; }
        audio { width: 100%; margin-top: 10px; }
        .stats { display: flex; justify-content: center; gap: 25px; margin: 8px 0; 
                 color: #888; font-size: 13px; flex-wrap: wrap; }
        .stats span { color: #ffd700; }
        .speed-control { display: flex; align-items: center; gap: 8px; margin-top: 10px; 
                         justify-content: center; color: #aaa; font-size: 14px; }
        .speed-control input { width: 120px; min-width: 80px; padding: 6px; }
        .speed-control span { color: #ffd700; }

        @media (max-width: 500px) {
            h1 { font-size: 1.4em; }
            .notes-display { font-size: 15px; }
            .search-row { flex-direction: column; }
            input { width: 100%; }
            button { width: 100%; }
            .stats { flex-direction: column; gap: 5px; text-align: center; }
            .speed-control { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <h1>🎵 SolRes</h1>
    <p class="subtitle">Universal musical language — describe the world with sound</p>

    <div class="stats">
        Primitives: <span>{{ primitives_count }}</span> | 
        Words: <span>{{ descriptions_count }}</span>
    </div>

    <div class="box">
        <div class="mode">
            <span>🎶 Describe mode</span>
        </div>
        <div class="search-row">
            <input type="text" id="wordInput" placeholder="Enter a word: sun, love, home..." 
                   onkeypress="if(event.key==='Enter') translateWord()" />
            <button class="btn-translate" onclick="translateWord()">🔍 Translate</button>
        </div>
        <div class="speed-control">
            Speed: <input type="range" id="speedSlider" min="0.5" max="2.5" step="0.1" value="1.0" 
                   oninput="updateSpeedLabel()">
            <span id="speedLabel">1.0x</span>
        </div>
        <div class="result" id="result">
            <div class="desc-display">Type a word to see its description and hear its melody</div>
            <div class="notes-display">—</div>
            <div class="meaning-display"></div>
        </div>
        <audio id="audioPlayer" controls style="display:none"></audio>
    </div>

    <div class="box">
        <h3 style="margin-bottom:10px">💡 Try these:</h3>
        <p class="examples">
            <span onclick="quickSearch('солнце')">солнце</span> · 
            <span onclick="quickSearch('луна')">луна</span> · 
            <span onclick="quickSearch('звезда')">звезда</span> · 
            <span onclick="quickSearch('вода')">вода</span> · 
            <span onclick="quickSearch('огонь')">огонь</span> · 
            <span onclick="quickSearch('гора')">гора</span> · 
            <span onclick="quickSearch('дом')">дом</span> · 
            <span onclick="quickSearch('птица')">птица</span> · 
            <span onclick="quickSearch('человек')">человек</span> · 
            <span onclick="quickSearch('река')">река</span> · 
            <span onclick="quickSearch('рыба')">рыба</span>
        </p>
    </div>

    <script>
        function updateSpeedLabel() {
            document.getElementById('speedLabel').textContent = 
                document.getElementById('speedSlider').value + 'x';
        }

        function quickSearch(word) {
            document.getElementById('wordInput').value = word;
            translateWord();
        }

        async function translateWord() {
            const word = document.getElementById('wordInput').value;
            if (!word) return;

            const res = await fetch('/translate?word=' + encodeURIComponent(word) + '&mode=melody');
            const data = await res.json();

            let descHTML = '';
            if (data.description) {
                descHTML = '<div class="desc-display">Description: ' + data.description.join(' + ') + '</div>';
            }

            document.getElementById('result').innerHTML = 
                descHTML +
                '<div class="notes-display">' + data.notes + '</div>' +
                '<div class="meaning-display">' + data.meaning + '</div>';

            const speed = document.getElementById('speedSlider').value;
            const audioRes = await fetch('/play?word=' + encodeURIComponent(word) + '&mode=melody&speed=' + speed);
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
    word = request.args.get('word', '')
    tonic = Note(NoteName.DO, 4)

    description = descriptors.get_description(word)
    if description:
        notes, _ = descriptors.describe_to_notes(word, tonic)
        meaning = [word]
    else:
        prim = primitives.get_by_ru(word) or primitives.get_by_en(word)
        if prim:
            notes = descriptors.describe_to_notes(word, tonic)[0]
            meaning = [prim["ru"], prim["en"]]
            description = [prim["ru"]]
        else:
            notes = [tonic]
            meaning = ["not found"]
            description = []

    SHARP_SEMITONES = {1, 3, 6, 8, 10}
    note_names = []
    for n in notes:
        midi = n.to_midi()
        semitone = midi % 12
        sharp = "♯" if semitone in SHARP_SEMITONES else ""
        note_names.append(f"{n.name.name}{sharp}{n.octave}")

    return jsonify({
        'notes': ' → '.join(note_names),
        'meaning': ', '.join(meaning) if isinstance(meaning, list) else meaning,
        'description': description
    })


@app.route('/play')
def play():
    word = request.args.get('word', '')
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