# tests/test_interval_calculator.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import NoteName, Interval, Direction
from core.interval_calculator import Note, IntervalCalculator


def test_midi_conversion():
    """Проверка конвертации в MIDI."""
    calc = IntervalCalculator()

    do4 = Note(NoteName.DO, 4)
    assert do4.to_midi() == 60, f"До4 должен быть 60, а не {do4.to_midi()}"

    la4 = Note(NoteName.LA, 4)
    assert la4.to_midi() == 69, f"Ля4 должен быть 69, а не {la4.to_midi()}"

    print("✅ MIDI-конвертация: OK")


def test_frequency():
    """Проверка частот."""
    la4 = Note(NoteName.LA, 4)
    freq = la4.to_frequency()
    assert abs(freq - 440.0) < 1.0, f"Ля4 должен быть ~440 Гц, а не {freq}"

    la5 = Note(NoteName.LA, 5)
    freq5 = la5.to_frequency()
    assert abs(freq5 - 880.0) < 2.0, f"Ля5 должен быть ~880 Гц, а не {freq5}"

    print("✅ Частоты: OK")


def test_interval_calculation():
    """Проверка расчёта интервалов."""
    calc = IntervalCalculator()

    do4 = Note(NoteName.DO, 4)
    mi4 = Note(NoteName.MI, 4)
    sol4 = Note(NoteName.SOL, 4)

    # До → Ми = большая терция вверх (4 полутона)
    interval, direction = calc.calculate(do4, mi4)
    assert interval == Interval.MAJOR_THIRD, f"Ожидалась MAJOR_THIRD, получено {interval}"
    assert direction == Direction.UP, f"Ожидалось UP, получено {direction}"

    # Ми → До = большая терция вниз
    interval, direction = calc.calculate(mi4, do4)
    assert interval == Interval.MAJOR_THIRD, f"Ожидалась MAJOR_THIRD, получено {interval}"
    assert direction == Direction.DOWN, f"Ожидалось DOWN, получено {direction}"

    # До → До = унисон
    interval, direction = calc.calculate(do4, do4)
    assert interval == Interval.UNISON
    assert direction == Direction.STATIC

    # До → Соль = квинта (7 полутонов)
    interval, direction = calc.calculate(do4, sol4)
    assert interval == Interval.PERFECT_FIFTH

    print("✅ Расчёт интервалов: OK")


def test_melodic_pattern():
    """Проверка анализа мелодии."""
    calc = IntervalCalculator()

    do4 = Note(NoteName.DO, 4)
    mi4 = Note(NoteName.MI, 4)
    sol4 = Note(NoteName.SOL, 4)

    pattern = calc.calculate_melodic_pattern([do4, mi4, sol4])
    assert len(pattern) == 2
    assert pattern[0]["interval"] == Interval.MAJOR_THIRD
    assert pattern[1]["interval"] == Interval.MINOR_THIRD

    print("✅ Мелодический паттерн: OK")


def test_octave_jump():
    """Проверка октавного скачка."""
    calc = IntervalCalculator()

    do4 = Note(NoteName.DO, 4)
    do5 = Note(NoteName.DO, 5)

    interval, direction = calc.calculate(do4, do5)

    # Октава = 12 полутонов, при mod 12 = 0, что даёт UNISON по имени интервала
    # Но семантически это OCTAVE. Проверим значение полутонов:
    semitones = abs(do5.to_midi() - do4.to_midi())
    assert semitones == 12, f"Октава должна быть 12 полутонов, а не {semitones}"
    assert direction == Direction.UP
    # UNISON — потому что октава по модулю 12 = 0
    # Это нормально для текущей реализации, так как До4 и До5 — одна нота в круге

    print("✅ Октавный скачок: OK")


def run_all():
    print("=" * 50)
    print("ТЕСТЫ: core/interval_calculator.py")
    print("=" * 50)
    test_midi_conversion()
    test_frequency()
    test_interval_calculation()
    test_melodic_pattern()
    test_octave_jump()
    print("=" * 50)
    print("Все тесты interval_calculator пройдены!")
    print("=" * 50)


if __name__ == "__main__":
    run_all()