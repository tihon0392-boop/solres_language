# tests/test_evolution.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.proposal import RuleProposal, ProposalStatus
from evolution.version_control import LanguageEvolution


def test_create_proposal():
    """Проверка создания предложения."""
    prop = RuleProposal(
        author="Тестировщик",
        description="Тестовое предложение",
        category="word"
    )
    prop.set_word_proposal("UNISON_STATIC,UNISON_STATIC", ["тест", "test"])

    assert prop.author == "Тестировщик"
    assert prop.status == ProposalStatus.PROPOSED
    assert prop.votes_up == 0
    assert prop.votes_down == 0
    assert prop.score() == 0
    print("✅ Создание предложения: OK")


def test_voting():
    """Проверка голосования."""
    prop = RuleProposal("Автор", "Предложение", "word")

    prop.vote(up=True)
    prop.vote(up=True)
    prop.vote(up=False)

    assert prop.votes_up == 2
    assert prop.votes_down == 1
    assert prop.score() == 1
    print("✅ Голосование: OK")


def test_serialization():
    """Проверка сохранения/загрузки."""
    prop = RuleProposal("Автор", "Тест сериализации", "grammar")
    prop.set_grammar_proposal("новое_правило", {"тип": "порядок_слов"})

    # Сохраняем
    filepath = prop.save("test_proposals")
    assert os.path.exists(filepath), "Файл не создан"

    # Загружаем
    loaded = RuleProposal.load(filepath)
    assert loaded.author == prop.author
    assert loaded.category == prop.category
    assert loaded.data == prop.data

    # Чистим
    os.remove(filepath)
    print("✅ Сериализация: OK")


def test_evolution_system():
    """Проверка системы эволюции."""
    evo = LanguageEvolution(proposals_dir="test_proposals", backups_dir="test_backups")

    # Создаём предложение
    prop = RuleProposal("Тестер", "Тест эволюции", "word")
    prop.set_word_proposal("TEST_PATTERN", ["test_word"])
    evo.submit_proposal(prop)

    # Голосуем
    evo.vote(0, up=True)

    # Проверяем топ
    top = evo.get_top_proposals()
    assert len(top) > 0
    assert top[0].score() > 0

    # Отклоняем
    evo.reject_proposal(0)
    assert evo.proposals[0].status == ProposalStatus.REJECTED

    # Чистим
    import shutil
    for d in ["test_proposals", "test_backups"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    print("✅ Система эволюции: OK")


def run_all():
    print("=" * 50)
    print("ТЕСТЫ: evolution/")
    print("=" * 50)
    test_create_proposal()
    test_voting()
    test_serialization()
    test_evolution_system()
    print("=" * 50)
    print("Все тесты evolution пройдены!")
    print("=" * 50)


if __name__ == "__main__":
    run_all()