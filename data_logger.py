import json


def build_data_logger(raw_case, case_text, response_text, item_score, total_score, model_name, rubric_version):
    record = {
    "raw_case_info": raw_case,
    "HPI_summary": case_text,
    "consultant_response": response_text,
    "rubric_score": item_score,
    "total_score": total_score,
    "model_name": model_name, 
    "rubric_version": rubric_version,
    }

    with open("data/data_logs.jsonl", "a") as f:
        lines = json.dumps(record)
        data = lines + "\n"
        f.write(data)

if __name__ == "__main__":
    build_data_logger(
        raw_case="Test raw case",
        case_text="Test HPI summary",
        response_text="Test consultant response",
        item_score={"A-1": 2, "A-2": 1},
        total_score=3,
        model_name="claude-haiku-4-5-20251001",
        rubric_version="v1"
    )