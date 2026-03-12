import hashlib
from math import gcd


class Enc:
    __alphabet_map = { }
    __alphabet_list = []

    def __init__(self):
        __alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

        self.__alphabet_list = list(__alphabet)
        for i, char in enumerate(__alphabet):
            self.__alphabet_map[char] = i

    def encode(self, data: str, code: int, module: int) -> tuple[str, str]:

        # Проверяем, что входные данные корректны
        ok, bad_char = self.__check_symbols(data)
        if not ok:
            return "", f"Неподдерживаемый символ для шифрования \"{bad_char}\""

        # Генерация ключей a и b
        a, b = self.__gen_keys(code, module)

        # Шифрование символов
        numbers = []
        for char in data:
            x = self.__alphabet_map[char]
            y = (a * x + b) % module
            numbers.append(str(y))

        # Контрольный хеш
        hash_input = data + str(code)
        hash_hex = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        # Итоговая строка
        return f"{module}:{" ".join(numbers)}|{hash_hex}", ""

    def decode(self, data: str, code: int) -> tuple[str, str]:
        try:
            module_str, rest = data.split(":", 1)
            module = int(module_str)
            numbers_str, hash_hex = rest.split("|", 1)
            y_list = [int(n) for n in numbers_str.split()]
        except Exception:
            return "", "Неверный формат данных"

        # Генерация ключей a и b
        a, b = self.__gen_keys(code, module)

        # Находим обратный элемент к a по модулю M
        inv_a = self.__mod_inv(a, module)
        if inv_a is None:
            return "", "Ошибка: a не имеет обратного элемента по модулю M"

        decoded_chars = []
        for y in y_list:
            x = ((y - b) * inv_a) % module
            if not (0 <= x <= 127):
                return "", "Ошибка: расшифрованный индекс вне диапазона"
            decoded_chars.append(self.__alphabet_list[x])

        decoded_text = "".join(decoded_chars)
        hash_check = hashlib.sha256((decoded_text + str(code)).encode("utf-8")).hexdigest()
        if hash_check.lower() != hash_hex.lower():
            return "", "Неверный код или повреждённые данные"

        return decoded_text, ""

    # Валидация символов во входной строке
    def __check_symbols(self, data: str) -> tuple[bool, str]:
        for char in data:
            if char not in self.__alphabet_map:
                return False, char
        return True, ""

    def __gen_keys(self, code: int, module: int) -> tuple[int, int]:
        key_bytes = hashlib.sha256(str(code).encode("utf-8")).digest()

        # Ключ а: взаимно прост с module
        a0 = key_bytes[0]
        a = a0
        if module > 1:
            while gcd(a, module) != 1:
                a += 1
                if a >= 256:
                    a = 1

        b0 = key_bytes[1]
        b = b0 % module
        return a, b

    def __ext_gcd(self, a, b):
        if b == 0:
            return a, 1, 0
        else:
            g, x1, y1 = self.__ext_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return g, x, y

    def __mod_inv(self, a, m):
        # Расширенный алгоритм Евклида
        g, x, _ = self.__ext_gcd(a, m)
        if g != 1:
            return None
        return x % m
