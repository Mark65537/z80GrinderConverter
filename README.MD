# Описание

Скрипт для конвертирование в различные звуковые форматы, в первую очередь в java grinder.

herz = -256.6 * byte + 37246

## Структура

- players - содержит плейеры для z80, которые могут поддерживать различные форматы звуковых файлов(.wav, .mp3, .flac)
- scripts - содержит различные скрипты
- z80ModeAsm - содержит коды в формате .asm для инициализации  различных режимов z80
- HerzDacGrinder.csv - таблица в которой написанно соответствие герц со значением байт
- z80GrinderConverter.py - исходный код программы

## Как использовать

```bash
python z80GrinderConverter.py -in <input_format> -out <output_format> <file_name>
```

или

```bash
py z80GrinderConverter.py -in <input_format> -out <output_format> <file_name>
```
