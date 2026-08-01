# core/synthesizer.py
import numpy as np
import sounddevice as sd
from .interval_calculator import Note  # Точка нужна

SAMPLE_RATE = 44100

class Synthesizer:
    def __init__(self, volume: float = 0.3):
        self.volume = volume

    def _generate_wave(self, frequency: float, duration_ms: int, wave_type: str = "piano") -> np.ndarray:
        num_samples = int(SAMPLE_RATE * duration_ms / 1000.0)
        t = np.linspace(0, duration_ms / 1000.0, num_samples, False)

        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "piano":
            wave = (
                np.sin(2 * np.pi * frequency * t) * 1.0 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 3 * t) * 0.25 +
                np.sin(2 * np.pi * frequency * 4 * t) * 0.125 +
                np.sin(2 * np.pi * frequency * 5 * t) * 0.06
            )
            decay = np.exp(-3.0 * t / (duration_ms / 1000.0))
            wave *= decay
        elif wave_type == "organ":
            wave = (
                np.sin(2 * np.pi * frequency * t) * 1.0 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.7 +
                np.sin(2 * np.pi * frequency * 3 * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 4 * t) * 0.3 +
                np.sin(2 * np.pi * frequency * 5 * t) * 0.2 +
                np.sin(2 * np.pi * frequency * 6 * t) * 0.1
            )
        elif wave_type == "violin":
            vibrato = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t)
            wave = np.sin(2 * np.pi * frequency * t * vibrato)
            wave += np.sin(2 * np.pi * frequency * 2 * t) * 0.3
            attack = np.linspace(0, 1, int(num_samples * 0.1))
            wave[:len(attack)] *= attack
        else:
            wave = np.sin(2 * np.pi * frequency * t)

        # Реверберация
        reverb_delay = int(SAMPLE_RATE * 0.03)
        reverb_wave = np.zeros_like(wave)
        if len(wave) > reverb_delay:
            reverb_wave[reverb_delay:] = wave[:-reverb_delay] * 0.2
        wave = wave + reverb_wave

        # Огибающая
        attack = int(num_samples * 0.01)
        release = int(num_samples * 0.05)
        envelope = np.ones(num_samples)
        if attack > 1:
            envelope[:attack] = np.linspace(0, 1, attack)
        if release > 1:
            envelope[-release:] = np.linspace(1, 0, release)

        return (wave * envelope * self.volume).astype(np.float32)

    def play_note(self, note: Note, duration_ms: int = 500, instrument: str = "piano"):
        wave = self._generate_wave(note.to_frequency(), duration_ms, instrument)
        sd.play(wave, SAMPLE_RATE)
        sd.wait()

    def play_sequence(self, sequence: list, instrument: str = "piano"):
        for item in sequence:
            if isinstance(item, tuple):
                note, duration = item
            else:
                note = item
                duration = 500
            wave = self._generate_wave(note.to_frequency(), duration, instrument)
            sd.play(wave, SAMPLE_RATE)
            sd.wait()

    def play_chord(self, notes: list[Note], duration_ms: int = 500, instrument: str = "piano"):
        if not notes:
            return
        num_samples = int(SAMPLE_RATE * duration_ms / 1000.0)
        chord = np.zeros(num_samples, dtype=np.float32)
        for note in notes:
            wave = self._generate_wave(note.to_frequency(), duration_ms, instrument)
            chord += wave
        max_val = np.max(np.abs(chord))
        if max_val > 0.9:
            chord = chord / max_val * 0.9
        sd.play(chord, SAMPLE_RATE)
        sd.wait()