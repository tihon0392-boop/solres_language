# web/app.py — ПОЛНАЯ ЗАМЕНА
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import io
import wave as wave_module

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
    source = db.Column(db.String(50), default='👤 User')
    created = db.Column(db.String(30))


class SharedSentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    words = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(50), default='Anonymous')
    created = db.Column(db.String(30))


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
    elif instrument == 'flute':
        wave_data = np.sin(2 * np.pi * frequency * t) * 1.0
        wave_data += np.sin(2 * np.pi * frequency * 2 * t) * 0.2
        wave_data += np.sin(2 * np.pi * frequency * 3 * t) * 0.1
    elif instrument == 'organ':
        wave_data = (
                np.sin(2 * np.pi * frequency * t) * 1.0 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.7 +
                np.sin(2 * np.pi * frequency * 3 * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 4 * t) * 0.3 +
                np.sin(2 * np.pi * frequency * 5 * t) * 0.2 +
                np.sin(2 * np.pi * frequency * 6 * t) * 0.1
        )
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
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


def generate_midi_wav(midi_notes, speed=1.0):
    base_duration = int(400 / speed)
    combined = np.array([], dtype=np.float32)
    silence = np.zeros(int(SAMPLE_RATE * 0.03 / speed), dtype=np.float32)
    for i, midi in enumerate(midi_notes):
        dur = base_duration if i < len(midi_notes) - 1 else int(600 / speed)
        w = generate_wave(midi_to_frequency(midi), dur)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


def generate_note_wav(midi_note, duration_ms=400):
    w = generate_wave(midi_to_frequency(midi_note), duration_ms)
    audio_int16 = (w * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
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
            .white-key { width: 22px; height: 80px; font-size: 0.3em; } .black-key { width: 14px; height: 50px; font-size: 0.22em; }
            .piano { height: 80px; width: 308px; } .piano-sequence { font-size: 0.7em; }
            table { font-size: 0.7em; } th, td { padding: 6px; } .table-wrap { max-height: 250px; }
            .speed-row { gap: 4px; font-size: 0.7em; } .speed-row input[type=range] { width: 60px; }
            .search-row { flex-direction: column; } .search-row input, .search-row .btn { width: 100%; }
            .sentence-row { flex-wrap: wrap; } .sentence-row .dropdown-search { min-width: 120px; }
            .top-row { flex-direction: column; align-items: flex-start; } .stats { gap: 10px; font-size: 0.65em; }
        }
    </style>
