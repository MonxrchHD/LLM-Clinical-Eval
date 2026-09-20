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


    info = get_case_input()
    raw = build_case_text(info)
    response_text, case_text = get_consultant_response(raw)
    
    rubric_text = ""
    for domain in rubric.domains:
        rubric_text += f"Domain: {domain.name}, \n"
        for item in domain.items:
            rubric_text += f"  Item: {item.id}, Topic: {item.topic}, Criteria: {item.criteria}\n"

    flags_text = ""
    for flag in rubric.flags:
        flags_text += f"{flag['name']}:\n{flag['description']}\n"


    scores = call_claude(build_llm_judge(rubric_text, case_text, flags_text, response_text), model = DEFAULT_MODEL,  max_tokens = DEFAULT_MAX_TOKENS)
    if scores.startswith("```json"):
        scores = scores.removeprefix("```json").removesuffix("```").strip()
    judge_scores = json.loads(scores)
    item_scores_only = judge_scores["scores"]
    flag_results = judge_scores["flags"]
    total_score = calculate_total(item_scores_only)
    print(total_score)
    print(flag_results)
    print(f"Total score: {total_score} / {rubric.total_points}")

    build_data_logger(
            raw_case = info,
            flattened_case = raw,
            case_text = case_text,
            response_text = response_text,
            item_scores = item_scores_only,
            flag_results = flag_results,
            total_score = total_score,
            model_name = DEFAULT_MODEL,
            rubric_version = "v1"
    )