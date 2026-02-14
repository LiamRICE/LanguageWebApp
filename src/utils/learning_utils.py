<<<<<<< Updated upstream
import random
from typing import List, Dict, Any
import json
from src.utils.technical_utils import string_similarity


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
    
    # print("Exercise data loaded:", len(final_data), "items.")
    return final_data


def pick_lowest_priority_items(items: List[Dict[str, Any]], n: int, priority_key: str = "letter_priority", is_seen: bool = False) -> List[Dict[str, Any]]:
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
        valid = [it for it in valid if it.get("is_seen") == True]
    else:
        valid = [it for it in valid if it.get("is_seen") == False]

    # print(valid, "\n\n")
    
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

    if priority_key == "letter_priority":
        keys = ["letter_name", "letter_sound"]
    else:
        keys = ["meaning", "pronunciation"]

    # select up to k items ensuring unique letter_name and letter_sound
    random.shuffle(pool)
    selected: List[Dict[str, Any]] = []
    seen_names = set()
    seen_sounds = set()
    for it in pool:
        if not isinstance(it, dict):
            continue
        name = it.get(keys[0])
        sound = it.get(keys[1])
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

    # print(f"Picked {len(selected)} items with lowest priority ({min_val}).\nItems: {selected}")
    return selected


def select_random_letters_excluding(selected: List[Dict[str, Any]], n: int,
                                    data: List[Dict[str, Any]]
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

    # print(f"Confusion pool size (excluding selected): {len(pool)}")
    final_list = []

    if not pool:
        return final_list

    if n <= len(pool):
        final_list = random.sample(pool, n)
    else:
        final_list = [random.choice(pool) for _ in range(n)]

    # print(f"Selected {len(final_list)} confusion items excluding selected ones.")

    return final_list


def select_random_words_excluding(selected: List[Dict[str, Any]], n: int,
                                    data: List[Dict[str, Any]]
                                    ) -> List[Dict[str, Any]]:
    if n <= 0:
        return []
    if not isinstance(data, list):
        return []

    sel_words = set()
    sel_pronunciation = set()
    sel_meaning = set()
    for it in selected:
        if not isinstance(it, dict):
            continue
        if "word" in it and it["word"] is not None:
            sel_words.add(it["word"])
        if "pronunciation" in it and it["pronunciation"] is not None:
            sel_pronunciation.add(it["pronunciation"])
        if "meaning" in it and it["meaning"] is not None:
            sel_meaning.add(it["meaning"])

    pool = [lt for lt in data
            if lt.get("word") not in sel_words and lt.get("pronunciation") not in sel_pronunciation and lt.get("meaning") not in sel_meaning]

    # print(f"Confusion pool size (excluding selected): {len(pool)}")
    final_list = []

    if not pool:
        return final_list

    if n <= len(pool):
        final_list = random.sample(pool, n)
    else:
        final_list = [random.choice(pool) for _ in range(n)]

    # print(f"Selected {len(final_list)} confusion items excluding selected ones.")

    return final_list


def random_question_from_pool(is_letters:bool=True) -> str:
    letter_question_pool = ["pick_one_of_four", "type_the_result"]
    word_question_pool = ["pick_one_of_four"]
    if is_letters:
        return random.choice(letter_question_pool)
    else:
        return random.choice(word_question_pool)


def get_pick_one_of_four_question_data(list1: List[Dict[str, Any]],
                        list2: List[Dict[str, Any]],
                        num_choices: int) -> tuple:
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
    # print("Learning item sized pool:", len(list1))
    # print("Confusion item sized pool:", len(list2))
    # print("Pool size for incorrect answers:", len(pool))
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

    instruction = question_key.replace("_", " ").capitalize() + " => " + " Select the correct " + answer_key.replace("_", " ") + "."
    small_buttons = False
    if answer_key in ["letter_name"]:
        small_buttons = True

    answers = [truth.get(answer_key)] + [it.get(answer_key) for it in others]
    random.shuffle(answers)
    correct_index = answers.index(truth.get(answer_key))

    # print("Correct answer:", truth)
    # print("Incorrect answers:", others)

    return question_value, answers, correct_index, instruction, small_buttons


def pick_one_of_four_question_data_words(list1: List[Dict[str, Any]],
                        list2: List[Dict[str, Any]],
                        num_choices: int) -> tuple:
    if num_choices < 2:
        raise ValueError("num_choices must be >= 2")

    valid1 = [it for it in list1 if isinstance(it, dict)]
    if not valid1:
        raise ValueError("first list must contain at least one dict")

    truth = random.choice(valid1)

    pool = [it for it in (list1 + list2) if isinstance(it, dict) and it is not truth]
    # print("Learning item sized pool:", len(list1))
    # print("Confusion item sized pool:", len(list2))
    # print("Pool size for incorrect answers:", len(pool))
    needed = num_choices - 1
    if needed > 0 and not pool:
        raise ValueError("not enough items to build choices")

    if needed <= len(pool):
        others = random.sample(pool, needed)
    else:
        others = [random.choice(pool) for _ in range(needed)]

    # allowed ordered key pairs
    allowed_pairs = [
        ("word", "meaning"),
        ("meaning", "word"),
        ("word", "pronunciation"),
        ("pronunciation", "word"),
        ("meaning", "pronunciation"),
        ("pronunciation", "meaning")
    ]
    possible_pairs = [pair for pair in allowed_pairs if pair[0] in truth and pair[1] in truth]

    if not possible_pairs:
        raise ValueError("truth item must contain a valid key pair (name/char or sound/char)")

    question_key, answer_key = random.choice(possible_pairs)
    question_value = truth.get(question_key)

    instruction = question_key.replace("_", " ").capitalize() + " => " + " Select the correct " + answer_key.replace("_", " ") + "."
    small_buttons = True

    answers = [truth.get(answer_key)] + [it.get(answer_key) for it in others]
    random.shuffle(answers)
    correct_index = answers.index(truth.get(answer_key))

    # print("Correct answer:", truth)
    # print("Incorrect answers:", others)

    return question_value, answers, correct_index, instruction, small_buttons


def get_type_the_result_question_data(list1: List[Dict[str, Any]],
                                    priority_key: str = "letter_priority") -> tuple:
    valid1 = [it for it in list1 if isinstance(it, dict)]
    if not valid1:
        raise ValueError("first list must contain at least one dict")
    
    truth = random.choice(valid1)

    # allowed ordered key pairs
    allowed_pairs = [
        ("letter_char", "letter_name"),
        ("letter_char", "letter_sound"),
    ]
    possible_pairs = [pair for pair in allowed_pairs if pair[0] in truth and pair[1] in truth]

    if not possible_pairs:
        raise ValueError("truth item must contain a valid key pair (char => name or char => sound)")
    
    question_key, answer_key = random.choice(possible_pairs)

    instruction = "Type the correct <b>" + answer_key.replace("_", " ") + " </b>."

    question_value = truth.get(question_key)
    answer_raw_value = truth.get(answer_key)

    # process the raw answer value to improve the ease of answer typing

    return question_value, answer_raw_value, instruction


def check_text_answer_is_valid(answer:str, truth:str) -> bool:
    # remove parts of characters between parentheses
    alt_truth = truth.split(" (")[0]
    # compute similarity between the two strings
    similarity_score = string_similarity(answer, truth)
    alt_similarity_score = string_similarity(answer, alt_truth)

    similarity = max(similarity_score, alt_similarity_score)

    # print(f"Similarity between {answer} and {truth} or {alt_truth} is {similarity_score} or {alt_similarity_score}")

    if similarity >= 0.8:
        return True
    else:
        return False

=======
import json
import os
import random


GLOBAL_LETTERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'global_data', "letters.json")
USER_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data', "user_data")