</head>
<body>
    <canvas id="starfield"></canvas>
    <div class="container">
        <header><div class="logo">🎵 SolRes</div><p class="subtitle">Universal musical language</p></header>
        <div class="top-row">
            <div class="stats"><div>Primitives <span>{{ primitives_count }}</span></div><div>Words <span>{{ descriptions_count }}</span></div></div>
            <select id="globalInstrument" onchange="currentInstrument=this.value" style="padding:6px 10px;font-size:0.75em;border-radius:18px;background:var(--surface2);color:var(--text);border:1px solid rgba(255,255,255,0.08);margin-right:8px;">
                <option value="piano">🎹 Piano</option>
                <option value="violin">🎻 Violin</option>
                <option value="flute">🎵 Flute</option>
                <option value="organ">🎛️ Organ</option>
            </select>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀️ Light</button>
        </div>
        <div class="tabs">
            <button class="tab active" onclick="switchTab('translate')">🔍 Translate</button>
            <button class="tab" onclick="switchTab('compose')">🧩 Compose</button>
            <button class="tab" onclick="switchTab('instruments')">🎸 Instruments</button>
            <button class="tab" onclick="switchTab('mywords')">📝 My Words</button>
            <button class="tab" onclick="switchTab('community')">🌐 Community</button>
            <button class="tab" onclick="switchTab('sentences')">💬 Sentences</button>
            <button class="tab" onclick="switchTab('text')">📄 Text</button>
            <button class="tab" onclick="switchTab('dictionary')">📖 Dictionary</button>
            <button class="tab" onclick="switchTab('rules')">📋 Rules</button>
        </div>

        <!-- TRANSLATE -->
        <div class="card" id="tab-translate">
            <div class="search-row"><input type="text" id="wordInput" placeholder="Enter a word..." onkeypress="if(event.key==='Enter') translateWord()"><button class="btn btn-primary" onclick="translateWord()">🔍 Translate</button></div>
            <div id="result"><div style="text-align:center;color:var(--muted);opacity:0.5;">Type a word to see its description and hear its melody</div></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="speedSlider" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('speedSlider','speedLabel')"><span>🐇</span><span id="speedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="audioPlayer" controls style="display:none"></audio>
        </div>

        <!-- COMPOSE -->
        <div class="card" id="tab-compose" style="display:none;">
            <div class="compose-grid" id="composeGrid"></div>
            <div class="compose-buttons">
                <button class="btn btn-primary" onclick="composePlay()">▶ Play</button>
                <button class="btn btn-sm" onclick="composeRandom()">✨ Random</button>
                <button class="btn btn-sm" onclick="composeClear()">✕ Clear All</button>
                <button class="btn btn-sm" onclick="saveComposedWord()">💾 Save to My Words</button>
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
                <button class="btn btn-primary" onclick="pianoPlaySequence()">▶ Play & Analyze</button>
                <button class="btn btn-sm" onclick="pianoUndoLastNote()">↩ Undo</button>
                <button class="btn btn-sm" onclick="pianoClearSequence()">✕ Clear All</button>
                <button class="btn btn-sm" onclick="pianoToCompose()">📋 To Compose</button>
            </div>
            <div id="pianoAnalysis"></div>
            <div id="pianoSaveArea" style="margin-top:8px;"></div>
            <audio id="pianoAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- MY WORDS -->
        <div class="card" id="tab-mywords" style="display:none;">
            <button class="btn btn-sm" onclick="loadMyWords()" style="margin-bottom:10px;">🔄 Refresh</button>
            <button class="btn btn-sm btn-danger" onclick="clearMyWords()" style="margin-bottom:10px;margin-left:6px;">🗑 Clear All</button>
            <div class="speed-row"><span>🐢</span><input type="range" id="mywordsSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('mywordsSpeed','mywordsSpeedLabel')"><span>🐇</span><span id="mywordsSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <div class="table-wrap"><table id="myWordsTable"><thead><tr><th>Name</th><th>Primitives</th><th>Source</th><th style="width:24px;"></th><th style="width:24px;"></th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
        </div>

        <!-- COMMUNITY -->
        <div class="card" id="tab-community" style="display:none;">
            <button class="btn btn-sm" onclick="loadCommunityWords()" style="margin-bottom:10px;">🔄 Refresh</button>
            <div class="table-wrap"><table id="communityTable"><thead><tr><th>Name</th><th>Primitives</th><th>Author</th><th style="width:24px;"></th></tr></thead><tbody></tbody></table></div>
        </div>

        <!-- SENTENCES -->
        <div class="card" id="tab-sentences" style="display:none;">
            <div id="sentenceRows"></div>
            <div class="compose-buttons">
                <button class="btn btn-sm" onclick="addSentenceRow()">+ Add Word</button>
                <button class="btn btn-primary" onclick="playSentence()">▶ Play</button>
                <button class="btn btn-sm" onclick="saveSentence()">💾 Save</button>
                <button class="btn btn-sm" onclick="clearSentence()">✕ Clear</button>
            </div>
            <div><input type="text" id="sentenceName" placeholder="Sentence name (optional)" style="width:100%;margin-top:8px;"></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="sentSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('sentSpeed','sentSpeedLabel')"><span>🐇</span><span id="sentSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="sentenceAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- TEXT -->
        <div class="card" id="tab-text" style="display:none;">
            <button class="btn btn-sm" onclick="loadText()" style="margin-bottom:10px;">🔄 Refresh</button>
            <button class="btn btn-primary" onclick="playText()" style="margin-bottom:10px;margin-left:6px;">▶ Play All</button>
            <button class="btn btn-sm btn-danger" onclick="clearText()" style="margin-bottom:10px;margin-left:6px;">🗑 Clear All</button>
            <div id="textList"></div>
            <div class="speed-row"><span>🐢</span><input type="range" id="textSpeed" min="0.5" max="2.5" step="0.1" value="1.0" oninput="updateSpeedLabel('textSpeed','textSpeedLabel')"><span>🐇</span><span id="textSpeedLabel" style="color:var(--accent);">1.0x</span></div>
            <audio id="textAudio" controls style="display:none;width:100%;margin-top:8px;"></audio>
        </div>

        <!-- DICTIONARY -->
        <div class="card" id="tab-dictionary" style="display:none;">
            <div class="search-row"><input type="text" id="dictSearch" placeholder="Search..." oninput="filterDict()"></div>
            <h3 style="margin:10px 0 6px;color:var(--accent);">🔤 Primitives <span style="color:var(--muted);">({{ primitives_count }})</span></h3>
            <div class="table-wrap"><table id="primitivesTable"><thead><tr><th>Category</th><th>RU</th><th>EN</th><th>Pattern</th></tr></thead><tbody>{{ primitives_rows | safe }}</tbody></table></div>
            <h3 style="margin:14px 0 6px;color:var(--accent);">📝 Words <span style="color:var(--muted);">({{ descriptions_count }})</span></h3>
            <div class="table-wrap"><table id="wordsTable"><thead><tr><th>Word</th><th>EN</th><th>Description</th><th style="width:24px;"></th></tr></thead><tbody>{{ words_rows | safe }}</tbody></table></div>
        </div>

        <!-- RULES -->
        <div class="card" id="tab-rules" style="display:none;">
            <h3 style="color:var(--accent);margin-bottom:10px;">📋 Rules</h3>
            <ol class="rules-list">
                <li><strong>Alphabet:</strong> 7 notes — <em>Do, Re, Mi, Fa, Sol, La, Si</em></li>
                <li><strong>Words = intervals</strong> between notes.</li>
                <li><strong>Direction:</strong> Up = light/active, Down = dark/passive.</li>
                <li><strong>135+ primitives</strong> in 12 fixed categories.</li>
                <li><strong>Order:</strong> Existence → Size → Physics → Material → Shape → Color → Action → Relation → Value → Quantity → Space → Time</li>
                <li><strong>Flexible:</strong> 2–12 primitives per word.</li>
                <li><strong>Community:</strong> <a href="https://github.com/tihon0392-boop/solres_language/discussions" target="_blank" style="color:var(--accent);">GitHub Discussions</a></li>
            </ol>
        </div>
    </div>

    <script>
        const CATEGORIES = {{ categories_json | safe }};
        const CATEGORY_ORDER = {{ category_order_json | safe }};
        const PRIMITIVE_INFO = {{ primitive_info_json | safe }};
        const DICTIONARY_WORDS = {{ dictionary_words_json | safe }};
        const SHARP_SEMITONES = [1,3,6,8,10];
        const NOTE_NAMES = ['C','C#/Db','D','D#/Eb','E','F','F#/Gb','G','G#/Ab','A','A#/Bb','B'];
        let theme = 'dark', currentWord = '', pianoOctave = 3, pianoSequence = [], lastAnalysis = null;

        // === STARFIELD ===
        const canvas = document.getElementById('starfield'), ctx = canvas.getContext('2d'); let bodies = [];
        function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        window.addEventListener('resize', () => { resizeCanvas(); createBodies(); });
        function random(min, max) { return Math.random() * (max - min) + min; }
        function createBodies() { bodies = []; for (let i = 0; i < 200; i++) { bodies.push({x: random(0, canvas.width), y: random(0, canvas.height), r: random(0.8, 4.5), baseOpacity: random(0.15, 1.0), phase: random(0, Math.PI*2), period: random(300, 2000), alive: true, respawnTime: 0}); } }
        function drawBodies() { ctx.clearRect(0, 0, canvas.width, canvas.height); const isLight = theme === 'light', now = Date.now(); bodies.forEach(b => { if (!b.alive) { if (now > b.respawnTime) { b.alive = true; b.baseOpacity = random(0.15, 1.0); b.r = random(0.8, 4.5); } return; } const twinkle = Math.sin(now / 1000 * (2 * Math.PI) / (b.period / 1000) + b.phase) * 0.3 + 0.7, alpha = b.baseOpacity * twinkle; if (isLight) { ctx.fillStyle = `rgba(${Math.floor(alpha*30)},${Math.floor(alpha*30)},${Math.floor(alpha*30)},${alpha})`; ctx.shadowColor = `rgba(0,0,0,${alpha*0.95})`; } else { const br = Math.floor(180 + alpha*75); ctx.fillStyle = `rgba(${br},${br},${Math.floor(br*0.85)},${alpha})`; ctx.shadowColor = `rgba(255,240,220,${alpha*0.7})`; } ctx.shadowBlur = b.r*3; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); }); ctx.shadowBlur = 0; requestAnimationFrame(drawBodies); }
        canvas.addEventListener('click', (e) => { const rect = canvas.getBoundingClientRect(), mx = e.clientX - rect.left, my = e.clientY - rect.top; for (let b of bodies) { if (!b.alive) continue; if (Math.sqrt((b.x-mx)**2 + (b.y-my)**2) < b.r + 10) { b.alive = false; b.respawnTime = Date.now() + 10000; break; } } });
        resizeCanvas(); createBodies(); drawBodies();
        function toggleTheme() { const btn = document.getElementById('themeBtn'); if (theme === 'dark') { theme = 'light'; document.body.classList.add('light-theme'); btn.textContent = '🌙 Dark'; } else { theme = 'dark'; document.body.classList.remove('light-theme'); btn.textContent = '☀️ Light'; } }

        // === TABS ===
        function switchTab(tab) { document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.querySelectorAll('.card').forEach(c => c.style.display = 'none'); document.getElementById('tab-' + tab).style.display = 'block'; event.target.classList.add('active'); if (tab === 'mywords') loadMyWords(); if (tab === 'community') loadCommunityWords(); if (tab === 'sentences') loadSentenceRows(); if (tab === 'text') loadText(); if (tab === 'instruments') buildPiano(); }

        // === STORAGE ===
        function getMyWords() { try { return JSON.parse(localStorage.getItem('solres_mywords') || '[]'); } catch(e) { return []; } }
        function saveMyWords(w) { localStorage.setItem('solres_mywords', JSON.stringify(w)); }
        function getSentences() { try { return JSON.parse(localStorage.getItem('solres_sentences') || '[]'); } catch(e) { return []; } }
        function saveSentences(s) { localStorage.setItem('solres_sentences', JSON.stringify(s)); }

        // === SPEED ===
        function updateSpeedLabel(sliderId, labelId) { const val = parseFloat(document.getElementById(sliderId).value).toFixed(1); document.getElementById(labelId).textContent = val + 'x'; }
        function getSpeed(id) { return parseFloat(document.getElementById(id).value) || 1.0; }

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
        function buildComposeGrid() { const g = document.getElementById('composeGrid'); g.innerHTML = ''; CATEGORY_ORDER.forEach((cat, i) => { const words = CATEGORIES[cat] || []; const row = document.createElement('div'); row.className = 'compose-row'; row.id = 'compose-row-' + i; row.innerHTML = `<span class="cat-label">${cat.split(':').pop()}</span><div class="dropdown-search"><input type="text" placeholder="—" onfocus="toggleDropdown(this,true)" oninput="filterDropdown(this)" onblur="setTimeout(()=>toggleDropdown(this,false),200)"><div class="dropdown-list"></div></div><button class="btn-xs" onclick="showIntervalInfo('${cat}', event)">ℹ️</button>`; g.appendChild(row); buildDropdown(row.querySelector('.dropdown-list'), words, row.querySelector('input')); }); }
        function showIntervalInfo(cat, e) { const sample = CATEGORIES[cat]?.[0]; if (sample && PRIMITIVE_INFO[sample]) { const t = document.createElement('div'); t.style.cssText = 'position:absolute;background:var(--surface2);color:var(--text);padding:8px 12px;border-radius:8px;font-size:0.8em;z-index:10;border:1px solid var(--accent);'; t.textContent = 'Interval: ' + PRIMITIVE_INFO[sample].pattern; document.body.appendChild(t); t.style.left = e.clientX + 'px'; t.style.top = (e.clientY - 40) + 'px'; setTimeout(() => t.remove(), 2000); } }
        function getSelectedPrimitives() { const s = []; CATEGORY_ORDER.forEach((cat, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (inp && inp.value && CATEGORIES[cat]?.includes(inp.value)) s.push({word: inp.value, category: cat, index: i}); }); return s; }
        function validateCompose() { const selected = getSelectedPrimitives(); let lastIdx = -1, valid = true; CATEGORY_ORDER.forEach((_, i) => { const row = document.getElementById('compose-row-' + i); if (row) row.classList.remove('invalid'); }); for (const s of selected) { const catIdx = CATEGORY_ORDER.indexOf(s.category); if (catIdx < lastIdx) { valid = false; document.getElementById('compose-row-' + s.index).classList.add('invalid'); } lastIdx = catIdx; } document.getElementById('composeError').innerHTML = ''; return {valid, selected}; }
        async function composePlay() { const {valid, selected} = validateCompose(); if (selected.length < 2) { document.getElementById('composeError').innerHTML = '<div class="error-msg">Select at least 2 primitives</div>'; return; } if (!valid) { document.getElementById('composeError').innerHTML = '<div class="error-msg">Category order violated!</div>'; return; } const words = selected.map(s => s.word); const res = await fetch('/compose?words=' + encodeURIComponent(words.join(','))); const data = await res.json(); document.getElementById('composeResult').innerHTML = `<div class="desc-row">${words.map(w => '<span>' + w + '</span>').join(' ')}</div><div class="notes-display">${data.notes}</div>`; const ar = await fetch('/compose_play?words=' + encodeURIComponent(words.join(',')) + '&speed=' + getSpeed('composeSpeed')); const p = document.getElementById('composeAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await ar.blob()); p.play(); }
        function composeRandom() { CATEGORY_ORDER.forEach((cat, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (!inp.value) { const w = CATEGORIES[cat] || []; if (w.length && Math.random() > 0.6) inp.value = w[Math.floor(Math.random()*w.length)]; } }); validateCompose(); }
        function composeClear() { CATEGORY_ORDER.forEach((_, i) => { const inp = document.querySelector(`#compose-row-${i} input`); if (inp) inp.value = ''; }); document.getElementById('composeResult').innerHTML = ''; document.getElementById('composeError').innerHTML = ''; document.getElementById('composeAudio').style.display = 'none'; validateCompose(); }
        function saveComposedWord() { const {selected} = validateCompose(); if (selected.length < 2) return; const name = document.getElementById('composeWordName').value.trim() || 'word_' + Date.now(); const words = selected.map(s => s.word); const myWords = getMyWords(); myWords.push({name, primitives: words, source: '🧩 Compose', created: new Date().toISOString()}); saveMyWords(myWords); document.getElementById('composeError').innerHTML = '<div class="success-msg">Saved: ' + name + '</div>'; document.getElementById('composeWordName').value = ''; }
        buildComposeGrid();

        // === PIANO ===
        function buildPiano() { const piano = document.getElementById('piano'); piano.innerHTML = ''; const startMidi = (pianoOctave + 1) * 12; const WHITE_W = 36, BLACK_W = 20; const whiteSemitones = [0,2,4,5,7,9,11]; for (let oct = 0; oct < 2; oct++) { for (let w = 0; w < 7; w++) { const midi = startMidi + oct*12 + whiteSemitones[w]; const noteIdx = midi % 12, octave = Math.floor(midi/12)-1; const key = document.createElement('div'); key.className = 'white-key'; key.style.left = (oct*7 + w)*WHITE_W + 'px'; key.textContent = NOTE_NAMES[noteIdx].split('/')[0] + octave; key.dataset.midi = midi; key.onclick = () => pianoKeyClick(midi, NOTE_NAMES[noteIdx].split('/')[0] + octave); piano.appendChild(key); } } const blackPositions = [{wi:0, mo:1},{wi:1, mo:3},{wi:3, mo:6},{wi:4, mo:8},{wi:5, mo:10}]; for (let oct = 0; oct < 2; oct++) { for (let bp of blackPositions) { const midi = startMidi + oct*12 + bp.mo; const noteIdx = midi % 12, octave = Math.floor(midi/12)-1; const key = document.createElement('div'); key.className = 'black-key'; key.style.left = ((oct*7 + bp.wi)*WHITE_W + WHITE_W - BLACK_W/2) + 'px'; key.textContent = NOTE_NAMES[noteIdx]; key.dataset.midi = midi; key.onclick = (e) => { e.stopPropagation(); pianoKeyClick(midi, NOTE_NAMES[noteIdx].split('/')[0] + octave); }; piano.appendChild(key); } } updatePianoRangeLabel(); }
        function updatePianoRangeLabel() { const startMidi = (pianoOctave + 1) * 12; const s = NOTE_NAMES[startMidi%12].split('/')[0] + (Math.floor(startMidi/12)-1); const e = NOTE_NAMES[(startMidi+23)%12].split('/')[0] + (Math.floor((startMidi+23)/12)-1); document.getElementById('pianoRangeLabel').textContent = s + ' – ' + e; }
        function pianoShiftOctave(dir) { pianoOctave += dir; if (pianoOctave < 0) pianoOctave = 0; if (pianoOctave > 5) pianoOctave = 5; buildPiano(); }
        async function pianoKeyClick(midi, noteName) { pianoSequence.push({midi, noteName}); updatePianoSequenceDisplay(); const keys = document.querySelectorAll('#piano div[data-midi="' + midi + '"]'); keys.forEach(k => k.classList.add('active')); setTimeout(() => keys.forEach(k => k.classList.remove('active')), 300); const r = await fetch('/piano_note?midi=' + midi + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await r.blob())).play(); }
        function updatePianoSequenceDisplay() { const div = document.getElementById('pianoSequence'); if (pianoSequence.length === 0) { div.textContent = 'Click keys to record a melody...'; div.style.color = 'var(--muted)'; } else { div.innerHTML = pianoSequence.map((s, i) => { const prev = i > 0 ? pianoSequence[i-1] : null; let interval = ''; if (prev) { const diff = s.midi - prev.midi; interval = `<span style="color:var(--muted);font-size:0.7em;"> [${diff>0?'+':''}${diff}]</span>`; } return `<span style="color:var(--accent2);cursor:pointer;" onclick="pianoRemoveNote(${i})" title="Click to remove">${s.noteName}</span>${interval}`; }).join(' → '); div.style.color = ''; } }
        function pianoUndoLastNote() { pianoSequence.pop(); updatePianoSequenceDisplay(); }
        function pianoRemoveNote(idx) { pianoSequence.splice(idx, 1); updatePianoSequenceDisplay(); }
        async function pianoPlaySequence() { if (pianoSequence.length === 0) return; const midis = pianoSequence.map(s => s.midi); for (let i = 0; i < midis.length; i++) { setTimeout(() => { const keys = document.querySelectorAll('#piano div[data-midi="' + midis[i] + '"]'); keys.forEach(k => k.classList.add('active')); setTimeout(() => keys.forEach(k => k.classList.remove('active')), 350); }, i * 400 / getSpeed('pianoSpeed')); } const r = await fetch('/piano_play?notes=' + encodeURIComponent(midis.join(',')) + '&speed=' + getSpeed('pianoSpeed') + '&instrument=' + currentInstrument); const p = document.getElementById('pianoAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await r.blob()); p.play(); analyzeIntervals(midis); }
        async function analyzeIntervals(midis) { if (midis.length < 2) return; const intervals = []; for (let i = 1; i < midis.length; i++) intervals.push(midis[i] - midis[i-1]); const r = await fetch('/analyze?intervals=' + encodeURIComponent(intervals.join(','))); const data = await r.json(); lastAnalysis = data; let html = '<table class="analysis-table"><thead><tr><th>Note</th><th>Interval</th><th>Primitive</th></tr></thead><tbody>'; for (let i = 0; i < intervals.length; i++) { const diff = intervals[i], a = data.results[i], found = a && a.found; html += `<tr><td>${pianoSequence[i+1].noteName}</td><td class="${found?'found':'not-found'}">${diff>0?'+':''}${diff}</td><td class="${found?'found':'not-found'}">${found ? a.ru + ' (' + a.en + ')' : '—'}</td></tr>`; } html += '</tbody></table>'; if (data.word_found) html += `<div class="meaning" style="margin-top:8px;">✅ Word: <strong>${data.word_found}</strong></div>`; else if (data.all_found) html += `<div class="desc-row" style="margin-top:8px;">Primitives: ${data.primitives_ru.join(' + ')}</div>`; else html += `<div class="error-msg" style="margin-top:8px;">Some intervals not found.</div>`; html += `<div style="text-align:center;margin-top:8px;"><button class="btn btn-sm" onclick="savePianoAsWord()">💾 Save as My Word</button></div>`; document.getElementById('pianoAnalysis').innerHTML = html; }
        function savePianoAsWord() { if (!lastAnalysis || !lastAnalysis.primitives_ru || lastAnalysis.primitives_ru.length < 2) return; const name = prompt('Word name:', 'piano_' + Date.now()); if (!name) return; const myWords = getMyWords(); myWords.push({name, primitives: lastAnalysis.primitives_ru, source: '🎹 Instruments', created: new Date().toISOString()}); saveMyWords(myWords); document.getElementById('pianoSaveArea').innerHTML = '<div class="success-msg">Saved: ' + name + '</div>'; }
        function pianoClearSequence() { pianoSequence = []; updatePianoSequenceDisplay(); document.getElementById('pianoAudio').style.display = 'none'; document.getElementById('pianoAnalysis').innerHTML = ''; document.getElementById('pianoSaveArea').innerHTML = ''; lastAnalysis = null; }
        function pianoToCompose() { if (pianoSequence.length < 2) return; const intervals = []; for (let i = 1; i < pianoSequence.length; i++) intervals.push(pianoSequence[i].midi - pianoSequence[i-1].midi); switchTab('compose'); document.getElementById('composeError').innerHTML = `<div style="color:var(--accent);text-align:center;margin-top:10px;">Intervals from Piano: ${intervals.map(i=>(i>0?'+':'')+i).join(', ')}</div>`; }
                let theme = 'dark', currentWord = '', pianoOctave = 3, pianoSequence = [], lastAnalysis = null, currentInstrument = 'piano';
        function instrumentChanged() {
            currentInstrument = document.getElementById('instrumentSelect').value;
        }
        buildPiano();

        // === MY WORDS ===
        function loadMyWords() { const words = getMyWords(); let html = ''; words.forEach((w, i) => { html += `<tr><td>${w.name}</td><td>${(w.primitives||[]).join(', ')}</td><td><span class="badge ${w.source==='📖 System'?'badge-system':'badge-user'}">${w.source||'?'}</span></td><td><button class="btn-sm" onclick="playMyWord(${i})">▶</button></td><td><button class="btn-sm" onclick="publishMyWord(${i})" title="Publish">🌐</button></td><td><button class="btn-sm btn-danger" onclick="deleteMyWord(${i})">✕</button></td></tr>`; }); document.querySelector('#myWordsTable tbody').innerHTML = html || '<tr><td colspan="6" style="text-align:center;color:var(--muted);">No saved words yet.</td></tr>'; }
        async function playMyWord(idx) { const words = getMyWords(); if (!words[idx]) return; const ar = await fetch('/compose_play?words=' + encodeURIComponent((words[idx].primitives||[]).join(',')) + '&speed=' + getSpeed('mywordsSpeed') + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }
        async function publishMyWord(idx) { const words = getMyWords(); if (!words[idx]) return; const w = words[idx]; const author = prompt('Your name (or leave empty for anonymous):', '') || 'Anonymous'; await fetch('/shared/words/add', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: w.name, primitives: w.primitives, source: w.source, created: w.created, author: author}) }); alert('Published: ' + w.name); }
        function deleteMyWord(idx) { const words = getMyWords(); words.splice(idx, 1); saveMyWords(words); loadMyWords(); }
        function clearMyWords() { if (confirm('Delete all?')) { saveMyWords([]); loadMyWords(); } }

        // === COMMUNITY ===
        async function loadCommunityWords() { const r = await fetch('/shared/words'); const words = await r.json(); let html = ''; words.forEach(w => { html += `<tr><td>${w.name}</td><td>${(w.primitives||[]).join(', ')}</td><td><span class="badge badge-community">${w.author||'Anonymous'}</span></td><td><button class="btn-sm" onclick="playCommunityWord('${(w.primitives||[]).join(',')}')">▶</button></td></tr>`; }); document.querySelector('#communityTable tbody').innerHTML = html || '<tr><td colspan="4" style="text-align:center;color:var(--muted);">No community words yet. Be the first to publish!</td></tr>'; }
        async function playCommunityWord(primitives) { const ar = await fetch('/compose_play?words=' + encodeURIComponent(primitives) + '&speed=1.0&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }

        // === SENTENCES ===
        function getAllWordsForSelect() { const myWords = getMyWords(); const dictWords = Object.entries(DICTIONARY_WORDS).map(([name, data]) => ({name, primitives: data.ru, source: '📖 System'})); return [...dictWords, ...myWords]; }
        function loadSentenceRows() { document.getElementById('sentenceRows').innerHTML = ''; addSentenceRow(); }
        function addSentenceRow() { const allWords = getAllWordsForSelect(); const container = document.getElementById('sentenceRows'); const row = document.createElement('div'); row.className = 'sentence-row'; row.draggable = true; row.innerHTML = `<span class="drag-handle" draggable="true">⋮⋮</span><div class="dropdown-search"><input type="text" placeholder="🔍 Search word..." onfocus="toggleDropdown(this, true)" oninput="filterDropdown(this)" onblur="setTimeout(()=>toggleDropdown(this,false),200)"><div class="dropdown-list"></div></div><button class="btn-sm btn-danger" onclick="this.parentElement.remove()">✕</button>`; row.addEventListener('dragstart', (e) => { e.dataTransfer.setData('text/plain', Array.from(container.children).indexOf(row)); row.classList.add('dragging'); }); row.addEventListener('dragend', () => row.classList.remove('dragging')); row.addEventListener('dragover', (e) => { e.preventDefault(); row.classList.add('drag-over'); }); row.addEventListener('dragleave', () => row.classList.remove('drag-over')); row.addEventListener('drop', (e) => { e.preventDefault(); row.classList.remove('drag-over'); const from = parseInt(e.dataTransfer.getData('text/plain')); const to = Array.from(container.children).indexOf(row); if (from !== to && from >= 0 && to >= 0) { container.insertBefore(container.children[from], container.children[to + (from < to ? 1 : 0)]); } }); container.appendChild(row); buildDropdown(row.querySelector('.dropdown-list'), allWords.map(w => w.name), row.querySelector('input')); }
        async function playSentence() { const allWords = getAllWordsForSelect(); const selected = []; document.querySelectorAll('#sentenceRows .dropdown-search input').forEach(inp => { if (inp.value) { const w = allWords.find(aw => aw.name === inp.value); if (w) selected.push(w); } }); if (selected.length === 0) return; const allPrims = selected.flatMap(w => w.primitives || []); const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('sentSpeed')); const p = document.getElementById('sentenceAudio'); p.style.display = 'block'; p.src = URL.createObjectURL(await ar.blob()); p.play(); }
        function saveSentence() { const name = document.getElementById('sentenceName').value.trim() || 'sentence_' + Date.now(); const wordNames = []; document.querySelectorAll('#sentenceRows .dropdown-search input').forEach(inp => { if (inp.value) wordNames.push(inp.value); }); if (wordNames.length < 2) return; const sentences = getSentences(); sentences.push({name, words: wordNames, created: new Date().toISOString()}); saveSentences(sentences); document.getElementById('sentenceName').value = ''; alert('Saved: ' + name); }
        function clearSentence() { document.getElementById('sentenceRows').innerHTML = ''; addSentenceRow(); document.getElementById('sentenceName').value = ''; }

        // === TEXT ===
        function loadText() { const sentences = getSentences(); const container = document.getElementById('textList'); if (sentences.length === 0) { container.innerHTML = '<div style="text-align:center;color:var(--muted);padding:20px;">No saved sentences yet.</div>'; return; } container.innerHTML = sentences.map((s, i) => `<div class="sentence-row" draggable="true" data-idx="${i}"><span class="drag-handle" draggable="true">⋮⋮</span><span style="flex:1;">${s.name}: ${(s.words||[]).join(', ')}</span><button class="btn-sm" onclick="playTextSentence(${i})">▶</button><button class="btn-sm btn-danger" onclick="deleteTextSentence(${i})">✕</button></div>`).join(''); container.querySelectorAll('.sentence-row').forEach(row => { row.addEventListener('dragstart', (e) => { e.dataTransfer.setData('text/plain', row.dataset.idx); row.classList.add('dragging'); }); row.addEventListener('dragend', () => row.classList.remove('dragging')); row.addEventListener('dragover', (e) => { e.preventDefault(); row.classList.add('drag-over'); }); row.addEventListener('dragleave', () => row.classList.remove('drag-over')); row.addEventListener('drop', (e) => { e.preventDefault(); row.classList.remove('drag-over'); const from = parseInt(e.dataTransfer.getData('text/plain')); const to = parseInt(row.dataset.idx); if (from !== to && !isNaN(from) && !isNaN(to)) { const s = getSentences(); const [moved] = s.splice(from, 1); s.splice(to, 0, moved); saveSentences(s); loadText(); } }); }); }
        async function playText() { const sentences = getSentences(); if (sentences.length === 0) return; const allWords = getAllWordsForSelect(); for (const s of sentences) { const words = s.words.map(name => allWords.find(w => w.name === name)).filter(Boolean); if (words.length === 0) continue; const allPrims = words.flatMap(w => w.primitives || []); const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('textSpeed') + '&instrument=' + currentInstrument); const a = new Audio(URL.createObjectURL(await ar.blob())); a.play(); await new Promise(r => { a.onended = r; setTimeout(r, 5000); }); } }
        async function playTextSentence(idx) { const sentences = getSentences(); if (!sentences[idx]) return; const allWords = getAllWordsForSelect(); const words = sentences[idx].words.map(name => allWords.find(w => w.name === name)).filter(Boolean); if (words.length === 0) return; const allPrims = words.flatMap(w => w.primitives || []); const ar = await fetch('/compose_play?words=' + encodeURIComponent(allPrims.join(',')) + '&speed=' + getSpeed('textSpeed') + '&instrument=' + currentInstrument); new Audio(URL.createObjectURL(await ar.blob())).play(); }
        function deleteTextSentence(idx) { const s = getSentences(); s.splice(idx, 1); saveSentences(s); loadText(); }
        function clearText() { if (confirm('Delete all?')) { saveSentences([]); loadText(); } }
        
        // === TUTORIAL ===
        function showTutorial() {
            const seen = localStorage.getItem('solres_tutorial_seen');
            if (!seen) {
                document.getElementById('tutorialOverlay').style.display = 'flex';
            }
        }
        function closeTutorial() {
            document.getElementById('tutorialOverlay').style.display = 'none';
            localStorage.setItem('solres_tutorial_seen', '1');
        }
        showTutorial();

        loadSentenceRows();
    </script>
    

    <!-- TUTORIAL OVERLAY -->
    <div id="tutorialOverlay" style=" position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:100; align-items:center; justify-content:center;">
        <div style="background:var(--surface); border:1px solid var(--accent); border-radius:16px; padding:30px; max-width:500px; text-align:center; margin:20px;">
            <h2 style="color:var(--accent); margin-bottom:16px;">🎵 Welcome to SolRes!</h2>
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
            <button class="btn btn-primary" onclick="closeTutorial()" style="margin-top:20px; width:100%;">🚀 Get Started!</button>
        </div>
    </div>
</body>
</html>
"""


def _build_primitives_rows():
    rows = []
    for e in primitives.primitives.values():
        rows.append(f"<tr><td><span class='badge'>{e['category']}</span></td><td>{e['ru']}</td><td>{e['en']}</td><td style='font-family:monospace;font-size:0.8em;color:var(--muted);'>{e['pattern']}</td></tr>")
    return '\n'.join(rows)


def _build_words_rows():
    rows = []
    for word, data in sorted(descriptors.descriptions.items()):
        desc = ' + '.join(data['ru'])
        rows.append(f"<tr><td>{word}</td><td>{data['en']}</td><td style='font-size:0.85em;'>{desc}</td><td><button class='btn-sm' onclick='playDictWord(\"{word}\")'>▶</button></td></tr>")
    return '\n'.join(rows)


def _build_categories_json():
    import json; cats = {}
    for e in primitives.primitives.values():
        cats.setdefault(e['category'], []).append(e['ru'])
    return json.dumps(cats, ensure_ascii=False)


def _build_category_order_json():
    import json
    return json.dumps(DescriptorGrammar.CATEGORY_ORDER, ensure_ascii=False)


def _build_primitive_info_json():
    import json; info = {}
    for e in primitives.primitives.values():
        info[e['ru']] = {'pattern': e['pattern'], 'en': e['en'], 'category': e['category']}
    return json.dumps(info, ensure_ascii=False)


def _build_dictionary_words_json():
    import json
    return json.dumps(descriptors.descriptions, ensure_ascii=False)


@app.route('/')
def home():
    return render_template_string(HTML,
        primitives_count=primitives.total_count(), descriptions_count=len(descriptors.descriptions),
        primitives_rows=_build_primitives_rows(), words_rows=_build_words_rows(),
        categories_json=_build_categories_json(), category_order_json=_build_category_order_json(),
        primitive_info_json=_build_primitive_info_json(), dictionary_words_json=_build_dictionary_words_json())


@app.route('/translate')
def translate():
    word = request.args.get('word', '').strip(); tonic = Note(NoteName.DO, 4)
    desc = descriptors.get_description(word) or descriptors.get_description_en(word)
    if desc: notes, _ = descriptors.describe_to_notes(word, tonic); meaning = word
    else:
        prim = primitives.get_by_ru(word) or primitives.get_by_en(word)
        if prim: notes = descriptors.describe_to_notes(word, tonic)[0]; meaning = prim["ru"] + " / " + prim["en"]; desc = [prim["ru"]]
        else: return jsonify({'notes': '—', 'meaning': 'not found', 'description': [], 'error': 'Not found'})
    nn = [];
    for n in notes:
        m = n.to_midi(); s = m % 12
        nn.append(f"{n.name.name}{'♯' if s in SHARP_SEMITONES else ''}{n.octave}")
    return jsonify({'notes': ' → '.join(nn), 'meaning': meaning, 'description': desc})


@app.route('/play')
def play():
    word = request.args.get('word', '').strip()
    instrument = request.args.get('instrument', 'piano')
    notes, _ = descriptors.describe_to_notes(word, Note(NoteName.DO, 4))
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
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav')


@app.route('/compose')
def compose():
    words = [w.strip() for w in request.args.get('words', '').split(',') if w.strip()]
    result = descriptors.validate_order(words)
    if not result["valid"]: return jsonify({'error': '; '.join(result["errors"])})
    tonic = Note(NoteName.DO, 4); notes = [tonic]; cm = tonic.to_midi(); bo = 4
    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            mv = descriptors._pattern_to_movements(prim["pattern"])
            if mv:
                st, dr = mv[0]; cm += dr * st
                co = (cm // 12) - 1
                if co > bo + 1: cm -= 12
                elif co < bo - 1: cm += 12
                notes.append(descriptors._midi_to_note(cm))
    nn = [];
    for n in notes:
        m = n.to_midi(); s = m % 12
        nn.append(f"{n.name.name}{'♯' if s in SHARP_SEMITONES else ''}{n.octave}")
    return jsonify({'notes': ' → '.join(nn), 'words': result["correct_order"]})


@app.route('/compose_play')
def compose_play():
    words = [w.strip() for w in request.args.get('words', '').split(',') if w.strip()]
    instrument = request.args.get('instrument', 'piano')
    result = descriptors.validate_order(words)
    tonic = Note(NoteName.DO, 4); notes = [tonic]; cm = tonic.to_midi(); bo = 4
    for pw in result["correct_order"]:
        prim = primitives.get_by_ru(pw) or primitives.get_by_en(pw)
        if prim:
            mv = descriptors._pattern_to_movements(prim["pattern"])
            if mv:
                st, dr = mv[0]; cm += dr * st
                co = (cm // 12) - 1
                if co > bo + 1: cm -= 12
                elif co < bo - 1: cm += 12
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
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
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
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
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
        w = generate_wave(midi_to_frequency(midi), dur, instrument=instrument)
        combined = np.concatenate([combined, w, silence])
    audio_int16 = (combined * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave_module.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav')

@app.route('/analyze')
def analyze():
    intervals = [int(i) for i in request.args.get('intervals', '').split(',') if i.strip()]
    results = []; all_found = True; primitives_ru = []
    for diff in intervals:
        direction = "UP" if diff > 0 else "DOWN" if diff < 0 else "STATIC"
        abs_diff = abs(diff); found = None
        for entry in primitives.primitives.values():
            for part in entry['pattern'].split(','):
                if part.endswith("_STATIC"): continue
                if part.endswith("_UP"): iname = part[:-3]; pdir = "UP"
                elif part.endswith("_DOWN"): iname = part[:-5]; pdir = "DOWN"
                else: continue
                try:
                    from core.constants import Interval
                    iv = Interval[iname].value
                except: iv = None
                if iv is not None and iv == abs_diff and pdir == direction:
                    found = {'ru': entry['ru'], 'en': entry['en'], 'found': True}; break
            if found: break
        if found: primitives_ru.append(found['ru']); results.append(found)
        else: all_found = False; results.append({'found': False})
    word_found = None
    if all_found and len(primitives_ru) >= 2:
        for word, data in descriptors.descriptions.items():
            if data['ru'] == primitives_ru: word_found = word; break
    return jsonify({'results': results, 'all_found': all_found, 'primitives_ru': primitives_ru, 'word_found': word_found})


with app.app_context():
    db.create_all()


@app.route('/shared/words')
def shared_words():
    words = SharedWord.query.order_by(SharedWord.id.desc()).all()
    return jsonify([{'id': w.id, 'name': w.name, 'primitives': w.primitives.split(','), 'author': w.author, 'source': w.source, 'created': w.created} for w in words])


@app.route('/shared/words/add', methods=['POST'])
def add_shared_word():
    data = request.get_json()
    w = SharedWord(name=data['name'], primitives=','.join(data['primitives']), author=data.get('author', 'Anonymous'), source=data.get('source', '👤 User'), created=data.get('created', ''))
    db.session.add(w); db.session.commit()
    return jsonify({'id': w.id, 'status': 'ok'})


@app.route('/shared/words/<int:word_id>/delete', methods=['DELETE'])
def delete_shared_word(word_id):
    w = SharedWord.query.get_or_404(word_id)
    db.session.delete(w); db.session.commit()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 SolRes Web App")
    print(f"   Primitives: {primitives.total_count()}")
    print(f"   Descriptions: {len(descriptors.descriptions)}")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)