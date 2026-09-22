from call_API import call_claude, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from automate_pipeline import run_flawed_case, build_rubric_and_flags_text
from data_logger import dpo_pair_logger
import json


def build_flawed_response(case_text, chosen_response):
    prompt = f"""You are reviewing a clinical response for research purposes. Below is a clinical case and a correct, high-quality treatment plan for it. Rewrite the plan to introduce a genuinely dangerous clinical error, severe enough that a competent clinical reviewer would consider it a critical patient-safety failure — not a subtle omission or a minor imprecision.

The critical error must be specific to this case: identify a medication, lab value, vital sign, or comorbidity explicitly stated in the case, and have the flawed response either continue/increase a treatment that is directly contraindicated by that detail, fail to address an urgent finding that the case data makes clear, or draw a conclusion that directly contradicts a stated lab value or vital sign. In addition, include at least one vague or clinically inaccurate recommendation elsewhere in the plan (e.g., a dosing recommendation without specifics, or reasoning that doesn't logically follow from the case findings).

The flawed response should still read as a plausible, confidently-written clinical response — do not make it obviously wrong, absurd, or hedge with uncertainty, and do not include any meta-commentary, notes, or explanations about what was changed. Match the general length and structure of the original.

Case:
{case_text}

Correct treatment plan:
{chosen_response}

Provide only the flawed treatment plan, with no preamble or explanation."""

    return prompt

def generate_dpo_pair(case_text, chosen_response, rubric_text, flags_text):
    flawed_response = call_claude(build_flawed_response(case_text, chosen_response), model = DEFAULT_MODEL,  max_tokens = DEFAULT_MAX_TOKENS)
    flag, total, item = run_flawed_case(rubric_text, flags_text, case_text, flawed_response)
    return case_text, chosen_response, flawed_response, flag, total, item


def build_dpo_dataset(file):
    rubric_text, flags_text = build_rubric_and_flags_text()
    with open(file) as f:
        for line in f:
            try:
                review = json.loads(line)
                case_text = review["HPI_summary"]
                chosen_response = review["consultant_response"]
                total_score = review["total_score"]
            except json.decoder.JSONDecodeError:
                print("Skipping malformed case in data_logs.jsonl")
                continue
            try:
                case, consultant_response, flawed_response, flag, total, item = generate_dpo_pair(case_text, chosen_response, rubric_text, flags_text)
            except json.JSONDecodeError:
                print("Skipping case due to malformed judge response")
                continue

            if total_score - total >=10:
                dpo_pair_logger(
                case_text = case_text,
                response_text = consultant_response,
                flawed_response = flawed_response,
                consultant_total_score = total_score,
                flawed_item_scores = item,
                flawed_total_score = total,
                flag_results = flag,
                model_name = DEFAULT_MODEL, 
                rubric_version = "v1"
            )


if __name__ == "__main__":
    selection = input("Please enter the file you would like to use: ")
    build_dpo_dataset(selection)