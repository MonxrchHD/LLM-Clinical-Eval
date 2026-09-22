import json
from data_logger import dpo_training_logger

def build_dpo_converter():
    with open("data/dpo_pairs.jsonl") as f:
        for line in f:
            convert = json.loads(line)
            prompt = convert["case_text"]
            chosen = convert["response_text"]
            rejected = convert["flawed_response"]

            dpo_training_logger(
                prompt = prompt,
                chosen = chosen,
                rejected = rejected
            )

if __name__ == "__main__":
    build_dpo_converter()