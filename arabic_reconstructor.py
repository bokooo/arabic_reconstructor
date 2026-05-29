
import sys
import os
import json
import time
import re
import tkinter as tk
from tkinter import ttk, messagebox

import psutil

try:
    from pynput import keyboard
    from pynput.keyboard import Controller, Key
except ImportError:
    print("Missing packages.")
    print("Run: pip install pynput psutil pywin32")
    sys.exit(1)

if sys.platform == "win32":
    import win32process
    import win32gui
    import win32clipboard
else:
    win32gui = None


# =========================================================
# CONFIG
# =========================================================

CONFIG_FILE = os.path.join(
    os.path.expanduser("~"),
    "advanced_arabic_reconstructor.json"
)


def load_tracked_programs():

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    return data
        except:
            pass

    return [
        "blender.exe",
        "designer.exe",
        "photoshop.exe",
        "notepad.exe"
    ]



def save_tracked_programs(programs):

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(programs, f, indent=4)

    except Exception as e:
        print("Config save error:", e)


# =========================================================
# ARABIC TABLE
# =========================================================

ARABIC_FORMS = {
    'ا': ('ﺍ', 'ﺎ', 'ﺍ', 'ﺎ'),
    'أ': ('ﺃ', 'ﺄ', 'ﺃ', 'ﺄ'),
    'إ': ('ﺇ', 'ﺈ', 'ﺇ', 'ﺈ'),
    'آ': ('ﺁ', 'ﺂ', 'ﺁ', 'ﺂ'),
    'ب': ('ﺏ', 'ﺐ', 'ﺒ', 'ﺑ'),
    'ت': ('ﺕ', 'ﺖ', 'ﺘ', 'ﺗ'),
    'ث': ('ﺙ', 'ﺚ', 'ﺜ', 'ﺛ'),
    'ج': ('ﺝ', 'ﺞ', 'ﺠ', 'ﺟ'),
    'ح': ('ﺡ', 'ﺢ', 'ﺤ', 'ﺣ'),
    'خ': ('ﺥ', 'ﺦ', 'ﺨ', 'ﺧ'),
    'د': ('ﺩ', 'ﺪ', 'ﺩ', 'ﺪ'),
    'ذ': ('ﺫ', 'ﺬ', 'ﺫ', 'ﺬ'),
    'ر': ('ﺭ', 'ﺮ', 'ﺭ', 'ﺮ'),
    'ز': ('ﺯ', 'ﺰ', 'ﺯ', 'ﺰ'),
    'س': ('ﺱ', 'ﺲ', 'ﺴ', 'ﺳ'),
    'ش': ('ﺵ', 'ﺶ', 'ﺸ', 'ﺷ'),
    'ص': ('ﺹ', 'ﺺ', 'ﺼ', 'ﺻ'),
    'ض': ('ﺽ', 'ﺾ', 'ﻀ', 'ﺿ'),
    'ط': ('ﻁ', 'ﻂ', 'ﻄ', 'ﻃ'),
    'ظ': ('ﻅ', 'ﻆ', 'ﻈ', 'ﻇ'),
    'ع': ('ﻉ', 'ﻊ', 'ﻌ', 'ﻋ'),
    'غ': ('ﻍ', 'ﻎ', 'ﻐ', 'ﻏ'),
    'ف': ('ﻑ', 'ﻒ', 'ﻔ', 'ﻓ'),
    'ق': ('ﻕ', 'ﻖ', 'ﻘ', 'ﻗ'),
    'ك': ('ﻙ', 'ﻚ', 'ﻜ', 'ﻛ'),
    'ل': ('ﻝ', 'ﻞ', 'ﻠ', 'ﻟ'),
    'م': ('ﻡ', 'ﻢ', 'ﻤ', 'ﻣ'),
    'ن': ('ﻥ', 'ﻦ', 'ﻨ', 'ﻧ'),
    'ه': ('ﻩ', 'ﻪ', 'ﻬ', 'ﻫ'),
    'و': ('ﻭ', 'ﻮ', 'ﻭ', 'ﻮ'),
    'ي': ('ﻱ', 'ﻲ', 'ﻴ', 'ﻳ'),
    'ى': ('ﻯ', 'ﻰ', 'ﻯ', 'ﻰ'),
    'ة': ('ﺓ', 'ﺔ', 'ﺓ', 'ﺔ'),
    'ئ': ('ﺉ', 'ﺊ', 'ﺌ', 'ﺋ'),
    'ؤ': ('ﺅ', 'ﺆ', 'ﺅ', 'ﺆ'),
    'ء': ('ء', 'ء', 'ء', 'ء'),
    'پ': ('ﭖ', 'ﭗ', 'ﭙ', 'ﭘ'),
    'چ': ('ﭺ', 'ﭻ', 'ﭽ', 'ﭼ'),
    'ژ': ('ﮊ', 'ﮋ', 'ﮊ', 'ﮋ'),
    'گ': ('ﮒ', 'ﮓ', 'ﮕ', 'ﮔ'),
}


