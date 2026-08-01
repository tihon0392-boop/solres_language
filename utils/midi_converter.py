# utils/midi_converter.py
import sys
import os

# Добавляем корень проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from core.interval_calculator import Note


class MIDIConverter:
    """
    Конвертирует фразы Сольрес в MIDI-файлы.
    MIDI-файлы можно открыть в любой музыкальной программе
    и назначить любой инструмент (фортепиано, скрипка, орган...).
    """

    def __init__(self, tempo: int = 120):
        """
        tempo: ударов в минуту (BPM)
        """
        self.tempo = tempo
        self.ticks_per_beat = 480  # Стандартное разрешение MIDI

    def phrase_to_midi(self, phrase: list, filename: str = "output.mid",
                       instrument: int = 0) -> None:
        """
        Конвертирует фразу в MIDI-файл.

        phrase: список из (Note, длительность_мс) или ("PAUSE", длительность_мс)
        filename: имя выходного файла
        instrument: номер инструмента по стандарту General MIDI:
            0  = Acoustic Grand Piano
            40 = Violin
            56 = Trumpet
            73 = Flute
            19 = Church Organ
            (полный список: https://www.midi.org/specifications/item/gm-level-1-sound-set)
        """
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Устанавливаем темп
        tempo_microseconds = int(60_000_000 / self.tempo)
        track.append(MetaMessage('set_tempo', tempo=tempo_microseconds))

        # Устанавливаем инструмент
        track.append(Message('program_change', program=instrument, time=0))

        # Конвертируем фразу в MIDI-сообщения
        for item in phrase:
            if isinstance(item, tuple):
                token, duration_ms = item

                if token == "PAUSE":
                    # Тишина = ничего не играем, просто ждём
                    ticks = self._ms_to_ticks(duration_ms)
                    # Добавляем пустое время к следующей ноте
                    # (в MIDI время указывается от предыдущего события)
                    if track:
                        # Хак: добавляем время к последнему сообщению
                        pass

                elif token == "END":
                    # Конец предложения — длинная пауза
                    ticks = self._ms_to_ticks(duration_ms)
                    # Добавим тихую ноту или просто паузу через время

                elif isinstance(token, Note):
                    midi_note = token.to_midi()
                    velocity = 80  # Громкость (0-127)
                    ticks_duration = self._ms_to_ticks(duration_ms)

                    # Note On
                    track.append(Message('note_on', note=midi_note,
                                         velocity=velocity, time=0))
                    # Note Off через нужное время
                    track.append(Message('note_off', note=midi_note,
                                         velocity=0, time=ticks_duration))

        # Сохраняем файл
        mid.save(filename)
        print(f"✅ MIDI-файл сохранён: {filename}")
        print(f"   Инструмент: {self._instrument_name(instrument)}")
        print(f"   Темп: {self.tempo} BPM")

    def phrase_to_midi_advanced(self, phrase: list, filename: str = "output.mid",
                                instrument: int = 0) -> None:
        """
        Улучшенная версия с правильной обработкой пауз.
        """
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Название трека
        track.append(MetaMessage('track_name', name='SolRes Language'))

        # Темп
        tempo_microseconds = int(60_000_000 / self.tempo)
        track.append(MetaMessage('set_tempo', tempo=tempo_microseconds))

        # Инструмент
        track.append(Message('program_change', program=instrument, time=0))

        # Настройки
        track.append(Message('control_change', control=7, value=100))  # Громкость
        track.append(Message('control_change', control=10, value=64))  # Панорама (центр)

        # Обрабатываем фразу
        current_time = 0
        for item in phrase:
            if isinstance(item, tuple):
                token, duration_ms = item
                ticks = self._ms_to_ticks(duration_ms)

                if token == "PAUSE" or token == "END":
                    # Добавляем паузу (увеличиваем время до следующего события)
                    current_time += ticks

                elif isinstance(token, Note):
                    midi_note = token.to_midi()
                    velocity = 80

                    # Note On (время от предыдущего события)
                    track.append(Message('note_on', note=midi_note,
                                         velocity=velocity, time=current_time))
                    current_time = 0  # Сбросили

                    # Note Off
                    track.append(Message('note_off', note=midi_note,
                                         velocity=0, time=ticks))

        # Конец трека
        track.append(MetaMessage('end_of_track', time=0))

        mid.save(filename)
        print(f"✅ MIDI-файл сохранён: {filename}")
        print(f"   Инструмент: {self._instrument_name(instrument)}")
        print(f"   Темп: {self.tempo} BPM")

    def _ms_to_ticks(self, milliseconds: int) -> int:
        """Переводит миллисекунды в MIDI-тики."""
        beats_per_ms = self.tempo / 60_000
        beats = milliseconds * beats_per_ms
        return int(beats * self.ticks_per_beat)

    def _instrument_name(self, program: int) -> str:
        """Возвращает название инструмента General MIDI."""
        instruments = {
            0: "Acoustic Grand Piano",
            1: "Bright Acoustic Piano",
            4: "Electric Piano",
            19: "Church Organ",
            24: "Acoustic Guitar (nylon)",
            40: "Violin",
            41: "Viola",
            42: "Cello",
            56: "Trumpet",
            57: "Trombone",
            66: "Alto Sax",
            68: "Oboe",
            73: "Flute",
            75: "Pan Flute",
        }
        return instruments.get(program, f"Program {program}")


