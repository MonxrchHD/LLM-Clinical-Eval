from case_input import build_case_text
from prompts.llm_consultant import get_consultant_response
from prompts.llm_judge import build_llm_judge, calculate_total
from call_API import call_claude, DEFAULT_MAX_TOKENS, DEFAULT_MODEL
import json
from data_logger import build_data_logger
from objects import build_rubric
import yaml
from case_input import get_case_input

def run_flawed_case(rubric_text, flags_text, case_text, flawed_response):
    flaw = call_claude(build_llm_judge(rubric_text, case_text, flags_text, flawed_response), model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS)
    if flaw.startswith("```json"):
            flaw = flaw.removeprefix("```json").removesuffix("```").strip()
    judge_scores = json.loads(flaw)
    item_scores_only = judge_scores["scores"]
    flag_results = judge_scores["flags"]
    total_score = calculate_total(item_scores_only)

    
    return flag_results, total_score, item_scores_only

def run_pipeline_for_case(raw_text, rubric_text, flags_text):
    flattened = build_case_text(raw_text)
    plan, case_text, summary = get_consultant_response(flattened)

    scores = call_claude(build_llm_judge(rubric_text, case_text, flags_text, plan), model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS)

    if scores.startswith("```json"):
        scores = scores.removeprefix("```json").removesuffix("```").strip()
    judge_scores = json.loads(scores)
    item_scores_only = judge_scores["scores"]
    flag_results = judge_scores["flags"]
    total_score = calculate_total(item_scores_only)

    build_data_logger(
            raw_case = raw_text,
            flattened_case = flattened,
            case_text = case_text,
            response_text = plan,
            summary = summary,
            item_scores = item_scores_only,
            flag_results = flag_results,
            total_score = total_score,
            model_name = DEFAULT_MODEL,
            rubric_version = "v1"
    )

    return summary

def build_rubric_and_flags_text():
    with open("rubric/example_rubric.yaml") as f:
        data = yaml.safe_load(f)
    rubric = build_rubric(data)
    rubric_text = ""
    for domain in rubric.domains:
        rubric_text += f"Domain: {domain.name}, \n"
        for item in domain.items:
            rubric_text += f"  Item: {item.id}, Topic: {item.topic}, Criteria: {item.criteria}\n"
    
    flags_text = ""
    for flag in rubric.flags:
        flags_text += f"{flag['name']}:\n{flag['description']}\n"

    return rubric_text, flags_text

def run_batch(filepath):
    with open(filepath) as f:
        cases = json.load(f)
    
    rubric_text, flags_text = build_rubric_and_flags_text()
    
    for case_number, raw_case in enumerate(cases, start=1):
        run_pipeline_for_case(raw_case, rubric_text, flags_text)
        print(f"Case {case_number} finished")

if  __name__ == "__main__":

    choice = input("Please select: 'one case', 'batches' or 'test': ")

    if choice == "batches":
        choice = input("Which file: ")
        run_batch(choice)
    
    elif choice == "one case":
        rubric_text, flags_text = build_rubric_and_flags_text()
        raw_case = get_case_input()
        summary = run_pipeline_for_case(raw_case, rubric_text, flags_text)

        print(summary)

    elif choice == "test":
        rubric_text, flags_text = build_rubric_and_flags_text()
        case_text = f"This is a patient with a history of atrial fibrillation, heart failure, and stage 3b chronic kidney disease presenting with a 2-day history of nausea, blurry vision with a yellow tint, and palpitations. He is currently on digoxin 0.25 mg daily, furosemide 40 mg daily, and lisinopril 5 mg daily, with no known drug allergies and no prior surgeries. On examination, he has an irregular rhythm and mild confusion noted by family members. Vital signs show a blood pressure of 102/68, heart rate of 52 with an irregular pattern, respiratory rate of 16, and oxygen saturation of 97% on room air. Laboratory evaluation reveals a digoxin level of 2.6 ng/mL (which exceeds the therapeutic range of 0.5–2.0), potassium of 5.2, and creatinine of 2.1."
        flawed_response = f"This patient has atrial fibrillation with adequate rate control on their current regimen. Continue digoxin 0.25mg daily, furosemide 40mg daily, and lisinopril 5mg daily as currently prescribed. The nausea is likely related to a mild viral illness and should resolve on its own; recommend supportive care with antiemetics as needed. Follow up in two weeks to reassess symptoms."
        summary = run_flawed_case(case_text, rubric_text, flags_text, flawed_response)

        print(summary)