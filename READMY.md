# 🎵 SolRes — Universal Musical Language
# 🎵 Сольрес — Универсальный музыкальный язык

> "Семь нот — алфавит. Интервалы — слова. Мелодия — мысль."
> "Seven notes — the alphabet. Intervals — words. Melody — thought."

---

## 🇬🇧 English

**SolRes** is a constructed language that encodes meaning through **musical intervals** rather than phonetic symbols.

**Creator**: Tikhon Shabanov | **License**: CC BY-SA 4.0 | **Date**: August 1, 2026

---

### 🌐 Try It Online

Run locally:
```bash
python web_app.py
```
Then open **http://127.0.0.1:5000** — type a word, hear its melody. Switch between Melody and Chord mode.

---

### 🧠 How It Works

1. **85 semantic primitives** (big, hot, bright, go, inside...) — each has a unique interval pattern
2. **Words are descriptions**: "sun" = big + hot + bright + rise + above + good + day
3. **Melodies are paths**: each primitive adds 2 notes, chained without repetition
4. **Grammar**: fixed word order (size → physics → color → action → relation → value → time)

| Word | Primitives | Melody |
|------|-----------|--------|
| ☀️ Sun | big+hot+bright+rise+above+good+day | DO→SOL→LA→SOL→LA→FA→SI→DO→FA→SI→LA→DO→RE→DO→FA |
| 🌙 Moon | big+cold+bright+rise+above+good+night | DO→DO→DO→DO→DO→DO→SI→DO→DO→SI→LA→DO→RE→DO→DO |
| 💧 Water | something+cold+bright+fall+inside+good+always | DO→DO→SOL→DO→SOL→DO→DO→DO→RE→SOL→RE→FA→SOL→DO→LA |

---

### 📂 Project Structure
```
solres_language/
├── core/ # Notes, intervals, sound synthesis
├── language/ # Primitives, descriptors, grammar, lexicon
├── chords/ # Chord-based communication (3-note words)
├── web/ # Flask web interface
├── evolution/ # Community proposals, voting, version control
├── tests/ # Unit tests
├── utils/ # MIDI export
└── midi_output/ # Generated .mid files
```

---

### 🧬 Language Evolution

SolRes is **alive**. Anyone can propose new words, rules, or primitives via GitHub Discussions.

1. **Propose** — create a discussion with tag `proposal`
2. **Discuss** — community reviews and votes
3. **Accept** — creator merges approved proposals

👉 **Join the discussion**: https://github.com/tihon0392-boop/solres_language/discussions

---

### 🔮 Roadmap

- [x] Core engine (notes, intervals, synthesis)
- [x] 85 semantic primitives
- [x] Descriptor grammar (words as descriptions)
- [x] Chord mode (3-note words)
- [x] Web interface (translate + play)
- [x] MIDI export (piano, violin, flute...)
- [x] Evolution system (proposals, voting)
- [ ] GitHub Discussions integration
- [ ] Moderated proposal acceptance
- [ ] Expanded primitives (200+)
- [ ] Scientific paper (arXiv)

---

### 📜 License

Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)

© 2026 Tikhon Shabanov

---

## 🇷🇺 Русский

**Сольрес** — искусственный язык, кодирующий смысл через **музыкальные интервалы**.

**Создатель**: Тихон Шабанов | **Лицензия**: CC BY-SA 4.0 | **Дата**: 1 августа 2026

---

### 🌐 Попробовать онлайн

Запустите локально:
```bash
python web_app.py
```
Откройте **http://127.0.0.1:5000** — введите слово, услышите мелодию. Переключайте режимы Мелодия/Аккорд.

---

### 🧠 Как это работает

1. **85 семантических примитивов** (большой, горячий, светлый, идти, внутри...)
2. **Слова = описания**: "солнце" = большой + горячий + светлый + подниматься + над + хороший + день
3. **Мелодии = пути**: каждый примитив добавляет 2 ноты, цепочка без повторов
4. **Грамматика**: фиксированный порядок (размер → свойства → цвет → действие → отношение → оценка → время)

| Слово | Примитивы | Мелодия |
|-------|----------|---------|
| ☀️ Солнце | большой+горячий+светлый+подниматься+над+хороший+день | DO→SOL→LA→SOL→LA→FA→SI→DO→FA→SI→LA→DO→RE→DO→FA |
| 🌙 Луна | большой+холодный+светлый+подниматься+над+хороший+ночь | DO→DO→DO→DO→DO→DO→SI→DO→DO→SI→LA→DO→RE→DO→DO |
| 💧 Вода | нечто+холодный+светлый+падать+внутри+хороший+всегда | DO→DO→SOL→DO→SOL→DO→DO→DO→RE→SOL→RE→FA→SOL→DO→LA |

---

### 🧬 Эволюция языка

Сольрес **живой**. Любой может предложить новые слова, правила или примитивы через GitHub Discussions.

👉 **Обсуждения**: https://github.com/tihon0392-boop/solres_language/discussions