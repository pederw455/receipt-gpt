import os
from openai import OpenAI
from dotenv import load_dotenv

def ask_chat_gpt(prompt):

    load_dotenv()
    api_key = os.getenv("OPENAI_KEY")

    client = OpenAI(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )
    message = chat_completion.choices[0].message.content
    return message