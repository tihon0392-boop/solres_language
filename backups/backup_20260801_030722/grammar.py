# language/grammar.py
from core.interval_calculator import Note, IntervalCalculator
from core.constants import NoteName, Interval, Direction, PAUSE, END_OF_SENTENCE


class Grammar:
    """
    Грамматика языка Сольрес.
    Строит предложения из слов, добавляя маркеры и паузы.
    """

    def __init__(self, lexicon):
        self.lexicon = lexicon
        self.calc = IntervalCalculator()

    def build_question(self, subject: str, predicate: str, tonic: Note) -> list:
        """
        Строит вопрос: "Ты идёшь?"
        Структура: [МАРКЕР_ВОПРОСА] + [подлежащее] + [сказуемое] + [КОНЕЦ]
        """
        phrase = []

        # 1. Маркер вопроса: тритон вверх (FA → SI)
        fa = self._get_note_from_tonic(tonic, 5)  # Кварта от тоники = FA
        si = self._get_note_from_tonic(tonic, 11)  # Большая септима = SI

        question_marker = [
            (fa, 200),
            (si, 300),
            ("PAUSE", 100),
        ]
        phrase.extend(question_marker)

        # 2. Подлежащее
        subject_notes = self.lexicon.words_to_notes(subject, tonic)
        subject_phrase = self._notes_to_phrase(subject_notes, 250)
        phrase.extend(subject_phrase)
        phrase.append(("PAUSE", 100))

        # 3. Сказуемое
        predicate_notes = self.lexicon.words_to_notes(predicate, tonic)
        predicate_phrase = self._notes_to_phrase(predicate_notes, 300)
        phrase.extend(predicate_phrase)

        # 4. Конец предложения (длинная пауза)
        phrase.append(("END", 500))

        return phrase

    def build_statement(self, subject: str, predicate: str, tonic: Note) -> list:
        """
        Строит утверждение: "Я иду."
        Структура: [подлежащее] + [сказуемое] + [КОНЕЦ]
        """
        phrase = []

        # 1. Подлежащее
        subject_notes = self.lexicon.words_to_notes(subject, tonic)
        subject_phrase = self._notes_to_phrase(subject_notes, 300)
        phrase.extend(subject_phrase)
        phrase.append(("PAUSE", 100))

        # 2. Сказуемое
        predicate_notes = self.lexicon.words_to_notes(predicate, tonic)
        predicate_phrase = self._notes_to_phrase(predicate_notes, 300)
        phrase.extend(predicate_phrase)

        # 3. Конец предложения
        phrase.append(("END", 500))

        return phrase

    def build_answer(self, answer: str, tonic: Note) -> list:
        """
        Строит ответ на вопрос: "Да" или "Нет"
        Структура: [МАРКЕР_ОТВЕТА] + [слово] + [КОНЕЦ]
        """
        phrase = []

        # Маркер ответа: тритон вниз (SI → FA) — разрешение напряжения
        si = self._get_note_from_tonic(tonic, 11)
        fa = self._get_note_from_tonic(tonic, 5)

        answer_marker = [
            (si, 200),
            (fa, 300),
            ("PAUSE", 100),
        ]
        phrase.extend(answer_marker)

        # Само слово ответа
        answer_notes = self.lexicon.words_to_notes(answer, tonic)
        answer_phrase = self._notes_to_phrase(answer_notes, 400)
        phrase.extend(answer_phrase)

        phrase.append(("END", 500))
        return phrase

    def _get_note_from_tonic(self, tonic: Note, semitones_up: int) -> Note:
        """Создаёт ноту на заданное число полутонов выше тоники."""
        midi = tonic.to_midi() + semitones_up
        return self._midi_to_note(midi)

    def _midi_to_note(self, midi: int) -> Note:
        """Преобразует MIDI-номер в Note."""
        from core.interval_calculator import NOTE_TO_SEMITONE

        octave = (midi // 12) - 1
        semitone_in_octave = midi % 12

        note_name = NoteName.DO  # По умолчанию
        for name_idx, semitone in NOTE_TO_SEMITONE.items():
            if semitone == semitone_in_octave:
                note_name = NoteName(name_idx)
                break

        return Note(note_name, octave)

    def _notes_to_phrase(self, notes: list[Note], base_duration: int) -> list:
        """Превращает список Note в список (Note, длительность) для синтезатора."""
        if not notes:
            return []

        result = []
        for i, note in enumerate(notes):
            if i == len(notes) - 1:
                dur = base_duration * 1.5  # Последняя нота длиннее
            else:
                dur = base_duration
            result.append((note, int(dur)))

        return result

    def phrase_to_sound(self, phrase: list, synth) -> None:
        """
        Проигрывает фразу на синтезаторе.
        phrase — список из (Note, длительность) или ("PAUSE", длительность)
        """
        import time

        for item in phrase:
            if isinstance(item, tuple):
                token, duration = item

                if token == "PAUSE":
                    time.sleep(duration / 1000.0)
                elif token == "END":
                    time.sleep(duration / 1000.0)
                elif isinstance(token, Note):
                    synth.play_note(token, duration, "piano")
                else:
                    synth.play_note(token, duration, "piano")


# Тест при запуске
if __name__ == "__main__":
    from core.constants import NoteName
    from core.interval_calculator import Note
    from core.synthesizer import Synthesizer
    from language.lexicon import Lexicon

    lex = Lexicon()
    gram = Grammar(lex)
    synth = Synthesizer(volume=0.25)
    tonic = Note(NoteName.DO, 4)

    print("=" * 50)
    print("ДЕМО ГРАММАТИКИ СОЛЬРЕС")
    print("=" * 50)

    # Вопрос: "Ты идёшь?"
    print("\n❓ Вопрос: 'Ты идёшь?'")
    question = gram.build_question("ты", "идти", tonic)
    print(f"Фраза состоит из {len(question)} элементов")
    gram.phrase_to_sound(question, synth)

    # Утверждение: "Я иду."
    print("✅ Утверждение: 'Я иду.'")
    statement = gram.build_statement("я", "идти", tonic)
    gram.phrase_to_sound(statement, synth)

    # Ответ: "Да"
    print("👍 Ответ: 'Да (радость).'")
    answer = gram.build_answer("радость", tonic)
    gram.phrase_to_sound(answer, synth)

    print("\nГотово!")