# language/lexicon.py
from core.interval_calculator import Note, IntervalCalculator, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval, Direction


class Lexicon:
    """
    Иерархический словарь языка Сольрес.
    Слова строятся как пути: категория → подкатегория → уточнение.
    """

    def __init__(self):
        self.calc = IntervalCalculator()
        self.words_by_pattern = {}
        self.words_by_meaning = {}

        # Дерево категорий для автодополнения
        self.category_tree = {}

        self._init_vocabulary()

    def _add_word(self, pattern_str: str, meanings: list[str], category: str = None):
        """Добавляет слово в словари."""
        self.words_by_pattern[pattern_str] = {
            "meanings": meanings,
            "category": category
        }
        for meaning in meanings:
            if meaning not in self.words_by_meaning:
                self.words_by_meaning[meaning] = []
            self.words_by_meaning[meaning].append(pattern_str)

    def _init_vocabulary(self):
        """
        Иерархический словарь.
        Формат: ПУТЬ = категория → подкатегория → уточнение
        """

        # ========== УРОВЕНЬ 1: КАТЕГОРИИ (первые 2-3 ноты) ==========

        # --- СВЕТ / НЕБЕСНЫЕ ТЕЛА ---
        # Корень: СВЕТ (MAJOR_THIRD_UP = 4 полутона вверх)
        self._add_word("MAJOR_THIRD_UP",
                       ["свет", "light", "свечение", "сияние"],
                       "корень:свет")

        # СВЕТ + МАЛАЯ ТЕРЦИЯ ВВЕРХ = СОЛНЦЕ (свет + тепло)
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_UP",
                       ["солнце", "sun", "дневное светило"],
                       "свет:солнце")

        # СВЕТ + МАЛАЯ ТЕРЦИЯ ВНИЗ = ЛУНА (свет + холод)
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_DOWN",
                       ["луна", "moon", "ночное светило"],
                       "свет:луна")

        # СВЕТ + КВИНТА ВВЕРХ = ЗВЕЗДА (далёкий свет)
        self._add_word("MAJOR_THIRD_UP,PERFECT_FIFTH_UP",
                       ["звезда", "star", "далёкий свет"],
                       "свет:звезда")

        # --- УТОЧНЕНИЯ СОЛНЦА ---
        # СОЛНЦЕ + СЕКУНДА ВВЕРХ = ВОСХОД
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_UP,MAJOR_SECOND_UP",
                       ["восход", "sunrise", "рассвет", "утреннее солнце"],
                       "свет:солнце:восход")

        # СОЛНЦЕ + ТЕРЦИЯ ВНИЗ = ЗАКАТ
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_UP,MINOR_THIRD_DOWN",
                       ["закат", "sunset", "вечернее солнце"],
                       "свет:солнце:закат")

        # --- УТОЧНЕНИЯ ЛУНЫ ---
        # ЛУНА + КВАРТА ВВЕРХ = ПОЛНОЛУНИЕ
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_DOWN,PERFECT_FOURTH_UP",
                       ["полнолуние", "full moon", "круглая луна"],
                       "свет:луна:полнолуние")

        # ЛУНА + МАЛАЯ СЕКУНДА ВНИЗ = МЕСЯЦ (серп)
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_DOWN,MINOR_SECOND_DOWN",
                       ["месяц", "crescent", "серп луны"],
                       "свет:луна:месяц")

        # --- УТОЧНЕНИЯ ЗВЕЗДЫ ---
        # ЗВЕЗДА + УНИСОН = ПОЛЯРНАЯ ЗВЕЗДА
        self._add_word("MAJOR_THIRD_UP,PERFECT_FIFTH_UP,UNISON_STATIC",
                       ["полярная звезда", "polaris", "north star"],
                       "свет:звезда:полярная")

        # ЗВЕЗДА + МАЛАЯ СЕКУНДА ВВЕРХ = МЕРЦАЮЩАЯ ЗВЕЗДА
        self._add_word("MAJOR_THIRD_UP,PERFECT_FIFTH_UP,MINOR_SECOND_UP",
                       ["мерцающая звезда", "twinkling star"],
                       "свет:звезда:мерцающая")

        # ========== ВОДА ==========
        # Корень: ВОДА (MINOR_THIRD_DOWN = течение вниз)
        self._add_word("MINOR_THIRD_DOWN",
                       ["вода", "water", "жидкость"],
                       "корень:вода")

        # ВОДА + СЕКУНДА ВНИЗ = РЕКА (течёт)
        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN",
                       ["река", "river", "поток"],
                       "вода:река")

        # ВОДА + КВИНТА ВВЕРХ = МОРЕ
        self._add_word("MINOR_THIRD_DOWN,PERFECT_FIFTH_UP",
                       ["море", "sea", "океан", "ocean"],
                       "вода:море")

        # РЕКА + КВАРТА ВВЕРХ = ВОДОПАД
        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN,PERFECT_FOURTH_UP",
                       ["водопад", "waterfall"],
                       "вода:река:водопад")

        # РЕКА + СЕКУНДА ВВЕРХ = РУЧЕЙ (маленькая река)
        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN,MAJOR_SECOND_UP",
                       ["ручей", "stream", "brook"],
                       "вода:река:ручей")

        # ========== ЗЕМЛЯ ==========
        self._add_word("PERFECT_FOURTH_DOWN",
                       ["земля", "earth", "почва", "ground"],
                       "корень:земля")

        # ЗЕМЛЯ + ТЕРЦИЯ ВВЕРХ = ГОРА
        self._add_word("PERFECT_FOURTH_DOWN,MAJOR_THIRD_UP",
                       ["гора", "mountain", "возвышенность"],
                       "земля:гора")

        # ЗЕМЛЯ + ТЕРЦИЯ ВНИЗ = ЯМА
        self._add_word("PERFECT_FOURTH_DOWN,MINOR_THIRD_DOWN",
                       ["яма", "pit", "hole", "углубление"],
                       "земля:яма")

        # ГОРА + КВИНТА ВВЕРХ = ВЕРШИНА
        self._add_word("PERFECT_FOURTH_DOWN,MAJOR_THIRD_UP,PERFECT_FIFTH_UP",
                       ["вершина", "peak", "summit"],
                       "земля:гора:вершина")

        # ========== ДЕЙСТВИЯ (MAJOR_SECOND = движение) ==========
        self._add_word("MAJOR_SECOND_UP",
                       ["движение", "motion", "move"],
                       "корень:движение")

        self._add_word("MAJOR_SECOND_UP,MAJOR_SECOND_UP",
                       ["идти", "go", "walk", "ходить"],
                       "движение:идти")

        self._add_word("MAJOR_SECOND_UP,MAJOR_THIRD_UP",
                       ["бежать", "run", "бег"],
                       "движение:бежать")

        self._add_word("MAJOR_SECOND_DOWN,MAJOR_THIRD_DOWN",
                       ["падать", "fall", "падение"],
                       "движение:падать")

        # ИДТИ + КВИНТА ВВЕРХ = ПУТЕШЕСТВИЕ
        self._add_word("MAJOR_SECOND_UP,MAJOR_SECOND_UP,PERFECT_FIFTH_UP",
                       ["путешествие", "journey", "travel", "поход"],
                       "движение:идти:путешествие")

        # ========== ЭМОЦИИ (MINOR_THIRD) ==========
        self._add_word("MINOR_THIRD_UP",
                       ["чувство", "feeling", "эмоция"],
                       "корень:чувство")

        self._add_word("MINOR_THIRD_UP,MAJOR_SECOND_UP",
                       ["радость", "joy", "счастье", "happy"],
                       "чувство:радость")

        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN",
                       ["грусть", "sadness", "печаль", "sad"],
                       "чувство:грусть")

        self._add_word("MINOR_THIRD_UP,PERFECT_FIFTH_UP",
                       ["любовь", "love", "сердце"],
                       "чувство:любовь")

        self._add_word("MINOR_THIRD_DOWN,TRITON_DOWN",
                       ["страх", "fear", "ужас", "afraid"],
                       "чувство:страх")

        # РАДОСТЬ + КВИНТА = ВОСТОРГ
        self._add_word("MINOR_THIRD_UP,MAJOR_SECOND_UP,PERFECT_FIFTH_UP",
                       ["восторг", "delight", "экстаз", "euphoria"],
                       "чувство:радость:восторг")

        # ========== МЕСТОИМЕНИЯ (UNISON) ==========
        self._add_word("UNISON_STATIC,UNISON_STATIC",
                       ["я", "I", "me", "себя", "сам"])

        self._add_word("UNISON_STATIC,MAJOR_SECOND_UP",
                       ["ты", "you", "тебя", "вы"])

        self._add_word("UNISON_STATIC,MAJOR_THIRD_UP",
                       ["он", "he", "она", "she", "оно", "it"])

        self._add_word("UNISON_STATIC,PERFECT_FOURTH_UP",
                       ["мы", "we", "нас", "вместе"])

        # ========== СВЯЗКИ ==========
        self._add_word("UNISON_STATIC,PERFECT_FOURTH_UP",
                       ["быть", "be", "являться", "is", "am", "are"])

        self._add_word("MINOR_SECOND_UP,MINOR_SECOND_DOWN",
                       ["нет", "no", "не", "not"])

        self._add_word("PERFECT_FIFTH_UP,PERFECT_FIFTH_DOWN",
                       ["да", "yes", "согласие", "true"])

    def pattern_to_string(self, pattern: list) -> str:
        parts = []
        for item in pattern:
            parts.append(f"{item['interval'].name}_{item['direction'].name}")
        return ",".join(parts)

    def notes_to_words(self, notes: list[Note]) -> list[str]:
        if len(notes) < 2:
            return []

        # Ищем точное совпадение (самый длинный путь)
        full_pattern = self.calc.calculate_melodic_pattern(notes)
        pattern_str = self.pattern_to_string(full_pattern)

        if pattern_str in self.words_by_pattern:
            return self.words_by_pattern[pattern_str]["meanings"]

        # Ищем частичные совпадения (укороченные пути)
        results = []
        for i in range(len(full_pattern), 1, -1):
            sub_pattern = self.pattern_to_string(full_pattern[:i])
            if sub_pattern in self.words_by_pattern:
                results.extend(self.words_by_pattern[sub_pattern]["meanings"])
                break

        return results if results else [f"неизвестно ({pattern_str})"]

    def words_to_notes(self, word: str, tonic: Note) -> list[Note]:
        word_lower = word.lower()

        if word_lower in self.words_by_meaning:
            patterns = self.words_by_meaning[word_lower]
            pattern_str = patterns[0]
            return self._pattern_to_notes(pattern_str, tonic)

        for pattern_str, data in self.words_by_pattern.items():
            if word_lower in [m.lower() for m in data["meanings"]]:
                return self._pattern_to_notes(pattern_str, tonic)

        return [tonic]

    def _pattern_to_notes(self, pattern_str: str, tonic: Note) -> list[Note]:
        notes = [tonic]
        current_midi = tonic.to_midi()

        parts = pattern_str.split(",")
        for part in parts:
            if part.endswith("_UP"):
                direction = 1
                interval_name = part[:-3]
            elif part.endswith("_DOWN"):
                direction = -1
                interval_name = part[:-5]
            elif part.endswith("_STATIC"):
                direction = 0
                interval_name = part[:-7]
            else:
                direction = 0
                interval_name = part

            interval_value = Interval[interval_name].value
            current_midi = current_midi + (direction * interval_value)

            octave = (current_midi // 12) - 1
            semitone_in_octave = current_midi % 12

            note_name = NoteName.DO
            for name_idx, semitone in NOTE_TO_SEMITONE.items():
                if semitone == semitone_in_octave:
                    note_name = NoteName(name_idx)
                    break

            notes.append(Note(note_name, octave))

        return notes

    def get_category(self, word: str) -> str:
        """Возвращает категорию слова."""
        word_lower = word.lower()
        for pattern_str, data in self.words_by_pattern.items():
            if word_lower in [m.lower() for m in data["meanings"]]:
                return data.get("category", "неизвестно")
        return "неизвестно"

    def search_by_prefix(self, prefix_notes: list[Note]) -> list[str]:
        """Ищет все слова, начинающиеся с данного префикса нот."""
        if len(prefix_notes) < 2:
            return []

        prefix_pattern = self.calc.calculate_melodic_pattern(prefix_notes)
        prefix_str = self.pattern_to_string(prefix_pattern)

        results = []
        for pattern_str, data in self.words_by_pattern.items():
            if pattern_str.startswith(prefix_str) and pattern_str != prefix_str:
                results.extend(data["meanings"])

        return results


if __name__ == "__main__":
    lex = Lexicon()

    print("=" * 60)
    print("🌳 ИЕРАРХИЧЕСКИЙ СЛОВАРЬ СОЛЬРЕС")
    print("=" * 60)

    from core.constants import NoteName

    tests = [
        ("солнце", "Солнце (3 ноты)"),
        ("восход", "Восход (4 ноты — уточнение солнца)"),
        ("полнолуние", "Полнолуние (4 ноты)"),
        ("водопад", "Водопад (4 ноты)"),
        ("восторг", "Восторг (4 ноты)"),
    ]

    for word, desc in tests:
        tonic = Note(NoteName.DO, 4)
        notes = lex.words_to_notes(word, tonic)
        category = lex.get_category(word)
        print(f"\n{desc}")
        print(f"  Путь: {category}")
        print(f"  Ноты: {' → '.join([str(n) for n in notes])}")
        print(f"  Длина: {len(notes)} нот")