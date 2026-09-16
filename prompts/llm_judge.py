from objects import Item, Domain, Rubric, build_items, build_domains, build_rubric
import yaml

with open("rubric/example_rubric.yaml") as f:
    data = yaml.safe_load(f)
rubric = build_rubric(data)

rubric_text = ""
for domain in rubric.domains:
    rubric_text += f"Domain: {domain.name}, \n"
    for item in domain.items:
        rubric_text += f"  Item: {item.id}, Topic: {item.topic}, Criteria: {item.criteria}\n"