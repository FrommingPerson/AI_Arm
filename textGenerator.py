from openai import OpenAI
import sys
import keyboard

from axisParser import generate_drawing_json as generate_drawing_json
from axisParser import letter_coordinates as letter_coordinates

client = OpenAI(api_key = "sk-svcacct-hX8lgGr6VTtt9puTz8A4198rGAA0pxfLkmcDsZPnCZM-T3BlbkFJUorG3ETpsFf2B4DDioSSJtK5W_1Qk4c45sH277zUAIgA")

def generateText():
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an adorable AI that envies human beings because of their abilities to be alive."
                    # "content": "You are Borat and you're try to dominate a fiministka and you're angry."
                },
                {
                    "role": "user",
                    "content": "Write a brief congratulatory message for a child, limited to 7 words or fewer and this message must be unique and try using unusual words and welcome words too in russian without uppercase. And please add / before the every second word (without space and newline bettwen / and the words)"
                    # "content": "Write a hate message for a feministka, limited to 9 words or fewer and this message must be like Borat would say and try make mistakes like Borat, this text should be in russian without uppercase. And please add / before the every second word (without space and newline bettwen / and the words)"
                }
            ],
            temperature=0.7,
            max_tokens=64,
            top_p=1
        )
        print("Enter key is pressed!")
        congratulation = response.choices[0].message.content

        print(f"A message from the superior form of being: {congratulation}")


        generate_drawing_json(congratulation, letter_coordinates)
        # return congratulation

    except Exception as e:
        print(f"An error occurred: {e}")

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