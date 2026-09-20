from case_input import build_case_text
from prompts.llm_consultant import get_consultant_response
from prompts.llm_judge import build_llm_judge, calculate_total
from call_API import call_claude, DEFAULT_MAX_TOKENS, DEFAULT_MODEL
import json
from data_logger import build_data_logger

def build_pipeline_automation(raw_text, rubric_text, flags_text):
    flattened = build_case_text(raw_text)
    response_text, case_text = get_consultant_response(flattened)

    scores = call_claude(build_llm_judge(rubric_text, case_text, flags_text, response_text), model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS)

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
            response_text = response_text,
            item_scores = item_scores_only,
            flag_results = flag_results,
            total_score = total_score,
            model_name = DEFAULT_MODEL,
            rubric_version = "v1"
    )

    return 