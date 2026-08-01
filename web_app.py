# web_app.py
from flask import Flask, render_template_string, request, jsonify, send_file
import sys
import os
import numpy as np
import sounddevice as sd
import tempfile
import io
import wave as wave_module

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.interval_calculator import Note
from core.constants import NoteName
from language.lexicon import Lexicon
from language.chords import ChordLexicon

app = Flask(__name__)
lexicon = Lexicon()
chord_lex = ChordLexicon()

SAMPLE_RATE = 44100


def generate_wave(frequency, duration_ms, volume=0.3):
    num_samples = int(SAMPLE_RATE * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms / 1000.0, num_samples, False)

    # Фортепианный тембр
    wave = (
            np.sin(2 * np.pi * frequency * t) * 1.0 +
            np.sin(2 * np.pi * frequency * 2 * t) * 0.5 +
            np.sin(2 * np.pi * frequency * 3 * t) * 0.25 +
            np.sin(2 * np.pi * frequency * 4 * t) * 0.125
    )
    decay = np.exp(-3.0 * t / (duration_ms / 1000.0))
    wave *= decay

    # Огибающая
    attack = int(num_samples * 0.01)
    release = int(num_samples * 0.05)
    envelope = np.ones(num_samples)
    if attack > 1:
        envelope[:attack] = np.linspace(0, 1, attack)
    if release > 1:
        envelope[-release:] = np.linspace(1, 0, release)

    return (wave * envelope * volume).astype(np.float32)


