# language/lexicon.py
from core.interval_calculator import Note, IntervalCalculator, NOTE_TO_SEMITONE
from core.constants import NoteName, Interval, Direction


class Lexicon:
    """
    Словарь языка Сольрес.
    Хранит слова как паттерны интервалов, а не конкретные ноты.
    """

    def __init__(self):
        self.calc = IntervalCalculator()
        self.words_by_pattern = {}
        self.words_by_meaning = {}
        self._init_vocabulary()

    def _add_word(self, pattern_str: str, meanings: list[str]):
        """Добавляет слово в оба словаря."""
        self.words_by_pattern[pattern_str] = meanings
        for meaning in meanings:
            if meaning not in self.words_by_meaning:
                self.words_by_meaning[meaning] = []
            self.words_by_meaning[meaning].append(pattern_str)

    def _init_vocabulary(self):
        """Расширенный словарь языка Сольрес."""

        # ========== ОБЪЕКТЫ ПРИРОДЫ (MAJOR_THIRD) ==========
        self._add_word("MAJOR_THIRD_UP,MINOR_THIRD_UP",
                       ["солнце", "sun", "свет", "день", "огонь", "звезда", "star"])

        self._add_word("MAJOR_THIRD_UP,MAJOR_THIRD_DOWN",
                       ["луна", "moon", "ночь", "отражение"])

        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN",
                       ["вода", "water", "река", "течение", "море", "sea"])

        self._add_word("MAJOR_THIRD_UP,PERFECT_FOURTH_UP",
                       ["гора", "mountain", "верх", "небо", "sky"])

        self._add_word("MINOR_THIRD_DOWN,PERFECT_FOURTH_DOWN",
                       ["земля", "earth", "земля", "почва", "ground", "низ"])

        self._add_word("MAJOR_THIRD_UP,MAJOR_SECOND_UP",
                       ["птица", "bird", "полёт", "fly", "крыло"])

        self._add_word("MAJOR_THIRD_DOWN,MAJOR_SECOND_UP",
                       ["рыба", "fish", "плыть", "swim"])

        self._add_word("MINOR_THIRD_UP,MINOR_SECOND_UP",
                       ["цветок", "flower", "растение", "plant", "трава"])

        self._add_word("MAJOR_THIRD_UP,TRITON_UP",
                       ["молния", "lightning", "гроза", "storm", "гром"])

        self._add_word("MINOR_THIRD_UP,PERFECT_FIFTH_UP",
                       ["ветер", "wind", "воздух", "air", "дышать"])

        # ========== ДЕЙСТВИЯ (MAJOR_SECOND) ==========
        self._add_word("MAJOR_SECOND_UP,MAJOR_SECOND_UP",
                       ["идти", "go", "двигаться", "walk", "ехать"])

        self._add_word("MAJOR_SECOND_DOWN,UNISON_STATIC",
                       ["стоять", "stand", "ждать", "stop", "стоп"])

        self._add_word("MAJOR_SECOND_UP,MINOR_THIRD_UP",
                       ["бежать", "run", "быстро", "спешить"])

        self._add_word("MAJOR_SECOND_DOWN,MAJOR_THIRD_DOWN",
                       ["падать", "fall", "упасть", "вниз"])

        self._add_word("MAJOR_SECOND_UP,PERFECT_FOURTH_UP",
                       ["прыгать", "jump", "прыжок", "вверх"])

        self._add_word("MAJOR_SECOND_UP,MAJOR_SECOND_DOWN",
                       ["давать", "give", "дать", "передать"])

        self._add_word("MAJOR_SECOND_DOWN,MAJOR_SECOND_UP",
                       ["брать", "take", "взять", "получить"])

        self._add_word("PERFECT_FIFTH_UP,MAJOR_SECOND_DOWN",
                       ["делать", "do", "создавать", "make", "работать", "work"])

        self._add_word("MAJOR_SECOND_UP,MINOR_SEVENTH_UP",
                       ["говорить", "say", "speak", "сказать", "talk"])

        self._add_word("MAJOR_SECOND_DOWN,MINOR_SECOND_DOWN",
                       ["спать", "sleep", "отдыхать", "rest"])

        self._add_word("MAJOR_SECOND_UP,MAJOR_SIXTH_UP",
                       ["петь", "sing", "песня", "song", "музыка"])

        self._add_word("PERFECT_FOURTH_UP,MAJOR_SECOND_UP",
                       ["смотреть", "see", "видеть", "look", "watch"])

        self._add_word("PERFECT_FOURTH_DOWN,MAJOR_SECOND_DOWN",
                       ["слышать", "hear", "слушать", "listen", "звук"])

        # ========== ЧУВСТВА (MINOR_THIRD) ==========
        self._add_word("MINOR_THIRD_UP,MAJOR_SECOND_UP",
                       ["радость", "joy", "счастье", "happy", "веселье"])

        self._add_word("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN",
                       ["грусть", "sadness", "печаль", "sad"])

        self._add_word("MINOR_THIRD_UP,PERFECT_FIFTH_UP",
                       ["любовь", "love", "любить", "сердце"])

        self._add_word("MINOR_THIRD_DOWN,TRITON_DOWN",
                       ["страх", "fear", "бояться", "ужас", "afraid"])

        self._add_word("MINOR_THIRD_UP,MINOR_SIXTH_UP",
                       ["надежда", "hope", "вера", "ждать"])

        self._add_word("MINOR_THIRD_DOWN,PERFECT_FIFTH_DOWN",
                       ["гнев", "anger", "злость", "ярость", "angry"])

        self._add_word("MAJOR_THIRD_UP,MINOR_SECOND_UP",
                       ["удивление", "surprise", "чудо", "wonder"])

        self._add_word("MINOR_THIRD_UP,UNISON_STATIC",
                       ["спокойствие", "peace", "мир", "тишина", "calm"])

        # ========== АБСТРАКТНЫЕ ПОНЯТИЯ (PERFECT_FOURTH) ==========
        self._add_word("PERFECT_FOURTH_UP,MAJOR_SECOND_DOWN",
                       ["дом", "home", "убежище", "house", "здание"])

        self._add_word("PERFECT_FOURTH_UP,MINOR_THIRD_UP",
                       ["друг", "friend", "дружба", "близкий"])

        self._add_word("PERFECT_FOURTH_DOWN,MINOR_THIRD_DOWN",
                       ["враг", "enemy", "противник", "чужой"])

        self._add_word("PERFECT_FOURTH_UP,PERFECT_FIFTH_UP",
                       ["сила", "power", "мощь", "strong", "энергия"])

        self._add_word("PERFECT_FOURTH_DOWN,PERFECT_FIFTH_DOWN",
                       ["слабость", "weakness", "слабый", "weak"])

        self._add_word("PERFECT_FOURTH_UP,MINOR_SEVENTH_UP",
                       ["мысль", "thought", "думать", "think", "идея", "idea"])

        self._add_word("PERFECT_FIFTH_UP,PERFECT_FOURTH_UP",
                       ["время", "time", "час", "пора"])

        self._add_word("PERFECT_FIFTH_DOWN,PERFECT_FOURTH_DOWN",
                       ["конец", "end", "финал", "смерть", "death"])

        self._add_word("PERFECT_FIFTH_UP,MAJOR_THIRD_UP",
                       ["начало", "beginning", "start", "рождение", "birth"])

        # ========== ПРИЛАГАТЕЛЬНЫЕ (MINOR_SIXTH) ==========
        self._add_word("MINOR_SIXTH_UP,MAJOR_SECOND_UP",
                       ["большой", "big", "large", "великий", "great"])

        self._add_word("MINOR_SIXTH_DOWN,MAJOR_SECOND_DOWN",
                       ["маленький", "small", "little", "tiny"])

        self._add_word("MAJOR_SIXTH_UP,MINOR_THIRD_UP",
                       ["красивый", "beautiful", "pretty", "красота"])

        self._add_word("MAJOR_SIXTH_DOWN,MINOR_THIRD_DOWN",
                       ["уродливый", "ugly", "страшный"])

        self._add_word("MINOR_SIXTH_UP,PERFECT_FIFTH_UP",
                       ["хороший", "good", "добрый", "nice"])

        self._add_word("MINOR_SIXTH_DOWN,TRITON_DOWN",
                       ["плохой", "bad", "злой", "evil"])

        self._add_word("MAJOR_SIXTH_UP,MAJOR_SECOND_UP",
                       ["новый", "new", "молодой", "young"])

        self._add_word("MAJOR_SIXTH_DOWN,MAJOR_SECOND_DOWN",
                       ["старый", "old", "древний"])

        # ========== НАРЕЧИЯ (MAJOR_SIXTH) ==========
        self._add_word("MAJOR_SIXTH_UP,PERFECT_FIFTH_UP",
                       ["быстро", "fast", "quick", "скоро"])

        self._add_word("MAJOR_SIXTH_DOWN,PERFECT_FIFTH_DOWN",
                       ["медленно", "slow", "тихо", "slowly"])

        self._add_word("MINOR_SEVENTH_UP,MAJOR_SECOND_UP",
                       ["громко", "loud", "громкий", "loudly"])

        self._add_word("MINOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN",
                       ["тихо", "quiet", "quietly", "шёпот"])

        self._add_word("MAJOR_SEVENTH_UP,MINOR_THIRD_UP",
                       ["всегда", "always", "вечно", "forever"])

        self._add_word("MAJOR_SEVENTH_DOWN,MINOR_THIRD_DOWN",
                       ["никогда", "never", "никогда"])

        # ========== МЕСТОИМЕНИЯ (UNISON) ==========
        self._add_word("UNISON_STATIC,UNISON_STATIC",
                       ["я", "I", "me", "себя", "сам"])

        self._add_word("UNISON_STATIC,MAJOR_SECOND_UP",
                       ["ты", "you", "тебя", "вы"])

        self._add_word("UNISON_STATIC,MAJOR_THIRD_UP",
                       ["он", "he", "она", "she", "оно", "it"])

        self._add_word("UNISON_STATIC,PERFECT_FOURTH_UP",
                       ["мы", "we", "нас", "вместе"])

        self._add_word("UNISON_STATIC,PERFECT_FIFTH_UP",
                       ["они", "they", "их", "them"])

        self._add_word("UNISON_STATIC,MAJOR_SEVENTH_UP",
                       ["кто", "who", "кто"])

        self._add_word("UNISON_STATIC,TRITON_UP",
                       ["что", "what", "что", "вещь", "thing"])

        # ========== СВЯЗКИ И СЛУЖЕБНЫЕ СЛОВА ==========
        self._add_word("UNISON_STATIC,PERFECT_FOURTH_UP",
                       ["быть", "be", "являться", "is", "am", "are"])

        self._add_word("MINOR_SECOND_UP,MINOR_SECOND_DOWN",
                       ["нет", "no", "не", "not", "отрицание"])

        self._add_word("PERFECT_FIFTH_UP,PERFECT_FIFTH_DOWN",
                       ["да", "yes", "согласие", "истина", "true"])

        self._add_word("MAJOR_SECOND_UP,PERFECT_FIFTH_UP",
                       ["и", "and", "также", "тоже", "плюс"])

        self._add_word("MAJOR_SECOND_DOWN,TRITON_DOWN",
                       ["или", "or", "либо", "выбор"])

        self._add_word("PERFECT_FOURTH_UP,MINOR_SECOND_UP",
                       ["для", "for", "ради", "чтобы"])

        self._add_word("PERFECT_FOURTH_DOWN,MINOR_SECOND_DOWN",
                       ["от", "from", "из", "прочь"])

        self._add_word("MINOR_SEVENTH_UP,PERFECT_FIFTH_UP",
                       ["здесь", "here", "тут", "сюда"])

        self._add_word("MINOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN",
                       ["там", "there", "туда", "далеко"])

    def pattern_to_string(self, pattern: list) -> str:
        """Превращает паттерн в строку-ключ."""
        parts = []
        for item in pattern:
            parts.append(f"{item['interval'].name}_{item['direction'].name}")
        return ",".join(parts)

    def notes_to_words(self, notes: list[Note]) -> list[str]:
        """Переводит последовательность нот в слова."""
        if len(notes) < 2:
            return []

        full_pattern = self.calc.calculate_melodic_pattern(notes)
        pattern_str = self.pattern_to_string(full_pattern)

        if pattern_str in self.words_by_pattern:
            return self.words_by_pattern[pattern_str]

        return [f"неизвестно ({pattern_str})"]

    def words_to_notes(self, word: str, tonic: Note) -> list[Note]:
        """Переводит слово в ноты от заданной тоники."""
        word_lower = word.lower()

        # Прямой поиск по ключу
        if word_lower in self.words_by_meaning:
            patterns = self.words_by_meaning[word_lower]
            pattern_str = patterns[0]
            return self._pattern_to_notes(pattern_str, tonic)

        # Поиск среди значений
        for pattern_str, meanings in self.words_by_pattern.items():
            if word_lower in [m.lower() for m in meanings]:
                return self._pattern_to_notes(pattern_str, tonic)

        return [tonic]

    def _pattern_to_notes(self, pattern_str: str, tonic: Note) -> list[Note]:
        """Превращает строку паттерна в конкретные ноты от тоники."""
        notes = [tonic]
        current_midi = tonic.to_midi()

        parts = pattern_str.split(",")
        for part in parts:
            # part выглядит как "MAJOR_THIRD_UP"
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

            # Получаем значение интервала
            interval_value = Interval[interval_name].value

            # Вычисляем MIDI следующей ноты
            current_midi = current_midi + (direction * interval_value)

            # Обратный поиск: MIDI → (NoteName, octave)
            octave = (current_midi // 12) - 1
            semitone_in_octave = current_midi % 12

            # Ищем имя ноты по полутону
            note_name = None
            for name_idx, semitone in NOTE_TO_SEMITONE.items():
                if semitone == semitone_in_octave:
                    note_name = NoteName(name_idx)
                    break

            if note_name is None:
                note_name = NoteName.DO  # Заглушка для диезов/бемолей

            next_note = Note(note_name, octave)
            notes.append(next_note)

        return notes


# Быстрый тест
if __name__ == "__main__":
    lex = Lexicon()

    print(f"Слов в базе: {len(lex.words_by_pattern)}")

    do = Note(NoteName.DO, 4)
    mi = Note(NoteName.MI, 4)
    sol = Note(NoteName.SOL, 4)

    # Тест: ноты → смысл
    result = lex.notes_to_words([do, mi, sol])
    print(f"До-Ми-Соль → {result}")

    # Тест: смысл → ноты
    notes = lex.words_to_notes("солнце", do)
    print(f"'солнце' от До → {[str(n) for n in notes]}")

    # Тест: английское слово
    notes2 = lex.words_to_notes("joy", do)
    print(f"'joy' от До → {[str(n) for n in notes2]}")