import operator
import re
from typing import List, Tuple

from fuzzywuzzy import fuzz


def _get_name_matches(name: str, guess_words: List[str]) -> int:
    matches = sum(word in name for word in guess_words)
    return matches


def _get_name_score(names: List[str], guess: str) -> int:
    names = [re.sub(r"[^\w\s]", "", name).lower() for name in names]
    guess_words = guess.split()
    matches = max(_get_name_matches(name, guess_words) for name in names)
    diff = max(fuzz.token_sort_ratio(guess, name) for name in names)
    return matches * 100 + diff


def _check_question(question: "PolyQuestion", guess: str) -> Tuple[int, int]:
    return question.id, _get_name_score([question.question], guess)


def _get_best_question_id(poly: "Poly", guess: str) -> int:
    return max(
        (_check_question(question, guess) for question in poly.questions),
        key=operator.itemgetter(1),
    )[0]


def search_question(poly: "Poly", guess: str) -> "PolyQuestion":
    return poly.get_question(_get_best_question_id(poly, guess))
