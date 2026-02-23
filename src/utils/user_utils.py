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
    
    # copy the data from the thai.json file and create a new user json file
    default_user_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'language_data', 'thai_data', 'thai.json')
    new_user_data_path = os.path.join(USER_FOLDER, f"{username}.json")
    os.makedirs(USER_FOLDER, exist_ok=True)
    try:
        with open(default_user_data_path, 'r', encoding='utf-8') as src_file:
            data = json.load(src_file)
        with open(new_user_data_path, 'w', encoding='utf-8') as dest_file:
            json.dump(data, dest_file, ensure_ascii=False, indent=4)
    except (json.JSONDecodeError, OSError):
        pass  # If copying fails, we still created the user in CSV
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


def read_user_json(username: str) -> dict:
    """
    Read the JSON file for the given username from USER_FOLDER and return its contents as a dict.
    Returns an empty dict if the file does not exist or cannot be read/parsed.
    """
    filepath = os.path.join(USER_FOLDER, f"{username}.json")
    if not os.path.isfile(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_user_json(username: str, user_data: dict) -> bool:
    """
    Save the given user_data dict to a JSON file for the given username in USER_FOLDER.
    Returns True if the data was saved successfully, False otherwise.
    """
    filepath = os.path.join(USER_FOLDER, f"{username}.json")
    os.makedirs(USER_FOLDER, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        return True
    except OSError:
        return False


def get_num_learned_letters(username:str) -> int:
    """
    Reads the user's JSON file and returns the number of Thai letters marked as learned.
    Returns 0 if the file does not exist or cannot be read/parsed.
    """
    user_data = read_user_json(username)
    thai_letters = user_data.get("thai_letters", [])
    if not isinstance(thai_letters, list):
        return 0
    learned_count = sum(1 for letter in thai_letters if letter.get("is_seen") == True)
    return learned_count


def get_num_learned_words(username:str) -> int:
    """
    Reads the user's JSON file and returns the number of Thai letters marked as learned.
    Returns 0 if the file does not exist or cannot be read/parsed.
    """
    user_data = read_user_json(username)
    thai_words = user_data.get("thai_words", [])
    if not isinstance(thai_words, list):
        return 0
    learned_count = sum(1 for word in thai_words if word.get("is_seen") == True)
    return learned_count


def add_user_settings(username:str, settings: dict) -> bool:
    """
    Adds or updates the user's settings in their JSON file.
    Returns True if the settings were saved successfully, False otherwise.
    """
    user_data = read_user_json(username)
    user_data['settings'] = settings
    return save_user_json(username, user_data)


def get_global_learning_statistics(username:str) -> dict:
    """
    Reads the user's JSON file and returns their learning statistics.
    Returns an empty dict if the file does not exist or cannot be read/parsed.
    """
    user_data = read_user_json(username)
    return user_data.get("statistics", {})


def get_thai_letters_learning_statistics(username:str) -> dict:
    """
    Reads the user's JSON file and returns their Thai letters learning statistics.
    Returns an empty dict if the file does not exist or cannot be read/parsed.
    """
    learning_info = read_user_json(username)
    thai_letters = learning_info.get("thai_letters", [])
    total_letters = len(thai_letters)
    learned_letters = sum(1 for letter in thai_letters if letter.get("is_seen") == True)

    return {
        "total_letters": total_letters,
        "learned_letters": learned_letters
    }


def add_user_statistics(username:str, statistics: dict) -> bool:
    """
    Adds or updates the user's learning statistics in their JSON file.
    Returns True if the statistics were saved successfully, False otherwise.
    """
    user_data = read_user_json(username)
    user_data['statistics'] = statistics
    return save_user_json(username, user_data)


def update_user_information_letter(username:str, letter_to_update:str, result:bool) -> bool:
    # update stats
    user_data = read_user_json(username)
    letters = user_data.get("thai_letters", [])

    question_letter = None
    for letter in letters:
        if letter.get("letter_char") == letter_to_update or letter.get("letter_name") == letter_to_update or letter.get("letter_sound") == letter_to_update:
            question_letter = letter
            break
    if question_letter is not None:
        question_letter["times_learned"] = question_letter.get("times_learned", 0) + 1
        if result:
            question_letter["times_correct"] = question_letter.get("times_correct", 0) + 1
        # update last_20_answers
        last_20 = question_letter.get("last_20_answers", [])
        last_20.append(result)
        if len(last_20) > 20:
            last_20 = last_20[-20:]
        question_letter["last_20_answers"] = last_20
    else:
        return False
    
    user_data["thai_letters"] = letters
    saved = save_user_json(username, user_data)

    # update global user statistics
    user_statistics = get_global_learning_statistics(username)
    user_statistics["total_questions"] = user_statistics.get("total_questions", 0) + 1
    user_statistics["total_correct"] = user_statistics.get("total_correct", 0) + (1 if result else 0)
    add_user_statistics(username, user_statistics)

    return True


def update_user_information_word(username:str, word_to_update:str, result:bool) -> bool:
    # update stats
    user_data = read_user_json(username)
    words = user_data.get("thai_words", [])

    question_word = None
    for word in words:
        if word.get("word") == word_to_update or word.get("meaning") == word_to_update or word.get("pronunciation") == word_to_update:
            question_word = word
            break
    if question_word is not None:
        question_word["times_learned"] = question_word.get("times_learned", 0) + 1
        if result:
            question_word["times_correct"] = question_word.get("times_correct", 0) + 1
        # update last_20_answers
        last_20 = question_word.get("last_20_answers", [])
        last_20.append(result)
        if len(last_20) > 20:
            last_20 = last_20[-20:]
        question_word["last_20_answers"] = last_20
    else:
        return False
    
    user_data["thai_words"] = words
    saved = save_user_json(username, user_data)

    # update global user statistics
    user_statistics = get_global_learning_statistics(username)
    user_statistics["total_questions"] = user_statistics.get("total_questions", 0) + 1
    user_statistics["total_correct"] = user_statistics.get("total_correct", 0) + (1 if result else 0)
    add_user_statistics(username, user_statistics)

    return True


def words_can_learn(username:str) -> list:
    user_data = read_user_json(username)

    user_letters = user_data.get("thai_letters", [])
    user_words = user_data.get("thai_words", [])

    learned_letters = [let.get("letter_char") for let in user_letters if let.get("is_seen", False) == True]

    final_words = []
    for word in user_words:
        know_all_letters = True
        for let in word.get("spelling"):
            if let not in learned_letters:
                know_all_letters = False
        if know_all_letters:
            final_words.add(word)
    
    return final_words
