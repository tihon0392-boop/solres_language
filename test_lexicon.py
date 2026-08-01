# tests/test_lexicon.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import NoteName
from core.interval_calculator import Note
from language.lexicon import Lexicon


def test_sun_meaning():
    """Проверка слова 'солнце'."""
    lex = Lexicon()

    do = Note(NoteName.DO, 4)
    mi = Note(NoteName.MI, 4)
    sol = Note(NoteName.SOL, 4)

    result = lex.notes_to_words([do, mi, sol])
    assert "солнце" in result, f"До-Ми-Соль должно быть 'солнце', получено {result}"
    print("✅ Солнце (ноты → смысл): OK")


def test_sun_to_notes():
    """Проверка перевода 'солнце' в ноты."""
    lex = Lexicon()
    tonic = Note(NoteName.DO, 4)

    notes = lex.words_to_notes("солнце", tonic)
    assert len(notes) == 3, f"Солнце должно быть 3 ноты, получено {len(notes)}"

    # Паттерн должен быть До-Ми-Соль
    midi_numbers = [n.to_midi() for n in notes]
    assert midi_numbers == [60, 64, 67], f"Ожидалось [60, 64, 67], получено {midi_numbers}"
    print("✅ Солнце (смысл → ноты): OK")


def test_multilingual():
    """Проверка мультиязычности."""
    lex = Lexicon()
    tonic = Note(NoteName.DO, 4)

    # Разные языки — одни и те же ноты
    notes_ru = lex.words_to_notes("солнце", tonic)
    notes_en = lex.words_to_notes("sun", tonic)

    midi_ru = [n.to_midi() for n in notes_ru]
    midi_en = [n.to_midi() for n in notes_en]

    assert midi_ru == midi_en, f"Солнце и sun должны давать одни ноты: {midi_ru} vs {midi_en}"
    print("✅ Мультиязычность: OK")


def test_emotions():
    """Проверка слов эмоций."""
    lex = Lexicon()
    tonic = Note(NoteName.DO, 4)

    for word in ["радость", "грусть", "любовь", "страх"]:
        notes = lex.words_to_notes(word, tonic)
        assert len(notes) >= 2, f"Слово '{word}' должно давать ноты"

    print("✅ Эмоции: OK")


def test_vocabulary_size():
    """Проверка размера словаря."""
    lex = Lexicon()
    assert len(lex.words_by_pattern) >= 60, f"Слишком мало слов: {len(lex.words_by_pattern)}"
    print(f"✅ Размер словаря: {len(lex.words_by_pattern)} слов")


def test_unknown_word():
    """Проверка неизвестного слова."""
    lex = Lexicon()
    tonic = Note(NoteName.DO, 4)

    notes = lex.words_to_notes("квантовая_запутанность", tonic)
    assert len(notes) == 1  # Возвращает только тонику
    print("✅ Неизвестное слово: OK (возвращает тонику)")


def run_all():
    print("=" * 50)
    print("ТЕСТЫ: language/lexicon.py")
    print("=" * 50)
    test_sun_meaning()
    test_sun_to_notes()
    test_multilingual()
    test_emotions()
    test_vocabulary_size()
    test_unknown_word()
    print("=" * 50)
    print("Все тесты lexicon пройдены!")
    print("=" * 50)


if __name__ == "__main__":
    run_all()