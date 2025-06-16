# law-classifier

Python-пакет для класифікації українських нормативно-правових актів за вісімома категоріями.

## Встановлення

```bash
# базова установка (підтримка лише .txt)
pip install law-classifier

# додаткові формати
pip install law-classifier[full]
```

## Використання CLI

```bash
# класифікувати один файл
law_classifier classify path/to/file.docx --json

# рекурсивна обробка папки
law_classifier batch ./laws --out results.csv --html --workers 4
```

Деталі алгоритму описано у [docs/algorithm.md](algorithm.md).
