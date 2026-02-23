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
