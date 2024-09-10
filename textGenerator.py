from openai import OpenAI
import random
import json
import sys
import keyboard
import requests
from axisParser import generate_drawing_json, letter_coordinates


# pathToPhrasesAray = "/var/folders/gy/dx7qqng51n98k4t8kcdmg3wh0000gn/T/_MEIHPPYui/phrases_array.json"

import json
import os
import sys
import random

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller stores the path in _MEIPASS when bundled
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Resolve the path to phrases_array.json
pathToPhrasesAray = get_resource_path("phrases_array.json")

def load_messages(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data["messages"]


def get_phrase_randomly(phrases):
    return random.choice(phrases)

# def generateText():
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an adorable AI that envies human beings because of their abilities to be alive."
#                 },
#                 {
#                     "role": "user",
#                     "content": "Write a brief congratulatory message for a child, limited to 7 words or fewer and this message must be unique and try using unusual words and welcome words too in Russian without uppercase. And please add / before the every second word (without space and newline between / and the words)"
#                 }
#             ],
#             temperature=1,
#             max_tokens=100,
#             top_p=1
#         )
#         print("Enter key is pressed!")
#         congratulation = response.choices[0].message.content

#         print(f"A message from the superior form of being: {congratulation}")

#         generate_drawing_json(congratulation, letter_coordinates)

#     except Exception as e:
#         phrasesArray = load_messages(pathToPhrasesAray)
#         onePhrase = get_phrase_randomly(phrasesArray)
#         print(f"An error occurred: {e}")
#         print(f"A random phrase: {onePhrase}")
#         generate_drawing_json(onePhrase, letter_coordinates)


def request_openai(add_line, system_content = "You are an adorable AI that envies human beings because of their abilities to be alive.", user_content = "Write a brief fortune-telling for a human being, limited to 7 words or fewer and this message must be unique, try using welcome words, ONLY IN RUSSIAN without uppercase."):
    generationPrompt = {
        "system_content": system_content,
        "user_content": user_content
    }
    try:
        generatedText = requests.post("https://openai.themostsite.site/", json=generationPrompt)

        if generatedText.status_code == 200:
            generatedText = generatedText.json().get("generated_text", "No generated text found.")
            generatedText = add_line(generatedText)
            print(f"A message from the superior form of being: {generatedText}")
            generate_drawing_json(generatedText, letter_coordinates) 
            with open('samples.txt', 'a') as file:
                file.write(generatedText + '\n')
        
        else: 
            return f"There is a problem with connection, error code {generatedText.status_code} and the data of the request is {generatedText.text}"
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        phraseArray = load_messages(pathToPhrasesAray)
        onePhrase = get_phrase_randomly(phraseArray)
        print(f"A random phrase {onePhrase}")
        phraseArray = load_messages(pathToPhrasesAray)
        onePhrase = get_phrase_randomly(phraseArray)
        print(f"A random phrase {onePhrase}")
        generate_drawing_json(onePhrase, letter_coordinates)