def add_learned_letter(username: str,
                        letter_char: str,
                        letter_name: str,
                        letter_sound: str,
                        letter_priority: int,
                        letter_num_practiced: int,
                        letter_total_correct_answers: int,
                        letter_last_ten_answers: list) -> None:
    """
    Add a learned letter to the user's JSON data file.
    The JSON file is located at ../data/user_data/{username}.json relative to this file.
    The letter is added to the "learned_letters" list in the JSON structure.
    """
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(user_file), exist_ok=True)
    
    # Initialize user data or load existing data
    if os.path.isfile(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
        
    # Ensure "learned_letters" key exists and is a list
    if "learned_letters" not in data or not isinstance(data["learned_letters"], list):
        data["learned_letters"] = []
        
    # Create the new letter dict
    new_letter = {
        "letter_char": letter_char,
        "letter_name": letter_name,
        "letter_sound": letter_sound,
        "letter_priority": letter_priority,
        "letter_num_practiced": letter_num_practiced,
        "letter_total_correct_answers": letter_total_correct_answers,
        "letter_last_ten_answers": letter_last_ten_answers
    }
    
    # Append the new letter and save the file
    data["learned_letters"].append(new_letter)
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def add_learned_word(username: str,
                        word: str,
                        word_characters: list,
                        word_meaning: str,
                        word_priority: int,
                        word_num_practiced: int,
                        word_total_correct_answers: int,
                        word_last_ten_answers: list) -> None:
    """
    Add a learned word to the user's JSON data file.
    The JSON file is located at ../data/user_data/{username}.json relative to this file.
    The word is added to the "learned_words" list in the JSON structure.
    """
    user_file = os.path.join(USER_FOLDER, f'{username}.json')

    # Ensure the directory exists
    os.makedirs(os.path.dirname(user_file), exist_ok=True)

    # Initialize user data or load existing data
    if os.path.isfile(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Ensure "learned_words" key exists and is a list
    if "learned_words" not in data or not isinstance(data["learned_words"], list):
        data["learned_words"] = []

    # Create the new word dict
    new_word = {
        "word": word,
        "word_characters": word_characters,
        "word_meaning": word_meaning,
        "word_priority": word_priority,
        "word_num_practiced": word_num_practiced,
        "word_total_correct_answers": word_total_correct_answers,
        "word_last_ten_answers": word_last_ten_answers
    }

    # Append the new word and save the file
    data["learned_words"].append(new_word)
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def update_letter_priority(username: str, letter_name: str, action: str) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_letters" not in data or not isinstance(data["learned_letters"], list):
        return False
    for letter in data["learned_letters"]:
        if letter.get("letter_name") == letter_name:
            if action == "increase":
                letter["letter_priority"] += 1
            elif action == "decrease":
                letter["letter_priority"] -= 1
            else:
                return False
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def update_letter_num_practiced(username: str, letter_name: str) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_letters" not in data or not isinstance(data["learned_letters"], list):
        return False
    for letter in data["learned_letters"]:
        if letter.get("letter_name") == letter_name:
            letter["letter_num_practiced"] += 1
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def update_letter_total_and_answers(username: str, letter_name: str, correct: bool) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_letters" not in data or not isinstance(data["learned_letters"], list):
        return False
    for letter in data["learned_letters"]:
        if letter.get("letter_name") == letter_name:
            if correct:
                letter["letter_total_correct_answers"] += 1
            if not isinstance(letter.get("letter_last_ten_answers"), list):
                letter["letter_last_ten_answers"] = []
            letter["letter_last_ten_answers"].append(correct)
            if len(letter["letter_last_ten_answers"]) > 10:
                letter["letter_last_ten_answers"] = letter["letter_last_ten_answers"][-10:]
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def update_word_priority(username: str, word: str, action: str) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_words" not in data or not isinstance(data["learned_words"], list):
        return False
    for learned_word in data["learned_words"]:
        if learned_word.get("word") == word:
            if action == "increase":
                learned_word["word_priority"] += 1
            elif action == "decrease":
                learned_word["word_priority"] -= 1
            else:
                return False
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def update_word_num_practiced(username: str, word: str) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_words" not in data or not isinstance(data["learned_words"], list):
        return False
    for learned_word in data["learned_words"]:
        if learned_word.get("word") == word:
            learned_word["word_num_practiced"] += 1
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def update_word_total_and_answers(username: str, word: str, correct: bool) -> bool:
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return False
    with open(user_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False
    if "learned_words" not in data or not isinstance(data["learned_words"], list):
        return False
    for learned_word in data["learned_words"]:
        if learned_word.get("word") == word:
            if correct:
                learned_word["word_total_correct_answers"] += 1
            if not isinstance(learned_word.get("word_last_ten_answers"), list):
                learned_word["word_last_ten_answers"] = []
            learned_word["word_last_ten_answers"].append(correct)
            if len(learned_word["word_last_ten_answers"]) > 10:
                learned_word["word_last_ten_answers"] = learned_word["word_last_ten_answers"][-10:]
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
    return False


def pull_random_global_letters(username: str) -> list:
    """
    Pull one letter from the global letters that is not among the user's learned letters using the highest priority,
    along with 4 additional letters that don't share the same character, name, or sound as the first.
    Returns a list (first letter is the highest priority selection).
    """
    # Load the global letters data
    try:
        with open(GLOBAL_LETTERS_FILE, 'r', encoding='utf-8') as f:
            global_letters = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Get letters the user has already learned (compare by letter_name)
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    learned_names = set()
    if os.path.isfile(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            try:
                user_data = json.load(f)
                learned_letters = user_data.get("learned_letters", [])
                for letter in learned_letters:
                    learned_names.add(letter.get("letter_name"))
            except json.JSONDecodeError:
                pass

    # Filter global letters not yet learned
    available = [letter for letter in global_letters if letter.get("letter_name") not in learned_names]
    if not available:
        return []

    # Find candidate letters with the highest priority (lowest int value)
    min_priority = min(letter.get("letter_priority", float('inf')) for letter in available)
    highest_candidates = [letter for letter in available if letter.get("letter_priority") == min_priority]
    primary = random.choice(highest_candidates)

    # For additional letters, filter out those sharing letter_char, letter_name, or letter_sound with primary letter
    def is_distinct(letter):
        return (letter.get("letter_char") != primary.get("letter_char") and
                letter.get("letter_name") != primary.get("letter_name") and
                letter.get("letter_sound") != primary.get("letter_sound"))
    additional_pool = [letter for letter in available if is_distinct(letter)]
    # Remove primary from the additional pool if present
    additional_pool = [letter for letter in additional_pool if letter != primary]

    additional = random.sample(additional_pool, k=min(4, len(additional_pool)))
    return [primary] + additional


def pull_random_learned_letters(username: str) -> list:
    """
    Pull one letter from the user's learned letters with the highest priority,
    along with 4 additional learned letters that don't share the same character, name, or sound as the first.
    Returns a list (first letter is the highest priority selection).
    """
    user_file = os.path.join(USER_FOLDER, f'{username}.json')
    if not os.path.isfile(user_file):
        return []
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    except json.JSONDecodeError:
        return []

    learned_letters = user_data.get("learned_letters")
    if not learned_letters or not isinstance(learned_letters, list):
        return []

    # Determine the letters with the highest priority (lowest int value)
    min_priority = min(letter.get("letter_priority", float('inf')) for letter in learned_letters)
    highest_candidates = [letter for letter in learned_letters if letter.get("letter_priority") == min_priority]
    primary = random.choice(highest_candidates)

    # For additional letters, exclude any that share letter_char, letter_name, or letter_sound with primary
    def is_distinct(letter):
        return (letter.get("letter_char") != primary.get("letter_char") and
                letter.get("letter_name") != primary.get("letter_name") and
                letter.get("letter_sound") != primary.get("letter_sound"))

    additional_pool = [letter for letter in learned_letters if is_distinct(letter) and letter != primary]
    additional = random.sample(additional_pool, k=min(4, len(additional_pool)))
    return [primary] + additional
>>>>>>> Stashed changes
