from case_input import build_case_text
from prompts.llm_consultant import get_consultant_response
from prompts.llm_judge import build_llm_judge, calculate_total
from call_API import call_claude, DEFAULT_MAX_TOKENS, DEFAULT_MODEL
import json
from data_logger import build_data_logger
from objects import build_rubric
import yaml
from case_input import get_case_input

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
if  __name__ == "__main__":
    
    rubric_text, flags_text = build_rubric_and_flags_text()
    raw_case = get_case_input()
    summary = run_pipeline_for_case(raw_case, rubric_text, flags_text)

    print(summary)