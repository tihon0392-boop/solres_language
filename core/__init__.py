# core/__init__.py
from .interval_calculator import Note, IntervalCalculator
from .constants import NoteName, Interval, Direction, PAUSE, END_OF_SENTENCE
# synthesizer не импортируем на сервере — требует sounddevice