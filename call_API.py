from dotenv import load_dotenv
import os
import anthropic

def call_claude(prompt, model = "claude-haiku-4-5-20251001",  max_tokens = 10000):
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text