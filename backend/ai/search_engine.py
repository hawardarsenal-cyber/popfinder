from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def smart_event_search(prompt, rules_text, web_text):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": f"You are PopFinder AI. Use these rules:\n{rules_text}"
            },
            {
                "role": "user",
                "content": f"User query: {prompt}\n\nWeb data:\n{web_text}"
            },
        ]
    )

    content = response.output[0].content[0].text
    return content

