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


