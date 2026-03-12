import base64
import datetime as dt
import tkinter as tk
from tkinter import ttk


WINDOW_TITLE = "Rippler — шифрование"
MIN_WIDTH = 800
MIN_HEIGHT = 600


class ContextMenu:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.menu = tk.Menu(root, tearoff=False)
        self.menu.add_command(label="Вырезать", command=lambda: self._event_generate("<<Cut>>"))
        self.menu.add_command(label="Копировать", command=lambda: self._event_generate("<<Copy>>"))
        self.menu.add_command(label="Вставить", command=lambda: self._event_generate("<<Paste>>"))
        self._widget = None

    def bind_widget(self, widget: tk.Widget) -> None:
        widget.bind("<Button-3>", self._open_menu)
        widget.bind("<Control-c>", lambda e: self._event_on_widget(widget, "<<Copy>>"))
        widget.bind("<Control-v>", lambda e: self._event_on_widget(widget, "<<Paste>>"))
        widget.bind("<Control-x>", lambda e: self._event_on_widget(widget, "<<Cut>>"))

    def _open_menu(self, event):
        self._widget = event.widget
        self.menu.tk_popup(event.x_root, event.y_root)

    def _event_generate(self, sequence: str) -> None:
        if self._widget is not None:
            self._widget.event_generate(sequence)

    @staticmethod
    def _event_on_widget(widget: tk.Widget, sequence: str):
        widget.event_generate(sequence)
        return "break"


def generate_ddhh_code() -> str:
    now = dt.datetime.now()
    return f"{now.day:02d}{now.hour:02d}"


def derive_shift(code: str, module: int) -> int:
    day = int(code[:2])
    hour = int(code[2:])
    return (day + hour + module) % 256


def encrypt_text(plain_text: str, module: int) -> tuple[str, str]:
    code = generate_ddhh_code()
    shift = derive_shift(code, module)
    raw = plain_text.encode("utf-8")
    encrypted_bytes = bytes((byte + shift) % 256 for byte in raw)
    payload = base64.urlsafe_b64encode(encrypted_bytes).decode("ascii")
    cipher = f"{module}:{payload}"
    return cipher, code


def decrypt_text(cipher_text: str, code: str) -> str:
    if len(code) != 4 or not code.isdigit():
        raise ValueError("Код должен содержать ровно 4 цифры (DDHH).")

    if ":" not in cipher_text:
        raise ValueError("Некорректный формат шифра. Ожидается: module:данные.")

    module_part, payload = cipher_text.split(":", 1)
    if not module_part.isdigit() or int(module_part) <= 0:
        raise ValueError("Некорректный модуль в шифре.")

    module = int(module_part)
    shift = derive_shift(code, module)

    try:
        encrypted_bytes = base64.urlsafe_b64decode(payload.encode("ascii"))
    except Exception as exc:
        raise ValueError("Невозможно декодировать шифр.") from exc

    plain_bytes = bytes((byte - shift) % 256 for byte in encrypted_bytes)
    try:
        return plain_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Код неверный или шифр повреждён.") from exc


class EncryptionFrame(ttk.Frame):
    def __init__(self, parent, context_menu: ContextMenu):
        super().__init__(parent, padding=16)

        ttk.Label(self, text="Шифрование", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(self, text="Текст для шифрования:").grid(row=1, column=0, sticky="w", pady=(12, 4))
        self.input_text = tk.Text(self, height=10, wrap="word")
        self.input_text.grid(row=2, column=0, columnspan=3, sticky="nsew")

        ttk.Label(self, text="Модуль (> 0):").grid(row=3, column=0, sticky="w", pady=(12, 4))
        self.module_var = tk.StringVar(value="256")
        module_entry = ttk.Entry(self, textvariable=self.module_var)
        module_entry.grid(row=4, column=0, sticky="ew")

        encrypt_btn = ttk.Button(self, text="Зашифровать", command=self.on_encrypt)
        encrypt_btn.grid(row=4, column=1, padx=8, sticky="ew")

        ttk.Label(self, text="Шифр:").grid(row=5, column=0, sticky="w", pady=(12, 4))
        self.cipher_var = tk.StringVar()
        cipher_entry = ttk.Entry(self, textvariable=self.cipher_var, state="readonly")
        cipher_entry.grid(row=6, column=0, columnspan=2, sticky="ew")
        ttk.Button(self, text="Копировать шифр", command=lambda: self.copy_value(self.cipher_var)).grid(row=6, column=2, padx=(8, 0), sticky="ew")

        ttk.Label(self, text="Код DDHH:").grid(row=7, column=0, sticky="w", pady=(12, 4))
        self.code_var = tk.StringVar()
        code_entry = ttk.Entry(self, textvariable=self.code_var, state="readonly")
        code_entry.grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Button(self, text="Копировать код", command=lambda: self.copy_value(self.code_var)).grid(row=8, column=2, padx=(8, 0), sticky="ew")

        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, foreground="#b00020").grid(row=9, column=0, columnspan=3, sticky="w", pady=(10, 0))

        for col in range(3):
            self.columnconfigure(col, weight=1)
        self.rowconfigure(2, weight=1)

        for widget in [self.input_text, module_entry, cipher_entry, code_entry]:
            context_menu.bind_widget(widget)

    def on_encrypt(self) -> None:
        self.status_var.set("")
        text = self.input_text.get("1.0", "end-1c")
        module_str = self.module_var.get().strip()

        if not module_str.isdigit() or int(module_str) <= 0:
            self.status_var.set("Введите корректный модуль (целое число > 0).")
            return

        module = int(module_str)
        cipher, code = encrypt_text(text, module)
        self.cipher_var.set(cipher)
        self.code_var.set(code)

    def copy_value(self, variable: tk.StringVar) -> None:
        value = variable.get()
        self.clipboard_clear()
        self.clipboard_append(value)


