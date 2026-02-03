import random
from typing import List, Dict, Any
import json


def load_thai_json_as_list(username:str = "", path: str = "src/data/language_data/thai_data/thai.json", is_letters: bool = True) -> List[Dict[str, Any]]:
    """
    Load a JSON file and return its contained dictionaries as a flat list.
    - If the file contains a list of dicts, that list is returned (filtered to dicts).
    - If the file contains a dict whose values are lists of dicts (like the provided thai.json),
      all dict elements from those lists are concatenated and returned.
    - On error or unexpected structure, returns an empty list.
    """
    if username != "":
        path = f"src/data/user_data/user_data/{username}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            print(f"Loading JSON data from {path}")
            data = json.load(f)
    except Exception:
        print(f"Error loading JSON data from {path}")
        return []
    
    if is_letters:
        data = data.get("thai_letters", [])
    else:
        data = data.get("thai_words", [])

    final_data = []
    if isinstance(data, list):
        final_data = [it for it in data if isinstance(it, dict)]

    elif isinstance(data, dict):
        final_data = []
        for v in data.values():
            if isinstance(v, list):
                final_data.extend([it for it in v if isinstance(it, dict)])
    
    print("Exercise data loaded:", len(final_data), "items.")
    return final_data


def pick_lowest_priority_items(items: List[Dict[str, Any]], n: int, priority_key: str = "priority", is_seen: bool = False) -> List[Dict[str, Any]]:
    """
    Sorts items by priority_key, selects items that have the lowest priority value,
    and returns up to n unique items chosen randomly from that lowest-priority pool.
    Sampling is always without replacement (i.e. no duplicates in the result).
    Items missing priority_key are ignored.
    """
    if n <= 0:
        return []

    valid = [it for it in items if priority_key in it]
    if is_seen:
        valid = [it for it in valid if it.get("is_seen", True)]
    else:
        valid = [it for it in valid if it.get("is_seen", False)]
    
    if not valid:
        return []

    # attempt numeric comparison first, fall back to direct comparison
    pool = []
    i = 0
    while len(pool) < n:
        try:
            min_val = min(float(it[priority_key]) for it in valid) + i
            pool = [it for it in valid if float(it[priority_key]) <= min_val]
        except Exception:
            min_val = min(it[priority_key] for it in valid) + i
            pool = [it for it in valid if it[priority_key] <= min_val]
        i += 1

    if not pool:
        return []

    k = min(n, len(pool))

    # select up to k items ensuring unique letter_name and letter_sound
    random.shuffle(pool)
    selected: List[Dict[str, Any]] = []
    seen_names = set()
    seen_sounds = set()
    for it in pool:
        if not isinstance(it, dict):
            continue
        name = it.get("letter_name")
        sound = it.get("letter_sound")
        # skip if would duplicate a seen name or sound (only consider non-None values)
        if name is not None and name in seen_names:
            continue
        if sound is not None and sound in seen_sounds:
            continue
        selected.append(it)
        if name is not None:
            seen_names.add(name)
        if sound is not None:
            seen_sounds.add(sound)
        if len(selected) >= k:
            break

    print(f"Picked {len(selected)} items with lowest priority ({min_val}).\nItems: {selected}")
    return selected


def select_random_letters_excluding(selected: List[Dict[str, Any]], n: int,
                                    data: List[Dict[str, Any]],
                                    list_key: str = "thai_letters"
                                    ) -> List[Dict[str, Any]]:
    """
    Return n random items from data[list_key] not present in `selected`.
    Comparison prefers 'letter_char' then 'letter_name'. If n <= len(pool)
    sampling is without replacement; otherwise sampling is with replacement.
    """
    if n <= 0:
        return []
    if not isinstance(data, list):
        return []

    sel_chars = set()
    sel_names = set()
    sel_sounds = set()
    for it in selected:
        if not isinstance(it, dict):
            continue
        if "letter_char" in it and it["letter_char"] is not None:
            sel_chars.add(it["letter_char"])
        if "letter_name" in it and it["letter_name"] is not None:
            sel_names.add(it["letter_name"])
        if "letter_sound" in it and it["letter_sound"] is not None:
            sel_sounds.add(it["letter_sound"])

    pool = [lt for lt in data
            if lt.get("letter_char") not in sel_chars and lt.get("letter_name") not in sel_names and lt.get("letter_sound") not in sel_sounds]

    print(f"Confusion pool size (excluding selected): {len(pool)}")
    final_list = []

    if not pool:
        return final_list

    if n <= len(pool):
        final_list = random.sample(pool, n)
    else:
        final_list = [random.choice(pool) for _ in range(n)]

    print(f"Selected {len(final_list)} confusion items excluding selected ones.")

    return final_list


def make_mc_question(list1: List[Dict[str, Any]],
                        list2: List[Dict[str, Any]],
                        num_choices: int,
                        priority_key: str = "letter_priority") -> tuple:
    """
    Return (question_value, answers_list, correct_index).
    - truth: one random dict from list1
    - other options: num_choices-1 items sampled from list1+list2 excluding truth
    - pick two distinct keys from truth that conform to allowed patterns:
        ("letter_name","letter_char"), ("letter_char","letter_name"),
        ("letter_sound","letter_char"), ("letter_char","letter_sound")
      (i.e. "letter_name" + "letter_sound" is not allowed)
    - answers_list is shuffled; correct_index is the index of the truth answer (0-based)
    """
    if num_choices < 2:
        raise ValueError("num_choices must be >= 2")

    valid1 = [it for it in list1 if isinstance(it, dict)]
    if not valid1:
        raise ValueError("first list must contain at least one dict")

    truth = random.choice(valid1)

    pool = [it for it in (list1 + list2) if isinstance(it, dict) and it is not truth]
    print("Learning item sized pool:", len(list1))
    print("Confusion item sized pool:", len(list2))
    print("Pool size for incorrect answers:", len(pool))
    needed = num_choices - 1
    if needed > 0 and not pool:
        raise ValueError("not enough items to build choices")

    if needed <= len(pool):
        others = random.sample(pool, needed)
    else:
        others = [random.choice(pool) for _ in range(needed)]

    # allowed ordered key pairs
    allowed_pairs = [
        ("letter_name", "letter_char"),
        ("letter_char", "letter_name"),
        ("letter_sound", "letter_char"),
        ("letter_char", "letter_sound"),
    ]
    possible_pairs = [pair for pair in allowed_pairs if pair[0] in truth and pair[1] in truth]

    if not possible_pairs:
        raise ValueError("truth item must contain a valid key pair (name/char or sound/char)")

    question_key, answer_key = random.choice(possible_pairs)
    question_value = truth.get(question_key)

    answers = [truth.get(answer_key)] + [it.get(answer_key) for it in others]
    random.shuffle(answers)
    correct_index = answers.index(truth.get(answer_key))

    print("Correct answer:", truth)
    print("Incorrect answers:", others)

    return question_value, answers, correct_index
