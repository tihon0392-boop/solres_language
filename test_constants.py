# tests/test_constants.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import NoteName, Interval, Direction


def test_note_names():
    """Проверка имён нот."""
    assert NoteName.DO == 0
    assert NoteName.SI == 6
    assert len(NoteName) == 7
    print("✅ Имена нот: OK")


def test_intervals():
    """Проверка интервалов."""
    assert Interval.UNISON == 0
    assert Interval.OCTAVE == 12
    assert Interval.TRITON == 6
    assert Interval.PERFECT_FIFTH == 7
    print("✅ Интервалы: OK")


def test_directions():
    """Проверка направлений."""
    assert Direction.UP == 1
    assert Direction.DOWN == -1
    assert Direction.STATIC == 0
    print("✅ Направления: OK")


def run_all():
    print("=" * 50)
    print("ТЕСТЫ: core/constants.py")
    print("=" * 50)
    test_note_names()
    test_intervals()
    test_directions()
    print("=" * 50)
    print("Все тесты constants пройдены!")
    print("=" * 50)


if __name__ == "__main__":
    run_all()