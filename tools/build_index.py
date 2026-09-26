"""Сборка и подпись каталога библиотеки слоёв Lucifer.

  python tools/build_index.py --genkey KEYFILE     создать ключ подписи (один раз; хранить НЕ в репозитории!)
  python tools/build_index.py --key KEYFILE        проверить все слои, собрать index.json и подписать его

Приложение Lucifer ставит только слои из каталога, подписанного этим ключом (публичный ключ зашит в приложении).
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ed25519          # noqa: E402
import keys             # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
ASCII = re.compile(r"^[\x20-\x7e]*$")


def validate(path):
    raw = open(path, "rb").read()
    p = json.loads(raw.decode("utf-8"))
    pid = os.path.splitext(os.path.basename(path))[0]
    err = []
    if p.get("schema") != 1:
        err.append("schema должен быть 1")
    if p.get("id") != pid:
        err.append(f"id «{p.get('id')}» не совпадает с именем файла «{pid}»")
    if not re.match(r"^[a-z0-9][a-z0-9-]{1,40}$", pid):
        err.append("id: латиница в нижнем регистре, цифры и дефис")
    layer = p.get("layer", "")
    if not layer or len(layer) > 11 or not ASCII.match(layer):
        err.append("layer: 1–11 латинских символов (имя слоя на экране пада)")
    exe = p.get("exe") or []
    if not exe or any(not e.endswith(".exe") or e != e.lower() for e in exe):
        err.append("exe: список имён программ в нижнем регистре, например blender.exe")
    if not isinstance(p.get("version"), int) or p["version"] < 1:
        err.append("version: целое число ≥ 1 (увеличивать при каждом изменении)")
    ks = p.get("keys") or []
    if len(ks) != 9:
        err.append("keys: ровно 9 клавиш, по порядку K1…K9 (слева направо, сверху вниз)")
    actions = list(enumerate(ks, 1)) + [(f"энкодер.{n}", (p.get("encoder") or {}).get(n)) for n in ("left", "press", "right")]
    for n, k in actions:
        if k is None:
            continue
        lab = k.get("label", "")
        if len(lab) > 8 or not ASCII.match(lab):
            err.append(f"K{n}: label до 8 латинских символов")
        try:
            keys.parse_action(k)
        except (ValueError, KeyError) as e:
            err.append(f"K{n}: {e}")
    return p, raw, err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", help="файл с секретным ключом (32 байта hex)")
    ap.add_argument("--genkey", help="создать новый ключ в этом файле")
    a = ap.parse_args()
    if a.genkey:
        sk = os.urandom(32)
        open(a.genkey, "w").write(sk.hex())
        print("Секретный ключ:", a.genkey, "— НЕ публиковать, не класть в репозиторий")
        print("Публичный ключ (вставить в приложение, LIBRARY_PUBKEY):", ed25519.public_key(sk).hex())
        return
    items, bad = [], 0
    for fn in sorted(os.listdir(PACKS)):
        if not fn.endswith(".json"):
            continue
        p, raw, err = validate(os.path.join(PACKS, fn))
        if err:
            bad += 1
            print(f"✗ {fn}:\n   " + "\n   ".join(err))
            continue
        items.append({k: p[k] for k in ("id", "name", "layer", "category", "exe", "version")} |
                     {"tested": bool(p.get("tested")), "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)})
        print(f"✓ {fn}")
    if bad:
        sys.exit(f"Ошибок в слоях: {bad}. Каталог не собран.")
    index = {"schema": 1, "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "packs": items}
    data = json.dumps(index, ensure_ascii=False, indent=1).encode("utf-8")
    open(os.path.join(ROOT, "index.json"), "wb").write(data)
    if a.key:
        sk = bytes.fromhex(open(a.key).read().strip())
        open(os.path.join(ROOT, "index.json.sig"), "w").write(ed25519.sign(sk, data).hex())
        print(f"Каталог: {len(items)} слоёв, подписан.")
    else:
        print(f"Каталог: {len(items)} слоёв. ВНИМАНИЕ: без --key не подписан — приложение его не примет.")


if __name__ == "__main__":
    main()
