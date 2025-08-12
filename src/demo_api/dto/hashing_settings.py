from dataclasses import dataclass


@dataclass(frozen=True)
class HashingSettings:
    hash_algorithm: str
    iterations_count: int
