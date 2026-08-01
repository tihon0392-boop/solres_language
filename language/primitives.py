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
        - СВОЙСТВА:РАЗМЕР (MINOR_SIXTH)
        - СВОЙСТВА:ФИЗИЧЕСКИЕ (MAJOR_SIXTH)
        - СВОЙСТВА:ЦВЕТ (MINOR_SIXTH)
        - ДЕЙСТВИЯ (MAJOR_SECOND)
        - МАТЕРИАЛЫ (PERFECT_FIFTH + MAJOR_SIXTH)
        - ФОРМЫ (MAJOR_SEVENTH + MINOR_THIRD)
        - ОТНОШЕНИЯ (PERFECT_FOURTH)
        - ОЦЕНКА (MINOR_THIRD)
        - КОЛИЧЕСТВО (PERFECT_FIFTH)
        - ПРОСТРАНСТВО (MINOR_SEVENTH)
        - ВРЕМЯ (MAJOR_SEVENTH)
        """
        # ===== СУЩЕСТВОВАНИЕ (UNISON) =====
        self._add("UNISON_STATIC", "существование", "я", "I", ["me", "self", "себя", "сам"])
        self._add("UNISON_STATIC,UNISON_STATIC", "существование", "ты", "you", ["вы", "тебя"])
        self._add("UNISON_STATIC,MAJOR_SECOND_UP", "существование", "он", "he",
                  ["она", "she", "оно", "it", "они", "they"])
        self._add("UNISON_STATIC,MAJOR_THIRD_UP", "существование", "это", "this", ["that", "то", "здесь", "here"])
        self._add("UNISON_STATIC,PERFECT_FOURTH_UP", "существование", "быть", "be",
                  ["is", "am", "are", "exist", "существовать"])
        self._add("UNISON_STATIC,PERFECT_FIFTH_UP", "существование", "нечто", "something",
                  ["вещь", "thing", "объект", "object"])
        self._add("UNISON_STATIC,MINOR_SECOND_UP", "существование", "ничто", "nothing",
                  ["пустота", "void", "ноль", "zero"])
        self._add("UNISON_STATIC,MAJOR_SIXTH_UP", "существование", "всё", "everything",
                  ["all", "мир", "world", "вселенная", "universe"])
        self._add("UNISON_STATIC,MINOR_SEVENTH_UP", "существование", "кто-то", "someone",
                  ["кто-нибудь", "anybody", "личность", "person"])

        # ===== СВОЙСТВА: РАЗМЕР (MINOR_SIXTH) =====
        self._add("MINOR_SIXTH_UP,MAJOR_SECOND_UP", "свойство:размер", "большой", "big",
                  ["large", "великий", "great", "огромный", "huge", "гигантский"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_SECOND_DOWN", "свойство:размер", "маленький", "small",
                  ["little", "tiny", "крошечный", "миниатюрный"])
        self._add("MINOR_SIXTH_UP,PERFECT_FIFTH_UP", "свойство:размер", "высокий", "tall",
                  ["high", "верхний", "upper", "длинный"])
        self._add("MINOR_SIXTH_DOWN,PERFECT_FIFTH_DOWN", "свойство:размер", "низкий", "low",
                  ["short", "нижний", "lower", "короткий"])
        self._add("MINOR_SIXTH_UP,MAJOR_THIRD_UP", "свойство:размер", "широкий", "wide",
                  ["broad", "просторный", "объёмный"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_THIRD_DOWN", "свойство:размер", "узкий", "narrow",
                  ["thin", "тесный", "тонкий"])
        self._add("MINOR_SIXTH_UP,MINOR_THIRD_UP", "свойство:размер", "глубокий", "deep",
                  ["глубина", "бездна", "проfound"])
        self._add("MINOR_SIXTH_DOWN,MINOR_THIRD_DOWN", "свойство:размер", "мелкий", "shallow",
                  ["поверхностный", "неглубокий"])

        # ===== СВОЙСТВА: ФИЗИЧЕСКИЕ (MAJOR_SIXTH) =====
        self._add("MAJOR_SIXTH_UP,MINOR_THIRD_UP", "свойство:физические", "горячий", "hot",
                  ["тёплый", "warm", "жаркий", "обжигающий"])
        self._add("MAJOR_SIXTH_DOWN,MINOR_THIRD_DOWN", "свойство:физические", "холодный", "cold",
                  ["ледяной", "freezing", "прохладный", "cool", "морозный"])
        self._add("MAJOR_SIXTH_UP,PERFECT_FIFTH_UP", "свойство:физические", "твёрдый", "hard",
                  ["solid", "крепкий", "жёсткий", "каменный"])
        self._add("MAJOR_SIXTH_DOWN,PERFECT_FIFTH_DOWN", "свойство:физические", "мягкий", "soft",
                  ["нежный", "gentle", "пушистый", "эластичный"])
        self._add("MAJOR_SIXTH_UP,MAJOR_SECOND_UP", "свойство:физические", "тяжёлый", "heavy",
                  ["weight", "весомый", "массивный"])
        self._add("MAJOR_SIXTH_DOWN,MAJOR_SECOND_DOWN", "свойство:физические", "лёгкий", "light",
                  ["невесомый", "weightless", "воздушный"])
        self._add("MAJOR_SIXTH_UP,MAJOR_SEVENTH_UP", "свойство:физические", "острый", "sharp",
                  ["колющий", "режущий", "остроконечный"])
        self._add("MAJOR_SIXTH_DOWN,MAJOR_SEVENTH_DOWN", "свойство:физические", "тупой", "dull",
                  ["blunt", "закруглённый", "плоский"])
        self._add("MAJOR_SIXTH_UP,TRITON_UP", "свойство:физические", "быстрый", "fast",
                  ["quick", "стремительный", "скоростной", "мгновенный"])
        self._add("MAJOR_SIXTH_DOWN,TRITON_DOWN", "свойство:физические", "медленный", "slow",
                  ["неторопливый", "плавный", "постепенный"])
        self._add("MAJOR_SIXTH_UP,MAJOR_THIRD_UP", "свойство:физические", "мокрый", "wet",
                  ["влажный", "сырой", "жидкий", "liquid"])
        self._add("MAJOR_SIXTH_DOWN,MAJOR_THIRD_DOWN", "свойство:физические", "сухой", "dry",
                  ["высушенный", "безводный", "arid"])
        self._add("MAJOR_SIXTH_UP,PERFECT_FOURTH_UP", "свойство:физические", "гладкий", "smooth",
                  ["ровный", "полированный", "скользкий"])
        self._add("MAJOR_SIXTH_DOWN,PERFECT_FOURTH_DOWN", "свойство:физические", "шершавый", "rough",
                  ["грубый", "неровный", "шероховатый"])

        # ===== СВОЙСТВА: ЦВЕТ (MINOR_SIXTH + дополнительные) =====
        self._add("MINOR_SIXTH_UP,PERFECT_FOURTH_UP", "свойство:цвет", "светлый", "bright",
                  ["яркий", "сияющий", "блестящий", "светящийся"])
        self._add("MINOR_SIXTH_DOWN,PERFECT_FOURTH_DOWN", "свойство:цвет", "тёмный", "dark",
                  ["мрачный", "тусклый", "чёрный", "black", "тёмный"])
        self._add("MINOR_SIXTH_UP,MINOR_SEVENTH_UP", "свойство:цвет", "белый", "white",
                  ["белоснежный", "чистый", "светлейший"])
        self._add("MINOR_SIXTH_DOWN,MINOR_SEVENTH_DOWN", "свойство:цвет", "красный", "red",
                  ["алый", "багровый", "рубиновый"])
        self._add("MINOR_SIXTH_UP,MAJOR_SIXTH_UP", "свойство:цвет", "синий", "blue", ["голубой", "лазурный", "синева"])
        self._add("MINOR_SIXTH_DOWN,MAJOR_SIXTH_DOWN", "свойство:цвет", "зелёный", "green",
                  ["изумрудный", "травяной", "зелень"])
        self._add("MINOR_SIXTH_UP,TRITON_UP", "свойство:цвет", "жёлтый", "yellow",
                  ["золотой", "golden", "солнечный", "янтарный"])
        self._add("MINOR_SIXTH_DOWN,TRITON_DOWN", "свойство:цвет", "фиолетовый", "purple",
                  ["лиловый", "violet", "пурпурный"])
        self._add("MINOR_SIXTH_UP,PERFECT_FIFTH_DOWN", "свойство:цвет", "оранжевый", "orange",
                  ["апельсиновый", "рыжий", "огненный"])
        self._add("MINOR_SIXTH_DOWN,PERFECT_FIFTH_UP", "свойство:цвет", "серый", "gray",
                  ["grey", "пепельный", "серебристый", "silver"])

        # ===== ДЕЙСТВИЯ (MAJOR_SECOND) =====
        self._add("MAJOR_SECOND_UP,MAJOR_SECOND_UP", "действие", "идти", "go",
                  ["walk", "move", "двигаться", "ехать", "шагать"])
        self._add("MAJOR_SECOND_DOWN,UNISON_STATIC", "действие", "стоять", "stand",
                  ["stop", "wait", "ждать", "остановиться", "замереть"])
        self._add("MAJOR_SECOND_UP,MINOR_THIRD_UP", "действие", "бежать", "run",
                  ["rush", "спешить", "мчаться", "нестись"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_THIRD_DOWN", "действие", "падать", "fall",
                  ["drop", "спускаться", "опускаться", "падать вниз"])
        self._add("MAJOR_SECOND_UP,PERFECT_FOURTH_UP", "действие", "подниматься", "rise",
                  ["ascend", "взлетать", "вверх", "восходить"])
        self._add("MAJOR_SECOND_DOWN,PERFECT_FOURTH_DOWN", "действие", "спускаться", "descend",
                  ["go down", "снижаться", "опускаться"])
        self._add("MAJOR_SECOND_UP,MAJOR_SECOND_DOWN", "действие", "давать", "give",
                  ["дать", "передать", "отдать", "дарить"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_SECOND_UP", "действие", "брать", "take",
                  ["взять", "получить", "забрать", "хватать"])
        self._add("MAJOR_SECOND_UP,PERFECT_FIFTH_UP", "действие", "делать", "do",
                  ["make", "create", "создавать", "работать", "строить"])
        self._add("MAJOR_SECOND_DOWN,PERFECT_FIFTH_DOWN", "действие", "ломать", "break",
                  ["destroy", "разрушать", "портить", "крушить"])
        self._add("MAJOR_SECOND_UP,MINOR_SEVENTH_UP", "действие", "говорить", "say",
                  ["speak", "talk", "рассказывать", "сообщать"])
        self._add("MAJOR_SECOND_DOWN,MINOR_SEVENTH_DOWN", "действие", "молчать", "be silent",
                  ["замолкать", "тишина", "безмолвие"])
        self._add("MAJOR_SECOND_UP,MAJOR_SIXTH_UP", "действие", "смотреть", "see",
                  ["look", "watch", "видеть", "наблюдать", "глядеть"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_SIXTH_DOWN", "действие", "слышать", "hear",
                  ["listen", "слушать", "звучать", "внимать"])
        self._add("MAJOR_SECOND_UP,TRITON_UP", "действие", "думать", "think",
                  ["мыслить", "размышлять", "понимать", "осознавать"])
        self._add("MAJOR_SECOND_DOWN,TRITON_DOWN", "действие", "чувствовать", "feel",
                  ["ощущать", "переживать", "эмоция", "чуять"])
        self._add("MAJOR_SECOND_UP,MAJOR_SEVENTH_UP", "действие", "жить", "live",
                  ["существовать", "обитать", "проживать", "дышать"])
        self._add("MAJOR_SECOND_DOWN,MAJOR_SEVENTH_DOWN", "действие", "умирать", "die",
                  ["погибать", "конец", "смерть", "исчезать"])
        self._add("MAJOR_SECOND_UP,UNISON_STATIC", "действие", "начинать", "begin",
                  ["start", "начало", "старт", "запускать"])
        self._add("MAJOR_SECOND_DOWN,MINOR_THIRD_UP", "действие", "заканчивать", "finish",
                  ["end", "завершать", "конец", "стоп"])
        self._add("MAJOR_SECOND_UP,MINOR_SECOND_UP", "действие", "менять", "change",
                  ["изменять", "меняться", "превращать", "трансформировать"])
        self._add("MAJOR_SECOND_DOWN,MINOR_SECOND_DOWN", "действие", "сохранять", "keep",
                  ["хранить", "беречь", "оставлять", "поддерживать"])

        # ===== МАТЕРИАЛЫ (PERFECT_FIFTH + MAJOR_SIXTH) =====
        self._add("PERFECT_FIFTH_UP,MAJOR_SIXTH_UP", "материал", "дерево", "wood", ["древесина", "деревянный", "лес"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_SIXTH_DOWN", "материал", "камень", "stone",
                  ["rock", "скала", "каменный", "минерал"])
        self._add("PERFECT_FIFTH_UP,MAJOR_SIXTH_DOWN", "материал", "металл", "metal",
                  ["iron", "steel", "железо", "сталь", "золото", "gold"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_SIXTH_UP", "материал", "вода", "water",
                  ["жидкость", "fluid", "влажность", "питьё"])
        self._add("PERFECT_FIFTH_UP,TRITON_UP", "материал", "огонь", "fire", ["пламя", "горение", "искра", "жар"])
        self._add("PERFECT_FIFTH_DOWN,TRITON_DOWN", "материал", "воздух", "air", ["атмосфера", "ветер", "газ", "небо"])
        self._add("PERFECT_FIFTH_UP,MINOR_THIRD_UP", "материал", "земля", "earth", ["почва", "грунт", "грязь", "soil"])
        self._add("PERFECT_FIFTH_DOWN,MINOR_THIRD_DOWN", "материал", "стекло", "glass",
                  ["прозрачный", "хрупкий", "окно"])
        self._add("PERFECT_FIFTH_UP,PERFECT_FOURTH_UP", "материал", "ткань", "fabric",
                  ["cloth", "текстиль", "одежда", "мягкий материал"])
        self._add("PERFECT_FIFTH_DOWN,PERFECT_FOURTH_DOWN", "материал", "бумага", "paper",
                  ["лист", "документ", "книга", "тонкий"])

        # ===== ФОРМЫ (MAJOR_SEVENTH + MINOR_THIRD) =====
        self._add("MAJOR_SEVENTH_UP,MINOR_THIRD_UP", "форма", "круглый", "round",
                  ["круг", "шар", "сфера", "окружность"])
        self._add("MAJOR_SEVENTH_DOWN,MINOR_THIRD_DOWN", "форма", "квадратный", "square",
                  ["прямоугольный", "угол", "рамка", "куб"])
        self._add("MAJOR_SEVENTH_UP,PERFECT_FIFTH_UP", "форма", "треугольный", "triangular",
                  ["треугольник", "пирамида", "угол"])
        self._add("MAJOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN", "форма", "прямой", "straight",
                  ["линия", "ровный", "прямая", "луч"])
        self._add("MAJOR_SEVENTH_UP,MAJOR_SECOND_UP", "форма", "изогнутый", "curved",
                  ["кривой", "дуга", "волна", "извилистый"])
        self._add("MAJOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN", "форма", "спиральный", "spiral",
                  ["винт", "закрученный", "пружина", "скрученный"])

        # ===== ОТНОШЕНИЯ (PERFECT_FOURTH) =====
        self._add("PERFECT_FOURTH_UP,MAJOR_SECOND_UP", "отношение", "и", "and", ["также", "тоже", "плюс", "вместе"])
        self._add("PERFECT_FOURTH_DOWN,MAJOR_SECOND_DOWN", "отношение", "или", "or", ["либо", "выбор", "альтернатива"])
        self._add("PERFECT_FOURTH_UP,MINOR_SECOND_UP", "отношение", "для", "for", ["ради", "чтобы", "цель"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_SECOND_DOWN", "отношение", "от", "from", ["из", "прочь", "источник"])
        self._add("PERFECT_FOURTH_UP,MINOR_THIRD_UP", "отношение", "с", "with",
                  ["вместе с", "используя", "посредством"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_THIRD_DOWN", "отношение", "без", "without", ["лишённый", "отсутствие"])
        self._add("PERFECT_FOURTH_UP,PERFECT_FIFTH_UP", "отношение", "внутри", "inside",
                  ["in", "в", "внутрь", "внутренний"])
        self._add("PERFECT_FOURTH_DOWN,PERFECT_FIFTH_DOWN", "отношение", "снаружи", "outside",
                  ["вне", "наружу", "out", "внешний"])
        self._add("PERFECT_FOURTH_UP,MINOR_SEVENTH_UP", "отношение", "над", "above",
                  ["сверху", "over", "выше", "поверх"])
        self._add("PERFECT_FOURTH_DOWN,MINOR_SEVENTH_DOWN", "отношение", "под", "below",
                  ["under", "снизу", "ниже", "под"])
        self._add("PERFECT_FOURTH_UP,MAJOR_SEVENTH_UP", "отношение", "рядом", "near",
                  ["близко", "около", "возле", "соседний"])
        self._add("PERFECT_FOURTH_DOWN,MAJOR_SEVENTH_DOWN", "отношение", "далеко", "far",
                  ["вдали", "удалённый", "дистанция", "отдалённый"])

        # ===== ОЦЕНКА (MINOR_THIRD) =====
        self._add("MINOR_THIRD_UP,MAJOR_SECOND_UP", "оценка", "хороший", "good",
                  ["добрый", "nice", "прекрасный", "отличный", "положительный"])
        self._add("MINOR_THIRD_DOWN,MAJOR_SECOND_DOWN", "оценка", "плохой", "bad",
                  ["злой", "evil", "ужасный", "terrible", "отрицательный"])
        self._add("MINOR_THIRD_UP,MAJOR_THIRD_UP", "оценка", "красивый", "beautiful",
                  ["pretty", "прекрасный", "эстетичный", "милый"])
        self._add("MINOR_THIRD_DOWN,MAJOR_THIRD_DOWN", "оценка", "уродливый", "ugly",
                  ["страшный", "некрасивый", "отвратительный"])
        self._add("MINOR_THIRD_UP,PERFECT_FIFTH_UP", "оценка", "правильный", "correct",
                  ["right", "true", "верный", "истинный", "точный"])
        self._add("MINOR_THIRD_DOWN,PERFECT_FIFTH_DOWN", "оценка", "неправильный", "wrong",
                  ["false", "ложный", "ошибочный", "неверный"])
        self._add("MINOR_THIRD_UP,TRITON_UP", "оценка", "важный", "important",
                  ["значимый", "главный", "существенный", "ключевой"])
        self._add("MINOR_THIRD_DOWN,TRITON_DOWN", "оценка", "неважный", "unimportant",
                  ["мелкий", "пустяковый", "trivial", "второстепенный"])
        self._add("MINOR_THIRD_UP,PERFECT_FOURTH_UP", "оценка", "полезный", "useful",
                  ["нужный", "практичный", "функциональный"])
        self._add("MINOR_THIRD_DOWN,PERFECT_FOURTH_DOWN", "оценка", "бесполезный", "useless",
                  ["ненужный", "напрасный", "бессмысленный"])
        self._add("MINOR_THIRD_UP,MAJOR_SIXTH_UP", "оценка", "новый", "new",
                  ["свежий", "молодой", "современный", "young"])
        self._add("MINOR_THIRD_DOWN,MAJOR_SIXTH_DOWN", "оценка", "старый", "old",
                  ["древний", "изношенный", "ветхий", "старинный"])

        # ===== КОЛИЧЕСТВО (PERFECT_FIFTH) =====
        self._add("PERFECT_FIFTH_UP,MAJOR_SECOND_UP", "количество", "один", "one",
                  ["1", "единица", "single", "единственный", "first"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_SECOND_UP", "количество", "два", "two", ["2", "пара", "double", "второй"])
        self._add("PERFECT_FIFTH_UP,MAJOR_SECOND_DOWN", "количество", "много", "many",
                  ["множество", "куча", "lots", "numerous", "масса"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_SECOND_DOWN", "количество", "мало", "few",
                  ["немного", "little", "скудный", "редкий"])
        self._add("PERFECT_FIFTH_UP,MAJOR_THIRD_UP", "количество", "весь", "all",
                  ["every", "каждый", "целый", "полный", "целиком"])
        self._add("PERFECT_FIFTH_DOWN,MAJOR_THIRD_DOWN", "количество", "часть", "part",
                  ["доля", "piece", "кусок", "фрагмент", "сегмент"])
        self._add("PERFECT_FIFTH_UP,PERFECT_FOURTH_UP", "количество", "больше", "more",
                  ["greater", "сильнее", "дополнительно", "плюс"])
        self._add("PERFECT_FIFTH_DOWN,PERFECT_FOURTH_DOWN", "количество", "меньше", "less",
                  ["меньший", "fewer", "слабее", "минус"])
        self._add("PERFECT_FIFTH_UP,TRITON_UP", "количество", "половина", "half",
                  ["1/2", "середина", "средний", "половинный"])
        self._add("PERFECT_FIFTH_DOWN,TRITON_DOWN", "количество", "пустой", "empty",
                  ["ничего", "ноль", "отсутствие", "вакуум"])

        # ===== ПРОСТРАНСТВО (MINOR_SEVENTH) =====
        self._add("MINOR_SEVENTH_UP,MAJOR_SECOND_UP", "пространство", "здесь", "here",
                  ["тут", "this place", "близко", "рядом"])
        self._add("MINOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN", "пространство", "там", "there",
                  ["туда", "that place", "далеко", "вдали"])
        self._add("MINOR_SEVENTH_UP,PERFECT_FIFTH_UP", "пространство", "впереди", "ahead",
                  ["front", "перед", "вперёд", "forward", "спереди"])
        self._add("MINOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN", "пространство", "сзади", "behind",
                  ["back", "позади", "назад", "backward", "сзади"])
        self._add("MINOR_SEVENTH_UP,MAJOR_THIRD_UP", "пространство", "слева", "left",
                  ["левый", "налево", "левая сторона"])
        self._add("MINOR_SEVENTH_DOWN,MAJOR_THIRD_DOWN", "пространство", "справа", "right",
                  ["правый", "направо", "правая сторона"])
        self._add("MINOR_SEVENTH_UP,TRITON_UP", "пространство", "север", "north", ["северный", "полюс", "холод"])
        self._add("MINOR_SEVENTH_DOWN,TRITON_DOWN", "пространство", "юг", "south", ["южный", "тепло", "экватор"])
        self._add("MINOR_SEVENTH_UP,MAJOR_SIXTH_UP", "пространство", "восток", "east", ["восход", "восточный", "утро"])
        self._add("MINOR_SEVENTH_DOWN,MAJOR_SIXTH_DOWN", "пространство", "запад", "west",
                  ["закат", "западный", "вечер"])

        # ===== ВРЕМЯ (MAJOR_SEVENTH) =====
        self._add("MAJOR_SEVENTH_UP,MAJOR_SECOND_UP", "время", "сейчас", "now",
                  ["present", "настоящее", "current", "в данный момент"])
        self._add("MAJOR_SEVENTH_DOWN,MAJOR_SECOND_DOWN", "время", "тогда", "then",
                  ["past", "прошлое", "раньше", "before", "было"])
        self._add("MAJOR_SEVENTH_UP,PERFECT_FIFTH_UP", "время", "потом", "later",
                  ["future", "будущее", "после", "after", "будет"])
        self._add("MAJOR_SEVENTH_DOWN,PERFECT_FIFTH_DOWN", "время", "никогда", "never",
                  ["ни разу", "никогда", "ни за что"])
        self._add("MAJOR_SEVENTH_UP,MINOR_THIRD_UP", "время", "всегда", "always",
                  ["вечно", "forever", "постоянно", "вечность"])
        self._add("MAJOR_SEVENTH_DOWN,MINOR_THIRD_DOWN", "время", "иногда", "sometimes",
                  ["порой", "временами", "occasionally", "редко"])
        self._add("MAJOR_SEVENTH_UP,PERFECT_FOURTH_UP", "время", "день", "day",
                  ["daytime", "светлое время", "сутки", "полдень"])
        self._add("MAJOR_SEVENTH_DOWN,PERFECT_FOURTH_DOWN", "время", "ночь", "night",
                  ["nighttime", "тёмное время", "полночь", "темнота"])
        self._add("MAJOR_SEVENTH_UP,TRITON_UP", "время", "утро", "morning", ["рассвет", "начало дня", "заря", "восход"])
        self._add("MAJOR_SEVENTH_DOWN,TRITON_DOWN", "время", "вечер", "evening",
                  ["закат", "сумерки", "конец дня", "заход"])
        self._add("MAJOR_SEVENTH_UP,MAJOR_THIRD_UP", "время", "быстро", "quickly",
                  ["скоро", "мгновенно", "стремительно", "вмиг"])
        self._add("MAJOR_SEVENTH_DOWN,MAJOR_THIRD_DOWN", "время", "медленно", "slowly",
                  ["постепенно", "неторопливо", "долго", "плавно"])

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