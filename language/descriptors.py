# language/descriptors.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from language.primitives import SemanticPrimitives
from core.interval_calculator import Note, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval


class DescriptorGrammar:
    ORDER = [
        "свойство:размер",
        "свойство:физические",
        "свойство:цвет",
        "действие",
        "отношение",
        "оценка",
        "время"
    ]

    def __init__(self):
        self.primitives = SemanticPrimitives()
        self.descriptions = {}
        self._init_descriptions()

    def _init_descriptions(self):
        self.descriptions = {
            "солнце": {"ru": ["большой", "горячий", "светлый", "подниматься", "над", "хороший", "день"], "en": "sun"},
            "луна": {"ru": ["большой", "холодный", "светлый", "подниматься", "над", "хороший", "ночь"], "en": "moon"},
            "звезда": {"ru": ["маленький", "горячий", "светлый", "быть", "над", "красивый", "ночь"], "en": "star"},
            "вода": {"ru": ["нечто", "холодный", "светлый", "падать", "внутри", "хороший", "всегда"], "en": "water"},
            "река": {"ru": ["нечто", "холодный", "светлый", "идти", "внутри", "хороший", "всегда"], "en": "river"},
            "огонь": {"ru": ["нечто", "горячий", "светлый", "подниматься", "над", "важный", "сейчас"], "en": "fire"},
            "гора": {"ru": ["большой", "твёрдый", "тёмный", "стоять", "над", "красивый", "всегда"], "en": "mountain"},
            "дом": {"ru": ["большой", "твёрдый", "светлый", "стоять", "внутри", "хороший", "всегда"], "en": "home"},
            "человек": {"ru": ["нечто", "горячий", "светлый", "думать", "внутри", "хороший", "сейчас"], "en": "human"},
            "птица": {"ru": ["маленький", "горячий", "светлый", "подниматься", "над", "красивый", "день"],
                      "en": "bird"},
            "рыба": {"ru": ["маленький", "холодный", "тёмный", "идти", "внутри", "хороший", "всегда"], "en": "fish"},
        }

    def _pattern_to_movements(self, pattern_str: str, skip_first_static: bool = False) -> list:
        movements = []
        parts = pattern_str.split(",")
        for i, part in enumerate(parts):
            # Пропускаем ВСЕ STATIC шаги
            if part.endswith("_STATIC"):
                continue

            if part.endswith("_UP"):
                direction = 1
                interval_name = part[:-3]
            elif part.endswith("_DOWN"):
                direction = -1
                interval_name = part[:-5]
            else:
                continue

            interval_value = Interval[interval_name].value
            movements.append((interval_value, direction))
        return movements

    def _midi_to_note(self, midi: int) -> Note:
        octave = (midi // 12) - 1
        semitone = midi % 12

        note_name_map = {
            0: NoteName.DO, 1: NoteName.DO, 2: NoteName.RE,
            3: NoteName.RE, 4: NoteName.MI, 5: NoteName.FA,
            6: NoteName.FA, 7: NoteName.SOL, 8: NoteName.SOL,
            9: NoteName.LA, 10: NoteName.LA, 11: NoteName.SI,
        }

        return Note(note_name_map[semitone], octave)

    def describe_to_notes(self, word: str, tonic: Note = None) -> tuple:
        if tonic is None:
            tonic = Note(NoteName.DO, 4)

        if word.lower() in self.descriptions:
            primitive_words = self.descriptions[word.lower()]["ru"]
        else:
            prim = self.primitives.get_by_ru(word)
            if prim:
                primitive_words = [word]
            else:
                return [tonic], []

        notes = [tonic]
        current_midi = tonic.to_midi()
        base_octave = 4
        boundaries = []

        for pw in primitive_words:
            prim = self.primitives.get_by_ru(pw)
            if prim:
                movements = self._pattern_to_movements(prim["pattern"])

                for semitones, direction in movements:
                    current_midi += direction * semitones

                    current_octave = (current_midi // 12) - 1
                    if current_octave > base_octave + 1:
                        current_midi -= 12
                    elif current_octave < base_octave - 1:
                        current_midi += 12

                    notes.append(self._midi_to_note(current_midi))

                boundaries.append(len(notes) - 1)

        return notes, boundaries

    def get_description(self, word: str) -> list:
        if word.lower() in self.descriptions:
            return self.descriptions[word.lower()]["ru"]
        return []

    def search_by_description(self, description_words: list) -> list:
        results = []
        desc_set = set(description_words)
        for word, data in self.descriptions.items():
            word_set = set(data["ru"])
            overlap = len(desc_set & word_set)
            threshold = max(1, len(desc_set) * 0.5)
            if overlap >= threshold:
                results.append((word, data["en"], overlap / len(desc_set)))
        return sorted(results, key=lambda x: x[2], reverse=True)


if __name__ == "__main__":
    dg = DescriptorGrammar()

    # Таблица диезов
    SHARP_SEMITONES = {1, 3, 6, 8, 10}

    print("=" * 60)
    print("📝 ФИНАЛЬНАЯ ОТЛАДКА")
    print("=" * 60)

    word = "солнце"
    notes, boundaries = dg.describe_to_notes(word)

    print(f"\n{word}: {len(notes)} нот")

    for i, n in enumerate(notes):
        midi = n.to_midi()
        semitone = midi % 12
        sharp = "♯" if semitone in SHARP_SEMITONES else ""
        marker = " |" if i in boundaries else ""
        print(f"  [{i}] {n.name.name}{sharp}{n.octave} (MIDI {midi}){marker}")