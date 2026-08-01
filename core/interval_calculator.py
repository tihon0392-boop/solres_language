# core/interval_calculator.py
from .constants import NoteName, Interval, Direction  # Точка всё ещё нужна здесь

NOTE_TO_SEMITONE = {
    0: 0,   # DO = C
    1: 2,   # RE = D
    2: 4,   # MI = E
    3: 5,   # FA = F
    4: 7,   # SOL = G
    5: 9,   # LA = A
    6: 11,  # SI = B
}

class Note:
    def __init__(self, name: NoteName, octave: int = 4):
        self.name = name
        self.octave = octave

    def to_midi(self) -> int:
        semitone = NOTE_TO_SEMITONE[self.name.value]
        return (self.octave + 1) * 12 + semitone

    def to_frequency(self, base_freq: float = 440.0) -> float:
        midi_note = self.to_midi()
        return base_freq * (2 ** ((midi_note - 69) / 12))

    def __repr__(self):
        return f"Note({self.name.name}, {self.octave})"


class IntervalCalculator:
    @staticmethod
    def calculate(note1: Note, note2: Note) -> tuple[Interval, Direction]:
        midi1 = note1.to_midi()
        midi2 = note2.to_midi()
        diff = midi2 - midi1

        if diff == 0:
            return Interval.UNISON, Direction.STATIC
        elif diff > 0:
            direction = Direction.UP
        else:
            direction = Direction.DOWN

        semitones = abs(diff) % 12
        return Interval(semitones), direction

    @staticmethod
    def calculate_melodic_pattern(notes: list[Note]) -> list[dict]:
        if len(notes) < 2:
            return []

        pattern = []
        for i in range(len(notes) - 1):
            interval, direction = IntervalCalculator.calculate(notes[i], notes[i+1])
            pattern.append({
                "interval": interval,
                "direction": direction,
                "semitones": interval.value
            })
        return pattern