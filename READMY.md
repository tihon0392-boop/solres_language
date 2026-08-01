# 🎵 SolRes — Universal Musical Language
# 🎵 Сольрес — Универсальный музыкальный язык

---

## 🇬🇧 English

**SolRes** is a language everyone can understand. It's based not on letters or words, but on **musical intervals** — the distances between notes.

> "Seven notes — the alphabet. Intervals — words. Melody — thought."

---

### 🧠 Philosophy

There are thousands of languages in the world. But there is one system that every initiate understands — **music**. Seven notes (Do, Re, Mi, Fa, Sol, La, Si) stretch infinitely up and down. Their combinations create meaning that is **felt**, not translated.

A major third sounds "bright" to a Russian, a Chinese, and an African. A tritone sounds "tense" to everyone. This is not a cultural convention — it's the **physics of sound**.

---

### 🔤 How It Works

**Alphabet: 7 notes**

Do  Re  Mi  Fa  Sol  La  Si
0   1   2   3   4    5   6

**Words: combinations of intervals**
- **Do → Mi → Sol** = +4, +3 semitones = ☀️ **Sun**
- **Do → Mi → Do** = +4, -4 semitones = 🌙 **Moon**
- **Fa → Si** = tritone (6 semitones) = ❓ **Question**

**Grammar: direction and pauses**
- ⬆️ **Up** — light, goodness, activity
- ⬇️ **Down** — darkness, rest, passivity
- ⏸️ **Pause** — word boundary
- ⏹️ **Long pause** — end of sentence

---

### 🚀 Quick Start

**Installation**

git clone https://github.com/TikhonShabanov/solres_language.git
cd solres_language
pip install -r requirements.txt

**Your first word**

from core import Note, NoteName, Synthesizer

synth = Synthesizer(volume=0.3)
do = Note(NoteName.DO, 4)
mi = Note(NoteName.MI, 4)
sol = Note(NoteName.SOL, 4)

# Play "Sun"
synth.play_sequence([(do, 500), (mi, 400), (sol, 700)])

**Translate from any language to SolRes**

from language.lexicon import Lexicon
from core import Note, NoteName

lex = Lexicon()
tonic = Note(NoteName.DO, 4)

# English, Russian, Chinese — same melody!
notes = lex.words_to_notes("love", tonic)   # English
notes = lex.words_to_notes("любовь", tonic) # Russian — same notes!

**Export to MIDI (studio quality!)**

python utils/midi_converter.py
# Files saved to midi_output/ — piano, violin, flute...

---

### 📂 Project Structure

solres_language/
├── core/                       # Core: notes, intervals, sound
│   ├── constants.py            # 7 notes, 13 intervals, directions
│   ├── interval_calculator.py  # Frequency math
│   └── synthesizer.py          # Sound generation & playback
│
├── language/                   # Linguistics
│   ├── lexicon.py              # Dictionary (68+ words, multilingual)
│   └── grammar.py              # Phrase & sentence building
│
├── evolution/                  # Language self-improvement
│   ├── proposal.py             # Proposal structure
│   └── version_control.py      # Voting & updates
│
├── utils/                      # Tools
│   └── midi_converter.py       # MIDI export (piano, violin, flute...)
│
├── tests/                      # Tests (100% passing ✅)
├── proposals/                  # Community proposals
├── backups/                    # Version backups
└── midi_output/                # Generated MIDI files

---

### 🧬 Language Evolution

SolRes is **alive**. Anyone can propose a new word or rule:

from evolution.proposal import RuleProposal
from evolution.version_control import LanguageEvolution

evo = LanguageEvolution()

# Propose a new word
prop = RuleProposal(
    author="Your name",
    description="Add word 'cat/кошка'",
    category="word"
)
prop.set_word_proposal("MAJOR_THIRD_UP,MINOR_SECOND_UP", ["cat", "кошка"])
evo.submit_proposal(prop)

# Vote
evo.vote(0, up=True)

# Accept the best proposal — language updates automatically
evo.approve_proposal(0, lexicon)

All proposals are stored in proposals/. Accepted ones are applied, old versions saved in backups/.

---

### 🌍 Sample Dictionary

