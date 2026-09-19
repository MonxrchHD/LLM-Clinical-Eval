import json

with open("data/data_logs.jsonl") as f:
    for case_number, line in enumerate(f, start = 1):
        print(f"---- Case {case_number} ----")
        review = json.loads(line)
        for key, value in review.items():
            print(f"{key}: \n{value}\n")
        