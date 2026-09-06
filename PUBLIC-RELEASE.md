# Публичный релиз

Релизный вход — [единая галерея](index.html). Десять финальных плакатов показаны по районам. Прежние версии и первоначальные эксперименты остаются в игнорируемом локальном архиве.

В публичный набор входят:

- `README.md`, `LICENSE`, `ARTWORK-LICENSE.md`;
- `index.html` и `scripts/build_gallery.py`;
- `posters/`: одинаковая структура каждого запроса — `input/`, `prompt/`, `metadata/`;
- `output/`: все готовые PNG в одной папке;
- `AGENTS.md`: правила продолжения проекта.

Локальный архив старого дерева — `archive/legacy/`; он исключён через `.gitignore`. Старые генераторы и их исторические пути сохранены только там. Действующая сборка использует `metadata/request.json` каждого запроса.

Атрибуция и сведения о материалах находятся в `ARTWORK-LICENSE.md` и метаданных запросов. Перенос каталогов не меняет условия использования исходных материалов.

## Первый коммит

В обычной git-копии проекта:

```bash
git init
python3 scripts/build_gallery.py
git add .gitignore README.md LICENSE ARTWORK-LICENSE.md PUBLIC-RELEASE.md AGENTS.md index.html scripts/build_gallery.py posters output
git commit -m "Prepare Moscow poster series for public release"
```

Для генерации по своей фотографии следуйте README.md и AGENTS.md; плакаты из output/ используются как стилевые референсы.
