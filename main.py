"""Rippler — приложение шифрования/дешифрования по ТЗ."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from rippler_crypto import CryptoError, decrypt, encrypt, generate_code


class ContextMenuMixin:
    def bind_context_menu(self, widget: tk.Widget) -> None:
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))

        def show_menu(event: tk.Event) -> None:
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)


class EncryptionFrame(ttk.Frame, ContextMenuMixin):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=12)

        ttk.Label(self, text="Исходный текст").grid(row=0, column=0, sticky="w")
        self.input_text = tk.Text(self, height=8, wrap="word")
        self.input_text.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(4, 10))

        ttk.Label(self, text="Модуль").grid(row=2, column=0, sticky="w")
        self.modulus_var = tk.StringVar(value="256")
        self.modulus_entry = ttk.Entry(self, textvariable=self.modulus_var, width=12)
        self.modulus_entry.grid(row=2, column=1, sticky="w", padx=(6, 12))
        self.bind_context_menu(self.modulus_entry)

        ttk.Button(self, text="Зашифровать", command=self.handle_encrypt).grid(row=2, column=2, sticky="w")

        ttk.Label(self, text="Код DDHH").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.code_var = tk.StringVar(value=generate_code())
        self.code_entry = ttk.Entry(self, textvariable=self.code_var, state="readonly", width=16)
        self.code_entry.grid(row=3, column=1, sticky="w", pady=(10, 0), padx=(6, 12))

        ttk.Button(self, text="Копировать код", command=lambda: self.copy_to_clipboard(self.code_var.get())).grid(
            row=3, column=2, sticky="w", pady=(10, 0)
        )

        ttk.Label(self, text="Зашифрованная строка").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.output_text = tk.Text(self, height=8, wrap="word", state="disabled")
        self.output_text.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=(4, 6))

        ttk.Button(self, text="Копировать шифр", command=self.copy_cipher).grid(row=6, column=0, sticky="w")

        self.bind_context_menu(self.input_text)
        self.bind_context_menu(self.output_text)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

    def copy_to_clipboard(self, value: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(value)

    def set_output(self, value: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", value)
        self.output_text.configure(state="disabled")

    def copy_cipher(self) -> None:
        cipher = self.output_text.get("1.0", "end").strip()
        if cipher:
            self.copy_to_clipboard(cipher)

    def handle_encrypt(self) -> None:
        text = self.input_text.get("1.0", "end").rstrip("\n")
        try:
            modulus = int(self.modulus_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Модуль должен быть целым числом.")
            return

        code = generate_code()
        self.code_var.set(code)

        if modulus < 128:
            messagebox.showwarning(
                "Предупреждение",
                "Модуль меньше 128 может привести к коллизиям (потере информации).",
            )

        try:
            cipher = encrypt(text=text, code=code, modulus=modulus)
        except CryptoError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return

        self.set_output(cipher)


class DecryptionFrame(ttk.Frame, ContextMenuMixin):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=12)

        ttk.Label(self, text="Строка шифра").grid(row=0, column=0, sticky="w")
        self.cipher_text = tk.Text(self, height=8, wrap="word")
        self.cipher_text.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(4, 10))

        ttk.Label(self, text="Код DDHH").grid(row=2, column=0, sticky="w")
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(self, textvariable=self.code_var, width=16)
        self.code_entry.grid(row=2, column=1, sticky="w", padx=(6, 12))

        ttk.Button(self, text="Расшифровать", command=self.handle_decrypt).grid(row=2, column=2, sticky="w")

        ttk.Label(self, text="Результат").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.result_text = tk.Text(self, height=8, wrap="word", state="disabled")
        self.result_text.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(4, 6))

        ttk.Button(self, text="Копировать результат", command=self.copy_result).grid(row=5, column=0, sticky="w")

        self.bind_context_menu(self.cipher_text)
        self.bind_context_menu(self.code_entry)
        self.bind_context_menu(self.result_text)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

    def set_result(self, value: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", value)
        self.result_text.configure(state="disabled")

    def copy_result(self) -> None:
        text = self.result_text.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)

    def handle_decrypt(self) -> None:
        cipher = self.cipher_text.get("1.0", "end").strip()
        code = self.code_var.get().strip()
        try:
            result = decrypt(cipher, code)
        except CryptoError as exc:
            self.set_result(str(exc))
            return
        self.set_result(result)


class FAQFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=12)
        faq = (
            "Алгоритм:\n"
            "• Генерация ключа: SHA-256 от кода DDHH (4 цифры), 32 байта ключа.\n"
            "• Шифрование: c = (idx + key_byte) % M.\n"
            "• Итог: M:числа|SHA-256(исходный_текст+код).\n"
            "• Дешифрование: idx = (c - key_byte) % M, проверка idx в диапазоне 0..127 и проверка хеша.\n\n"
            "Как пользоваться:\n"
            "1) В разделе «Шифрование» введите текст и модуль, нажмите «Зашифровать».\n"
            "2) Скопируйте шифр и код DDHH.\n"
            "3) В разделе «Дешифрование» вставьте шифр и код, нажмите «Расшифровать».\n\n"
            "Контакты: support@example.com"
        )

        text = tk.Text(self, wrap="word", state="normal")
        text.insert("1.0", faq)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Rippler — шифрование текста")
        self.geometry("900x650")
        self.minsize(800, 600)

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        self.menu_button = ttk.Button(top, text="☰", width=3, command=self.toggle_menu)
        self.menu_button.pack(side="left")
        ttk.Label(top, text="Rippler", font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        self.nav = ttk.Frame(body, padding=8)
        self.nav.pack(side="left", fill="y")

        ttk.Button(self.nav, text="Шифрование", command=lambda: self.show("enc")).pack(fill="x", pady=4)
        ttk.Button(self.nav, text="Дешифрование", command=lambda: self.show("dec")).pack(fill="x", pady=4)
        ttk.Button(self.nav, text="FAQ", command=lambda: self.show("faq")).pack(fill="x", pady=4)

        self.content = ttk.Frame(body)
        self.content.pack(side="left", fill="both", expand=True)

        self.frames: dict[str, ttk.Frame] = {
            "enc": EncryptionFrame(self.content),
            "dec": DecryptionFrame(self.content),
            "faq": FAQFrame(self.content),
        }

        for frame in self.frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show("enc")

    def show(self, name: str) -> None:
        self.frames[name].tkraise()

    def toggle_menu(self) -> None:
        if self.nav.winfo_manager():
            self.nav.pack_forget()
        else:
            self.nav.pack(side="left", fill="y", before=self.content)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
