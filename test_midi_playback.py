# test_midi_playback.py
import os

print("=" * 50)
print("ДИАГНОСТИКА MIDI")
print("=" * 50)

# 1. Проверим, есть ли файлы
midi_dir = "midi_output"
if os.path.exists(midi_dir):
    files = os.listdir(midi_dir)
    print(f"✅ Папка {midi_dir} найдена")
    print(f"   Файлы: {files}")
else:
    print(f"❌ Папка {midi_dir} не найдена")

# 2. Попробуем открыть через системный проигрыватель
import subprocess
import sys

test_file = "midi_output/sun_piano.mid"
if os.path.exists(test_file):
    print(f"\n✅ Тестовый файл найден: {test_file}")

    # Пробуем открыть через Windows Media Player
    print("\n▶️ Пробую открыть через Windows...")
    try:
        os.startfile(test_file)
        print("   Файл открыт в программе по умолчанию.")
        print("   ДОЛЖНА БЫЛА ЗАПУСТИТЬСЯ МУЗЫКА!")
        print("   Если нет — смотрите дальше.")
    except Exception as e:
        print(f"   Ошибка: {e}")
else:
    print(f"\n❌ Файл не найден: {test_file}")

# 3. Проверка pygame
print("\n" + "=" * 50)
print("ПРОВЕРКА PYGAME")
print("=" * 50)

try:
    import pygame

    print("✅ pygame установлен")
    print(f"   Версия: {pygame.version.ver}")

    pygame.mixer.init()
    print("✅ Микшер инициализирован")

    try:
        pygame.mixer.music.load(test_file)
        print("✅ Файл загружен в микшер")
        pygame.mixer.music.play()
        print("▶️ Воспроизведение запущено...")

        import time

        time.sleep(3)

        if pygame.mixer.music.get_busy():
            print("✅ Музыка играет!")
        else:
            print("❌ Микшер не играет — возможно, нет MIDI-синтезатора")

        pygame.mixer.music.stop()
    except Exception as e:
        print(f"❌ Ошибка pygame: {e}")

    pygame.mixer.quit()

except ImportError:
    print("❌ pygame не установлен")