# test_constance.py
import sys
import os

print("Python видит эти папки:")
for path in sys.path:
    print(f"  {path}")

print(f"\nТекущая папка: {os.getcwd()}")
print(f"Папка скрипта: {os.path.dirname(os.path.abspath(__file__))}")

# Пробуем найти папку core
print("\nСодержимое текущей папки:")
for item in os.listdir('.'):
    print(f"  {item}")

# Проверяем, видит ли Python __init__.py
import os.path
init_path = os.path.join('core', '__init__.py')
print(f"\nФайл {init_path} существует? {os.path.isfile(init_path)}")

# Пробуем импорт
try:
    from core import Note
    print("\n✅ Импорт работает!")
except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")