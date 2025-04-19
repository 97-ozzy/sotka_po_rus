import json

# 1. Загружаем существующий JSON-файл
with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. Записываем обратно, но с компактным форматированием
with open('data/questions.json', 'w', encoding='utf-8') as f:
    # Сначала преобразуем в строку с минификацией (без пробелов и переносов)
    json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

    # Затем добавляем переносы строк только после массивов верхнего уровня
    json_str = json_str.replace('],[', '],\n    [')  # для вложенных массивов
    json_str = json_str.replace('"4":[', '"4": [\n    [')  # для ключа "4"
    json_str = json_str.replace('"9":[', '"9": [\n    [')  # для ключа "9"
    json_str = json_str.replace(']]', ']\n  ]')  # закрывающие скобки

    f.write(json_str)