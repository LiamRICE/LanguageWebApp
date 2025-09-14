import csv
import os
import json

# Define the CSV file path relative to this file
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data', 'secure.csv')
USER_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data', "user_data")


def create_user(username: str, password: str) -> bool:
    """
    Create a new username-password pair if it does not exist.
    Returns True if the new user is created, False if the username already exists.
    """
    if user_exists(username):
        return False

    # Ensure the directory for the CSV file exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # If file doesn't exist, create it and optionally add a header
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['username', 'password'])
        writer.writerow([username, password])
    return True


def check_user(username: str, password: str) -> bool:
    """
    Check if the username-password pair exists in the CSV file.
    Returns True if a matching pair is found, False otherwise.
    """
    if not os.path.isfile(DATA_FILE):
        return False

    with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return True
    return False


def user_exists(username: str) -> bool:
    """
    Helper function to check if a username exists in the CSV file.
    Returns True if the username is found, False otherwise.
    """
    if not os.path.isfile(DATA_FILE):
        return False

    with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                return True
    return False


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
