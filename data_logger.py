import json


def build_data_logger(raw_case, flattened_case, case_text, response_text, summary, item_scores, total_score, flag_results, model_name, rubric_version):
    record = {
        "raw_case_info": raw_case,
        "flattened_case": flattened_case,
        "HPI_summary": case_text,
        "consultant_response": response_text,
        "Clinical_summary": summary,
        "item_scores": item_scores,
        "total_score": total_score,
        "flag_results": flag_results,
        "model_name": model_name,
        "rubric_version": rubric_version,
    }

    with open("data/data_logs.jsonl", "a") as f:
        lines = json.dumps(record)
        data = lines + "\n"
        f.write(data)


def dpo_pair_logger(case_text, response_text, flawed_response, consultant_total_score, flawed_total_score, flawed_item_scores, flag_results, model_name, rubric_version):
    record = {

        "case_text": case_text,
        "response_text": response_text,
        "flawed_response": flawed_response,
        "consultant_total_score": consultant_total_score,
        "flawed_total_score": flawed_total_score,
        "flawed_item_scores": flawed_item_scores,
        "flag_results": flag_results,
        "model_name": model_name,
        "rubric_version": rubric_version,
    }

    with open("data/dpo_pairs.jsonl", "a") as f:
        lines = json.dumps(record)
        data = lines + "\n"
        f.write(data)


def dpo_training_logger(prompt, chosen, rejected):
    record = {
        "prompt": prompt,
        "chosen": chosen,
        "rejected": rejected
    }

    with open("data/dpo_training_data.jsonl", "a") as f:
        lines = json.dumps(record)
        data = lines + "\n"
        f.write(data)
