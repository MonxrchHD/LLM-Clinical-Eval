import json

def build_data_logger(raw_case, flattened_case, case_text, response_text, item_scores, total_score, flag_results, model_name, rubric_version):
    record = {
    "raw_case_info": raw_case,
    "flattened_case": flattened_case,
    "HPI_summary": case_text,
    "consultant_response": response_text,
    "item_scores": item_scores,
    "total_score": total_score,
    "flag_results":flag_results,
    "model_name": model_name, 
    "rubric_version": rubric_version,
    }

    with open("data/data_logs.jsonl", "a") as f:
        lines = json.dumps(record)
        data = lines + "\n"
        f.write(data)

