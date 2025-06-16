# law-classifier

Python-пакет для класифікації українських нормативно-правових актів за вісімома категоріями.

## Встановлення

```bash
pip install law-classifier
```

> **Note**: `law-classifier` relies on the [PyYAML](https://pyyaml.org/) package
> to parse rule definitions. If this dependency is missing, importing
> `law_classifier.rules` will fail with a clear error instructing you to
> install `pyyaml`.

## Використання CLI

```bash
# класифікувати один файл
law_classifier classify path/to/file.docx --json

# рекурсивна обробка папки
law_classifier batch ./laws --out results.csv --html --workers 4
```

Деталі алгоритму описано у [docs/algorithm.md](algorithm.md).
