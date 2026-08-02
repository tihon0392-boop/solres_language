# language/descriptors.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from language.primitives import SemanticPrimitives
from core.interval_calculator import Note, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval


class DescriptorGrammar:
    """
    Грамматика описаний.
    Порядок категорий ФИКСИРОВАН: существование → размер → физика → материал → форма →
    цвет → действие → отношение → оценка → количество → пространство → время.
    Минимум 2 примитива, максимум 12. Неиспользуемые категории пропускаются.
    """

    CATEGORY_ORDER = [
        "существование",
        "свойство:размер",
        "свойство:физические",
        "материал",
        "форма",
        "свойство:цвет",
        "действие",
        "отношение",
        "оценка",
        "количество",
        "пространство",
        "время"
    ]

    def __init__(self):
        self.primitives = SemanticPrimitives()
        self.descriptions = {}
        self._init_descriptions()

    def _init_descriptions(self):
        """Гибкие описания: минимум 2, максимум 12 примитивов."""

        self.descriptions = {
            # ===== НЕБЕСНЫЕ ТЕЛА =====
            "солнце": {
                "ru": ["большой", "горячий", "светлый", "подниматься", "над", "хороший", "день"],
                "en": "sun"
            },
            "луна": {
                "ru": ["большой", "холодный", "светлый", "подниматься", "над", "хороший", "ночь"],
                "en": "moon"
            },
            "звезда": {
                "ru": ["маленький", "горячий", "светлый", "быть", "над", "красивый", "ночь"],
                "en": "star"
            },

            # ===== ВОДА И СТИХИИ =====
            "вода": {
                "ru": ["холодный", "мокрый", "падать"],
                "en": "water"
            },
            "река": {
                "ru": ["холодный", "мокрый", "идти", "внутри"],
                "en": "river"
            },
            "море": {
                "ru": ["большой", "холодный", "синий", "двигаться", "снаружи"],
                "en": "sea"
            },
            "дождь": {
                "ru": ["холодный", "мокрый", "серый", "падать", "снаружи", "иногда"],
                "en": "rain"
            },
            "снег": {
                "ru": ["холодный", "мягкий", "белый", "падать", "снаружи", "красивый", "иногда"],
                "en": "snow"
            },
            "лёд": {
                "ru": ["твёрдый", "холодный", "прозрачный", "стоять", "снаружи"],
                "en": "ice"
            },
            "огонь": {
                "ru": ["горячий", "светлый", "подниматься", "над", "важный", "сейчас"],
                "en": "fire"
            },
            "воздух": {
                "ru": ["лёгкий", "невидимый", "двигаться", "снаружи", "всегда"],
                "en": "air"
            },
            "земля": {
                "ru": ["твёрдый", "коричневый", "стоять", "под", "всегда"],
                "en": "earth"
            },

            # ===== ГОРЫ И ЛАНДШАФТ =====
            "гора": {
                "ru": ["большой", "твёрдый", "камень", "стоять", "над", "красивый", "всегда"],
                "en": "mountain"
            },
            "лес": {
                "ru": ["большой", "зелёный", "дерево", "стоять", "снаружи", "хороший"],
                "en": "forest"
            },
            "пустыня": {
                "ru": ["большой", "горячий", "сухой", "песок", "снаружи", "пустой"],
                "en": "desert"
            },

            # ===== РАСТЕНИЯ =====
            "дерево": {
                "ru": ["большой", "твёрдый", "дерево", "зелёный", "стоять", "снаружи", "всегда"],
                "en": "tree"
            },
            "цветок": {
                "ru": ["маленький", "мягкий", "красный", "подниматься", "снаружи", "красивый", "день"],
                "en": "flower"
            },
            "трава": {
                "ru": ["маленький", "мягкий", "зелёный", "стоять", "снаружи", "всегда"],
                "en": "grass"
            },

            # ===== ЖИВОТНЫЕ =====
            "птица": {
                "ru": ["маленький", "горячий", "светлый", "подниматься", "над", "красивый", "день"],
                "en": "bird"
            },
            "рыба": {
                "ru": ["маленький", "холодный", "мокрый", "идти", "внутри"],
                "en": "fish"
            },
            "собака": {
                "ru": ["нечто", "твёрдый", "бежать", "с", "хороший", "всегда"],
                "en": "dog"
            },
            "кошка": {
                "ru": ["маленький", "мягкий", "серый", "стоять", "внутри", "красивый", "иногда"],
                "en": "cat"
            },
            "змея": {
                "ru": ["маленький", "гладкий", "зелёный", "двигаться", "снаружи", "плохой"],
                "en": "snake"
            },

            # ===== ЧЕЛОВЕК =====
            "человек": {
                "ru": ["нечто", "горячий", "думать", "внутри", "хороший", "сейчас"],
                "en": "human"
            },
            "ребёнок": {
                "ru": ["маленький", "мягкий", "светлый", "бежать", "с", "хороший", "новый"],
                "en": "child"
            },
            "друг": {
                "ru": ["нечто", "горячий", "быть", "с", "хороший", "всегда"],
                "en": "friend"
            },

            # ===== ДОМ И ЗДАНИЯ =====
            "дом": {
                "ru": ["большой", "твёрдый", "стоять", "внутри", "хороший"],
                "en": "home"
            },
            "город": {
                "ru": ["большой", "твёрдый", "металл", "стоять", "снаружи", "много"],
                "en": "city"
            },

            # ===== ЕДА =====
            "хлеб": {
                "ru": ["нечто", "мягкий", "делать", "внутри", "хороший"],
                "en": "bread"
            },
            "вода_питьевая": {
                "ru": ["нечто", "холодный", "мокрый", "брать", "внутри", "хороший"],
                "en": "drinking water"
            },

            # ===== ЭМОЦИИ =====
            "радость": {
                "ru": ["нечто", "быстрый", "светлый", "чувствовать", "внутри", "хороший", "сейчас"],
                "en": "joy"
            },
            "грусть": {
                "ru": ["нечто", "медленный", "тёмный", "чувствовать", "внутри", "плохой", "иногда"],
                "en": "sadness"
            },
            "любовь": {
                "ru": ["нечто", "горячий", "красный", "чувствовать", "внутри", "красивый", "всегда"],
                "en": "love"
            },
            "страх": {
                "ru": ["нечто", "быстрый", "тёмный", "чувствовать", "внутри", "плохой", "сейчас"],
                "en": "fear"
            },

            # ===== ВРЕМЕНА ГОДА =====
            "весна": {
                "ru": ["тёплый", "зелёный", "начинать", "снаружи", "красивый", "утро"],
                "en": "spring"
            },
            "лето": {
                "ru": ["горячий", "жёлтый", "жить", "снаружи", "хороший", "день"],
                "en": "summer"
            },
            "осень": {
                "ru": ["холодный", "оранжевый", "падать", "снаружи", "красивый", "вечер"],
                "en": "autumn"
            },
            "зима": {
                "ru": ["холодный", "белый", "падать", "снаружи", "плохой", "ночь"],
                "en": "winter"
            },
        }

    def _pattern_to_movements(self, pattern_str: str) -> list:
        movements = []
        parts = pattern_str.split(",")
        for part in parts:
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

        # Поиск: сначала русский, потом английский, потом примитив
        if word.lower() in self.descriptions:
            primitive_words = self.descriptions[word.lower()]["ru"]
        else:
            # Ищем в английских названиях
            found = self.get_description_en(word)
            if found:
                primitive_words = found
            else:
                prim = self.primitives.get_by_ru(word) or self.primitives.get_by_en(word)
                if prim:
                    primitive_words = [word]
                else:
                    return [tonic], []

            # Остальное без изменений...

        # Сортируем примитивы согласно CATEGORY_ORDER
        ordered_words = []
        for cat in self.CATEGORY_ORDER:
            for pw in primitive_words:
                prim = self.primitives.get_by_ru(pw) or self.primitives.get_by_en(pw)
                if prim and prim["category"] == cat:
                    if pw not in ordered_words:
                        ordered_words.append(pw)

        notes = [tonic]
        current_midi = tonic.to_midi()
        base_octave = 4
        boundaries = []

        for pw in ordered_words:
            prim = self.primitives.get_by_ru(pw) or self.primitives.get_by_en(pw)
            if prim:
                movements = self._pattern_to_movements(prim["pattern"])
                if movements:
                    semitones, direction = movements[0]
                    # Ограничиваем скачок 2-4 полутонами для плавности
                    step = max(2, min(4, semitones))
                    current_midi += direction * step

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

    def validate_order(self, primitive_words: list) -> dict:
        """
        Проверяет, что примитивы идут в правильном порядке категорий.
        Возвращает: {"valid": True/False, "errors": [список ошибок], "correct_order": [...]}
        """
        # Определяем категорию каждого примитива
        word_categories = []
        for pw in primitive_words:
            prim = self.primitives.get_by_ru(pw) or self.primitives.get_by_en(pw)
            if prim:
                word_categories.append((pw, prim["category"]))
            else:
                return {
                    "valid": False,
                    "errors": [f"Неизвестный примитив: '{pw}'"],
                    "correct_order": []
                }

        # Проверяем порядок
        errors = []
        last_cat_index = -1

        for pw, cat in word_categories:
            if cat not in self.CATEGORY_ORDER:
                errors.append(f"Неизвестная категория: '{cat}' (примитив '{pw}')")
                continue

            cat_index = self.CATEGORY_ORDER.index(cat)

            if cat_index < last_cat_index:
                prev_cat = self.CATEGORY_ORDER[last_cat_index]
                errors.append(
                    f"Нарушен порядок: '{pw}' (категория '{cat}') идёт после "
                    f"категории '{prev_cat}'. Правильный порядок: "
                    f"{' → '.join(self.CATEGORY_ORDER[last_cat_index:cat_index + 1])}"
                )

            last_cat_index = max(last_cat_index, cat_index)

        # Строим правильный порядок
        correct_order = [pw for pw, _ in sorted(word_categories,
                                                key=lambda x: self.CATEGORY_ORDER.index(x[1]) if x[
                                                                                                     1] in self.CATEGORY_ORDER else 999)]

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "correct_order": correct_order,
            "original_order": [pw for pw, _ in word_categories]
        }

    def get_description_en(self, word: str) -> list:
        """Возвращает описание для английского слова."""
        word_lower = word.lower()
        for data in self.descriptions.values():
            if data["en"].lower() == word_lower:
                return data["ru"]
        return []


if __name__ == "__main__":
    from core.synthesizer import Synthesizer
    from core.constants import NoteName
    from core.interval_calculator import Note

    dg = DescriptorGrammar()
    synth = Synthesizer(volume=0.25)

    print("=" * 50)
    print("🎵 ТЕСТ МЕЛОДИЙ (С ОГРАНИЧЕНИЕМ СКАЧКОВ)")
    print("=" * 50)

    words = ["солнце", "вода", "кошка", "любовь", "зима"]

    for word in words:
        notes, _ = dg.describe_to_notes(word)
        SHARP = {1, 3, 6, 8, 10}
        note_names = []
        for n in notes:
            midi = n.to_midi()
            sharp = "♯" if midi % 12 in SHARP else ""
            note_names.append(f"{n.name.name}{sharp}{n.octave}")

        print(f"\n{word}: {' → '.join(note_names)}")
        synth.play_sequence([(n, 350) for n in notes], "piano")