class DecryptionFrame(ttk.Frame):
    def __init__(self, parent, context_menu: ContextMenu):
        super().__init__(parent, padding=16)

        ttk.Label(self, text="Расшифровка", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w")

        ttk.Label(self, text="Строка шифра:").grid(row=1, column=0, sticky="w", pady=(12, 4))
        self.cipher_var = tk.StringVar()
        cipher_entry = ttk.Entry(self, textvariable=self.cipher_var)
        cipher_entry.grid(row=2, column=0, sticky="ew")

        ttk.Label(self, text="Код (4 цифры DDHH):").grid(row=3, column=0, sticky="w", pady=(12, 4))
        self.code_var = tk.StringVar()
        code_entry = ttk.Entry(self, textvariable=self.code_var)
        code_entry.grid(row=4, column=0, sticky="ew")

        ttk.Button(self, text="Расшифровать", command=self.on_decrypt).grid(row=5, column=0, sticky="ew", pady=(12, 0))

        ttk.Label(self, text="Результат / ошибка:").grid(row=6, column=0, sticky="w", pady=(12, 4))
        self.result_var = tk.StringVar()
        result_entry = ttk.Entry(self, textvariable=self.result_var, state="readonly")
        result_entry.grid(row=7, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)

        for widget in [cipher_entry, code_entry, result_entry]:
            context_menu.bind_widget(widget)

    def on_decrypt(self) -> None:
        cipher = self.cipher_var.get().strip()
        code = self.code_var.get().strip()
        try:
            plain = decrypt_text(cipher, code)
            self.result_var.set(plain)
        except ValueError as exc:
            self.result_var.set(str(exc))


class FaqFrame(ttk.Frame):
    def __init__(self, parent, context_menu: ContextMenu):
        super().__init__(parent, padding=16)

        ttk.Label(self, text="FAQ", font=("Arial", 16, "bold")).pack(anchor="w")

        content = (
            "Описание алгоритма:\n"
            "1) Берётся код DDHH (день и час) и модуль.\n"
            "2) На основе DDHH и модуля вычисляется сдвиг для байтов.\n"
            "3) Текст кодируется в UTF-8, сдвигается и сериализуется в Base64.\n\n"
            "Краткая инструкция:\n"
            "• Во вкладке «Шифрование» введите текст и модуль, затем нажмите «Зашифровать».\n"
            "• Скопируйте шифр и код DDHH.\n"
            "• Во вкладке «Расшифровка» вставьте шифр и код, нажмите «Расшифровать».\n\n"
            "Контакты:\n"
            "Email: support@example.com\n"
            "Telegram: @example_support\n"
            "Телефон: +7 (000) 000-00-00"
        )

        text = tk.Text(self, wrap="word", height=20)
        text.insert("1.0", content)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, pady=(10, 0))
        context_menu.bind_widget(text)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.geometry("1000x700")

        self.context_menu = ContextMenu(self)

        top_bar = ttk.Frame(self, padding=(8, 8))
        top_bar.pack(fill="x")

        self.nav_visible = tk.BooleanVar(value=True)
        ttk.Button(top_bar, text="☰", width=3, command=self.toggle_nav).pack(side="left")
        ttk.Label(top_bar, text="Rippler", font=("Arial", 14, "bold")).pack(side="left", padx=(8, 0))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        self.nav_frame = ttk.Frame(body, padding=8)
        self.nav_frame.pack(side="left", fill="y")

        content = ttk.Frame(body, padding=4)
        content.pack(side="left", fill="both", expand=True)

        self.frames = {
            "EncryptionFrame": EncryptionFrame(content, self.context_menu),
            "DecryptionFrame": DecryptionFrame(content, self.context_menu),
            "FaqFrame": FaqFrame(content, self.context_menu),
        }

        self.current_frame = None
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        ttk.Button(self.nav_frame, text="Шифрование", command=lambda: self.show_frame("EncryptionFrame")).pack(fill="x", pady=4)
        ttk.Button(self.nav_frame, text="Расшифровка", command=lambda: self.show_frame("DecryptionFrame")).pack(fill="x", pady=4)
        ttk.Button(self.nav_frame, text="FAQ", command=lambda: self.show_frame("FaqFrame")).pack(fill="x", pady=4)

        self.show_frame("EncryptionFrame")

    def show_frame(self, name: str) -> None:
        frame = self.frames[name]
        frame.tkraise()
        self.current_frame = frame

    def toggle_nav(self) -> None:
        if self.nav_visible.get():
            self.nav_frame.pack_forget()
            self.nav_visible.set(False)
        else:
            self.nav_frame.pack(side="left", fill="y")
            self.nav_visible.set(True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
