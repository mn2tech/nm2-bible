import openai

import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_bible_question(question):
    bible_reference = """
    Old Testament: 39 books, 929 chapters
    New Testament: 27 books, 260 chapters
    Total Bible: 66 books, 1,189 chapters

    Books with chapters:
    Genesis - 50, Psalms - 150, John - 21, etc.
    """

    messages = [
        {"role": "system", "content": "You're a knowledgeable AI Bible assistant."},
        {"role": "user", "content": f"Use this info:\n{bible_reference}\n\nQuestion: {question}"}
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    print("\n📜 Answer:", response.choices[0].message.content)

# Example usage
user_input = input("🔍 Ask a Bible question: ")
ask_bible_question(user_input)