| Word | Pattern | Notes from C |
|------|---------|--------------|
| ☀️ Sun | MAJOR_THIRD_UP, MINOR_THIRD_UP | C-E-G |
| 🌙 Moon | MAJOR_THIRD_UP, MAJOR_THIRD_DOWN | C-E-C |
| 💧 Water | MINOR_THIRD_DOWN, MAJOR_SECOND_DOWN | C-A-G |
| ❤️ Love | MINOR_THIRD_UP, PERFECT_FIFTH_UP | C-Eb-C |
| 🏠 Home | PERFECT_FOURTH_UP, MAJOR_SECOND_DOWN | C-F-Eb |
| 🐦 Bird | MAJOR_THIRD_UP, MAJOR_SECOND_UP | C-E-F# |

*Full dictionary: language/lexicon.py*

---

### 🎼 Why It Works

Intervals are **vibration mathematics**:

| Interval | Semitones | Frequency ratio | Perception |
|----------|-----------|-----------------|-------------|
| Unison | 0 | 1:1 | "I", unity |
| Major third | 4 | 5:4 | Light, joy, nature |
| Perfect fifth | 7 | 3:2 | Tool, created thing |
| Tritone | 6 | √2:1 | Question, tension |

These ratios are **universal** — valid for all cultures and even non-human intelligence.

---

### 📜 License & Authorship

**Creator**: Tikhon Shabanov

**License**: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)

This means:
- ✅ Free to use
- ✅ Free to modify and extend
- ⚠️ Must credit the author
- ⚠️ Derivative works must use the same license

**Publication date**: August 1, 2026

---

### 🔮 Roadmap

- [x] Core (notes, intervals, sound)
- [x] Dictionary (68 words)
- [x] Grammar (questions, statements)
- [x] MIDI export (piano, violin, flute)
- [x] Evolution (proposals, voting)
- [x] Tests (100% passing)
- [ ] Web interface (play & translate online)
- [ ] Mobile app
- [ ] SolRes → color/gesture converter (for the deaf)
- [ ] Scientific paper (arXiv)

---

### 🤝 How to Contribute

1. **Propose a word**: create .json in proposals/ or use RuleProposal
2. **Improve code**: Pull Request on GitHub
3. **Spread the word**: share with musicians and linguists

---

*"Music is a language that needs no translation. SolRes gives it grammar."*

---

## 🇷🇺 Русский

**Сольрес** — это язык, который понимает каждый. Он основан не на буквах или словах, а на **музыкальных интервалах** — расстояниях между нотами.

> "Семь нот — алфавит. Интервалы — слова. Мелодия — мысль."

---

### 🧠 Философия

В мире тысячи языков. Но есть одна система, понятная всем посвящённым — **музыка**. Семь нот (До, Ре, Ми, Фа, Соль, Ля, Си) бесконечно тянутся вверх и вниз. Их комбинации создают смысл, который **чувствуется**, а не переводится.

Мажорная терция звучит "светло" для русского, китайца и африканца. Тритон — "тревожно" для всех. Это не культурная договорённость, а **физика звука**.

---

### 🔤 Как это работает

**Алфавит: 7 нот**

До  Ре  Ми  Фа  Соль  Ля  Си
0   1   2   3   4     5   6

**Слова: комбинации интервалов**
- **До → Ми → Соль** = +4, +3 полутона = ☀️ **Солнце**
- **До → Ми → До** = +4, -4 полутона = 🌙 **Луна**
- **Фа → Си** = тритон (6 полутонов) = ❓ **Вопрос**

**Грамматика: направление и паузы**
- ⬆️ **Вверх** — свет, добро, активность
- ⬇️ **Вниз** — тьма, покой, пассивность
- ⏸️ **Пауза** — граница слова
- ⏹️ **Длинная пауза** — конец предложения

---

### 🚀 Быстрый старт

**Установка**

git clone https://github.com/TikhonShabanov/solres_language.git
cd solres_language
pip install -r requirements.txt

**Первое слово**

from core import Note, NoteName, Synthesizer

synth = Synthesizer(volume=0.3)
do = Note(NoteName.DO, 4)
mi = Note(NoteName.MI, 4)
sol = Note(NoteName.SOL, 4)

# Сыграть "Солнце"
synth.play_sequence([(do, 500), (mi, 400), (sol, 700)])

**Перевод на Сольрес**

from language.lexicon import Lexicon
from core import Note, NoteName

lex = Lexicon()
tonic = Note(NoteName.DO, 4)

# Русский, английский, китайский — одна и та же мелодия!
notes = lex.words_to_notes("любовь", tonic)   # Русский
notes = lex.words_to_notes("love", tonic)     # Английский — те же ноты!

**Экспорт в MIDI (студийное качество!)**

python utils/midi_converter.py
# Файлы сохранятся в midi_output/ — фортепиано, скрипка, флейта...

