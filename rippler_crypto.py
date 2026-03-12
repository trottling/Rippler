"""Криптологическая логика Rippler по ТЗ."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

ALPHABET = (
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
)


@dataclass
class CryptoError(Exception):
    """Ошибка шифрования/дешифрования."""

    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


def generate_code(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return f"{now.day:02d}{now.hour:02d}"


def validate_code(code: str) -> None:
    if len(code) != 4 or not code.isdigit():
        raise CryptoError("Код должен состоять ровно из 4 цифр (формат DDHH).")


def derive_key_bytes(code: str) -> bytes:
    validate_code(code)
    return hashlib.sha256(code.encode("utf-8")).digest()


def _alphabet_index(ch: str) -> int:
    idx = ALPHABET.find(ch)
    if idx == -1:
        raise CryptoError(f"Недопустимый символ: '{ch}'")
    return idx


def encrypt(text: str, code: str, modulus: int) -> str:
    if not text:
        raise CryptoError("Введите текст для шифрования.")
    if modulus <= 0:
        raise CryptoError("Модуль должен быть положительным целым числом.")

    key_bytes = derive_key_bytes(code)
    nums: list[str] = []
    for i, ch in enumerate(text):
        idx = _alphabet_index(ch)
        kb = key_bytes[i % 32]
        c = (idx + kb) % modulus
        nums.append(str(c))

    numbers_str = " ".join(nums)
    checksum = hashlib.sha256((text + code).encode("utf-8")).hexdigest()
    return f"{modulus}:{numbers_str}|{checksum}"


def decrypt(cipher_text: str, code: str) -> str:
    if not cipher_text.strip():
        raise CryptoError("Введите строку шифра.")
    validate_code(code)

    if ":" not in cipher_text:
        raise CryptoError("Неверный формат шифра: отсутствует разделитель ':'.")
    modulus_part, rest = cipher_text.split(":", 1)
    try:
        modulus = int(modulus_part)
    except ValueError as exc:
        raise CryptoError("Неверный формат шифра: модуль должен быть целым числом.") from exc
    if modulus <= 0:
        raise CryptoError("Неверный формат шифра: модуль должен быть положительным.")

    if "|" not in rest:
        raise CryptoError("Неверный формат шифра: отсутствует разделитель '|'.")
    numbers_part, hash_part = rest.split("|", 1)
    hash_part = hash_part.strip()
    if len(hash_part) != 64 or any(c not in "0123456789abcdefABCDEF" for c in hash_part):
        raise CryptoError("Неверный формат шифра: контрольный хеш должен быть SHA-256 в hex.")

    numbers_part = numbers_part.strip()
    num_tokens = numbers_part.split() if numbers_part else []
    if not num_tokens:
        raise CryptoError("Неверный формат шифра: отсутствуют числовые значения.")

    values: list[int] = []
    for token in num_tokens:
        try:
            value = int(token)
        except ValueError as exc:
            raise CryptoError("Неверный формат шифра: список чисел содержит нечисловое значение.") from exc
        if value < 0:
            raise CryptoError("Неверный формат шифра: числа не могут быть отрицательными.")
        values.append(value)

    key_bytes = derive_key_bytes(code)
    chars: list[str] = []
    for i, c in enumerate(values):
        kb = key_bytes[i % 32]
        idx = (c - kb) % modulus
        if not 0 <= idx < 128:
            raise CryptoError("Неверный код или повреждённые данные")
        chars.append(ALPHABET[idx])

    result = "".join(chars)
    check = hashlib.sha256((result + code).encode("utf-8")).hexdigest()
    if check.lower() != hash_part.lower():
        raise CryptoError("Неверный код или повреждённые данные")

    return result