DISCONNECTORS = {
    'ا', 'أ', 'إ', 'آ',
    'د', 'ذ', 'ر', 'ز',
    'و', 'ؤ', 'ء', 'ژ'
}


HARAKAT = {
    'َ', 'ً', 'ُ', 'ٌ',
    'ِ', 'ٍ', 'ْ', 'ّ'
}


# =========================================================
# LIGATURES
# =========================================================

LAM_ALEF_LIGATURES = {
    'لا': 'ﻻ',
    'لأ': 'ﻷ',
    'لإ': 'ﻹ',
    'لآ': 'ﻵ'
}


# =========================================================
# TEXT HELPERS
# =========================================================

ENGLISH_PATTERN = re.compile(r'[A-Za-z0-9]')



def is_arabic_char(ch):
    return ch in ARABIC_FORMS



def apply_ligatures(text):

    for k, v in LAM_ALEF_LIGATURES.items():
        text = text.replace(k, v)

    return text



def shape_arabic(text):

    chars = list(text)
    result = []

    for i, ch in enumerate(chars):

        if ch not in ARABIC_FORMS:
            result.append(ch)
            continue

        prev_char = chars[i - 1] if i > 0 else None
        next_char = chars[i + 1] if i < len(chars) - 1 else None

        connect_prev = (
            prev_char in ARABIC_FORMS
            and prev_char not in DISCONNECTORS
        )

        connect_next = (
            next_char in ARABIC_FORMS
            and ch not in DISCONNECTORS
        )

        if connect_prev and connect_next:
            form = 2
        elif connect_prev:
            form = 1
        elif connect_next:
            form = 3
        else:
            form = 0

        result.append(ARABIC_FORMS[ch][form])

    return ''.join(result)



def reverse_preserving_english(text):

    tokens = re.findall(r'[A-Za-z0-9_./:-]+|.', text)

    tokens.reverse()

    return ''.join(tokens)



def process_line(line):

    line = apply_ligatures(line)

    shaped = shape_arabic(line)

    reversed_line = reverse_preserving_english(shaped)

    return reversed_line



def reconstruct_text(text):

    lines = text.split('\n')

    processed = []

    for line in lines:

        if not line.strip():
            processed.append(line)
            continue

        processed.append(process_line(line))

    return '\n'.join(processed)


# =========================================================
# HOTKEY ENGINE
# =========================================================

class BackgroundHookEngine:

    def __init__(self):

        self.keyboard = Controller()
        self.listener = None
        self.tracked_executables = load_tracked_programs()

    def get_active_process_name(self):

        try:
            hwnd = win32gui.GetForegroundWindow()

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            process = psutil.Process(pid)

            return process.name().lower()

        except:
            return ""

    def clipboard_get(self):

        try:
            win32clipboard.OpenClipboard()

            data = win32clipboard.GetClipboardData(
                win32clipboard.CF_UNICODETEXT
            )

            win32clipboard.CloseClipboard()

            return data

        except:

            try:
                win32clipboard.CloseClipboard()
            except:
                pass

            return ""

    def clipboard_set(self, text):

        try:
            win32clipboard.OpenClipboard()

            win32clipboard.EmptyClipboard()

            win32clipboard.SetClipboardText(
                text,
                win32clipboard.CF_UNICODETEXT
            )

            win32clipboard.CloseClipboard()

        except:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

    def press_combo(self, key_char):

        self.keyboard.press(Key.ctrl)
        self.keyboard.press(key_char)

        time.sleep(0.04)

        self.keyboard.release(key_char)
        self.keyboard.release(Key.ctrl)

    def allowed_app(self):

        current = self.get_active_process_name()

        return any(
            app in current
            for app in self.tracked_executables
        )

    def process_selection(self):

        if not self.allowed_app():
            return

        old_clipboard = self.clipboard_get()

        self.press_combo('c')

        time.sleep(0.12)

        text = self.clipboard_get()

        if not text:
            return

        processed = reconstruct_text(text)

        self.clipboard_set(processed)

        time.sleep(0.06)

        self.press_combo('v')

        time.sleep(0.06)

        self.clipboard_set(old_clipboard)

    def on_press(self, key):

        try:
            if key == Key.f8:
                self.process_selection()

        except Exception as e:
            print("Hook error:", e)

    def start(self):

        self.listener = keyboard.Listener(
            on_press=self.on_press
        )

        self.listener.start()


