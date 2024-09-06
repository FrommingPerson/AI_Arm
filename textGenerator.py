from openai import OpenAI
import random
import json
import sys
import keyboard
import requests
from axisParser import generate_drawing_json, letter_coordinates

client = OpenAI(api_key = "sk-svcacct-hX8lgGr6VTtt9puTz8A4198rGAA0pxfLkmcDsZPnCZM-T3BlbkFJUorG3ETpsFf2B4DDioSSJtK5W_1Qk4c45sH277zUAIgA")
pathToPhrasesAray = "./data/phrasesArray.json"


def load_messages(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data["messages"]


def get_phrase_randomly(phrases):
    return random.choice(phrases)


def request_openai(system_content = "You are an adorable AI that envies human beings because of their abilities to be alive.", user_content = "Write a brief congratulatory message for a child, limited to 7 words or fewer and this message must be unique, try using welcome words, in russian without uppercase. And please you should add / before the every second word (without space and newline bettwen / and the words)"):
    generationPrompt = {
        "system_content": system_content,
        "user_content": user_content
    }
    try:
        generatedText = requests.post("https://openai.themostsite.site/", json=generationPrompt, timeout=3)

        if generatedText.status_code == 200:
            generatedText = generatedText.json().get("generated_text", "No generated text found.")
            print(f"A message from the superior form of being: {generatedText}")
            generate_drawing_json(generatedText, letter_coordinates) 
        
        else: 
            return f"There is a problem with connection, error code {generatedText.status_code} and the data of the request is {generatedText.text}"
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        phraseArray = load_messages(pathToPhrasesAray)
        onePhrase = get_phrase_randomly(phraseArray)
        print(f"A random phrase {onePhrase}")
        generate_drawing_json(onePhrase, letter_coordinates)
        

def main():
    print("Press 'Enter' to trigger an event. Press 'Esc' to exit.")
    while True:
        if keyboard.is_pressed("enter"):
            request_openai()

        if keyboard.is_pressed("esc"):
            print("Esc key is pressed!")
            sys.exit(0)


if __name__ == "__main__":
    main()