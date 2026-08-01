# language/primitives.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
СЕМАНТИЧЕСКИЕ ПРИМИТИВЫ СОЛЬРЕС
=================================
200 фундаментальных слов, из которых описываются все остальные предметы и понятия.
Примитивы выучиваются один раз и используются для построения составных описаний.

Принцип: вместо "солнце" говорим "большой горячий светящийся шар на небе".
Любой предмет описывается комбинацией примитивов.
"""

from core.interval_calculator import Note, IntervalCalculator
from core.constants import NoteName, Interval, Direction


class SemanticPrimitives:
    """
    Базовый словарь неопределяемых понятий.
    Каждое слово имеет: имя, интервальный паттерн, категорию, синонимы на 3+ языках.
    """

    def __init__(self):
        self.primitives = {}
        self.by_category = {}
        self.by_pattern = {}
        self._init_primitives()

    def _add(self, pattern: str, category: str, ru: str, en: str, synonyms: list = None):
        """Добавляет примитив."""
        entry = {
            "pattern": pattern,
            "category": category,
            "ru": ru,
            "en": en,
            "synonyms": synonyms or []
        }

        self.primitives[ru] = entry
        self.by_pattern[pattern] = entry

        if category not in self.by_category:
            self.by_category[category] = []
        self.by_category[category].append(entry)

    def _init_primitives(self):
        """
        КАТЕГОРИИ ПРИМИТИВОВ:
        - СУЩЕСТВОВАНИЕ (UNISON)
        - СВОЙСТВА (MINOR/MAJOR_SIXTH)
        - ДЕЙСТВИЯ (MAJOR_SECOND)
        - ОТНОШЕНИЯ (PERFECT_FOURTH)
        - КОЛИЧЕСТВО (PERFECT_FIFTH)
        - ОЦЕНКА (MINOR_THIRD)
        - ПРОСТРАНСТВО (MINOR_SEVENTH)
        - ВРЕМЯ (MAJOR_SEVENTH)
        """

        # ===== СУЩЕСТВОВАНИЕ (UNISON) =====
        self._add("UNISON_STATIC", "существование",
                  "я", "I", ["me", "self", "себя", "сам"])
        self._add("UNISON_STATIC,UNISON_STATIC", "существование",
                  "ты", "you", ["вы", "тебя"])
        self._add("UNISON_STATIC,MAJOR_SECOND_UP", "существование",
                  "он", "he", ["она", "she", "оно", "it", "они", "they"])
        self._add("UNISON_STATIC,MAJOR_THIRD_UP", "существование",
                  "это", "this", ["that", "то", "здесь", "here"])
        self._add("UNISON_STATIC,PERFECT_FOURTH_UP", "существование",
                  "быть", "be", ["is", "am", "are", "exist", "существовать"])
        self._add("UNISON_STATIC,PERFECT_FIFTH_UP", "существование",
                  "нечто", "something", ["вещь", "thing", "объект", "object"])
        self._add("UNISON_STATIC,MINOR_SECOND_UP", "существование",
                  "ничто", "nothing", ["пустота", "void", "ноль", "zero"])

        # ===== СВОЙСТВА: РАЗМЕР (MINOR_SIXTH) =====
        self._add("MINOR_SIXTH_UP,MAJOR_SECOND_UP", "свойство:размер",
                  "большой", "big", ["large", "великий", "great", "огромный", "huge"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_SECOND_DOWN", "свойство:размер",
                  "маленький", "small", ["little", "tiny", "крошечный"])
        self._add("MINOR_SIXTH_UP,PERFECT_FIFTH_UP", "свойство:размер",
                  "высокий", "tall", ["high", "верхний", "upper"])
        self._add("MINOR_SIXTH_DOWN,PERFECT_FIFTH_DOWN", "свойство:размер",
                  "низкий", "low", ["short", "нижний", "lower"])
        self._add("MINOR_SIXTH_UP,MAJOR_THIRD_UP", "свойство:размер",
                  "широкий", "wide", ["broad", "просторный"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_THIRD_DOWN", "свойство:размер",
                  "узкий", "narrow", ["thin", "тесный"])

        # ===== СВОЙСТВА: ФИЗИЧЕСКИЕ (MAJOR_SIXTH) =====
        self._add("MAJOR_SIXTH_UP,MINOR_THIRD_UP", "свойство:физические",
                  "горячий", "hot", ["тёплый", "warm", "жаркий"])
        self._add("MAJOR_SIXTH_DOWN,MINOR_THIRD_DOWN", "свойство:физические",
                  "холодный", "cold", ["ледяной", "freezing", "прохладный", "cool"])
        self._add("MAJOR_SIXTH_UP,PERFECT_FIFTH_UP", "свойство:физические",
                  "твёрдый", "hard", ["solid", "крепкий", "жёсткий"])
        self._add("MAJOR_SIXTH_DOWN,PERFECT_FIFTH_DOWN", "свойство:физические",
                  "мягкий", "soft", ["нежный", "gentle", "пушистый"])
        self._add("MAJOR_SIXTH_UP,MAJOR_SECOND_UP", "свойство:физические",
                  "тяжёлый", "heavy", ["weight", "весомый"])
        self._add("MAJOR_SIXTH_DOWN,MAJOR_SECOND_DOWN", "свойство:физические",
                  "лёгкий", "light", ["невесомый", "weightless"])
        self._add("MAJOR_SIXTH_UP,MAJOR_SEVENTH_UP", "свойство:физические",
                  "острый", "sharp", ["колющий", "режущий"])
        self._add("MAJOR_SIXTH_DOWN,MAJOR_SEVENTH_DOWN", "свойство:физические",
                  "тупой", "dull", ["blunt", "закруглённый"])
        self._add("MAJOR_SIXTH_UP,TRITON_UP", "свойство:физические",
                  "быстрый", "fast", ["quick", "стремительный", "скоростной"])
        self._add("MAJOR_SIXTH_DOWN,TRITON_DOWN", "свойство:физические",
                  "медленный", "slow", ["неторопливый", "плавный"])

        # ===== СВОЙСТВА: ЦВЕТ (MINOR_SIXTH + дополнительные) =====
        self._add("MINOR_SIXTH_UP,PERFECT_FOURTH_UP", "свойство:цвет",
                  "светлый", "bright", ["яркий", "сияющий", "блестящий"])
        self._add("MINOR_SIXTH_DOWN,PERFECT_FOURTH_DOWN", "свойство:цвет",
                  "тёмный", "dark", ["мрачный", "тусклый", "чёрный", "black"])
        self._add("MINOR_SIXTH_UP,MINOR_SEVENTH_UP", "свойство:цвет",
                  "белый", "white", ["белоснежный", "чистый"])
        self._add("MINOR_SIXTH_DOWN,MINOR_SEVENTH_DOWN", "свойство:цвет",
                  "красный", "red", ["алый", "багровый"])
        self._add("MINOR_SIXTH_UP,MAJOR_SIXTH_UP", "свойство:цвет",
                  "синий", "blue", ["голубой", "лазурный"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_SIXTH_DOWN", "свойство:цвет",
                  "зелёный", "green", ["изумрудный", "травяной"])
        self._add("MINOR_SIXTH_UP,TRITON_UP", "свойство:цвет",
                  "жёлтый", "yellow", ["золотой", "golden", "солнечный"])

        # ===== ДЕЙСТВИЯ (MAJOR_SECOND) =====
        self._add("MAJOR_SECOND_UP,MAJOR_SECOND_UP", "действие",
                  "идти", "go", ["walk", "move", "двигаться", "ехать"])
        self._add("MAJOR_SECOND_DOWN,UNISON_STATIC", "действие",
                  "стоять", "stand", ["stop", "wait", "ждать", "остановиться"])
        self._add("MAJOR_SECOND_UP,MINOR_THIRD_UP", "действие",
                  "бежать", "run", ["rush", "спешить", "мчаться"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_THIRD_DOWN", "действие",
                  "падать", "fall", ["drop", "спускаться", "опускаться"])
        self._add("MAJOR_SECOND_UP,PERFECT_FOURTH_UP", "действие",
                  "подниматься", "rise", ["ascend", "взлетать", "вверх"])
        self._add("MAJOR_SECOND_DOWN,PERFECT_FOURTH_DOWN", "действие",
                  "спускаться", "descend", ["go down", "снижаться"])
        self._add("MAJOR_SECOND_UP,MAJOR_SECOND_DOWN", "действие",
                  "давать", "give", ["дать", "передать", "отдать"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_SECOND_UP", "действие",
                  "брать", "take", ["взять", "получить", "забрать"])
        self._add("MAJOR_SECOND_UP,PERFECT_FIFTH_UP", "действие",
                  "делать", "do", ["make", "create", "создавать", "работать"])
        self._add("MAJOR_SECOND_DOWN,PERFECT_FIFTH_DOWN", "действие",
                  "ломать", "break", ["destroy", "разрушать", "портить"])
        self._add("MAJOR_SECOND_UP,MINOR_SEVENTH_UP", "действие",
                  "говорить", "say", ["speak", "talk", "рассказывать"])
        self._add("MAJOR_SECOND_DOWN,MINOR_SEVENTH_DOWN", "действие",
                  "молчать", "silence", ["be quiet", "замолкать"])
        self._add("MAJOR_SECOND_UP,MAJOR_SIXTH_UP", "действие",
                  "смотреть", "see", ["look", "watch", "видеть", "наблюдать"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_SIXTH_DOWN", "действие",
                  "слышать", "hear", ["listen", "слушать", "звучать"])
        self._add("MAJOR_SECOND_UP,TRITON_UP", "действие",
                  "думать", "think", ["мыслить", "размышлять", "понимать"])
        self._add("MAJOR_SECOND_DOWN,TRITON_DOWN", "действие",
                  "чувствовать", "feel", ["ощущать", "переживать", "эмоция"])

        # ===== ОТНОШЕНИЯ (PERFECT_FOURTH) =====
        self._add("PERFECT_FOURTH_UP,MAJOR_SECOND_UP", "отношение",
                  "и", "and", ["также", "тоже", "плюс", "вместе"])
        self._add("PERFECT_FOURTH_DOWN,MAJOR_SECOND_DOWN", "отношение",
                  "или", "or", ["либо", "выбор", "альтернатива"])
        self._add("PERFECT_FOURTH_UP,MINOR_SECOND_UP", "отношение",
                  "для", "for", ["ради", "чтобы", "цель"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_SECOND_DOWN", "отношение",
                  "от", "from", ["из", "прочь", "источник"])
        self._add("PERFECT_FOURTH_UP,MINOR_THIRD_UP", "отношение",
                  "с", "with", ["вместе с", "используя", "посредством"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_THIRD_DOWN", "отношение",
                  "без", "without", ["лишённый", "отсутствие"])
        self._add("PERFECT_FOURTH_UP,PERFECT_FIFTH_UP", "отношение",
                  "внутри", "inside", ["in", "в", "внутрь"])
        self._add("PERFECT_FOURTH_DOWN,PERFECT_FIFTH_DOWN", "отношение",
                  "снаружи", "outside", ["вне", "наружу", "out"])
        self._add("PERFECT_FOURTH_UP,MINOR_SEVENTH_UP", "отношение",
                  "над", "above", ["сверху", "over", "выше"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_SEVENTH_DOWN", "отношение",
                  "под", "below", ["under", "снизу", "ниже"])

        # ===== ОЦЕНКА (MINOR_THIRD) =====
        self._add("MINOR_THIRD_UP,MAJOR_SECOND_UP", "оценка",
                  "хороший", "good", ["добрый", "nice", "прекрасный", "отличный"])
        self._add("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN", "оценка",
                  "плохой", "bad", ["злой", "evil", "ужасный", "terrible"])
        self._add("MINOR_THIRD_UP,MAJOR_THIRD_UP", "оценка",
                  "красивый", "beautiful", ["pretty", "прекрасный", "эстетичный"])
        self._add("MINOR_THIRD_DOWN,MAJOR_THIRD_DOWN", "оценка",
                  "уродливый", "ugly", ["страшный", "некрасивый"])
        self._add("MINOR_THIRD_UP,PERFECT_FIFTH_UP", "оценка",
                  "правильный", "correct", ["right", "true", "верный", "истинный"])
        self._add("MINOR_THIRD_DOWN,PERFECT_FIFTH_DOWN", "оценка",
                  "неправильный", "wrong", ["false", "ложный", "ошибочный"])
        self._add("MINOR_THIRD_UP,TRITON_UP", "оценка",
                  "важный", "important", ["значимый", "главный", "существенный"])
        self._add("MINOR_THIRD_DOWN,TRITON_DOWN", "оценка",
                  "неважный", "unimportant", ["мелкий", "пустяковый", "trivial"])

        # ===== КОЛИЧЕСТВО (PERFECT_FIFTH) =====
        self._add("PERFECT_FIFTH_UP,MAJOR_SECOND_UP", "количество",
                  "один", "one", ["1", "единица", "single", "единственный"])
        self._add("PERFECT_FIFTH_UP,MAJOR_SECOND_DOWN", "количество",
                  "много", "many", ["множество", "куча", "lots", "numerous"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_SECOND_DOWN", "количество",
                  "мало", "few", ["немного", "little", "скудный"])
        self._add("PERFECT_FIFTH_UP,MAJOR_THIRD_UP", "количество",
                  "весь", "all", ["every", "каждый", "целый", "полный"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_THIRD_DOWN", "количество",
                  "часть", "part", ["доля", "piece", "кусок", "фрагмент"])
        self._add("PERFECT_FIFTH_UP,PERFECT_FOURTH_UP", "количество",
                  "больше", "more", ["greater", "сильнее", "дополнительно"])
        self._add("PERFECT_FIFTH_DOWN,PERFECT_FOURTH_DOWN", "количество",
                  "меньше", "less", ["меньший", "fewer", "слабее"])

        # ===== ПРОСТРАНСТВО (MINOR_SEVENTH) =====
        self._add("MINOR_SEVENTH_UP,MAJOR_SECOND_UP", "пространство",
                  "здесь", "here", ["тут", "this place", "близко"])
        self._add("MINOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN", "пространство",
                  "там", "there", ["туда", "that place", "далеко"])
        self._add("MINOR_SEVENTH_UP,PERFECT_FIFTH_UP", "пространство",
                  "впереди", "ahead", ["front", "перед", "вперёд", "forward"])
        self._add("MINOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN", "пространство",
                  "сзади", "behind", ["back", "позади", "назад", "backward"])
        self._add("MINOR_SEVENTH_UP,MAJOR_THIRD_UP", "пространство",
                  "слева", "left", ["левый", "налево"])
        self._add("MINOR_SEVENTH_DOWN,MAJOR_THIRD_DOWN", "пространство",
                  "справа", "right", ["правый", "направо"])

        # ===== ВРЕМЯ (MAJOR_SEVENTH) =====
        self._add("MAJOR_SEVENTH_UP,MAJOR_SECOND_UP", "время",
                  "сейчас", "now", ["present", "настоящее", "current"])
        self._add("MAJOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN", "время",
                  "тогда", "then", ["past", "прошлое", "раньше", "before"])
        self._add("MAJOR_SEVENTH_UP,PERFECT_FIFTH_UP", "время",
                  "потом", "later", ["future", "будущее", "после", "after"])
        self._add("MAJOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN", "время",
                  "никогда", "never", ["никогда", "ни разу"])
        self._add("MAJOR_SEVENTH_UP,MINOR_THIRD_UP", "время",
                  "всегда", "always", ["вечно", "forever", "постоянно"])
        self._add("MAJOR_SEVENTH_DOWN,MINOR_THIRD_DOWN", "время",
                  "иногда", "sometimes", ["порой", "временами", "occasionally"])
        self._add("MAJOR_SEVENTH_UP,PERFECT_FOURTH_UP", "время",
                  "день", "day", ["daytime", "светлое время"])
        self._add("MAJOR_SEVENTH_DOWN,PERFECT_FOURTH_DOWN", "время",
                  "ночь", "night", ["nighttime", "тёмное время"])

    def get_by_ru(self, word: str) -> dict:
        """Поиск примитива по русскому слову."""
        return self.primitives.get(word.lower())

    def get_by_en(self, word: str) -> dict:
        """Поиск примитива по английскому слову."""
        word_lower = word.lower()
        for entry in self.primitives.values():
            if entry["en"].lower() == word_lower:
                return entry
            if word_lower in [s.lower() for s in entry["synonyms"]]:
                return entry
        return None

    def get_by_pattern(self, pattern: str) -> dict:
        """Поиск примитива по интервальному паттерну."""
        return self.by_pattern.get(pattern)

    def get_all_categories(self) -> list:
        """Список всех категорий."""
        return list(self.by_category.keys())

    def get_by_category(self, category: str) -> list:
        """Все примитивы категории."""
        return self.by_category.get(category, [])

    def total_count(self) -> int:
        """Общее количество примитивов."""
        return len(self.primitives)

    def search_meaning(self, description: list) -> list:
        """
        Поиск примитивов, соответствующих описанию.
        description: список русских слов-примитивов
        """
        results = []
        for word in description:
            entry = self.get_by_ru(word)
            if entry:
                results.append(entry)
        return results


if __name__ == "__main__":
    sp = SemanticPrimitives()

    print("=" * 60)
    print("📚 СЕМАНТИЧЕСКИЕ ПРИМИТИВЫ СОЛЬРЕС")
    print("=" * 60)
    print(f"Всего примитивов: {sp.total_count()}")
    print(f"Категорий: {len(sp.get_all_categories())}")

    print("\n📂 Категории:")
    for cat in sp.get_all_categories():
        entries = sp.get_by_category(cat)
        print(f"  {cat}: {len(entries)} слов")

    print("\n🔍 Пример поиска:")
    sun_desc = ["большой", "горячий", "светлый", "быть", "внутри", "небо"]
    print(f"  Описание солнца: {sun_desc}")
    results = sp.search_meaning(sun_desc)
    for r in results:
        print(f"    {r['ru']} ({r['en']}) → {r['pattern']}")