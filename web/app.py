# web/app.py — замените импорты и все 'solres2026secret' на SECRET_KEY
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import io
import wave as wave_module

from config import SECRET_KEY
from core.interval_calculator import Note
from core.constants import NoteName
from language.primitives import SemanticPrimitives
from language.descriptors import DescriptorGrammar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../shared.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

primitives = SemanticPrimitives()
descriptors = DescriptorGrammar()

SAMPLE_RATE = 44100
SHARP_SEMITONES = {1, 3, 6, 8, 10}


class SharedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    primitives = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(50), default='Anonymous')
    source = db.Column(db.String(50), default='User')
    created = db.Column(db.String(30))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)


class SharedSentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    words = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(50), default='Anonymous')
    created = db.Column(db.String(30))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

class SharedText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sentences = db.Column(db.String(1000), nullable=False)
    author = db.Column(db.String(50), default='Anonymous')
    created = db.Column(db.String(30))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)


def midi_to_frequency(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12))


def generate_wave(frequency, duration_ms, volume=0.3, instrument='piano'):
    num_samples = int(SAMPLE_RATE * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms / 1000.0, num_samples, False)

    if instrument == 'piano':
        wave_data = (
                np.sin(2 * np.pi * frequency * t) * 1.0 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 3 * t) * 0.25 +
                np.sin(2 * np.pi * frequency * 4 * t) * 0.125
        )
        decay = np.exp(-3.0 * t / (duration_ms / 1000.0))
        wave_data *= decay
    elif instrument == 'violin':
        vibrato = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t)
        wave_data = np.sin(2 * np.pi * frequency * t * vibrato)
        wave_data += np.sin(2 * np.pi * frequency * 2 * t) * 0.3
        attack = int(num_samples * 0.1)
        wave_data[:attack] *= np.linspace(0, 1, attack)
        decay = np.exp(-2.0 * t / (duration_ms / 1000.0))
        wave_data *= decay
    elif instrument == 'flute':
        wave_data = np.sin(2 * np.pi * frequency * t) * 1.0
        wave_data += np.sin(2 * np.pi * frequency * 2 * t) * 0.2
        wave_data += np.sin(2 * np.pi * frequency * 3 * t) * 0.1
        decay = np.exp(-2.5 * t / (duration_ms / 1000.0))
        wave_data *= decay
    elif instrument == 'organ':
        wave_data = (
                np.sin(2 * np.pi * frequency * t) * 1.0 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.7 +
                np.sin(2 * np.pi * frequency * 3 * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 4 * t) * 0.3 +
                np.sin(2 * np.pi * frequency * 5 * t) * 0.2 +
                np.sin(2 * np.pi * frequency * 6 * t) * 0.1
        )
        wave_data *= 0.7
    else:
        wave_data = np.sin(2 * np.pi * frequency * t)

    attack = int(num_samples * 0.01);
    release = int(num_samples * 0.05)
    envelope = np.ones(num_samples)
    if attack > 1: envelope[:attack] = np.linspace(0, 1, attack)
    if release > 1: envelope[-release:] = np.linspace(1, 0, release)
    return (wave_data * envelope * volume).astype(np.float32)


def generate_word_wav(notes, speed=1.0, instrument='piano'):
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, note in enumerate(notes):
        dur = base_duration if i < len(notes) - 1 else int(600 / speed)
        w = generate_wave(note.to_frequency(), dur, instrument=instrument)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


def generate_midi_wav(midi_notes, speed=1.0, instrument='piano'):
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, midi in enumerate(midi_notes):
        dur = base_duration if i < len(midi_notes) - 1 else int(600 / speed)
        w = generate_wave(midi_to_frequency(midi), dur, 0.3, instrument=instrument)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


