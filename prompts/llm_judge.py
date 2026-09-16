from objects import Item, Domain, Rubric, build_items, build_domains, build_rubric
import yaml
from prompts.llm_consultant import build_consultant_prompt
from dotenv import load_dotenv
import os
import anthropic

with open("rubric/example_rubric.yaml") as f:
    data = yaml.safe_load(f)
rubric = build_rubric(data)

def build_llm_judge(rubric_text, case_text, response_text):
    prompt = f"""You are an expert clinical reviewer scoring an AI-generated clinical response against a structured rubric.

Below is the rubric, listing each domain, its items, and the scoring criteria (0, 1, or 2) for each item.

{rubric_text}

Here is the clinical case that was presented:

{case_text}

Here is the response you are scoring:

{response_text}

Score the response on every single item listed in the rubric above. For each item, assign the score (0, 1, or 2) that best matches the response according to that item's criteria. Base your scoring only on what is explicitly present in the response — do not give credit for something the response does not actually say, and do not penalize for information that was not clinically necessary for this case.

Respond with ONLY a single JSON object, and nothing else — no explanation, no markdown formatting, no text before or after the JSON. Use each item's exact ID as the key, and the numeric score as the value. For example, if the rubric had items A-1 and A-2, your entire response would look exactly like:
{{"A-1": 2, "A-2": 1}}

Now provide the complete JSON object with a score for every item ID in the rubric above."""
    return prompt

if __name__ == "__main__":
    case_text = """Chief complaint: Progressive shortness of breath and leg swelling over the past 10 days.

History of present illness: 67-year-old presents with worsening dyspnea on exertion, now occurring after walking less than one block, plus orthopnea (sleeping on 3 pillows) and bilateral lower extremity swelling. Reports a 6 lb weight gain over the past week. Denies chest pain, fever, or cough.

PMH: Heart failure with reduced ejection fraction (EF 35%, diagnosed 2 years ago), hypertension, atrial fibrillation.

PSH: Coronary artery bypass graft (CABG) 5 years ago.

Current medications: Lisinopril 20mg daily, metoprolol succinate 50mg daily, furosemide 20mg daily, apixaban 5mg twice daily, atorvastatin 40mg daily.

Allergies: NKDA.

Labs (today): Sodium 133 mEq/L, potassium 4.2 mEq/L, creatinine 1.3 mg/dL (baseline 1.0 mg/dL), BNP 1450 pg/mL (baseline ~300 pg/mL), unremarkable CBC.

Vitals: BP 128/78, HR 88 (irregularly irregular), RR 20, SpO2 94% on room air, weight up 6 lb from last visit."""

    rubric_text = ""
    for domain in rubric.domains:
        rubric_text += f"Domain: {domain.name}, \n"
        for item in domain.items:
            rubric_text += f"  Item: {item.id}, Topic: {item.topic}, Criteria: {item.criteria}\n"
    response_text = build_consultant_prompt(case_text)
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10000,
        messages=[{"role": "user", "content": build_llm_judge(rubric_text, case_text, response_text)}]
    )
    print(response.content[0].text)
        
    