# =========================================================
# GUI
# =========================================================

class AppGUI:

    def __init__(self, root, engine):

        self.root = root
        self.engine = engine

        self.root.title("Advanced Arabic Reconstructor")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        self.build_ui()

    def build_ui(self):

        title = ttk.Label(
            self.root,
            text="Advanced Arabic Reconstructor",
            font=("Arial", 14, "bold")
        )

        title.pack(pady=12)

        info = ttk.Label(
            self.root,
            text="Select Arabic text then press F8"
        )

        info.pack(pady=4)

        top = ttk.Frame(self.root)
        top.pack(fill='x', padx=20, pady=10)

        self.entry_var = tk.StringVar()

        self.entry = ttk.Entry(
            top,
            textvariable=self.entry_var
        )

        self.entry.pack(
            side='left',
            fill='x',
            expand=True,
            padx=(0, 6)
        )

        add_btn = ttk.Button(
            top,
            text="Add Program",
            command=self.add_program
        )

        add_btn.pack(side='right')

        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20)

        self.listbox = tk.Listbox(
            frame,
            font=("Consolas", 10)
        )

        self.listbox.pack(
            side='left',
            fill='both',
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient='vertical',
            command=self.listbox.yview
        )

        scrollbar.pack(side='right', fill='y')

        self.listbox.config(
            yscrollcommand=scrollbar.set
        )

        bottom = ttk.Frame(self.root)
        bottom.pack(fill='x', padx=20, pady=15)

        remove_btn = ttk.Button(
            bottom,
            text="Remove Selected",
            command=self.remove_selected
        )

        remove_btn.pack(side='left')

        minimize_btn = ttk.Button(
            bottom,
            text="Minimize",
            command=self.root.iconify
        )

        minimize_btn.pack(side='right')

        self.refresh()

    def refresh(self):

        self.listbox.delete(0, tk.END)

        for item in self.engine.tracked_executables:
            self.listbox.insert(tk.END, item)

    def add_program(self):

        prog = self.entry_var.get().strip().lower()

        if not prog:
            return

        if '\\' in prog or '/' in prog:
            prog = os.path.basename(prog)

        if not prog.endswith('.exe'):
            prog += '.exe'

        if prog not in self.engine.tracked_executables:

            self.engine.tracked_executables.append(prog)

            save_tracked_programs(
                self.engine.tracked_executables
            )

            self.refresh()

            self.entry_var.set('')

        else:
            messagebox.showwarning(
                'Duplicate',
                'Program already exists.'
            )

    def remove_selected(self):

        try:
            idx = self.listbox.curselection()[0]

            item = self.listbox.get(idx)

            self.engine.tracked_executables.remove(item)

            save_tracked_programs(
                self.engine.tracked_executables
            )

            self.refresh()

        except:
            messagebox.showwarning(
                'Selection Error',
                'Nothing selected.'
            )


# =========================================================
# MAIN
# =========================================================

if __name__ == '__main__':

    engine = BackgroundHookEngine()

    engine.start()

    root = tk.Tk()

    app = AppGUI(root, engine)

    def close_app():
        root.destroy()
        sys.exit(0)

    root.protocol(
        'WM_DELETE_WINDOW',
        close_app
    )

    root.mainloop()