# Демонстрация
if __name__ == "__main__":
    import os
    from core.constants import NoteName
    from core.interval_calculator import Note
    from language.lexicon import Lexicon
    from language.grammar import Grammar

    # Создаём папку для MIDI-файлов
    output_dir = "midi_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    lex = Lexicon()
    gram = Grammar(lex)
    converter = MIDIConverter(tempo=100)
    tonic = Note(NoteName.DO, 4)

    print("=" * 60)
    print("🎼 MIDI ЭКСПОРТ СОЛЬРЕС")
    print("=" * 60)

    # 1. Слово "Солнце" на фортепиано
    print("\n☀️ Слово 'Солнце' — Фортепиано")
    sun_notes = lex.words_to_notes("солнце", tonic)
    phrase = [(n, 500) for n in sun_notes]
    converter.phrase_to_midi_advanced(phrase, f"{output_dir}/sun_piano.mid", instrument=0)

    # 2. Слово "Солнце" на скрипке
    print("\n☀️ Слово 'Солнце' — Скрипка")
    converter.phrase_to_midi_advanced(phrase, f"{output_dir}/sun_violin.mid", instrument=40)

    # 3. Слово "Солнце" на флейте
    print("\n☀️ Слово 'Солнце' — Флейта")
    converter.phrase_to_midi_advanced(phrase, f"{output_dir}/sun_flute.mid", instrument=73)

    # 4. Диалог на фортепиано
    print("\n💬 Диалог 'Ты идёшь? Я иду.'")
    question = gram.build_question("ты", "идти", tonic)
    answer = gram.build_statement("я", "идти", tonic)
    full_dialogue = question + answer
    converter.phrase_to_midi_advanced(full_dialogue, f"{output_dir}/dialogue_piano.mid", instrument=0)

    # 5. Эмоции на скрипке
    print("\n🎭 Эмоции — Скрипка")
    emotions_phrase = (
            gram.build_statement("я", "радость", tonic) +
            gram.build_statement("я", "грусть", tonic) +
            gram.build_statement("я", "любовь", tonic)
    )
    converter.phrase_to_midi_advanced(emotions_phrase, f"{output_dir}/emotions_violin.mid", instrument=40)

    print("\n" + "=" * 60)
    print(f"✅ Все MIDI-файлы сохранены в папку '{output_dir}/'")
    print("   Откройте их в любой музыкальной программе!")
    print("=" * 60)