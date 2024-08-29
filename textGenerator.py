from openai import OpenAI
import random
import json
import sys
import keyboard


from axisParser import generate_drawing_json as generate_drawing_json
from axisParser import letter_coordinates as letter_coordinates

client = OpenAI(api_key = "sk-svcacct-hX8lgGr6VTtt9puTz8A4198rGAA0pxfLkmcDsZPnCZM-T3BlbkFJUorG3ETpsFf2B4DDioSSJtK5W_1Qk4c45sH277zUAIgA")
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

def generateText():
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an adorable AI that envies human beings because of their abilities to be alive."
                },
                {
                    "role": "user",
                    "content": "Write a brief congratulatory message for a child, limited to 7 words or fewer and this message must be unique and try using unusual words and welcome words too in Russian without uppercase. And please add / before the every second word (without space and newline between / and the words)"
                }
            ],
            temperature=1,
            max_tokens=100,
            top_p=1
        )
        print("Enter key is pressed!")
        congratulation = response.choices[0].message.content

        print(f"A message from the superior form of being: {congratulation}")

        generate_drawing_json(congratulation, letter_coordinates)

    except Exception as e:
        phrasesArray = load_messages(pathToPhrasesAray)
        onePhrase = get_phrase_randomly(phrasesArray)
        print(f"An error occurred: {e}")
        print(f"A random phrase: {onePhrase}")
        generate_drawing_json(onePhrase, letter_coordinates)



# def main():
#     print("Press 'Enter' to trigger an event. Press 'Esc' to exit.")
#     while True:
#         if keyboard.is_pressed("enter"):
#             generateText()

#         if keyboard.is_pressed("esc"):
#             print("Esc key is pressed!")
#             sys.exit(0)


    # Set up the hotkey for the Enter key
        # keyboard.add_hotkey('enter', on_enter)

    # Block the program, keeping it running until the Esc key is pressed
        # keyboard.wait('esc')

# if __name__ == "__main__":
#     main()