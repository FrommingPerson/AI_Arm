import json
import hashlib
import time

isReplaced:bool = True
file_path = "./data/phrasesArray.json"

def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("The file phrasesArray.json is not found")
        

def replace_second_space_with_slash(message:str):
    global isReplaced
    space_count = 0
    new_message = []
    if message.__contains__("/"):
        return message.lower()
    else:
        isReplaced = False
        for char in message:
            if char == ' ':
                space_count += 1
                if space_count % 2 == 0:
                    new_message.append('/')
                    continue
            new_message.append(char.lower())
        return ''.join(new_message)


def modify_messages(data):
    for idx, message in enumerate(data["messages"]):
        modified_message = replace_second_space_with_slash(message)
        data["messages"][idx] = modified_message
    return data


def save_json(file_path, data):
    global isReplaced
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print("There is no a phrase to replace spaces" if isReplaced == True else "Each 2nd space was replaced to /")
        isReplaced = True


def activate_replacement(file_path = './data/phrasesArray.json'):
    data = load_json(file_path)
    modified_data = modify_messages(data)
    save_json(file_path, modified_data)

initial_hash = hash_file(file_path)

while True:
    current_hash = hash_file(file_path)
    if current_hash != initial_hash:
        initial_hash = current_hash
        activate_replacement()
    time.sleep(15)  