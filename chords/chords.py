# chords/chords.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.interval_calculator import Note, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval


class ChordLexicon:
    """
    Аккордовый словарь Сольрес.
    Базовый аккорд = категория. Добавочная нота = уточнение.
    """

    def __init__(self):
        self.base_chords = {}  # Базовые аккорды (3 ноты)
        self.extensions = {}  # Расширения (4-я нота)
        self._init_chords()

    def _init_chords(self):
        # Базовые аккорды: (интервал1, интервал2) → [значения]
        self.base_chords = {
            (4, 7): ["свет", "light", "солнце", "sun", "радость", "joy"],
            (3, 7): ["тьма", "darkness", "грусть", "sadness", "луна", "moon"],
            (3, 6): ["страх", "fear", "опасность", "danger"],
            (5, 7): ["вопрос", "question", "поиск", "search"],
            (4, 9): ["любовь", "love", "нежность"],
            (5, 9): ["дом", "home", "убежище", "shelter"],
        }

        # Расширения: (базовый_аккорд, добавочный_интервал) → уточнение
        self.extensions = {
            # СОЛНЦЕ (4,7) + ...
            ((4, 7), 2): "восход",  # + большая секунда = восход
            ((4, 7), -3): "закат",  # + малая терция вниз = закат
            ((4, 7), 9): "полдень",  # + большая секста = полдень

            # ЛУНА (3,7) + ...
            ((3, 7), 5): "полнолуние",  # + кварта = полная луна
            ((3, 7), -1): "месяц",  # + малая секунда вниз = серп

            # ЛЮБОВЬ (4,9) + ...
            ((4, 9), 7): "страсть",  # + квинта = страсть
            ((4, 9), -5): "тоска",  # + кварта вниз = тоска

            # ДОМ (5,9) + ...
            ((5, 9), 4): "крепость",  # + большая терция = крепость
            ((5, 9), -2): "убежище",  # + секунда вниз = убежище
        }

    def notes_to_chord_meaning(self, notes: list[Note]) -> list[str]:
        """Ноты → смысл аккорда с расширением."""
        if len(notes) < 3:
            return []

        tonic = notes[0].to_midi()
        intervals = []

        for note in notes[1:]:
            interval = (note.to_midi() - tonic) % 12
            intervals.append(interval)

        # Ищем базовый аккорд (первые 3 ноты)
        base_key = tuple(sorted(intervals[:2]))
        meanings = []

        if base_key in self.base_chords:
            meanings.extend(self.base_chords[base_key])

        # Ищем расширение (4-я нота)
        if len(intervals) >= 3:
            ext_interval = intervals[2]
            # Нормализуем направление
            if ext_interval > 6:
                ext_interval = ext_interval - 12

            ext_key = (base_key, ext_interval)
            if ext_key in self.extensions:
                meanings.append(self.extensions[ext_key])

        return meanings if meanings else [f"аккорд {intervals}"]

    def meaning_to_chord(self, meaning: str, tonic: Note) -> list[Note]:
        """Смысл → ноты аккорда (с расширением)."""
        meaning_lower = meaning.lower()

        # Ищем в базовых
        for intervals, meanings in self.base_chords.items():
            if meaning_lower in [m.lower() for m in meanings]:
                return self._build_chord(intervals, tonic)

        # Ищем в расширениях
        for (base_intervals, ext), ext_meaning in self.extensions.items():
            if meaning_lower == ext_meaning.lower():
                base_chord = self._build_chord(base_intervals, tonic)
                # Добавляем расширение
                ext_midi = tonic.to_midi() + ext
                if ext < 0:
                    ext_midi = tonic.to_midi() + ext + 12
                octave = (ext_midi // 12) - 1
                semitone = ext_midi % 12

                note_name = NoteName.DO
                for name_idx, st in NOTE_TO_SEMITONE.items():
                    if st == semitone:
                        note_name = NoteName(name_idx)
                        break

                base_chord.append(Note(note_name, octave))
                return base_chord

        return [tonic]

    def _build_chord(self, intervals: tuple, tonic: Note) -> list[Note]:
        """Строит аккорд от тоники."""
        tonic_midi = tonic.to_midi()
        notes = [tonic]

        for semitones in intervals:
            midi = tonic_midi + semitones
            octave = (midi // 12) - 1
            semitone_in_octave = midi % 12

            note_name = NoteName.DO
            for name_idx, st in NOTE_TO_SEMITONE.items():
                if st == semitone_in_octave:
                    note_name = NoteName(name_idx)
                    break

            notes.append(Note(note_name, octave))

        return notes

    def get_all_chords(self) -> dict:
        return self.base_chords


if __name__ == "__main__":
    from core.interval_calculator import Note
    from core.constants import NoteName
    from core.synthesizer import Synthesizer

    chord_lex = ChordLexicon()
    synth = Synthesizer(volume=0.2)
    tonic = Note(NoteName.DO, 4)

    print("=" * 60)
    print("🎹 АККОРДЫ С РАСШИРЕНИЯМИ")
    print("=" * 60)

    tests = [
        ("солнце", "Базовый мажорный аккорд"),
        ("восход", "Солнце + расширение"),
        ("закат", "Солнце + расширение вниз"),
        ("страсть", "Любовь + расширение"),
    ]

    for meaning, desc in tests:
        notes = chord_lex.meaning_to_chord(meaning, tonic)
        note_names = [n.name.name for n in notes]
        print(f"\n{desc}: {meaning}")
        print(f"  Аккорд: {' + '.join(note_names)} ({len(notes)} ноты)")
        synth.play_chord(notes, 1000, "piano")