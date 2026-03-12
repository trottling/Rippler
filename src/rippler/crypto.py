"""Utility functions for Rippler encryption/decryption."""

from __future__ import annotations

from datetime import datetime
import hashlib
import re

# ASCII table in direct order from 0x00 to 0x7F.
ALPHABET = "".join(chr(i) for i in range(128))

ERR_INVALID_CIPHER_FORMAT = "Некорректный формат шифра"
ERR_INVALID_CODE = "Неверный код"
ERR_INVALID_CODE_OR_CORRUPTED = "Неверный код или повреждённые данные"
ERR_INVALID_MODULUS = "Модуль должен быть больше 0"
ERR_EMPTY_INPUT = "Пустой ввод"
ERR_INVALID_SYMBOL = "Недопустимый символ"

_CODE_RE = re.compile(r"^\d{4}$")


def generate_code(now: datetime) -> str:
    """Generate code in DDHH format from datetime."""
    return now.strftime("%d%H")


def derive_key_bytes(code: str) -> bytes:
    """Build a 32-byte key from code using SHA-256."""
    return hashlib.sha256(code.encode("utf-8")).digest()


def _first_invalid_char(text: str) -> str | None:
    for ch in text:
        if ch not in ALPHABET:
            return ch
    return None


def encrypt(text: str, code: str, modulus: int) -> str:
    """Encrypt text with code and modulus."""
    if not text:
        raise ValueError(ERR_EMPTY_INPUT)
    if modulus <= 0:
        raise ValueError(ERR_INVALID_MODULUS)

    invalid_char = _first_invalid_char(text)
    if invalid_char is not None:
        raise ValueError(f"{ERR_INVALID_SYMBOL}: {invalid_char}")

    key_bytes = derive_key_bytes(code)
    m = modulus

    numbers = []
    for i, ch in enumerate(text):
        idx = ALPHABET.index(ch)
        c = (idx + key_bytes[i % 32]) % m
        numbers.append(str(c))

    digest = hashlib.sha256(f"{text}{code}".encode("utf-8")).hexdigest()
    return f"{m}:{' '.join(numbers)}|{digest}"


def decrypt(cipher: str, code: str) -> str:
    """Decrypt cipher text and validate integrity hash."""
    if not cipher:
        raise ValueError(ERR_EMPTY_INPUT)
    if not _CODE_RE.fullmatch(code):
        raise ValueError(ERR_INVALID_CODE)

    if ":" not in cipher or cipher.count("|") != 1:
        raise ValueError(ERR_INVALID_CIPHER_FORMAT)

    modulus_part, rest = cipher.split(":", 1)
    if not modulus_part:
        raise ValueError(ERR_INVALID_CIPHER_FORMAT)

    try:
        m = int(modulus_part)
    except ValueError as exc:
        raise ValueError(ERR_INVALID_CIPHER_FORMAT) from exc

    if m <= 0:
        raise ValueError(ERR_INVALID_MODULUS)

    numbers_part, incoming_hash = rest.split("|", 1)
    if not incoming_hash:
        raise ValueError(ERR_INVALID_CIPHER_FORMAT)

    numbers_part = numbers_part.strip()
    nums: list[int] = []
    if numbers_part:
        try:
            nums = [int(token) for token in numbers_part.split()]
        except ValueError as exc:
            raise ValueError(ERR_INVALID_CIPHER_FORMAT) from exc

    key_bytes = derive_key_bytes(code)
    result_chars = []

    for i, c in enumerate(nums):
        idx = (c - key_bytes[i % 32]) % m
        if idx >= 128:
            raise ValueError(ERR_INVALID_CODE_OR_CORRUPTED)
        result_chars.append(ALPHABET[idx])

    text = "".join(result_chars)
    expected_hash = hashlib.sha256(f"{text}{code}".encode("utf-8")).hexdigest()
    if expected_hash.lower() != incoming_hash.lower():
        raise ValueError(ERR_INVALID_CODE_OR_CORRUPTED)

    return text