---

### 📂 Структура проекта

solres_language/
├── core/                       # Ядро: ноты, интервалы, звук
│   ├── constants.py            # 7 нот, 13 интервалов, направления
│   ├── interval_calculator.py  # Математика частот
│   └── synthesizer.py          # Генерация и проигрывание звука
│
├── language/                   # Лингвистика
│   ├── lexicon.py              # Словарь (68+ слов, мультиязычный)
│   └── grammar.py              # Построение фраз и предложений
│
├── evolution/                  # Саморазвитие языка
│   ├── proposal.py             # Структура предложения
│   └── version_control.py      # Голосование и обновление
│
├── utils/                      # Инструменты
│   └── midi_converter.py       # Экспорт в MIDI (фортепиано, скрипка...)
│
├── tests/                      # Тесты (все пройдены ✅)
├── proposals/                  # Предложения сообщества
├── backups/                    # Резервные копии версий
└── midi_output/                # Сгенерированные MIDI-файлы

---

### 🧬 Эволюция языка

Сольрес **живой**. Любой человек может предложить новое слово или правило:

from evolution.proposal import RuleProposal
from evolution.version_control import LanguageEvolution

evo = LanguageEvolution()

# Предложить новое слово
prop = RuleProposal(
    author="Ваше имя",
    description="Добавить слово 'кошка/cat'",
    category="word"
)
prop.set_word_proposal("MAJOR_THIRD_UP,MINOR_SECOND_UP", ["кошка", "cat"])
evo.submit_proposal(prop)

# Проголосовать
evo.vote(0, up=True)

# Принять лучшее — язык обновится автоматически
evo.approve_proposal(0, lexicon)

Все предложения хранятся в proposals/. Принятые применяются, старые версии сохраняются в backups/.

---

### 🌍 Пример словаря

| Слово | Паттерн | Ноты от До |
|-------|---------|------------|
| ☀️ Солнце | MAJOR_THIRD_UP, MINOR_THIRD_UP | До-Ми-Соль |
| 🌙 Луна | MAJOR_THIRD_UP, MAJOR_THIRD_DOWN | До-Ми-До |
| 💧 Вода | MINOR_THIRD_DOWN, MAJOR_SECOND_DOWN | До-Ля-Соль |
| ❤️ Любовь | MINOR_THIRD_UP, PERFECT_FIFTH_UP | До-Ми♭-До |
| 🏠 Дом | PERFECT_FOURTH_UP, MAJOR_SECOND_DOWN | До-Фа-Ми♭ |
| 🐦 Птица | MAJOR_THIRD_UP, MAJOR_SECOND_UP | До-Ми-Фа# |

*Полный словарь: language/lexicon.py*

---

### 🎼 Почему это работает

Интервалы — это **математика вибраций**:

| Интервал | Полутонов | Отношение частот | Восприятие |
|----------|-----------|------------------|------------|
| Унисон | 0 | 1:1 | "Я", единство |
| Мажорная терция | 4 | 5:4 | Свет, радость, природа |
| Квинта | 7 | 3:2 | Инструмент, созданное |
| Тритон | 6 | √2:1 | Вопрос, напряжение |

Эти соотношения **универсальны** для всех культур и даже для нечеловеческого разума.

---

### 📜 Лицензия и авторство

**Создатель**: Тихон Шабанов

**Лицензия**: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)

Это означает:
- ✅ Можно использовать свободно
- ✅ Можно изменять и дополнять
- ⚠️ Нужно указывать автора
- ⚠️ Производные проекты — под той же лицензией

**Дата публикации**: 1 августа 2026

---

### 🔮 Дорожная карта

- [x] Ядро (ноты, интервалы, звук)
- [x] Словарь (68 слов)
- [x] Грамматика (вопросы, утверждения)
- [x] MIDI-экспорт (фортепиано, скрипка, флейта)
- [x] Эволюция (предложения, голосование)
- [x] Тесты (100% пройдены)
- [ ] Веб-интерфейс (играть и переводить онлайн)
- [ ] Мобильное приложение
- [ ] Конвертер Сольрес → цвет/жест (для глухих)
- [ ] Научная статья (arXiv)

---

### 🤝 Как помочь

1. **Предложить слово**: создайте .json в proposals/ или используйте RuleProposal
2. **Улучшить код**: Pull Request на GitHub
3. **Рассказать миру**: поделитесь проектом с музыкантами и лингвистами

---

*"Музыка — это язык, который не нужно переводить. Сольрес делает его грамматикой."*