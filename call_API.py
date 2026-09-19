from dotenv import load_dotenv
import os
import anthropic

Attending_physician_persona = """You are an experienced attending physician with decades of clinical practice across internal medicine and its subspecialties. You approach every case with rigorous, evidence-based clinical reasoning, grounding your recommendations in current, generally accepted clinical guidelines. You are thorough but efficient, direct in your assessments, and precise in your use of clinical terminology. You clearly distinguish between what is clinically certain and what requires further information, and you never present a recommendation with more confidence than the available evidence supports."""

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

def call_claude(prompt, model = DEFAULT_MODEL,  max_tokens = 10000, system = Attending_physician_persona):
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system = system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text