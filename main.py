# main.py
from core import Note, NoteName, Synthesizer
from language.lexicon import Lexicon
from language.grammar import Grammar


def demo_basic():
    """Демонстрация базовых возможностей."""
    lex = Lexicon()
    gram = Grammar(lex)
    synth = Synthesizer(volume=0.25)
    tonic = Note(NoteName.DO, 4)

    print("=" * 60)
    print("🎵 СОЛЬРЕС — УНИВЕРСАЛЬНЫЙ МУЗЫКАЛЬНЫЙ ЯЗЫК")
    print("=" * 60)
    print(f"Слов в словаре: {len(lex.words_by_pattern)}")
    print()

    # Диалог
    print("❓ Вопрос: 'Ты меня слышишь?'")
    q = gram.build_question("ты", "слышать", tonic)
    gram.phrase_to_sound(q, synth)

    print("✅ Ответ: 'Я слышу.'")
    a = gram.build_statement("я", "слышать", tonic)
    gram.phrase_to_sound(a, synth)

    print("❓ Вопрос: 'Ты идёшь?'")
    q2 = gram.build_question("ты", "идти", tonic)
    gram.phrase_to_sound(q2, synth)

    print("✅ Ответ: 'Я иду.'")
    a2 = gram.build_statement("я", "идти", tonic)
    gram.phrase_to_sound(a2, synth)


def demo_emotions():
    """Демонстрация эмоций."""
    lex = Lexicon()
    gram = Grammar(lex)
    synth = Synthesizer(volume=0.2)
    tonic = Note(NoteName.DO, 4)

    print("\n" + "=" * 60)
    print("🎭 ЭМОЦИИ НА СОЛЬРЕСЕ")
    print("=" * 60)

    emotions = [
        ("радость", "Я чувствую радость"),
        ("грусть", "Я чувствую грусть"),
        ("любовь", "Я чувствую любовь"),
        ("страх", "Я чувствую страх"),
        ("спокойствие", "Я чувствую спокойствие"),
    ]

    for emotion, text in emotions:
        print(f"\n🎵 {text}")
        phrase = gram.build_statement("я", emotion, tonic)
        gram.phrase_to_sound(phrase, synth)


def demo_translation():
    """Демонстрация перевода с русского на Сольрес."""
    lex = Lexicon()
    synth = Synthesizer(volume=0.2)
    tonic = Note(NoteName.DO, 4)

    print("\n" + "=" * 60)
    print("🌍 ПЕРЕВОД С РУССКОГО НА СОЛЬРЕС")
    print("=" * 60)

    words_to_translate = ["солнце", "вода", "птица", "любовь", "дом", "идти"]

    for word in words_to_translate:
        notes = lex.words_to_notes(word, tonic)
        note_names = [str(n) for n in notes]
        print(f"  {word} → {note_names}")
        # Играем слово
        synth.play_sequence([(n, 300) for n in notes], "piano")


if __name__ == "__main__":
    demo_basic()
    demo_emotions()
    demo_translation()

    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)