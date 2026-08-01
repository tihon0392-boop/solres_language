# run_evolution.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evolution.proposal import RuleProposal
from evolution.version_control import LanguageEvolution
from language.lexicon import Lexicon


def demo_evolution():
    """Демонстрация работы эволюции языка."""

    print("=" * 60)
    print("🧬 ЭВОЛЮЦИЯ ЯЗЫКА СОЛЬРЕС")
    print("=" * 60)
    print()

    # Инициализация
    evolution = LanguageEvolution()
    lexicon = Lexicon()

    print(f"Начальный размер словаря: {len(lexicon.words_by_pattern)} слов")
    print()

    # --- Предложение 1: Новое слово ---
    print("1️⃣  ПРЕДЛОЖЕНИЕ НОВОГО СЛОВА")
    print("-" * 40)

    prop1 = RuleProposal(
        author="Создатель",
        description="Добавить слово 'кошка/cat' — животное",
        category="word"
    )
    prop1.set_word_proposal(
        pattern_str="MAJOR_THIRD_UP,MINOR_SECOND_UP",
        meanings=["кошка", "cat", "кот", "мурлыкать"]
    )
    evolution.submit_proposal(prop1)

    # --- Предложение 2: Новое слово ---
    print("\n2️⃣  ПРЕДЛОЖЕНИЕ НОВОГО СЛОВА")
    print("-" * 40)

    prop2 = RuleProposal(
        author="Сообщество",
        description="Добавить слово 'собака/dog' — животное",
        category="word"
    )
    prop2.set_word_proposal(
        pattern_str="MAJOR_THIRD_DOWN,MAJOR_SECOND_UP",
        meanings=["собака", "dog", "пёс", "лаять"]
    )
    evolution.submit_proposal(prop2)

    # --- Предложение 3: Новое значение интервала ---
    print("\n3️⃣  ПРЕДЛОЖЕНИЕ НОВОГО ЗНАЧЕНИЯ")
    print("-" * 40)

    prop3 = RuleProposal(
        author="Исследователь",
        description="Добавить значение 'технология' для PERFECT_FIFTH",
        category="interval_meaning"
    )
    prop3.set_interval_proposal(
        interval="PERFECT_FIFTH",
        new_meaning="технология, машина, компьютер"
    )
    evolution.submit_proposal(prop3)

    # --- Голосование ---
    print("\n" + "=" * 60)
    print("🗳️  ГОЛОСОВАНИЕ")
    print("=" * 60)

    evolution.vote(0, up=True)  # За кошку
    evolution.vote(0, up=True)  # За кошку
    evolution.vote(1, up=True)  # За собаку
    evolution.vote(2, up=False)  # Против изменения интервала

    # --- Просмотр предложений ---
    evolution.show_proposals()

    # --- Принятие лучшего предложения ---
    print("\n" + "=" * 60)
    print("⚡ ПРИНЯТИЕ ПРЕДЛОЖЕНИЯ")
    print("=" * 60)

    top = evolution.get_top_proposals(limit=1)
    if top:
        best_index = evolution.proposals.index(top[0])
        print(f"\nЛучшее предложение: {top[0].description}")
        print(f"Счёт: {top[0].score()}")
        print("\nПрименяем к языку...")

        success = evolution.approve_proposal(best_index, lexicon)

        if success:
            print(f"\nНовый размер словаря: {len(lexicon.words_by_pattern)} слов")

            # Проверяем новое слово
            from core.constants import NoteName
            from core.interval_calculator import Note

            tonic = Note(NoteName.DO, 4)
            cat_notes = lexicon.words_to_notes("кошка", tonic)
            print(f"Слово 'кошка': {[str(n) for n in cat_notes]}")

    # --- История ---
    evolution.show_history()

    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЭВОЛЮЦИИ ЗАВЕРШЕНА")
    print("=" * 60)
    print()
    print("📁 Предложения сохранены в папке 'proposals/'")
    print("💾 Резервные копии в папке 'backups/'")
    print()
    print("🔮 Теперь любой человек может:")
    print("   1. Создать предложение (proposal)")
    print("   2. Проголосовать за/против")
    print("   3. Принять лучшее — язык обновится автоматически!")
    print()
    print("   Язык Сольрес ЖИВЁТ и ЭВОЛЮЦИОНИРУЕТ!")


if __name__ == "__main__":
    demo_evolution()