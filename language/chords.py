# language/chords.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.interval_calculator import Note, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval


class ChordLexicon:
    """
    Аккордовый словарь Сольрес.
    Аккорд = мгновенное слово. Три ноты одновременно = одно понятие.
    """

    def __init__(self):
        self.chords = {}
        self._init_chords()

    def _init_chords(self):
        # Структура: (интервал1, интервал2) → [значения]
        # Интервал от тоники до второй ноты, от тоники до третьей ноты

        self.chords = {
            # Мажорное трезвучие: тоника + большая терция + квинта
            (4, 7): ["солнце", "sun", "радость", "joy", "день", "свет", "да", "yes"],

            # Минорное трезвучие: тоника + малая терция + квинта
            (3, 7): ["грусть", "sadness", "луна", "moon", "ночь", "размышление"],

            # Уменьшённое: тоника + малая терция + тритон
            (3, 6): ["страх", "fear", "опасность", "danger", "тревога"],

            # Увеличенное: тоника + большая терция + малая секста
            (4, 8): ["удивление", "surprise", "чудо", "wonder"],

            # Sus4 (задержанное): тоника + кварта + квинта
            (5, 7): ["вопрос", "question", "неизвестность", "поиск"],

            # Мажорный секстаккорд: тоника + большая терция + большая секста
            (4, 9): ["любовь", "love", "нежность", "ласка"],

            # Квартсекстаккорд: тоника + кварта + большая секста
            (5, 9): ["дом", "home", "безопасность", "убежище"],
        }

    def notes_to_chord(self, notes: list[Note]) -> list[str]:
        """Три ноты → смысл аккорда."""
        if len(notes) < 3:
            return []

        tonic = notes[0].to_midi()
        interval1 = notes[1].to_midi() - tonic
        interval2 = notes[2].to_midi() - tonic

        # Нормализуем в пределах октавы
        interval1 = interval1 % 12
        interval2 = interval2 % 12

        # Сортируем для единообразия
        key = tuple(sorted([interval1, interval2]))

        if key in self.chords:
            return self.chords[key]

        return [f"аккорд {interval1}-{interval2}"]

    def chord_to_notes(self, meaning: str, tonic: Note) -> list[Note]:
        """Смысл → три ноты аккорда."""
        meaning_lower = meaning.lower()

        for intervals, meanings in self.chords.items():
            if meaning_lower in [m.lower() for m in meanings]:
                return self._build_chord(intervals, tonic)

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
        """Возвращает все аккорды."""
        return self.chords


if __name__ == "__main__":
    from core.interval_calculator import Note
    from core.constants import NoteName
    from core.synthesizer import Synthesizer

    chord_lex = ChordLexicon()
    synth = Synthesizer(volume=0.2)

    print("=" * 50)
    print("🎵 АККОРДОВЫЙ РЕЖИМ СОЛЬРЕС")
    print("=" * 50)

    tonic = Note(NoteName.DO, 4)

    for meaning in ["солнце", "грусть", "страх", "любовь", "вопрос"]:
        notes = chord_lex.chord_to_notes(meaning, tonic)
        print(f"\n{meaning}: {[str(n) for n in notes]}")
        synth.play_chord(notes, 1000, "piano")