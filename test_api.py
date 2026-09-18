from dotenv import load_dotenv
import os
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=10000,
    messages=[{"role": "user", "content": "In a clinical setting, explain MI to me if I were your patient."}]
)
print(response.content[0].text)
