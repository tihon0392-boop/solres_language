# language/phonology.py
class MusicalWord:
    def __init__(self):
        self.intervals = []      # Схема интервалов: тон, полутон...
        self.rhythm = []         # Схема длительностей: быстро, медленно
        self.dynamics = []       # Схема громкости: тихо, громко
        self.articulation = "LEGATO" # Как соединять ноты: плавно или отрывисто (паузы)

# Функция, создающая слово "Солнце" (быстрое, громкое, радостное)
def create_bright_sun():
    word = MusicalWord()
    word.intervals = ["MAJOR_THIRD_UP", "MINOR_THIRD_UP"]
    word.rhythm = ["FAST", "LONG"]    # Первая нота быстрая, вторая тянется
    word.dynamics = ["FORTE", "PIANO"] # Первая громко, вторая затихает
    return word