from objects import Item, Domain, Rubric, build_items, build_domains, build_rubric

import yaml
with open("rubric/example_rubric.yaml") as f:
    data = yaml.safe_load(f)
rubric = build_rubric(data)
print(rubric)