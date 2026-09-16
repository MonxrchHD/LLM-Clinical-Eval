from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Item:
    id: str
    topic: str
    criteria: dict[int, str]

@dataclass
class Domain:
    name: str
    max_points: int
    items: List[Item]

@dataclass
class Rubric:
    rubric_name: str
    total_points: int
    domains: List[Domain]
    flags: Dict[str, bool]

def build_items(item_dicts):
    items = []
    for item_dict in item_dicts:
        curr_item = Item(item_dict["id"], item_dict["topic"], item_dict["criteria"])
        items.append(curr_item)
    return items

def build_domains(domain_dicts):
    domains = []
    for domain_dict in domain_dicts:
        items = build_items(domain_dict["items"])
        curr_domain = Domain(domain_dict["name"], domain_dict["max_points"], items)
        domains.append(curr_domain)
    return domains

def build_rubric(rubric_dict):
    domains = build_domains(rubric_dict["domains"])
    rubric = Rubric(rubric_dict["rubric_name"], rubric_dict["total_points"], domains, rubric_dict["flags"])
    return rubric