def generate_word_wav(notes, mode='melody'):
    """Генерирует WAV-файл для слова/аккорда."""
    combined = np.array([], dtype=np.float32)

    if mode == 'chord':
        num_samples = int(SAMPLE_RATE * 800 / 1000.0)
        chord = np.zeros(num_samples, dtype=np.float32)
        for note in notes:
            wave_data = generate_wave(note.to_frequency(), 800)
            chord += wave_data
        max_val = np.max(np.abs(chord))
        if max_val > 0.9:
            chord = chord / max_val * 0.9
        combined = chord
    else:
        silence = np.zeros(int(SAMPLE_RATE * 0.05), dtype=np.float32)
        for i, note in enumerate(notes):
            dur = 400 if i < len(notes) - 1 else 600
            wave_data = generate_wave(note.to_frequency(), dur)
            combined = np.concatenate([combined, wave_data, silence])

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
    <title>SolRes — Универсальный музыкальный язык</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 50px auto; 
               padding: 20px; background: #0a0a1a; color: #e0e0e0; }
        h1 { color: #ffd700; text-align: center; font-size: 2em; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 30px; }
        .box { background: #1a1a2e; border-radius: 12px; padding: 25px; margin: 20px 0; }
        input { width: 65%; padding: 12px; font-size: 16px; border-radius: 8px; 
                border: 2px solid #2a2a3e; background: #0d0d1a; color: #fff; }
        input:focus { border-color: #ffd700; outline: none; }
        button { padding: 12px 20px; font-size: 16px; border-radius: 8px; border: none; 
                 cursor: pointer; font-weight: bold; margin-left: 5px; }
        .btn-translate { background: #ffd700; color: #000; }
        .btn-translate:hover { background: #ffed4a; }
        .btn-play { background: #4CAF50; color: #fff; }
        .btn-play:hover { background: #66BB6A; }
        .mode { display: flex; gap: 10px; margin-bottom: 15px; }
        .mode button { background: #2a2a3e; color: #aaa; }
        .mode button.active { background: #ffd700; color: #000; }
        .result { margin-top: 20px; }
        .notes-display { font-size: 24px; color: #ffd700; font-weight: bold; letter-spacing: 2px; 
                          text-align: center; margin: 15px 0; }
        .meaning-display { font-size: 18px; color: #00ff88; text-align: center; }
        .examples { color: #888; font-size: 14px; line-height: 1.8; }
        .examples span { color: #ffd700; cursor: pointer; }
        .examples span:hover { text-decoration: underline; }
        .search-row { display: flex; gap: 10px; align-items: center; }
        audio { width: 100%; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>🎵 SolRes</h1>
    <p class="subtitle">Универсальный музыкальный язык — пойми без слов</p>

    <div class="box">
        <div class="mode">
            <button id="btnMelody" class="active" onclick="setMode('melody')">🎶 Мелодия</button>
            <button id="btnChord" onclick="setMode('chord')">🎹 Аккорд</button>
        </div>
        <div class="search-row">
            <input type="text" id="wordInput" placeholder="Введите слово: солнце, love, дом..." 
                   onkeypress="if(event.key==='Enter') translateWord()" />
            <button class="btn-translate" onclick="translateWord()">🔍 Перевести</button>
        </div>
        <div class="result" id="result">
            <div class="notes-display">—</div>
            <div class="meaning-display">Введите слово для перевода</div>
        </div>
        <audio id="audioPlayer" controls style="display:none"></audio>
    </div>

    <div class="box">
        <h3 style="margin-bottom:10px">💡 Примеры (нажмите):</h3>
        <p class="examples">
            <span onclick="quickSearch('солнце')">солнце</span> · 
            <span onclick="quickSearch('sun')">sun</span> · 
            <span onclick="quickSearch('любовь')">любовь</span> · 
            <span onclick="quickSearch('love')">love</span> · 
            <span onclick="quickSearch('дом')">дом</span> · 
            <span onclick="quickSearch('home')">home</span> · 
            <span onclick="quickSearch('идти')">идти</span> · 
            <span onclick="quickSearch('страх')">страх</span> · 
            <span onclick="quickSearch('fear')">fear</span> · 
            <span onclick="quickSearch('птица')">птица</span> · 
            <span onclick="quickSearch('bird')">bird</span> · 
            <span onclick="quickSearch('радость')">радость</span> · 
            <span onclick="quickSearch('joy')">joy</span>
        </p>
    </div>

    <script>
        let mode = 'melody';

        function setMode(m) {
            mode = m;
            document.getElementById('btnMelody').className = m === 'melody' ? 'active' : '';
            document.getElementById('btnChord').className = m === 'chord' ? 'active' : '';
        }

        function quickSearch(word) {
            document.getElementById('wordInput').value = word;
            translateWord();
        }

        async function translateWord() {
            const word = document.getElementById('wordInput').value;
            if (!word) return;

            const res = await fetch('/translate?word=' + encodeURIComponent(word) + '&mode=' + mode);
            const data = await res.json();

            document.getElementById('result').innerHTML = 
                '<div class="notes-display">' + data.notes + '</div>' +
                '<div class="meaning-display">' + data.meaning + '</div>';

            // Загружаем аудио
            const audioRes = await fetch('/play?word=' + encodeURIComponent(word) + '&mode=' + mode);
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
    return render_template_string(HTML)


@app.route('/translate')
def translate():
    word = request.args.get('word', '')
    mode = request.args.get('mode', 'melody')
    tonic = Note(NoteName.DO, 4)

    if mode == 'chord':
        notes = chord_lex.chord_to_notes(word, tonic)
        meaning = chord_lex.notes_to_chord(notes)
    else:
        notes = lexicon.words_to_notes(word, tonic)
        if len(notes) >= 2:
            meaning = lexicon.notes_to_words(notes)
        else:
            meaning = ["слово не найдено"]
            notes = [tonic]

    note_names = [n.name.name for n in notes]

    return jsonify({
        'notes': ' → '.join(note_names),
        'meaning': ', '.join(meaning)
    })


@app.route('/play')
def play():
    word = request.args.get('word', '')
    mode = request.args.get('mode', 'melody')
    tonic = Note(NoteName.DO, 4)

    if mode == 'chord':
        notes = chord_lex.chord_to_notes(word, tonic)
    else:
        notes = lexicon.words_to_notes(word, tonic)
        if len(notes) < 2:
            notes = [tonic]

    wav_buf = generate_word_wav(notes, mode)
    return send_file(wav_buf, mimetype='audio/wav')


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 SolRes Web App")
    print("Откройте http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)