def generate_note_wav(midi_note, duration_ms=400, instrument='piano'):
    w = generate_wave(midi_to_frequency(midi_note), duration_ms, 0.3, instrument=instrument)
    audio_int16 = (w * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


HTML = r"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolRes — Universal Musical Language</title>
    <style>
        #tutorialOverlay { display: none; }
        :root { --bg: #020210; --accent: #ff6a00; --accent2: #ff9500; --accent-glow: rgba(255,106,0,0.4); --surface: rgba(12,12,32,0.85); --surface2: rgba(20,20,50,0.9); --green: #00e676; --text: #d0d0e0; --muted: #707090; --red: #ff4757; --radius: 16px; --transition: 0.2s ease; }
        .light-theme { --bg: #f5f0e8; --accent: #7c3aed; --accent2: #a78bfa; --accent-glow: rgba(124,58,237,0.3); --surface: rgba(255,255,255,0.85); --surface2: rgba(240,235,225,0.9); --text: #1a1a2e; --muted: #6a6a7a; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 16px; transition: background 0.5s, color 0.5s; }
        #starfield { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
        .container { max-width: 900px; margin: 0 auto; position: relative; z-index: 1; }
        header { text-align: center; margin-bottom: 16px; }
        .logo { font-size: 2.3em; font-weight: 700; background: linear-gradient(135deg, var(--accent2), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .subtitle { color: var(--muted); font-size: 0.8em; }
        .top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
        .stats { display: flex; gap: 14px; font-size: 0.7em; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
        .stats span { color: var(--accent); font-weight: 600; }
        .theme-toggle { background: var(--surface2); border: 1px solid rgba(255,255,255,0.08); color: var(--text); padding: 6px 12px; border-radius: 18px; cursor: pointer; font-size: 0.75em; font-family: inherit; }
        .tabs { display: flex; gap: 2px; margin-bottom: 12px; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 4px; }
        .tabs::-webkit-scrollbar { height: 3px; }
        .tabs::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
        .tab { padding: 8px 12px; border-radius: 10px 10px 0 0; background: var(--surface2); color: var(--muted); cursor: pointer; font-size: 0.75em; font-weight: 500; border: none; font-family: inherit; white-space: nowrap; flex-shrink: 0; }
        .tab.active { background: var(--surface); color: var(--accent); font-weight: 600; }
        .card { background: var(--surface); border: 1px solid rgba(255,255,255,0.04); border-radius: 0 0 var(--radius) var(--radius); padding: 18px; backdrop-filter: blur(10px); }
        .search-row { display: flex; gap: 8px; margin-bottom: 10px; }
        input, select { padding: 8px 10px; font-size: 13px; border-radius: 8px; border: 2px solid rgba(255,255,255,0.06); background: var(--surface2); color: var(--text); font-family: inherit; }
        .light-theme input, .light-theme select { border-color: rgba(0,0,0,0.1); }
        input:focus, select:focus { border-color: var(--accent); outline: none; }
        .btn { padding: 8px 14px; font-size: 13px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; font-family: inherit; }
        .btn-primary { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #000; }
        .btn-sm { padding: 5px 8px; font-size: 0.7em; border-radius: 6px; background: var(--surface2); color: var(--accent); border: 1px solid rgba(255,255,255,0.05); cursor: pointer; }
        .btn-xs { padding: 2px 5px; font-size: 0.65em; border-radius: 4px; background: transparent; color: var(--muted); border: 1px solid rgba(255,255,255,0.1); cursor: pointer; }
        .btn-danger { background: rgba(255,71,87,0.2); color: var(--red); border: 1px solid var(--red); }
        .notes-display { font-size: 1.2em; font-weight: 600; letter-spacing: 2px; text-align: center; padding: 10px; background: var(--surface2); border-radius: 10px; color: var(--accent2); word-break: break-all; font-family: 'Courier New', monospace; margin-top: 8px; }
        .desc-row { font-size: 0.8em; color: var(--muted); text-align: center; margin-top: 8px; }
        .desc-row span { display: inline-block; background: var(--surface2); padding: 2px 7px; border-radius: 12px; margin: 1px; }
        .meaning { text-align: center; margin-top: 6px; color: var(--green); font-weight: 500; }
        .error-msg { background: rgba(255,71,87,0.1); border: 1px solid rgba(255,71,87,0.3); color: var(--red); padding: 10px; border-radius: 10px; font-size: 0.8em; margin-top: 10px; text-align: center; }
        .success-msg { background: rgba(0,230,118,0.1); border: 1px solid rgba(0,230,118,0.3); color: var(--green); padding: 10px; border-radius: 10px; font-size: 0.8em; margin-top: 10px; text-align: center; }
        .compose-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; }
        .compose-row { display: flex; align-items: center; gap: 6px; padding: 4px 0; }
        .compose-row .cat-label { width: 80px; font-size: 0.65em; color: var(--muted); text-transform: uppercase; text-align: right; }
        .compose-row .dropdown-search { flex: 1; min-width: 100px; position: relative; }
        .compose-row .dropdown-search input { width: 100%; }
        .compose-row .dropdown-search .dropdown-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 180px; overflow-y: auto; background: var(--surface2); border: 1px solid var(--accent); border-radius: 0 0 8px 8px; z-index: 10; display: none; }
        .compose-row .dropdown-search .dropdown-list div { padding: 6px 10px; cursor: pointer; font-size: 0.8em; }
        .compose-row .dropdown-search .dropdown-list div:hover { background: var(--accent-glow); color: var(--accent2); }
        .compose-row.invalid input { border-color: var(--red) !important; }
        .compose-buttons { display: flex; gap: 8px; margin-top: 12px; justify-content: center; flex-wrap: wrap; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8em; margin-top: 8px; }
        th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.04); }
        th { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.7em; }
        .table-wrap { max-height: 350px; overflow-y: auto; border-radius: 10px; }
        .badge { display: inline-block; padding: 2px 7px; border-radius: 10px; font-size: 0.75em; }
        .badge-user { background: rgba(0,230,118,0.2); color: var(--green); }
        .badge-system { background: var(--accent-glow); color: var(--accent2); }
        .badge-community { background: rgba(100,150,255,0.2); color: #80b0ff; }
        .instrument-select { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; justify-content: center; flex-wrap: wrap; }
        .piano-container { overflow-x: auto; padding: 8px 0; display: flex; justify-content: center; }
        .piano { position: relative; height: 130px; width: 504px; user-select: none; }
        .white-key { width: 36px; height: 130px; background: #f0f0f0; border: 1px solid #aaa; border-radius: 0 0 5px 5px; cursor: pointer; position: absolute; z-index: 1; font-size: 0.5em; color: #888; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px; transition: background 0.1s; }
        .white-key:hover { background: #fff; } .white-key.active { background: var(--accent2); color: #000; }
        .black-key { width: 20px; height: 82px; background: #1a1a1a; border: 1px solid #000; border-radius: 0 0 4px 4px; cursor: pointer; position: absolute; z-index: 2; font-size: 0.35em; color: #aaa; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 3px; transition: background 0.1s; }
        .black-key:hover { background: #333; } .black-key.active { background: var(--accent); }
        .piano-sequence { min-height: 24px; padding: 6px; background: var(--surface2); border-radius: 6px; margin-bottom: 10px; text-align: center; font-family: 'Courier New', monospace; font-size: 0.8em; color: var(--accent2); }
        .piano-buttons { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }
        .analysis-table { width: 100%; margin-top: 10px; font-size: 0.75em; }
        .analysis-table td { padding: 5px 8px; } .found { color: var(--green); } .not-found { color: var(--red); }
        .sentence-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 6px; background: var(--surface2); border-radius: 8px; }
        .sentence-row select, .sentence-row input { flex: 1; }
        .drag-handle { cursor: grab; color: var(--muted); font-size: 1.2em; padding: 0 4px; } .drag-handle:active { cursor: grabbing; }
        .dragging { opacity: 0.5; } .drag-over { border-color: var(--accent) !important; }
        audio { width: 100%; margin-top: 8px; border-radius: 6px; }
        .speed-row { display: flex; align-items: center; gap: 8px; justify-content: center; margin-top: 10px; color: var(--muted); font-size: 0.8em; }
        .speed-row input[type=range] { width: 80px; accent-color: var(--accent); }
        .rules-list { list-style: none; padding: 0; }
        .rules-list li { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); line-height: 1.6; }
        .rules-list strong { color: var(--accent); }
        .dropdown-search { position: relative; flex: 1; }
        .dropdown-search input { width: 100%; }
        .dropdown-search .dropdown-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: var(--surface2); border: 1px solid var(--accent); border-radius: 0 0 8px 8px; z-index: 10; display: none; }
        .dropdown-search .dropdown-list div { padding: 8px 12px; cursor: pointer; font-size: 0.85em; }
        .dropdown-search .dropdown-list div:hover { background: var(--accent-glow); color: var(--accent2); }
        @media (max-width: 600px) {
            .logo { font-size: 1.6em; } .subtitle { font-size: 0.7em; } .container { padding: 0 6px; }
            .tabs { gap: 1px; } .tab { font-size: 0.68em; padding: 7px 9px; }
            .card { padding: 14px; border-radius: 0 0 12px 12px; }
            .compose-grid { grid-template-columns: 1fr; gap: 8px; }
            .compose-row .cat-label { width: 60px; font-size: 0.6em; }
            .compose-row .dropdown-search { min-width: auto; } .compose-row input { font-size: 14px; padding: 10px; }
            .btn { padding: 10px 16px; font-size: 14px; } .btn-sm { padding: 8px 12px; font-size: 0.75em; }
            .compose-buttons .btn { flex: 1; min-width: 0; }
            .white-key { width: 20px; height: 70px; font-size: 0.25em; padding-bottom: 2px; }
            .black-key { width: 13px; height: 44px; font-size: 0.2em; }
            .piano { height: 70px; width: 280px; }
            .piano-sequence { font-size: 0.65em; }
            table { font-size: 0.7em; } th, td { padding: 6px; } .table-wrap { max-height: 250px; }
            .speed-row { gap: 4px; font-size: 0.7em; } .speed-row input[type=range] { width: 60px; }
            .search-row { flex-direction: column; } .search-row input, .search-row .btn { width: 100%; }
            .sentence-row { flex-wrap: wrap; } .sentence-row .dropdown-search { min-width: 120px; }
            .top-row { flex-direction: column; align-items: flex-start; } .stats { gap: 10px; font-size: 0.65em; }
        }
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--accent);
            color: #000;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9em;
            z-index: 200;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        .toast.show { opacity: 1; }
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 150;
            display: flex; align-items: center; justify-content: center;
        }
        .modal-box {
            background: var(--surface); border: 1px solid var(--accent);
            border-radius: 16px; padding: 24px; text-align: center;
            min-width: 280px;
        }
        .modal-box input {
            width: 100%; margin: 12px 0; padding: 10px; font-size: 15px;
            border-radius: 8px; border: 2px solid var(--surface2);
            background: var(--surface2); color: var(--text);
        }
        .modal-box .btn { margin: 4px; }
    </style>
</head>
<body>
    <canvas id="starfield"></canvas>
    <div class="container">
        <header><div class="logo">🎵 SolRes</div><p class="subtitle">Universal musical language</p></header>
        <div class="top-row">
            <div class="stats"><div>Primitives <span>{{ primitives_count }}</span></div><div>Words <span>{{ descriptions_count }}</span></div></div>
            <select id="langSelect" onchange="changeLanguage()" style="padding:6px 10px;font-size:0.75em;border-radius:18px;background:var(--surface2);color:var(--text);border:1px solid rgba(255,255,255,0.08);margin-right:8px;">
                <option value="en">🇬🇧 EN</option>
                <option value="ru">🇷🇺 RU</option>
            </select>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀️ Light</button>
        </div>
        <div class="tabs">
            <button class="tab active" data-lang="translate" onclick="switchTab('translate')">🔍 Translate</button>
            <button class="tab" data-lang="compose" onclick="switchTab('compose')">🧩 Compose</button>
            <button class="tab" data-lang="instruments" onclick="switchTab('instruments')">🎸 Instruments</button>
            <button class="tab" data-lang="mywords" onclick="switchTab('mywords')">📝 My Words</button>
            <button class="tab" data-lang="sentences" onclick="switchTab('sentences')">💬 Sentences</button>
            <button class="tab" data-lang="text" onclick="switchTab('text')">📄 Text</button>
            <button class="tab" data-lang="community" onclick="switchTab('community')">🌐 Community</button>
            <button class="tab" data-lang="dictionary" onclick="switchTab('dictionary')">📖 Dictionary</button>
            <button class="tab" data-lang="rules" onclick="switchTab('rules')">📋 Rules</button>
        </div>

        <!-- TRANSLATE -->
        <div class="card" id="tab-translate">
            <div class="search-row"><input type="text" id="wordInput" placeholder="Enter a word..." onkeypress="if(event.key==='Enter') translateWord()"><button class="btn btn-primary" data-lang="translate" onclick="translateWord()">🔍 Translate</button></div>
            <div id="result"><div style="text-align:center;color:var(--muted);opacity:0.5;">Type a word to see its description and hear its melody</div></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="speedSlider" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('speedSlider','speedLabel')"><span>🐇</span><span id="speedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="audioPlayer" controls style="display:none"></audio>
        </div>

        <!-- COMPOSE -->
        <div class="card" id="tab-compose" style="display:none;">
            <div class="compose-grid" id="composeGrid"></div>
            <div class="compose-buttons">
                <button class="btn btn-primary" data-lang="play" onclick="composePlay()">▶ Play</button>
                <button class="btn btn-sm" data-lang="saveAsWord" onclick="saveComposedWord()">💾 Save to My Words</button>
                <button class="btn btn-sm" data-lang="random" onclick="composeRandom()">✨ Random</button>
                <button class="btn btn-sm" data-lang="clearAll" onclick="composeClear()">✕ Clear All</button>
                
            </div>
            <div><input type="text" id="composeWordName" placeholder="Word name (optional)" style="width:100%;margin-top:8px;"></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="composeSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('composeSpeed','composeSpeedLabel')"><span>🐇</span><span id="composeSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <div id="composeError"></div><div id="composeResult"></div>
            <audio id="composeAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- INSTRUMENTS -->
        <div class="card" id="tab-instruments" style="display:none;">
            <div class="instrument-select">
                <button class="btn btn-sm" onclick="pianoShiftOctave(-1)">◀</button>
                <span style="color:var(--accent);font-weight:600;min-width:70px;text-align:center;" id="pianoRangeLabel">C3 – B4</span>
                <button class="btn btn-sm" onclick="pianoShiftOctave(1)">▶</button>
                <label style="margin-left:12px;">Instrument:</label>
                <select id="instrumentSelect" onchange="instrumentChanged()">
                    <option value="piano">🎹 Piano</option>
                    <option value="violin">🎻 Violin</option>
                    <option value="flute">🎵 Flute</option>
                    <option value="organ">🎛️ Organ</option>
                </select>
            </div>
            <div class="piano-sequence" id="pianoSequence">Click keys to record a melody...</div>
            <div class="piano-container"><div class="piano" id="piano"></div></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="pianoSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('pianoSpeed','pianoSpeedLabel')"><span>🐇</span><span id="pianoSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <div class="piano-buttons" style="margin-top:10px;">
                <button class="btn btn-primary" data-lang="playAnalyze" onclick="pianoPlaySequence()">▶ Play & Analyze</button>
                <button class="btn btn-sm" data-lang="pause" onclick="pianoAddPause()">⏸ Pause</button>
                <button class="btn btn-sm" data-lang="undo" onclick="pianoUndoLastNote()">↩ Undo</button>
                <button class="btn btn-sm" data-lang="clearAll" onclick="pianoClearSequence()">✕ Clear All</button>
                <button class="btn btn-sm" data-lang="toCompose" onclick="pianoToCompose()">📋 To Compose</button>
            </div>
            <div id="pianoAnalysis"></div>
            <div id="pianoSaveArea" style="margin-top:8px;"></div>
            <audio id="pianoAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- MY WORDS -->
        <div class="card" id="tab-mywords" style="display:none;">
            <button class="btn btn-sm" data-lang="refresh" onclick="loadMyWords()" style="margin-bottom:10px;">🔄 Refresh</button>
            <button class="btn btn-sm btn-danger" data-lang="clearAll" onclick="clearMyWords()" style="margin-bottom:10px;margin-left:6px;">🗑 Clear All</button>
            <div class="speed-row"><span>🐢</span><input type="range" id="mywordsSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('mywordsSpeed','mywordsSpeedLabel')"><span>🐇</span><span id="mywordsSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <div class="table-wrap"><table id="myWordsTable"><thead><tr><th>Name</th><th>Primitives</th><th>Source</th><th style="width:24px;"></th><th style="width:24px;"></th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
        </div>

        <!-- COMMUNITY -->
        <div class="card" id="tab-community" style="display:none;">
            <div class="tabs" style="margin-bottom:12px;">
                <button class="tab active" data-lang="words" onclick="switchCommunityTab('words')">📝 Words</button>
                <button class="tab" data-lang="sentences" onclick="switchCommunityTab('sentences')">💬 Sentences</button>
                <button class="tab" data-lang="text" onclick="switchCommunityTab('text')">📄 Text</button>
            </div>
            <button class="btn btn-sm" data-lang="refresh" onclick="loadCommunityWords()" style="margin-bottom:10px;" id="communityRefresh">🔄 Refresh</button>
            <div class="speed-row"><span>🐢</span><input type="range" id="communitySpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('communitySpeed','communitySpeedLabel')"><span>🐇</span><span id="communitySpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <div id="community-words">
                <div class="table-wrap"><table id="communityTable"><thead><tr><th>Name</th><th>Primitives</th><th>Author</th><th>Rating</th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
            </div>
            <div id="community-sentences" style="display:none;">
                <div class="table-wrap"><table id="communitySentencesTable"><thead><tr><th>Name</th><th>Words</th><th>Author</th><th>Rating</th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
            </div>
            <div id="community-text" style="display:none;">
                <div class="table-wrap"><table id="communityTextTable"><thead><tr><th>Name</th><th>Sentences</th><th>Author</th><th>Rating</th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
            </div>
        </div>

        <!-- SENTENCES -->
        <div class="card" id="tab-sentences" style="display:none;">
            <div id="sentenceEmpty" style="text-align:center;color:var(--muted);padding:20px;">No saved sentences yet.</div>
            <div id="sentenceRows"></div>
            <div class="compose-buttons">
                <button class="btn btn-sm" data-lang="addWord" onclick="addSentenceRow()">+ Add Word</button>
                <button class="btn btn-primary" data-lang="play" onclick="playSentence()">▶ Play</button>
                <button class="btn btn-sm" data-lang="save" onclick="saveSentence()">💾 Save</button>
                <button class="btn btn-sm" data-lang="publish" onclick="publishSentence()">🌐 Publish</button>
                <button class="btn btn-sm" data-lang="clear" onclick="clearSentence()">✕ Clear</button>
            </div>
            <div><input type="text" id="sentenceName" placeholder="Sentence name (optional)" style="width:100%;margin-top:8px;"></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="sentSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('sentSpeed','sentSpeedLabel')"><span>🐇</span><span id="sentSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="sentenceAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- TEXT -->
        <div class="card" id="tab-text" style="display:none;">
            <button class="btn btn-sm" data-lang="refresh" onclick="loadText()" style="margin-bottom:10px;">🔄 Refresh</button>
            <button class="btn btn-primary" data-lang="playAll" onclick="playText()" style="margin-bottom:10px;margin-left:6px;">▶ Play All</button>
            <button class="btn btn-sm" data-lang="publishAll" onclick="publishText()" style="margin-bottom:10px;margin-left:6px;">🌐 Publish All</button>
            <button class="btn btn-sm btn-danger" data-lang="clearAll" onclick="clearText()" style="margin-bottom:10px;margin-left:6px;">🗑 Clear All</button>
            <div id="textList"></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="textSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('textSpeed','textSpeedLabel')"><span>🐇</span><span id="textSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="textAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- DICTIONARY -->
        <div class="card" id="tab-dictionary" style="display:none;">
            <div class="search-row"><input type="text" id="dictSearch" placeholder="Search..." oninput="filterDict()"></div>
            <h3 style="margin:10px 0 6px;color:var(--accent);">🔤 Primitives <span style="color:var(--muted);">({{ primitives_count }})</span></h3>
            <div class="table-wrap"><table id="primitivesTable"><thead><tr><th data-lang="category">Category</th><th data-lang="ru">RU</th><th data-lang="en">EN</th><th data-lang="pattern">Pattern</th></tr></thead><tbody>{{ primitives_rows | safe }}</tbody></table></div>
            <h3 style="margin:14px 0 6px;color:var(--accent);">📝 Words <span style="color:var(--muted);">({{ descriptions_count }})</span></h3>
            <div class="table-wrap"><table id="wordsTable"><thead><tr><th data-lang="ru">Word</th><th data-lang="en">EN</th><th data-lang="description">Description</th><th style="width:24px;"></th></tr></thead><tbody>{{ words_rows | safe }}</tbody></table></div>
        </div>

        <!-- RULES -->
        <div class="card" id="tab-rules" style="display:none;">
            <h3 style="color:var(--accent);margin-bottom:10px;">📋 Rules</h3>
            <ol class="rules-list">
                <li><span data-lang="rule1"><strong>Alphabet:</strong> 7 notes — <em>Do, Re, Mi, Fa, Sol, La, Si</em></span></li>
                <li><span data-lang="rule2"><strong>Words = intervals</strong> between notes.</span></li>
                <li><span data-lang="rule3"><strong>Direction:</strong> Up = light/active, Down = dark/passive.</span></li>
                <li><span data-lang="rule4"><strong>135+ primitives</strong> in 12 fixed categories.</span></li>
                <li><span data-lang="rule5"><strong>Order:</strong> Existence → Size → Physics → Material → Shape → Color → Action → Relation → Value → Quantity → Space → Time</span></li>
                <li><span data-lang="rule6"><strong>Flexible:</strong> 2–12 primitives per word.</span></li>
                <li><span data-lang="rule7"><strong>Community:</strong> <a href="https://github.com/tihon0392-boop/solres_language/discussions" target="_blank" style="color:var(--accent);">GitHub Discussions</a></span></li>
            </ol>
        </div>
    </div>

    <script>
        let theme = 'dark', currentWord = '', pianoOctave = 3, pianoSequence = [], lastAnalysis = null, currentInstrument = 'piano', backspaceTimer = null;
        const CATEGORIES = {{ categories_json | safe }};
        const CATEGORY_ORDER = {{ category_order_json | safe }};
        const PRIMITIVE_INFO = {{ primitive_info_json | safe }};
        const DICTIONARY_WORDS = {{ dictionary_words_json | safe }};
        const SHARP_SEMITONES = [1,3,6,8,10];
        const SECRET_KEY = '{{ secret_key | safe }}';
        const NOTE_NAMES = ['C','C#/Db','D','D#/Eb','E','F','F#/Gb','G','G#/Ab','A','A#/Bb','B'];
        const LANG = {
        
            primitiveNames: {
                'я': 'I', 'ты': 'you', 'он': 'he', 'это': 'this', 'быть': 'be',
                'нечто': 'something', 'ничто': 'nothing', 'всё': 'everything', 'кто-то': 'someone',
                'большой': 'big', 'маленький': 'small', 'высокий': 'tall', 'низкий': 'low',
                'широкий': 'wide', 'узкий': 'narrow', 'глубокий': 'deep', 'мелкий': 'shallow',
                'горячий': 'hot', 'холодный': 'cold', 'твёрдый': 'hard', 'мягкий': 'soft',
                'тяжёлый': 'heavy', 'лёгкий': 'light', 'острый': 'sharp', 'тупой': 'dull',
                'быстрый': 'fast', 'медленный': 'slow', 'мокрый': 'wet', 'сухой': 'dry',
                'гладкий': 'smooth', 'шершавый': 'rough',
                'светлый': 'bright', 'тёмный': 'dark', 'белый': 'white', 'красный': 'red',
                'синий': 'blue', 'зелёный': 'green', 'жёлтый': 'yellow', 'фиолетовый': 'purple',
                'оранжевый': 'orange', 'серый': 'gray',
                'идти': 'go', 'стоять': 'stand', 'бежать': 'run', 'падать': 'fall',
                'подниматься': 'rise', 'спускаться': 'descend', 'давать': 'give', 'брать': 'take',
                'делать': 'do', 'ломать': 'break', 'говорить': 'say', 'молчать': 'be silent',
                'смотреть': 'see', 'слышать': 'hear', 'думать': 'think', 'чувствовать': 'feel',
                'жить': 'live', 'умирать': 'die', 'начинать': 'begin', 'заканчивать': 'finish',
                'менять': 'change', 'сохранять': 'keep',
                'дерево': 'wood', 'камень': 'stone', 'металл': 'metal', 'вода': 'water',
                'огонь': 'fire', 'воздух': 'air', 'земля': 'earth', 'стекло': 'glass',
                'ткань': 'fabric', 'бумага': 'paper',
                'круглый': 'round', 'квадратный': 'square', 'треугольный': 'triangular',
                'прямой': 'straight', 'изогнутый': 'curved', 'спиральный': 'spiral',
                'и': 'and', 'или': 'or', 'для': 'for', 'от': 'from', 'с': 'with',
                'без': 'without', 'внутри': 'inside', 'снаружи': 'outside', 'над': 'above',
                'под': 'below', 'рядом': 'near', 'далеко': 'far',
                'хороший': 'good', 'плохой': 'bad', 'красивый': 'beautiful', 'уродливый': 'ugly',
                'правильный': 'correct', 'неправильный': 'wrong', 'важный': 'important',
                'неважный': 'unimportant', 'полезный': 'useful', 'бесполезный': 'useless',
                'новый': 'new', 'старый': 'old',
                'один': 'one', 'два': 'two', 'много': 'many', 'мало': 'few',
                'весь': 'all', 'часть': 'part', 'больше': 'more', 'меньше': 'less',
                'половина': 'half', 'пустой': 'empty',
                'здесь': 'here', 'там': 'there', 'впереди': 'ahead', 'сзади': 'behind',
                'слева': 'left', 'справа': 'right', 'север': 'north', 'юг': 'south',
                'восток': 'east', 'запад': 'west',
                'сейчас': 'now', 'тогда': 'then', 'потом': 'later', 'никогда': 'never',
                'всегда': 'always', 'иногда': 'sometimes', 'день': 'day', 'ночь': 'night',
                'утро': 'morning', 'вечер': 'evening', 'быстро': 'quickly', 'медленно': 'slowly'
            },  
        
            categories: {
                'существование': 'existence',
                'свойство:размер': 'size',
                'свойство:физические': 'physics',
                'материал': 'material',
                'форма': 'shape',
                'свойство:цвет': 'color',
                'действие': 'action',
                'отношение': 'relation',
                'оценка': 'value',
                'количество': 'quantity',
                'пространство': 'space',
                'время': 'time'
            },
            ru: {
                translate: '🔍 Перевод', compose: '🧩 Собрать', instruments: '🎸 Инструменты',
                mywords: '📝 Мои слова', sentences: '💬 Предложения', text: '📄 Текст',
                community: '🌐 Сообщество', dictionary: '📖 Словарь', rules: '📋 Правила',
                play: '▶ Играть', save: '💾 Сохранить', publish: '🌐 Опубликовать',
                refresh: '🔄 Обновить', clear: '✕ Очистить', undo: '↩ Отмена',
                speed: 'Скорость', search: '🔍 Искать...',
                noWords: 'Нет сохранённых слов.', noSentences: 'Нет сохранённых предложений.',
                noCommunityWords: 'Нет опубликованных слов.', noCommunitySentences: 'Нет опубликованных предложений.',
                noCommunityTexts: 'Нет опубликованных текстов.', typeWord: 'Введите слово...',
                recordMelody: 'Нажмите клавиши для записи...', welcome: '🎵 Добро пожаловать в SolRes!',
                getStarted: '🚀 Начать!',
                tutorial1: '🔍 <b>Перевод</b> — введите слово, услышьте мелодию',
                tutorial2: '🧩 <b>Сборка</b> — создайте слово из 135+ примитивов',
                tutorial3: '🎸 <b>Инструменты</b> — играйте на пианино',
                tutorial4: '📝 <b>Мои слова</b> — сохраняйте свои слова',
                tutorial5: '🌐 <b>Сообщество</b> — смотрите слова других',
                tutorial6: '💬 <b>Предложения</b> — соединяйте слова',
                tutorial7: '📄 <b>Текст</b> — создавайте текст',
                tutorial8: '⚡ <b>Скорость</b> — меняйте темп',
                tutorial9: '☀️ <b>Тема</b> — светлая/тёмная',
                primitives: 'Примитивы', words: 'Слова', category: 'Категория', pattern: 'Паттерн',
                author: 'Автор', rating: 'Рейтинг', name: 'Название', source: 'Источник',
                light: '☀️ Светлая', dark: '🌙 Тёмная', addWord: '+ Слово',
                playAll: '▶ Играть всё', publishAll: '🌐 Опубликовать всё',
                clearAll: '🗑 Очистить всё', searchWord: '🔍 Искать слово...',
                sentenceName: 'Название предложения', wordName: 'Название слова',
                description: 'Описание', noTexts: 'Нет сохранённых предложений.',
                enterWord: 'Введите слово...', playAnalyze: '▶ Играть и анализировать',
                toCompose: '📋 В сборку', saveAsWord: '💾 Сохранить как слово',
                yourName: 'Ваше имя', enterName: 'Введите имя...',
                textName: 'Название текста', enterTextName: 'Введите название текста...',
                nothingToPublish: 'Нечего публиковать.', select2words: 'Выберите минимум 2 слова',
                published: 'Опубликовано: ', saved: 'Сохранено: ',
                ru: 'RU',
                pause: '⏸ Пауза',
                note: 'Нота', interval: 'Интервал', primitive: 'Примитив',
                rule1: '<strong>Алфавит:</strong> 7 нот — <em>До, Ре, Ми, Фа, Соль, Ля, Си</em>',
                rule2: '<strong>Слова = интервалы</strong> между нотами.',
                rule3: '<strong>Направление:</strong> Вверх = свет/активность, Вниз = тьма/пассив.',
                rule4: '<strong>135+ примитивов</strong> в 12 фиксированных категориях.',
                rule5: '<strong>Порядок:</strong> Существование → Размер → Физика → Материал → Форма → Цвет → Действие → Отношение → Оценка → Количество → Пространство → Время',
                rule6: '<strong>Гибкость:</strong> 2–12 примитивов на слово.',
                rule7: '<strong>Сообщество:</strong> <a href="https://github.com/tihon0392-boop/solres_language/discussions" target="_blank" style="color:var(--accent);">GitHub Discussions</a>',
            },
            en: {
                translate: '🔍 Translate', compose: '🧩 Compose', instruments: '🎸 Instruments',
                mywords: '📝 My Words', sentences: '💬 Sentences', text: '📄 Text',
                community: '🌐 Community', dictionary: '📖 Dictionary', rules: '📋 Rules',
                play: '▶ Play', save: '💾 Save', publish: '🌐 Publish',
                refresh: '🔄 Refresh', clear: '✕ Clear', undo: '↩ Undo',
                speed: 'Speed', search: '🔍 Search...',
                noWords: 'No saved words yet.', noSentences: 'No saved sentences yet.',
                noCommunityWords: 'No community words yet.', noCommunitySentences: 'No published sentences yet.',
                noCommunityTexts: 'No published texts yet.', typeWord: 'Type a word...',
                recordMelody: 'Click keys to record...', welcome: '🎵 Welcome to SolRes!',
                getStarted: '🚀 Get Started!',
                tutorial1: '🔍 <b>Translate</b> — type a word, hear its melody',
                tutorial2: '🧩 <b>Compose</b> — build words from 135+ primitives',
                tutorial3: '🎸 <b>Instruments</b> — play piano, analyze intervals',
                tutorial4: '📝 <b>My Words</b> — save your custom words',
                tutorial5: '🌐 <b>Community</b> — explore words from others',
                tutorial6: '💬 <b>Sentences</b> — chain words together',
                tutorial7: '📄 <b>Text</b> — build text from sentences',
                tutorial8: '⚡ <b>Speed slider</b> — adjust playback speed',
                tutorial9: '☀️ <b>Theme toggle</b> — switch dark/light mode',
                primitives: 'Primitives', words: 'Words', category: 'Category', pattern: 'Pattern',
                author: 'Author', rating: 'Rating', name: 'Name', source: 'Source',
                light: '☀️ Light', dark: '🌙 Dark', addWord: '+ Add Word',
                playAll: '▶ Play All', publishAll: '🌐 Publish All',
                clearAll: '🗑 Clear All', searchWord: '🔍 Search word...',
                sentenceName: 'Sentence name', wordName: 'Word name',
                description: 'Description', noTexts: 'No saved sentences yet.',
                enterWord: 'Enter a word...', playAnalyze: '▶ Play & Analyze',
                toCompose: '📋 To Compose', saveAsWord: '💾 Save as My Word',
                yourName: 'Your name', enterName: 'Enter your name...',
                textName: 'Text name', enterTextName: 'Enter text name...',
                nothingToPublish: 'Nothing to publish.', select2words: 'Select at least 2 words',
                published: 'Published: ', saved: 'Saved: ',
                ru: 'RU',
                pause: '⏸ Pause',
                note: 'Note', interval: 'Interval', primitive: 'Primitive',
                rule1: '<strong>Alphabet:</strong> 7 notes — <em>Do, Re, Mi, Fa, Sol, La, Si</em>',
                rule2: '<strong>Words = intervals</strong> between notes.',
                rule3: '<strong>Direction:</strong> Up = light/active, Down = dark/passive.',
                rule4: '<strong>135+ primitives</strong> in 12 fixed categories.',
                rule5: '<strong>Order:</strong> Existence → Size → Physics → Material → Shape → Color → Action → Relation → Value → Quantity → Space → Time',
                rule6: '<strong>Flexible:</strong> 2–12 primitives per word.',
                rule7: '<strong>Community:</strong> <a href="https://github.com/tihon0392-boop/solres_language/discussions" target="_blank" style="color:var(--accent);">GitHub Discussions</a>',
                
            }
        };
        let currentLang = 'en';
        function t(key) { return (LANG[currentLang] && LANG[currentLang][key]) || key; }
        function changeLanguage() {
            currentLang = document.getElementById('langSelect').value;
            applyLanguage();
        }
        function applyLanguage() {
            // Вкладки и кнопки с data-lang
            document.querySelectorAll('[data-lang]').forEach(el => {
                const value = t(el.dataset.lang);
                if (value && value.includes('<')) {
                    el.innerHTML = value;
                } else if (value) {
                    el.textContent = value;
                }
            });
    
            // Перевод категорий в таблице примитивов
            const catMap = LANG.categories || {};
            document.querySelectorAll('#primitivesTable .badge').forEach(badge => {
                const ruText = badge.textContent.trim();
                if (currentLang === 'en' && catMap[ruText]) {
                    badge.textContent = catMap[ruText];
                } else if (currentLang === 'ru') {
                    for (const [ru, en] of Object.entries(catMap)) {
                        if (badge.textContent.trim() === en) badge.textContent = ru;
                    }
                }
            });
            // Перевод примитивов в выпадающих списках Compose
            const pn = LANG.primitiveNames || {};
            document.querySelectorAll('.compose-row .dropdown-list div').forEach(div => {
                const ruText = div.textContent.trim();
                if (currentLang === 'en' && pn[ruText]) {
                    div.textContent = pn[ruText];
                } else if (currentLang === 'ru') {
                    for (const [ru, en] of Object.entries(pn)) {
                        if (div.textContent.trim() === en) div.textContent = ru;
                    }
                }
            });
    
            
    
            // Placeholder-ы
            document.getElementById('wordInput').placeholder = t('typeWord');
            document.getElementById('sentenceName').placeholder = t('sentenceName');
            document.getElementById('composeWordName').placeholder = t('wordName');
            document.getElementById('dictSearch').placeholder = t('search');
    
            // Кнопка темы
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = t(theme === 'dark' ? 'light' : 'dark');
    
            // Туториал
            const tut = document.getElementById('tutorialOverlay');
            if (tut) {
                tut.querySelector('h2').textContent = t('welcome');
                const ps = tut.querySelectorAll('p');
                for (let i = 1; i <= 9; i++) {
                    if (ps[i-1]) ps[i-1].innerHTML = t('tutorial' + i);
                }
                const btn2 = tut.querySelector('button');
                if (btn2) btn2.textContent = t('getStarted');
            }
    
            // Пианино placeholder
            const seq = document.getElementById('pianoSequence');
            if (seq && seq.style.color === 'var(--muted)') seq.textContent = t('recordMelody');
    
            // Заглушки Translate
            const result = document.getElementById('result');
            if (result && result.querySelector('div[style]')) {
                result.querySelector('div').textContent = t('typeWord');
            }
        }

        // === STARFIELD ===
        const canvas = document.getElementById('starfield'), ctx = canvas.getContext('2d'); let bodies = [];
        function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        window.addEventListener('resize', () => { resizeCanvas(); createBodies(); });
        function random(min, max) { return Math.random() * (max - min) + min; }
        function createBodies() { bodies = []; for (let i = 0; i < 200; i++) { bodies.push({x: random(0, canvas.width), y: random(0, canvas.height), r: random(0.8, 4.5), baseOpacity: random(0.15, 1.0), phase: random(0, Math.PI*2), period: random(300, 2000), alive: true, respawnTime: 0}); } }
        function drawBodies() { ctx.clearRect(0, 0, canvas.width, canvas.height); const isLight = theme === 'light', now = Date.now(); bodies.forEach(b => { if (!b.alive) { if (now > b.respawnTime) { b.alive = true; b.baseOpacity = random(0.15, 1.0); b.r = random(0.8, 4.5); } return; } const twinkle = Math.sin(now / 1000 * (2 * Math.PI) / (b.period / 1000) + b.phase) * 0.3 + 0.7, alpha = b.baseOpacity * twinkle; if (isLight) { ctx.fillStyle = `rgba(${Math.floor(alpha*30)},${Math.floor(alpha*30)},${Math.floor(alpha*30)},${alpha})`; ctx.shadowColor = `rgba(0,0,0,${alpha*0.95})`; } else { const br = Math.floor(180 + alpha*75); ctx.fillStyle = `rgba(${br},${br},${Math.floor(br*0.85)},${alpha})`; ctx.shadowColor = `rgba(255,240,220,${alpha*0.7})`; } ctx.shadowBlur = b.r*3; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); }); ctx.shadowBlur = 0; requestAnimationFrame(drawBodies); }
        canvas.addEventListener('click', (e) => { const rect = canvas.getBoundingClientRect(), mx = e.clientX - rect.left, my = e.clientY - rect.top; for (let b of bodies) { if (!b.alive) continue; if (Math.sqrt((b.x-mx)**2 + (b.y-my)**2) < b.r + 10) { b.alive = false; b.respawnTime = Date.now() + 10000; break; } } });
        resizeCanvas(); createBodies(); drawBodies();
        function toggleTheme() { 
            const btn = document.getElementById('themeBtn'); 
            if (theme === 'dark') { 
                theme = 'light'; 
                document.body.classList.add('light-theme'); 
            } else { 
                theme = 'dark'; 
                document.body.classList.remove('light-theme'); 
            } 
            btn.textContent = t(theme === 'dark' ? 'light' : 'dark'); 
        }

        // === TABS ===
        function switchTab(tab) { document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.querySelectorAll('.card').forEach(c => c.style.display = 'none'); document.getElementById('tab-' + tab).style.display = 'block'; event.target.classList.add('active'); if (tab === 'mywords') loadMyWords(); if (tab === 'community') loadCommunityWords(); if (tab === 'sentences') { loadSentenceRows(); document.getElementById('sentenceEmpty').style.display = 'none'; } if (tab === 'text') loadText(); if (tab === 'instruments') buildPiano(); }

        // === STORAGE ===
        function getMyWords() { try { return JSON.parse(localStorage.getItem('solres_mywords') || '[]'); } catch(e) { return []; } }
        function saveMyWords(w) { localStorage.setItem('solres_mywords', JSON.stringify(w)); }
        function getSentences() { try { return JSON.parse(localStorage.getItem('solres_sentences') || '[]'); } catch(e) { return []; } }
        function saveSentences(s) { localStorage.setItem('solres_sentences', JSON.stringify(s)); }

        // === SPEED ===
        function updateSpeedLabel(sliderId, labelId) { const val = parseFloat(document.getElementById(sliderId).value).toFixed(1); document.getElementById(labelId).textContent = val + 'x'; }
        function getSpeed(id) { return parseFloat(document.getElementById(id).value) || 1.0; }
        function showToast(msg) {
            let toast = document.getElementById('toast');
            if (!toast) {
                toast = document.createElement('div');
                toast.id = 'toast';
                toast.className = 'toast';
                document.body.appendChild(toast);
            }
            toast.textContent = msg;
            toast.classList.add('show');
            clearTimeout(toast._timeout);
            toast._timeout = setTimeout(() => toast.classList.remove('show'), 2000);
        }
        function showPrompt(title, placeholder, callback) {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.innerHTML = `
                <div class="modal-box">
                    <h3 style="color:var(--accent);margin-bottom:8px;">${title}</h3>
                    <input type="text" id="modalInput" placeholder="${placeholder}" autofocus>
                    <div style="display:flex;gap:8px;justify-content:center;">
                        <button class="btn btn-primary" data-lang="ok" id="modalOk">OK</button>
                        <button class="btn btn-sm" data-lang="cancel" id="modalCancel">Cancel</button>
                    </div>
                </div>`;
            document.body.appendChild(overlay);
            
            const input = overlay.querySelector('#modalInput');
            overlay.querySelector('#modalOk').onclick = () => {
                const val = input.value.trim();
                document.body.removeChild(overlay);
                callback(val);
            };
            overlay.querySelector('#modalCancel').onclick = () => {
                document.body.removeChild(overlay);
                callback(null);
            };
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const val = input.value.trim();
                    document.body.removeChild(overlay);
                    callback(val);
                }
                if (e.key === 'Escape') {
                    document.body.removeChild(overlay);
                    callback(null);
                }
            });
            input.focus();
        }
        function showPatternInfo(pattern) {
            const parts = pattern.split(',');
            let info = parts.map(p => {
                if (p.endsWith('_UP')) return p.replace('_UP', '') + ' ↑';
                if (p.endsWith('_DOWN')) return p.replace('_DOWN', '') + ' ↓';
                if (p.endsWith('_STATIC')) return p.replace('_STATIC', '') + ' →';
                return p;
            }).join(' + ');
            showToast(pattern + ' = ' + info);
        }

        // === TRANSLATE ===
        async function translateWord() { const word = document.getElementById('wordInput').value.trim(); if (!word) return; currentWord = word; const res = await fetch('/translate?word=' + encodeURIComponent(word)); const data = await res.json(); let html = ''; if (data.error) { html = '<div class="error-msg">' + data.error + '</div>'; } else { if (data.description) { html += '<div class="desc-row">'; data.description.forEach(d => { html += '<span>' + d + '</span> '; }); html += '</div>'; } html += '<div class="notes-display">' + data.notes + '</div>'; if (data.meaning && data.meaning !== 'not found') { html += '<div class="meaning">' + data.meaning + '</div>'; } } document.getElementById('result').innerHTML = html; if (!data.error) playAudio(); }
        async function playAudio() { if (!currentWord) return; const r = await fetch('/play?word=' + encodeURIComponent(currentWord) + '&speed=' + getSpeed('speedSlider')); const p = document.getElementById('audioPlayer'); p.style.display = 'block'; p.src = URL.createObjectURL(await r.blob()); p.play(); }

        // === DICTIONARY ===
        function filterDict() { const q = document.getElementById('dictSearch').value.toLowerCase(); document.querySelectorAll('#primitivesTable tbody tr, #wordsTable tbody tr').forEach(tr => { tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none'; }); }
        function playDictWord(word) { document.getElementById('wordInput').value = word; switchTab('translate'); translateWord(); }

        // === DROPDOWN ===
        function buildDropdown(list, items, input) { list.innerHTML = items.map((item, i) => `<div data-idx="${i}" onmousedown="selectDropdown(this, '${item.replace(/'/g, "\\'")}')">${item}</div>`).join(''); }
        function toggleDropdown(input, show) { const list = input.parentElement.querySelector('.dropdown-list'); list.style.display = show ? 'block' : 'none'; if (show) filterDropdown(input); }
        function filterDropdown(input) { const list = input.parentElement.querySelector('.dropdown-list'); const q = input.value.toLowerCase(); list.querySelectorAll('div').forEach(d => { d.style.display = d.textContent.toLowerCase().includes(q) ? '' : 'none'; }); list.style.display = 'block'; }
        function selectDropdown(div, word) { const input = div.parentElement.parentElement.querySelector('input'); input.value = word; div.parentElement.style.display = 'none'; if (typeof validateCompose === 'function') validateCompose(); }

        // === COMPOSE ===
        function buildComposeGrid() { const g = document.getElementById('composeGrid'); g.innerHTML = ''; CATEGORY_ORDER.forEach((cat, i) => { const words = CATEGORIES[cat] || []; const row = document.createElement('div'); row.className = 'compose-row'; row.id = 'compose-row-' + i; row.innerHTML = `<span class="cat-label">${cat.split(':').pop()}</span><div class="dropdown-search"><input type="text" placeholder="—" onfocus="toggleDropdown(this,true)" oninput="filterDropdown(this)" onblur="setTimeout(()=>toggleDropdown(this,false),200)"><div class="dropdown-list"></div></div><button class="btn-xs" data-lang="info" onclick="showIntervalInfo('${cat}', event)">ℹ️</button>`; g.appendChild(row); buildDropdown(row.querySelector('.dropdown-list'), words, row.querySelector('input')); }); }
        function showIntervalInfo(cat, e) { const sample = CATEGORIES[cat]?.[0]; if (sample && PRIMITIVE_INFO[sample]) { const t = document.createElement('div'); t.style.cssText = 'position:absolute;background:var(--surface2);color:var(--text);padding:8px 12px;border-radius:8px;font-size:0.8em;z-index:10;border:1px solid var(--accent);'; t.textContent = 'Interval: ' + PRIMITIVE_INFO[sample].pattern; document.body.appendChild(t); t.style.left = e.clientX + 'px'; t.style.top = (e.clientY - 40) + 'px'; setTimeout(() => t.remove(), 2000); } }
        function getSelectedPrimitives() { const s = []; CATEGORY_ORDER.forEach((cat, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (inp && inp.value && CATEGORIES[cat]?.includes(inp.value)) s.push({word: inp.value, category: cat, index: i}); }); return s; }
        function validateCompose() { const selected = getSelectedPrimitives(); let lastIdx = -1, valid = true; CATEGORY_ORDER.forEach((_, i) => { const row = document.getElementById('compose-row-' + i); if (row) row.classList.remove('invalid'); }); for (const s of selected) { const catIdx = CATEGORY_ORDER.indexOf(s.category); if (catIdx < lastIdx) { valid = false; document.getElementById('compose-row-' + s.index).classList.add('invalid'); } lastIdx = catIdx; } document.getElementById('composeError').innerHTML = ''; return {valid, selected}; }
        async function composePlay() { const {valid, selected} = validateCompose(); if (selected.length < 2) { document.getElementById('composeError').innerHTML = '<div class="error-msg">Select at least 2 primitives</div>'; return; } if (!valid) { document.getElementById('composeError').innerHTML = '<div class="error-msg">Category order violated!</div>'; return; } const words = selected.map(s => s.word); const res = await fetch('/compose?words=' + encodeURIComponent(words.join(','))); const data = await res.json(); document.getElementById('composeResult').innerHTML = `<div class="desc-row">${words.map(w => '<span>' + w + '</span>').join(' ')}</div><div class="notes-display">${data.notes}</div>`; const ar = await fetch('/compose_play?words=' + encodeURIComponent(words.join(',')) + '&speed=' + getSpeed('composeSpeed')); const p = document.getElementById('composeAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await ar.blob()); p.play(); }
        function composeRandom() { CATEGORY_ORDER.forEach((cat, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (!inp.value) { const w = CATEGORIES[cat] || []; if (w.length && Math.random() > 0.6) inp.value = w[Math.floor(Math.random()*w.length)]; } }); validateCompose(); }
        function composeClear() { CATEGORY_ORDER.forEach((_, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (inp) inp.value = ''; }); document.getElementById('composeResult').innerHTML = ''; document.getElementById('composeError').innerHTML = ''; document.getElementById('composeAudio').style.display = 'none'; validateCompose(); }
        function saveComposedWord() { const {selected} = validateCompose(); if (selected.length < 2) return; const name = document.getElementById('composeWordName').value.trim() || 'word_' + Date.now(); const words = selected.map(s => s.word); const myWords = getMyWords(); myWords.push({name, primitives: words, source: '🧩 Compose', created: new Date().toISOString()}); saveMyWords(myWords); document.getElementById('composeError').innerHTML = '<div class="success-msg">Saved: ' + name + '</div>'; document.getElementById('composeWordName').value = ''; }
        buildComposeGrid();

        // === PIANO === 
        function buildPiano() { 
            const mobile = window.innerWidth <= 600;
            const WHITE_W = mobile ? 20 : 36;
            const BLACK_W = mobile ? 13 : 20;
            const WHITE_H = mobile ? 70 : 130;
            const BLACK_H = mobile ? 44 : 82;
            const piano = document.getElementById('piano'); 
            piano.innerHTML = ''; 
            piano.style.width = (14 * WHITE_W) + 'px';
            piano.style.height = WHITE_H + 'px';
            const startMidi = (pianoOctave + 1) * 12;
            const whiteSemitones = [0,2,4,5,7,9,11]; 
            for (let oct = 0; oct < 2; oct++) { 
                for (let w = 0; w < 7; w++) { 
                    const midi = startMidi + oct*12 + whiteSemitones[w]; 
                    const noteIdx = midi % 12, octave = Math.floor(midi/12)-1; 
                    const key = document.createElement('div'); 
                    key.className = 'white-key'; 
                    key.style.left = (oct*7 + w)*WHITE_W + 'px'; 
                    key.style.width = WHITE_W + 'px'; 
                    key.style.height = WHITE_H + 'px'; 
                    key.style.fontSize = (mobile ? '0.25em' : '0.5em');
                    key.textContent = NOTE_NAMES[noteIdx].split('/')[0] + octave; 
                    key.dataset.midi = midi; 
                    key.onclick = () => pianoKeyClick(midi, NOTE_NAMES[noteIdx].split('/')[0] + octave); 
                    piano.appendChild(key); 
                } 
            } 
            const blackPositions = [{wi:0, mo:1},{wi:1, mo:3},{wi:3, mo:6},{wi:4, mo:8},{wi:5, mo:10}]; 
            for (let oct = 0; oct < 2; oct++) { 
                for (let bp of blackPositions) { 
                    const midi = startMidi + oct*12 + bp.mo; 
                    const noteIdx = midi % 12, octave = Math.floor(midi/12)-1; 
                    const key = document.createElement('div'); 
                    key.className = 'black-key'; 
                    key.style.left = ((oct*7 + bp.wi)*WHITE_W + WHITE_W - BLACK_W/2) + 'px'; 
                    key.style.width = BLACK_W + 'px'; 
                    key.style.height = BLACK_H + 'px'; 
                    key.style.fontSize = (mobile ? '0.2em' : '0.35em');
                    key.textContent = NOTE_NAMES[noteIdx]; 
                    key.dataset.midi = midi; 
                    key.onclick = (e) => { e.stopPropagation(); pianoKeyClick(midi, NOTE_NAMES[noteIdx].split('/')[0] + octave); }; 
                    piano.appendChild(key); 
                } 
            } 
            updatePianoRangeLabel(); 
        }
        function updatePianoRangeLabel() { const startMidi = (pianoOctave + 1) * 12; const s = NOTE_NAMES[startMidi%12].split('/')[0] + (Math.floor(startMidi/12)-1); const e = NOTE_NAMES[(startMidi+23)%12].split('/')[0] + (Math.floor((startMidi+23)/12)-1); document.getElementById('pianoRangeLabel').textContent = s + ' – ' + e; }
        function pianoShiftOctave(dir) { pianoOctave += dir; if (pianoOctave < 0) pianoOctave = 0; if (pianoOctave > 5) pianoOctave = 5; buildPiano(); }
        async function pianoKeyClick(midi, noteName) { pianoSequence.push({midi, noteName}); updatePianoSequenceDisplay(); const keys = document.querySelectorAll('#piano div[data-midi="' + midi + '"]'); keys.forEach(k => k.classList.add('active')); setTimeout(() => keys.forEach(k => k.classList.remove('active')), 300); const r = await fetch('/piano_note?midi=' + midi + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await r.blob())).play(); }
        function updatePianoSequenceDisplay() {
            const div = document.getElementById('pianoSequence');
            if (pianoSequence.length === 0) {
                div.textContent = 'Click keys to record a melody...';
                div.style.color = 'var(--muted)';
            } else {
                div.innerHTML = pianoSequence.map((s, i) => {
                    if (s.noteName === '⏸') return '<span style="color:var(--accent);">|</span>';
                    const prev = i > 0 ? pianoSequence[i-1] : null;
                    let interval = '';
                    if (prev && prev.noteName !== '⏸') {
                        const diff = s.midi - prev.midi;
                        interval = `<span style="color:var(--muted);font-size:0.7em;"> [${diff>0?'+':''}${diff}]</span>`;
                    }
                    return `<span style="color:var(--accent2);cursor:pointer;" onclick="pianoRemoveNote(${i})">${s.noteName}</span>${interval}`;
                }).join(' → ');
                div.style.color = '';
            }
        }
        function pianoUndoLastNote() { pianoSequence.pop(); updatePianoSequenceDisplay(); }
        function pianoRemoveNote(idx) { pianoSequence.splice(idx, 1); updatePianoSequenceDisplay(); }
        function pianoRemoveNote(idx) { pianoSequence.splice(idx, 1); updatePianoSequenceDisplay(); }
        function pianoAddPause() { pianoSequence.push({midi: null, noteName: '⏸'}); updatePianoSequenceDisplay(); }
        async function pianoPlaySequence() { if (pianoSequence.length === 0) return; const midis = pianoSequence.map(s => s.midi); for (let i = 0; i < midis.length; i++) { setTimeout(() => { const keys = document.querySelectorAll('#piano div[data-midi="' + midis[i] + '"]'); keys.forEach(k => k.classList.add('active')); setTimeout(() => keys.forEach(k => k.classList.remove('active')), 350); }, i * 400 / getSpeed('pianoSpeed')); } const r = await fetch('/piano_play?notes=' + encodeURIComponent(midis.join(',')) + '&speed=' + getSpeed('pianoSpeed') + '&instrument=' + currentInstrument); const p = document.getElementById('pianoAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await r.blob()); p.play(); analyzeIntervals(midis); }
        async function analyzeIntervals(midis) {
            // Разбиваем на группы по паузам (midi === null)
            const groups = [];
            let currentGroup = [];
            for (let i = 0; i < pianoSequence.length; i++) {
                if (pianoSequence[i].noteName === '⏸') {
                    if (currentGroup.length >= 2) groups.push(currentGroup);
                    currentGroup = [];
                } else {
                    currentGroup.push(pianoSequence[i].midi);
                }
            }
            if (currentGroup.length >= 2) groups.push(currentGroup);
    
            if (groups.length === 0) {
                document.getElementById('pianoAnalysis').innerHTML = '<div class="error-msg">Need at least 2 notes in a group.</div>';
                return;
            }
    
            let allHtml = '';
            let allPrimitivesList = [];
            for (const group of groups) {
                const intervals = [];
                for (let i = 1; i < group.length; i++) intervals.push(group[i] - group[i-1]);
                const r = await fetch('/analyze?intervals=' + encodeURIComponent(intervals.join(',')));
                const data = await r.json();
                lastAnalysis = data; 
                let html = '<table class="analysis-table"><thead><tr><th data-lang="note">Note</th><th data-lang="interval">Interval</th><th data-lang="primitive">Primitive</th></tr></thead><tbody>';
                for (let i = 0; i < intervals.length; i++) { 
                    const diff = intervals[i], a = data.results[i]; 
                    let found = false;
                    let text = '—';
                    if (a && a.options) {
                        found = true;
                        text = a.options.map(o => {
                            const name = currentLang === 'en' ? (LANG.primitiveNames[o.ru] || o.en || o.ru) : o.ru;
                            return name;
                        }).join(', ');
                    } else if (a && a.found) {
                        found = true;
                        text = currentLang === 'en' ? (LANG.primitiveNames[a.ru] || a.en || a.ru) : a.ru;
                    }
                    html += `<tr><td>${pianoSequence[i+1].noteName}</td><td class="${found?'found':'not-found'}">${diff>0?'+':''}${diff}</td><td class="${found?'found':'not-found'}">${text}</td></tr>`; 
                } 
                html += '</tbody></table>'; 
                if (data.word_found) html += `<div class="meaning" style="margin-top:8px;">✅ Word: <strong>${data.word_found}</strong></div>`;
                else if (data.all_found) {
                    const prims = data.primitives_ru.map(r => {
                        return currentLang === 'en' ? (LANG.primitiveNames[r] || r) : r;
                    }).join(' + ');
                    html += `<div class="desc-row" style="margin-top:8px;">Primitives: ${prims}</div>`;
                }
                else html += `<div class="error-msg" style="margin-top:8px;">Some intervals not found.</div>`; 
                html += `<div style="text-align:center;margin-top:8px;"><button class="btn btn-sm" data-lang="saveAsWord" onclick="savePianoAsWord()">💾 Save as My Word</button></div>`; 
                allHtml += html;
                if (data.primitives_ru) allPrimitivesList = allPrimitivesList.concat(data.primitives_ru);
            }
            document.getElementById('pianoAnalysis').innerHTML = allHtml;
        }
        
        function savePianoAsWord() {
            if (!lastAnalysis || !lastAnalysis.primitives_ru || lastAnalysis.primitives_ru.length < 2) return;
            showPrompt('Word name', 'Enter word name...', function(name) {
                if (!name) return;
                const myWords = getMyWords();
                myWords.push({name, primitives: lastAnalysis.primitives_ru, source: '🎹 Instruments', created: new Date().toISOString()});
                saveMyWords(myWords);
                document.getElementById('pianoSaveArea').innerHTML = '<div class="success-msg">Saved: ' + name + '</div>';
                showToast('Saved: ' + name);
            });
        }
        function pianoClearSequence() { pianoSequence = []; updatePianoSequenceDisplay(); document.getElementById('pianoAudio').style.display = 'none'; document.getElementById('pianoAnalysis').innerHTML = ''; document.getElementById('pianoSaveArea').innerHTML = ''; lastAnalysis = null; }
        function pianoToCompose() { if (pianoSequence.length < 2) return; const intervals = []; for (let i = 1; i < pianoSequence.length; i++) intervals.push(pianoSequence[i].midi - pianoSequence[i-1].midi); switchTab('compose'); document.getElementById('composeError').innerHTML = `<div style="color:var(--accent);text-align:center;margin-top:10px;">Intervals from Piano: ${intervals.map(i=>(i>0?'+':'')+i).join(', ')}</div>`; }
        function instrumentChanged() { currentInstrument = document.getElementById('instrumentSelect').value; }
        // === KEYBOARD BINDINGS ===
        const KEY_MAP = {
            'KeyA': 0, 'KeyW': 1, 'KeyS': 2, 'KeyE': 3, 'KeyD': 4,
            'KeyF': 5, 'KeyT': 6, 'KeyG': 7, 'KeyY': 8, 'KeyH': 9,
            'KeyU': 10, 'KeyJ': 11, 'KeyK': 12
        };
        
        document.addEventListener('keydown', (e) => {
            // Блокируем клавиши пианино только если фокус в основных полях сайта
            const focusedId = e.target.id;
            if (focusedId === 'wordInput' || focusedId === 'dictSearch' || 
                focusedId === 'sentenceName' || focusedId === 'composeWordName') return;
            if (e.repeat) return;
            if (e.code === 'Space') { e.preventDefault(); pianoAddPause(); return; }
            if (e.code === 'ArrowLeft') { pianoShiftOctave(-1); return; }
            if (e.code === 'ArrowRight') { pianoShiftOctave(1); return; }
            if (e.code === 'Enter') { e.preventDefault(); pianoPlaySequence(); return; }
            if (e.code === 'KeyP') { e.preventDefault(); pianoAddPause(); return; }
            if (e.code === 'Backspace') {
                e.preventDefault();
                if (!backspaceTimer) {
                    backspaceTimer = setTimeout(() => {
                        pianoClearSequence();
                        backspaceTimer = null;
                    }, 3000);
                }
                return;
            }
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Backspace') {
                if (backspaceTimer) {
                    clearTimeout(backspaceTimer);
                    backspaceTimer = null;
                    pianoUndoLastNote();
                }
            }
        });
            
            const semitoneOffset = KEY_MAP[e.code];
            if (semitoneOffset !== undefined) {
                const startMidi = (pianoOctave + 1) * 12;
                const midi = startMidi + semitoneOffset;
                const noteIdx = midi % 12;
                const noteName = NOTE_NAMES[noteIdx].split('/')[0];
                const octave = Math.floor(midi / 12) - 1;
                pianoKeyClick(midi, noteName + octave);
            }
        });
        buildPiano();

        // === MY WORDS ===
        function loadMyWords() { const words = getMyWords(); let html = ''; words.forEach((w, i) => { html += `<tr><td>${w.name}</td><td>${(w.primitives||[]).join(', ')}</td><td><span class="badge ${w.source==='📖 System'?'badge-system':'badge-user'}">${w.source||'?'}</span></td><td><button class="btn-sm" onclick="playMyWord(${i})">▶</button></td><td><button class="btn-sm" onclick="publishMyWord(${i})" title="Publish">🌐</button></td><td><button class="btn-sm btn-danger" onclick="deleteMyWord(${i})">✕</button></td></tr>`; }); document.querySelector('#myWordsTable tbody').innerHTML = html || '<tr><td colspan="6" style="text-align:center;color:var(--muted);">No saved words yet.</td></tr>'; }
        async function playMyWord(idx) { const words = getMyWords(); if (!words[idx]) return; const ar = await fetch('/compose_play?words=' + encodeURIComponent((words[idx].primitives||[]).join(',')) + '&speed=' + getSpeed('mywordsSpeed') + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }
        async function publishMyWord(idx) {
            const words = getMyWords(); if (!words[idx]) return; const w = words[idx];
            showPrompt('Your name', 'Enter your name...', async function(author) {
                author = author || 'Anonymous';
                await fetch('/shared/words/add', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json', 'X-SolRes-Key': SECRET_KEY}, 
                    body: JSON.stringify({name: w.name, primitives: w.primitives, source: w.source, created: w.created, author}) 
                });
                showToast('Published: ' + w.name);
            });
        }
        function deleteMyWord(idx) { const words = getMyWords(); words.splice(idx, 1); saveMyWords(words); loadMyWords(); }
        function clearMyWords() { if (confirm('Delete all?')) { saveMyWords([]); loadMyWords(); } }

        // === COMMUNITY ===
        async function loadCommunityWords() {
            const r = await fetch('/shared/words'); const words = await r.json(); let html = '';
            words.forEach(w => { const score = (w.likes||0)-(w.dislikes||0);
                html += `<tr><td>${w.name}</td><td>${(w.primitives||[]).join(', ')}</td><td><span class="badge badge-community">${w.author||'Anonymous'}</span></td><td style="white-space:nowrap;"><button class="btn-xs" onclick="voteWord(${w.id},'like')">👍 ${w.likes||0}</button><span style="margin:0 4px;color:${score>=0?'var(--green)':'var(--red)'};">${score}</span><button class="btn-xs" onclick="voteWord(${w.id},'dislike')">👎 ${w.dislikes||0}</button></td><td><button class="btn-sm" onclick="playCommunityWord('${(w.primitives||[]).join(',')}')">▶</button></td></tr>`; });
            document.querySelector('#communityTable tbody').innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--muted);">No community words yet.</td></tr>';
        }
        let communityTab = 'words';
        function switchCommunityTab(tab) { communityTab = tab; document.querySelectorAll('#tab-community .tab').forEach(t => t.classList.remove('active')); event.target.classList.add('active'); document.getElementById('community-words').style.display = tab==='words'?'block':'none'; document.getElementById('community-sentences').style.display = tab==='sentences'?'block':'none'; document.getElementById('community-text').style.display = tab==='text'?'block':'none'; if (tab==='words') loadCommunityWords(); if (tab==='sentences') loadCommunitySentences(); if (tab==='text') loadCommunityText(); }
        async function loadCommunitySentences() {
            const r = await fetch('/shared/sentences'); const sentences = await r.json(); let html = '';
            sentences.forEach(s => { const score = (s.likes||0)-(s.dislikes||0);
                html += `<tr><td>${s.name}</td><td>${(s.words||[]).join(', ')}</td><td><span class="badge badge-community">${s.author||'Anonymous'}</span></td><td style="white-space:nowrap;"><button class="btn-xs" onclick="voteSentence(${s.id},'like')">👍 ${s.likes||0}</button><span style="margin:0 4px;color:${score>=0?'var(--green)':'var(--red)'};">${score}</span><button class="btn-xs" onclick="voteSentence(${s.id},'dislike')">👎 ${s.dislikes||0}</button></td><td><button class="btn-sm" onclick="playCommunitySentence('${(s.words||[]).join(',')}')">▶</button></td></tr>`; });
            document.querySelector('#communitySentencesTable tbody').innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px;">No published sentences yet.</td></tr>';
        }
        async function loadCommunityText() {
            const r = await fetch('/shared/text');
            const texts = await r.json();
            let html = '';
            texts.forEach(t => {
                const score = (t.likes||0)-(t.dislikes||0);
                html += `<tr><td>${t.name}</td><td>${(t.sentences||[]).join(' | ')}</td><td><span class="badge badge-community">${t.author||'Anonymous'}</span></td><td style="white-space:nowrap;"><button class="btn-xs" onclick="voteText(${t.id},'like')">👍 ${t.likes||0}</button><span style="margin:0 4px;color:${score>=0?'var(--green)':'var(--red)'};">${score}</span><button class="btn-xs" onclick="voteText(${t.id},'dislike')">👎 ${t.dislikes||0}</button></td><td><button class="btn-sm" onclick='playCommunityText(${JSON.stringify(t.sentences)})'>▶</button></td></tr>`;
            });
            document.querySelector('#communityTextTable tbody').innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px;">No published texts yet.</td></tr>';
        }
        async function voteText(id, type) { await fetch('/shared/text/'+id+'/'+type, {method:'POST'}); loadCommunityText(); }
        async function playCommunityText(sentences) {
            const allWords = getAllWordsForSelect();
            for (const sentName of sentences) {
                const sent = getSentences().find(s => s.name === sentName);
                if (!sent) continue;
                let allPrims = [];
                sent.words.forEach(wordName => {
                    const w = allWords.find(aw => aw.name === wordName);
                    if (w) allPrims = allPrims.concat(w.primitives || []);
                });
                if (allPrims.length === 0) continue;
                    const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('communitySpeed') + '&instrument=' + currentInstrument);
                const a = new Audio(URL.createObjectURL(await ar.blob()));
                a.play();
                await new Promise(r => { a.onended = r; });
            }
        }
        async function voteWord(id, type) { await fetch('/shared/words/'+id+'/'+type, {method:'POST'}); loadCommunityWords(); }
        async function voteSentence(id, type) { await fetch('/shared/sentences/'+id+'/'+type, {method:'POST'}); if (communityTab==='sentences') loadCommunitySentences(); else loadCommunityText(); }
        async function playCommunityWord(primitives) { const ar = await fetch('/compose_play?words='+encodeURIComponent(primitives)+'&speed='+getSpeed('communitySpeed')+'&instrument='+currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }
        async function playCommunitySentence(wordsStr) { const ar = await fetch('/compose_play?words='+encodeURIComponent(wordsStr)+'&speed='+getSpeed('communitySpeed')+'&instrument='+currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }

        // === SENTENCES ===
        function getAllWordsForSelect() { const myWords = getMyWords(); const dictWords = Object.entries(DICTIONARY_WORDS).map(([name, data]) => ({name, primitives: data.ru, source: '📖 System'})); return [...dictWords, ...myWords]; }
        function loadSentenceRows() { document.getElementById('sentenceRows').innerHTML = ''; addSentenceRow(); }
        function addSentenceRow() { const allWords = getAllWordsForSelect(); const container = document.getElementById('sentenceRows'); const row = document.createElement('div'); row.className = 'sentence-row'; row.draggable = true; row.innerHTML = `<span class="drag-handle" draggable="true">⋮⋮</span><div class="dropdown-search"><input type="text" placeholder="🔍 Search word..." onfocus="toggleDropdown(this, true)" oninput="filterDropdown(this)" onblur="setTimeout(()=>toggleDropdown(this,false),200)"><div class="dropdown-list"></div></div><button class="btn-sm btn-danger" onclick="this.parentElement.remove()">✕</button>`; row.addEventListener('dragstart', (e) => { e.dataTransfer.setData('text/plain', Array.from(container.children).indexOf(row)); row.classList.add('dragging'); }); row.addEventListener('dragend', () => row.classList.remove('dragging')); row.addEventListener('dragover', (e) => { e.preventDefault(); row.classList.add('drag-over'); }); row.addEventListener('dragleave', () => row.classList.remove('drag-over')); row.addEventListener('drop', (e) => { e.preventDefault(); row.classList.remove('drag-over'); const from = parseInt(e.dataTransfer.getData('text/plain')); const to = Array.from(container.children).indexOf(row); if (from !== to && from >= 0 && to >= 0) { container.insertBefore(container.children[from], container.children[to + (from < to ? 1 : 0)]); } }); container.appendChild(row); buildDropdown(row.querySelector('.dropdown-list'), allWords.map(w => w.name), row.querySelector('input')); }
        async function playSentence() { const allWords = getAllWordsForSelect(); const selected = []; document.querySelectorAll('#sentenceRows .dropdown-search input').forEach(inp => { if (inp.value) { const w = allWords.find(aw => aw.name === inp.value); if (w) selected.push(w.primitives || []); } }); const allPrims = selected.flat(); if (allPrims.length === 0) return; const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('sentSpeed')); const p = document.getElementById('sentenceAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await ar.blob()); p.play(); }
        function saveSentence() { const name = document.getElementById('sentenceName').value.trim() || 'sentence_' + Date.now(); const wordNames = []; document.querySelectorAll('#sentenceRows .dropdown-search input').forEach(inp => { if (inp.value) wordNames.push(inp.value); }); if (wordNames.length < 2) return; const sentences = getSentences(); sentences.push({name, words: wordNames, created: new Date().toISOString()}); saveSentences(sentences); document.getElementById('sentenceName').value = ''; showToast('Saved: ' + name); }
        async function publishSentence() {
            const name = document.getElementById('sentenceName').value.trim() || 'sentence_' + Date.now();
            const allWords = getAllWordsForSelect();
            const wordPrimitives = [];
            document.querySelectorAll('#sentenceRows .dropdown-search input').forEach(inp => {
                if (inp.value) {
                    const w = allWords.find(aw => aw.name === inp.value);
                    if (w) wordPrimitives.push(w.primitives.join(','));
                }
            });
            if (wordPrimitives.length < 2) { showToast('Select at least 2 words'); return; }
            showPrompt('Your name', 'Enter your name...', async function(author) {
                author = author || 'Anonymous';
                await fetch('/shared/sentences/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'X-SolRes-Key': SECRET_KEY},
                    body: JSON.stringify({name, words: wordPrimitives, author, created: new Date().toISOString()})
                });
                showToast('Published: ' + name);
            });
        }
        function clearSentence() { document.getElementById('sentenceRows').innerHTML = ''; addSentenceRow(); document.getElementById('sentenceName').value = ''; }

        // === TEXT ===
        function loadText() { const sentences = getSentences(); const container = document.getElementById('textList'); if (sentences.length === 0) { container.innerHTML = '<div style="text-align:center;color:var(--muted);padding:20px;">No saved sentences yet.</div>'; return; } container.innerHTML = sentences.map((s, i) => `<div class="sentence-row" draggable="true" data-idx="${i}"><span class="drag-handle" draggable="true">⋮⋮</span><span style="flex:1;">${s.name}: ${(s.words||[]).join(', ')}</span><button class="btn-sm" onclick="playTextSentence(${i})">▶</button><button class="btn-sm btn-danger" onclick="deleteTextSentence(${i})">✕</button></div>`).join(''); container.querySelectorAll('.sentence-row').forEach(row => { row.addEventListener('dragstart', (e) => { e.dataTransfer.setData('text/plain', row.dataset.idx); row.classList.add('dragging'); }); row.addEventListener('dragend', () => row.classList.remove('dragging')); row.addEventListener('dragover', (e) => { e.preventDefault(); row.classList.add('drag-over'); }); row.addEventListener('dragleave', () => row.classList.remove('drag-over')); row.addEventListener('drop', (e) => { e.preventDefault(); row.classList.remove('drag-over'); const from = parseInt(e.dataTransfer.getData('text/plain')); const to = parseInt(row.dataset.idx); if (from !== to && !isNaN(from) && !isNaN(to)) { const s = getSentences(); const [moved] = s.splice(from, 1); s.splice(to, 0, moved); saveSentences(s); loadText(); } }); }); }
        async function playText() { 
            const sentences = getSentences(); 
            if (sentences.length === 0) return; 
            const allWords = getAllWordsForSelect(); 
            for (const s of sentences) { 
                const words = s.words.map(name => allWords.find(w => w.name === name)).filter(Boolean); 
                if (words.length === 0) continue; 
                const allPrims = words.flatMap(w => w.primitives || []); 
                const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('textSpeed') + '&instrument=' + currentInstrument); 
                const a = new Audio(URL.createObjectURL(await ar.blob())); 
                a.play(); 
                await new Promise(r => { a.onended = r; }); 
            } 
        }
        async function playTextSentence(idx) { const sentences = getSentences(); if (!sentences[idx]) return; const allWords = getAllWordsForSelect(); const words = sentences[idx].words.map(name => allWords.find(w => w.name === name)).filter(Boolean); if (words.length === 0) return; const allPrims = words.flatMap(w => w.primitives || []); const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('textSpeed') + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }
        function deleteTextSentence(idx) { const s = getSentences(); s.splice(idx, 1); saveSentences(s); loadText(); }
        function clearText() { if (confirm('Delete all?')) { saveSentences([]); loadText(); } }
        async function publishText() {
            const sentences = getSentences();
            if (sentences.length === 0) { showToast('Nothing to publish.'); return; }
            showPrompt('Your name', 'Enter your name...', function(author) {
                author = author || 'Anonymous';
                showPrompt('Text name', 'Enter text name...', async function(name) {
                    name = name || 'text_' + Date.now();
                    const sentNames = sentences.map(s => s.name);
                    await fetch('/shared/text/add', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json', 'X-SolRes-Key': SECRET_KEY},
                        body: JSON.stringify({name, sentences: sentNames, author, created: new Date().toISOString()})
                    });
                    showToast('Published: ' + name);
                });
            });
        }

        // === TUTORIAL ===
        function showTutorial() { const seen = localStorage.getItem('solres_tutorial_seen'); const overlay = document.getElementById('tutorialOverlay'); if (!seen && overlay) { overlay.style.display = 'flex'; } }
        function closeTutorial() { const overlay = document.getElementById('tutorialOverlay'); if (overlay) { overlay.style.display = 'none'; localStorage.setItem('solres_tutorial_seen', '1'); } }

        applyLanguage();
        loadSentenceRows();
    </script>
    <div id="tutorialOverlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:100; align-items:center; justify-content:center;">
        <div style="background:var(--surface); border:1px solid var(--accent); border-radius:16px; padding:30px; max-width:500px; text-align:center; margin:20px;">
            <h2 style="color:var(--accent);">🎵 Welcome to SolRes!</h2>
            <div style="text-align:left; line-height:2; font-size:0.9em; color:var(--text);">
                <p>🔍 <b>Translate</b> — type a word, hear its melody</p>
                <p>🧩 <b>Compose</b> — build words from 135+ primitives</p>
                <p>🎸 <b>Instruments</b> — play piano, analyze intervals</p>
                <p>📝 <b>My Words</b> — save your custom words</p>
                <p>🌐 <b>Community</b> — explore words from others</p>
                <p>💬 <b>Sentences</b> — chain words together</p>
                <p>📄 <b>Text</b> — build text from sentences</p>
                <p>⚡ <b>Speed slider</b> — adjust playback speed</p>
                <p>☀️ <b>Theme toggle</b> — switch dark/light mode</p>
            </div>
            <button class="btn btn-primary" data-lang="getStarted" onclick="closeTutorial()" style="margin-top:20px; width:100%;">🚀 Get Started!</button>
        </div>
    </div>
    <script>showTutorial();</script>
</body>
</html>
"""


def _build_primitives_rows():
    rows = []
    for e in primitives.primitives.values():
        rows.append(
            f"<tr><td><span class='badge'>{e['category']}</span></td><td>{e['ru']}</td><td>{e['en']}</td>"
            f"<td style='font-family:monospace;font-size:0.8em;color:var(--accent);cursor:pointer;' "
            f"onclick=\"showPatternInfo('{e['pattern']}')\" title='Click to see intervals'>{e['pattern']}</td></tr>")
    return '\n'.join(rows)


def _build_words_rows():
    rows = []
    for word, data in sorted(descriptors.descriptions.items()):
        desc = ' + '.join(data['ru'])
        rows.append(
            f"<tr><td>{word}</td><td>{data['en']}</td><td style='font-size:0.85em;'>{desc}</td><td><button class='btn-sm' onclick='playDictWord(\"{word}\")'>▶</button></td></tr>")
    return '\n'.join(rows)


def _build_categories_json():
    import json;
    cats = {}
    for e in primitives.primitives.values():
        cats.setdefault(e['category'], []).append(e['ru'])
    return json.dumps(cats, ensure_ascii=False)


def _build_category_order_json():
    import json
    return json.dumps(DescriptorGrammar.CATEGORY_ORDER, ensure_ascii=False)


def _build_primitive_info_json():
    import json;
    info = {}
    for e in primitives.primitives.values():
        info[e['ru']] = {'pattern': e['pattern'], 'en': e['en'], 'category': e['category']}
    return json.dumps(info, ensure_ascii=False)


def _build_dictionary_words_json():
    import json
    return json.dumps(descriptors.descriptions, ensure_ascii=False)


@app.route('/')
def home():
    return render_template_string(HTML,
                                  primitives_count=primitives.total_count(),
                                  descriptions_count=len(descriptors.descriptions),
                                  primitives_rows=_build_primitives_rows(), words_rows=_build_words_rows(),
                                  categories_json=_build_categories_json(),
                                  category_order_json=_build_category_order_json(),
                                  primitive_info_json=_build_primitive_info_json(),
                                  dictionary_words_json=_build_dictionary_words_json(),
                                  secret_key=SECRET_KEY)


@app.route('/translate')
def translate():
    word = request.args.get('word', '').strip();
    tonic = Note(NoteName.DO, 4)
    desc = descriptors.get_description(word) or descriptors.get_description_en(word)
    if desc:
        notes, _ = descriptors.describe_to_notes(word, tonic); meaning = word
    else:
        prim = primitives.get_by_ru(word) or primitives.get_by_en(word)
        if prim:
            notes = descriptors.describe_to_notes(word, tonic)[0]; meaning = prim["ru"] + " / " + prim["en"]; desc = [
                prim["ru"]]
        else:
            return jsonify({'notes': '—', 'meaning': 'not found', 'description': [], 'error': 'Not found'})
    nn = [];
    for n in notes:
        m = n.to_midi();
        s = m % 12
        nn.append(f"{n.name.name}{'♯' if s in SHARP_SEMITONES else ''}{n.octave}")
    return jsonify({'notes': ' → '.join(nn), 'meaning': meaning, 'description': desc})


@app.route('/play')
def play():
    word = request.args.get('word', '').strip()
    notes, _ = descriptors.describe_to_notes(word, Note(NoteName.DO, 4))
    return send_file(generate_word_wav(notes, float(request.args.get('speed', '1.0'))), mimetype='audio/wav')


@app.route('/compose')
def compose():
    words = [w.strip() for w in request.args.get('words', '').split(',') if w.strip()]
    result = descriptors.validate_order(words)
    if not result["valid"]: return jsonify({'error': '; '.join(result["errors"])})
    tonic = Note(NoteName.DO, 4);
    notes = [tonic];
    cm = tonic.to_midi();
    bo = 4
    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            mv = descriptors._pattern_to_movements(prim["pattern"])
            if mv:
                st, dr = mv[0];
                cm += dr * st
                co = (cm // 12) - 1
                if co > bo + 1:
                    cm -= 12
                elif co < bo - 1:
                    cm += 12
                notes.append(descriptors._midi_to_note(cm))
    nn = [];
    for n in notes:
        m = n.to_midi();
        s = m % 12
        nn.append(f"{n.name.name}{'♯' if s in SHARP_SEMITONES else ''}{n.octave}")
    return jsonify({'notes': ' → '.join(nn), 'words': result["correct_order"]})


@app.route('/compose_play')
def compose_play():
    words = [w.strip() for w in request.args.get('words', '').split(',') if w.strip()]
    instrument = request.args.get('instrument', 'piano')
    result = descriptors.validate_order(words)
    tonic = Note(NoteName.DO, 4);
    notes = [tonic];
    cm = tonic.to_midi();
    bo = 4
    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            mv = descriptors._pattern_to_movements(prim["pattern"])
            if mv:
                st, dr = mv[0];
                cm += dr * st
                co = (cm // 12) - 1
                if co > bo + 1:
                    cm -= 12
                elif co < bo - 1:
                    cm += 12
                notes.append(descriptors._midi_to_note(cm))
    speed = float(request.args.get('speed', '1.0'))
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, note in enumerate(notes):
        dur = base_duration if i < len(notes) - 1 else int(600 / speed)
        w = generate_wave(note.to_frequency(), dur, instrument=instrument)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav')


@app.route('/piano_note')
def piano_note():
    midi = int(request.args.get('midi', 60))
    instrument = request.args.get('instrument', 'piano')
    w = generate_wave(midi_to_frequency(midi), 400, 0.3, instrument)
    audio_int16 = (w * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav')


@app.route('/piano_play')
def piano_play():
    midi_notes = [int(n) for n in request.args.get('notes', '').split(',') if n.strip()]
    instrument = request.args.get('instrument', 'piano')
    speed = float(request.args.get('speed', '1.0'))
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, midi in enumerate(midi_notes):
        dur = base_duration if i < len(midi_notes) - 1 else int(600 / speed)
        w = generate_wave(midi_to_frequency(midi), dur, 0.3, instrument=instrument)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1);
        wf.setsampwidth(2);
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav')


@app.route('/analyze')
def analyze():
    intervals = [int(i) for i in request.args.get('intervals', '').split(',') if i.strip()]

    # Определяем направления для всех интервалов
    directions = []
    for diff in intervals:
        if diff > 0:
            directions.append("UP")
        elif diff < 0:
            directions.append("DOWN")
        else:
            directions.append("STATIC")

    # Строим строку паттерна из интервалов
    def interval_to_name(semitones, direction):
        for name, val in {
            'UNISON': 0, 'MINOR_SECOND': 1, 'MAJOR_SECOND': 2,
            'MINOR_THIRD': 3, 'MAJOR_THIRD': 4, 'PERFECT_FOURTH': 5,
            'TRITON': 6, 'PERFECT_FIFTH': 7, 'MINOR_SIXTH': 8,
            'MAJOR_SIXTH': 9, 'MINOR_SEVENTH': 10, 'MAJOR_SEVENTH': 11, 'OCTAVE': 12
        }.items():
            if val == semitones:
                return f"{name}_{direction}"
        return f"UNKNOWN_{direction}"

    played_pattern = ','.join(interval_to_name(abs(intervals[i]), directions[i]) for i in range(len(intervals)))

    # Ищем полное совпадение паттерна
    results = []
    all_found = True
    primitives_ru = []

    # Сначала ищем полное совпадение
    for entry in primitives.primitives.values():
        if entry['pattern'] == played_pattern:
            # Нашли точное совпадение — это одно слово
            for _ in intervals:
                results.append({'ru': entry['ru'], 'en': entry['en'], 'found': True})
                primitives_ru.append(entry['ru'])
            break
    else:
        # Полного совпадения нет — ищем все возможные примитивы для каждого интервала
        for i, diff in enumerate(intervals):
            direction = directions[i]
            abs_diff = abs(diff)
            found_list = []
            for entry in primitives.primitives.values():
                for part in entry['pattern'].split(','):
                    if part.endswith("_UP"):
                        iname = part[:-3]; pdir = "UP"
                    elif part.endswith("_DOWN"):
                        iname = part[:-5]; pdir = "DOWN"
                    elif part.endswith("_STATIC"):
                        iname = part[:-7]; pdir = "STATIC"
                    else:
                        continue
                    try:
                        from core.constants import Interval
                        iv = Interval[iname].value
                    except:
                        iv = None
                    if iv is not None and iv == abs_diff and pdir == direction:
                        found_list.append({'ru': entry['ru'], 'en': entry['en'], 'found': True})
                        break
            if found_list:
                results.append({'found': True, 'options': found_list})
                primitives_ru.append(' / '.join(f['ru'] for f in found_list))
            else:
                all_found = False
                results.append({'found': False})

    # Ищем слово по полной последовательности
    word_found = None
    if all_found and len(primitives_ru) >= 2:
        for word, data in descriptors.descriptions.items():
            if data['ru'] == primitives_ru:
                word_found = word
                break

    return jsonify(
        {'results': results, 'all_found': all_found, 'primitives_ru': primitives_ru, 'word_found': word_found,
         'played_pattern': played_pattern})

@app.route('/shared/words')
def shared_words():
    words = SharedWord.query.order_by(SharedWord.id.desc()).all()
    return jsonify([{'id': w.id, 'name': w.name, 'primitives': w.primitives.split(','), 'author': w.author,
                     'source': w.source, 'created': w.created, 'likes': w.likes or 0, 'dislikes': w.dislikes or 0} for w
                    in words])


@app.route('/shared/words/add', methods=['POST'])
def add_shared_word():
    data = request.get_json()
    if request.headers.get('X-SolRes-Key') != SECRET_KEY: return jsonify({'error': 'Unauthorized'}), 403
    w = SharedWord(name=data['name'], primitives=','.join(data['primitives']), author=data.get('author', 'Anonymous'),
                   source=data.get('source', '👤 User'), created=data.get('created', ''))
    db.session.add(w);
    db.session.commit()
    return jsonify({'id': w.id, 'status': 'ok'})


@app.route('/shared/words/<int:word_id>/delete', methods=['DELETE'])
def delete_shared_word(word_id):
    w = SharedWord.query.get_or_404(word_id);
    db.session.delete(w);
    db.session.commit()
    return jsonify({'status': 'ok'})


@app.route('/shared/words/<int:word_id>/like', methods=['POST'])
def like_word(word_id):
    w = SharedWord.query.get_or_404(word_id);
    w.likes = (w.likes or 0) + 1;
    db.session.commit()
    return jsonify({'id': w.id, 'likes': w.likes, 'dislikes': w.dislikes, 'score': (w.likes or 0) - (w.dislikes or 0)})


@app.route('/shared/words/<int:word_id>/dislike', methods=['POST'])
def dislike_word(word_id):
    w = SharedWord.query.get_or_404(word_id);
    w.dislikes = (w.dislikes or 0) + 1;
    db.session.commit()
    score = (w.likes or 0) - (w.dislikes or 0)
    if score <= -100: db.session.delete(w); db.session.commit(); return jsonify({'deleted': True, 'score': score})
    return jsonify({'id': w.id, 'likes': w.likes, 'dislikes': w.dislikes, 'score': score})


@app.route('/shared/sentences')
def shared_sentences():
    sents = SharedSentence.query.order_by(SharedSentence.id.desc()).all()
    return jsonify([{'id': s.id, 'name': s.name, 'words': s.words.split(','), 'author': s.author, 'created': s.created,
                     'likes': s.likes or 0, 'dislikes': s.dislikes or 0} for s in sents])


@app.route('/shared/sentences/add', methods=['POST'])
def add_shared_sentence():
    data = request.get_json()
    if request.headers.get('X-SolRes-Key') != SECRET_KEY: return jsonify({'error': 'Unauthorized'}), 403
    s = SharedSentence(name=data['name'], words=','.join(data['words']), author=data.get('author', 'Anonymous'),
                       created=data.get('created', ''))
    db.session.add(s);
    db.session.commit()
    return jsonify({'id': s.id, 'status': 'ok'})


@app.route('/shared/sentences/<int:sent_id>/like', methods=['POST'])
def like_sentence(sent_id):
    s = SharedSentence.query.get_or_404(sent_id);
    s.likes = (s.likes or 0) + 1;
    db.session.commit()
    return jsonify({'id': s.id, 'likes': s.likes, 'dislikes': s.dislikes, 'score': (s.likes or 0) - (s.dislikes or 0)})


@app.route('/shared/sentences/<int:sent_id>/dislike', methods=['POST'])
def dislike_sentence(sent_id):
    s = SharedSentence.query.get_or_404(sent_id);
    s.dislikes = (s.dislikes or 0) + 1;
    db.session.commit()
    score = (s.likes or 0) - (s.dislikes or 0)
    if score <= -100: db.session.delete(s); db.session.commit(); return jsonify({'deleted': True, 'score': score})
    return jsonify({'id': s.id, 'likes': s.likes, 'dislikes': s.dislikes, 'score': score})

@app.route('/shared/text')
def shared_text():
    texts = SharedText.query.order_by(SharedText.id.desc()).all()
    return jsonify([{'id': t.id, 'name': t.name, 'sentences': t.sentences.split('||'), 'author': t.author, 'created': t.created, 'likes': t.likes or 0, 'dislikes': t.dislikes or 0} for t in texts])

@app.route('/shared/text/add', methods=['POST'])
def add_shared_text():
    data = request.get_json()
    if request.headers.get('X-SolRes-Key') != SECRET_KEY: return jsonify({'error': 'Unauthorized'}), 403
    t = SharedText(name=data['name'], sentences='||'.join(data['sentences']), author=data.get('author', 'Anonymous'), created=data.get('created', ''))
    db.session.add(t); db.session.commit()
    return jsonify({'id': t.id, 'status': 'ok'})

@app.route('/shared/text/<int:text_id>/like', methods=['POST'])
def like_text(text_id):
    t = SharedText.query.get_or_404(text_id); t.likes = (t.likes or 0) + 1; db.session.commit()
    return jsonify({'id': t.id, 'likes': t.likes, 'dislikes': t.dislikes, 'score': (t.likes or 0) - (t.dislikes or 0)})

@app.route('/shared/text/<int:text_id>/dislike', methods=['POST'])
def dislike_text(text_id):
    t = SharedText.query.get_or_404(text_id); t.dislikes = (t.dislikes or 0) + 1; db.session.commit()
    score = (t.likes or 0) - (t.dislikes or 0)
    if score <= -100: db.session.delete(t); db.session.commit(); return jsonify({'deleted': True, 'score': score})
    return jsonify({'id': t.id, 'likes': t.likes, 'dislikes': t.dislikes, 'score': score})


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 SolRes Web App")
    print(f"   Primitives: {primitives.total_count()}")
    print(f"   Descriptions: {len(descriptors.descriptions)}")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)