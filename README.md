# Lucifer Layers — библиотека раскладок для MacroPad Lucifer

Приложение Lucifer само замечает, что вы открыли программу, для которой здесь есть раскладка,
и предлагает её установить. Каталог скачивается целиком, совпадение ищется на вашем компьютере —
какие программы у вас стоят, никуда не отправляется.

## Формат слоя — `packs/<id>.json`

```json
{
  "schema": 1,
  "id": "blender",                 // = имя файла; латиница, цифры, дефис
  "name": "Blender",               // название в приложении
  "layer": "BLENDER",              // имя слоя на экране пада, до 11 латинских символов
  "category": "3D",
  "exe": ["blender.exe"],          // для каких программ (нижний регистр)
  "version": 1,                    // увеличивать при каждом изменении
  "author": "Lucifer",
  "tested": false,                 // проверено ли на живой программе
  "keys": [                        // ровно 9, K1…K9: слева направо, сверху вниз
    { "label": "GRAB", "combo": "G", "desc": "Переместить" },
    { "label": "VOL+", "media": "vol+", "desc": "Громче" }
  ],
  "encoder": {                     // R1 поворот влево, R2 нажатие, R3 поворот вправо
    "left":  { "label": "FRAME-", "combo": "Left",  "desc": "Кадр назад" },
    "press": { "label": "PLAY",   "combo": "Space", "desc": "Воспроизвести" },
    "right": { "label": "FRAME+", "combo": "Right", "desc": "Кадр вперёд" }
  }
}
```

- `label` — подпись на экране пада, до 8 латинских символов.
- `combo` — сочетание: `Ctrl`, `Shift`, `Alt`, `Win` + клавиша: `A`…`Z`, `0`…`9`, `F1`…`F24`, `Space`, `Tab`, `Esc`,
  `Enter`, `Backspace`, `Delete`, `Home`, `End`, `PageUp`, `PageDown`, `Left`/`Right`/`Up`/`Down`, `Num 0`…`Num 9`,
  знаки `- = [ ] \ ; ' ` , . /`. Пример: `Ctrl+Shift+Z`.
- `media` — `play`, `next`, `prev`, `stop`, `mute`, `vol+`, `vol-`.
- Слои — только данные (клавиши и подписи). Никаких скриптов и команд.

## Публикация

```
python tools/build_index.py --key ПУТЬ\к\lucifer_library.key
git add . && git commit -m "..." && git push
```

`build_index.py` проверяет каждый слой, собирает `index.json` и подписывает его (`index.json.sig`).
Приложение принимает только каталог с правильной подписью. Секретный ключ хранится у владельца
и **никогда** не кладётся в репозиторий (`*.key` в `.gitignore`).

Раздача: `https://cdn.jsdelivr.net/gh/<пользователь>/lucifer-layers@main/index.json`
