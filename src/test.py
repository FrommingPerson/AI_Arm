import json

def load_json(file_path):
    """Загружает данные из JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_json(file_path, data):
    """Сохраняет данные в JSON-файл."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def replace_second_space_with_slash(message):
    """Заменяет каждый второй пробел на '/'."""
    space_count = 0
    new_message = []

    for char in message:
        if char == ' ':
            space_count += 1
            if space_count % 2 == 0:
                new_message.append('/')
                continue
        new_message.append(char)

    return ''.join(new_message)

def modify_messages(data):
    """Изменяет каждое сообщение, заменяя каждый второй пробел на '/'."""
    for idx, message in enumerate(data["messages"]):
        modified_message = replace_second_space_with_slash(message)
        data["messages"][idx] = modified_message
    return data

# Пример использования
file_path = './data/phrasesArray.json'  # Путь к файлу
data = load_json(file_path)
modified_data = modify_messages(data)
save_json(file_path, modified_data)
print("Каждый второй пробел заменён на '/'.")
