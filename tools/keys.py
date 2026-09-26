"""Разбор записи действий из файлов слоёв: «Ctrl+Shift+Z», «Num 0», «media:play».
Та же таблица, что в приложении (app/hid_keys.py) — HID-коды не зависят от раскладки клавиатуры."""
MOD = {"ctrl": 0x01, "control": 0x01, "shift": 0x02, "alt": 0x04, "win": 0x08, "meta": 0x08, "cmd": 0x08}

KEYS = {}
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    KEYS[ch.lower()] = 0x04 + i
for i, ch in enumerate("1234567890"):
    KEYS[ch] = 0x1E + i
KEYS.update({
    "enter": 0x28, "return": 0x28, "esc": 0x29, "escape": 0x29, "backspace": 0x2A, "tab": 0x2B, "space": 0x2C,
    "-": 0x2D, "minus": 0x2D, "=": 0x2E, "equal": 0x2E, "plus": 0x2E, "[": 0x2F, "]": 0x30, "\\": 0x31, ";": 0x33,
    "'": 0x34, "`": 0x35, ",": 0x36, ".": 0x37, "/": 0x38, "capslock": 0x39,
    "printscreen": 0x46, "scrolllock": 0x47, "pause": 0x48, "insert": 0x49, "home": 0x4A, "pageup": 0x4B, "pgup": 0x4B,
    "delete": 0x4C, "del": 0x4C, "end": 0x4D, "pagedown": 0x4E, "pgdn": 0x4E,
    "right": 0x4F, "→": 0x4F, "left": 0x50, "←": 0x50, "down": 0x51, "↓": 0x51, "up": 0x52, "↑": 0x52,
    "num /": 0x54, "num *": 0x55, "num -": 0x56, "num +": 0x57, "num enter": 0x58, "num 0": 0x62, "num .": 0x63,
})
for i in range(24):
    KEYS[f"f{i + 1}"] = (0x3A + i) if i < 12 else (0x68 + i - 12)
for i in range(9):
    KEYS[f"num {i + 1}"] = 0x59 + i

MEDIA = {"play": 0xCD, "playpause": 0xCD, "next": 0xB5, "prev": 0xB6, "previous": 0xB6, "stop": 0xB7,
         "mute": 0xE2, "vol+": 0xE9, "volup": 0xE9, "vol-": 0xEA, "voldown": 0xEA}


def parse_combo(text):
    """'Ctrl+Shift+Z' -> (mod, hid). Клавиша «+» пишется как 'Plus', сама по себе '+' — тоже можно."""
    t = text.strip()
    if t == "+":
        return 0, KEYS["plus"]
    parts = [p.strip() for p in (t[:-1].split("+") + ["+"] if t.endswith("++") else t.split("+"))]
    mod = 0
    for p in parts[:-1]:
        m = MOD.get(p.lower())
        if m is None:
            raise ValueError(f"неизвестный модификатор «{p}» в «{text}»")
        mod |= m
    key = KEYS.get(parts[-1].lower())
    if key is None:
        raise ValueError(f"неизвестная клавиша «{parts[-1]}» в «{text}»")
    return mod, key


def parse_action(a):
    """Действие из файла слоя -> ('none'|'key'|'media', mod, key, media)."""
    if not a or a.get("none"):
        return ("none", 0, 0, 0)
    if "media" in a:
        m = MEDIA.get(str(a["media"]).lower())
        if m is None:
            raise ValueError(f"неизвестная медиаклавиша «{a['media']}»")
        return ("media", 0, 0, m)
    mod, key = parse_combo(a["combo"])
    return ("key", mod, key, 0)
