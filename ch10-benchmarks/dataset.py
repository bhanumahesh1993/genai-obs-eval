"""A tiny multiple-choice benchmark subset.

These items are hand-authored in the shape of public knowledge and
reasoning benchmarks (MMLU-Pro, GPQA-style four/five-option MCQ).
They are ORIGINAL, not copied from any leaderboard set, so running
them here cannot contaminate a real benchmark and no license
applies. For a real run, replace SUBSET with a loader over a public
set you are licensed to use (for example the Hugging Face `datasets`
loaders for MMLU-Pro or GPQA); keep the `Item` shape and the rest of
the harness works unchanged.

Keep the subset small and READ every item. A benchmark you have not
read is a benchmark you cannot trust.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: str
    category: str
    question: str
    choices: dict[str, str]  # {"A": "...", "B": "...", ...}
    answer: str              # the correct letter, e.g. "C"


SUBSET: list[Item] = [
    Item(
        "chem-01",
        "chemistry",
        "Which quantity is conserved in every chemical reaction?",
        {"A": "Temperature", "B": "Number of moles of gas",
         "C": "Total mass", "D": "Volume"},
        "C",
    ),
    Item(
        "logic-01",
        "reasoning",
        "If all Blorps are Zings, and no Zings are Frobs, which "
        "statement must be true?",
        {"A": "Some Blorps are Frobs", "B": "No Blorps are Frobs",
         "C": "All Frobs are Zings", "D": "Some Frobs are Blorps"},
        "B",
    ),
    Item(
        "math-01",
        "math",
        "A shirt costs 40 after a 20 percent discount. What was the "
        "original price?",
        {"A": "48", "B": "50", "C": "60", "D": "32"},
        "B",
    ),
    Item(
        "bio-01",
        "biology",
        "In eukaryotic cells, ATP is produced mainly in the:",
        {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondrion",
         "D": "Golgi apparatus"},
        "C",
    ),
    Item(
        "cs-01",
        "computer-science",
        "What is the worst-case time complexity of binary search on "
        "a sorted array of n elements?",
        {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"},
        "B",
    ),
    Item(
        "phys-01",
        "physics",
        "A ball is dropped (ignore air resistance). Which quantity "
        "stays constant during the fall?",
        {"A": "Speed", "B": "Kinetic energy",
         "C": "Total mechanical energy", "D": "Momentum"},
        "C",
    ),
    Item(
        "logic-02",
        "reasoning",
        "Tom is older than Aisha. Aisha is older than Wei. Who is "
        "youngest?",
        {"A": "Tom", "B": "Aisha", "C": "Wei",
         "D": "Cannot be determined"},
        "C",
    ),
    Item(
        "math-02",
        "math",
        "What is the next number in the sequence 2, 6, 12, 20, 30, ?",
        {"A": "36", "B": "40", "C": "42", "D": "48"},
        "C",
    ),
]
