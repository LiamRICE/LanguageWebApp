import os
import json

import firebase_admin
from firebase_admin import credentials, firestore


# Path to the default Thai language data template.
# This is static reference data (not per-user output), so it's still read from disk
# and copied into each new user's Firestore document on creation.
DEFAULT_USER_DATA_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'language_data', 'thai_data', 'thai.json'
)

# Initialise Firebase. Guarded so re-importing this module doesn't raise
# "The default Firebase app already exists" errors.
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/liamslanguagelearningappdb-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Firestore collections:
#   CREDENTIALS_COLLECTION: username -> {"password": ...}
#   USER_DATA_COLLECTION:   username -> {"thai_letters": [...], "thai_words": [...],
#                                          "settings": {...}, "statistics": {...}}
# Kept separate (rather than one merged document) so learning-data reads never
# carry the password field along with them.
CREDENTIALS_COLLECTION = "credentials"
USER_DATA_COLLECTION = "user_data"

print("Database connected:", db)


def create_user(username: str, password: str) -> bool:
    """
    Create a new username-password pair if it does not exist.
    Returns True if the new user is created, False if the username already exists.
    """
    if user_exists(username):
        return False

    # Store the credential
    db.collection(CREDENTIALS_COLLECTION).document(username).set({"password": password})

    # Copy the default Thai language data into a new Firestore document for this user
    try:
        with open(DEFAULT_USER_DATA_FILE, 'r', encoding='utf-8') as src_file:
            data = json.load(src_file)
        db.collection(USER_DATA_COLLECTION).document(username).set(data)
    except (json.JSONDecodeError, OSError):
        pass  # If copying fails, we still created the credential

    return True


def check_user(username: str, password: str) -> bool:
    """
    Check if the username-password pair exists.
    Returns True if a matching pair is found, False otherwise.
    """
    doc = db.collection(CREDENTIALS_COLLECTION).document(username).get()
    if not doc.exists:
        return False
    return doc.to_dict().get("password") == password


def user_exists(username: str) -> bool:
    """
    Helper function to check if a username exists.
    Returns True if the username is found, False otherwise.
    """
    doc = db.collection(CREDENTIALS_COLLECTION).document(username).get()
    return doc.exists


def read_user_json(username: str) -> dict:
    """
    Read the Firestore document for the given username and return its contents as a dict.
    Returns an empty dict if the document does not exist or cannot be read.
    """
    doc = db.collection(USER_DATA_COLLECTION).document(username).get()
    if not doc.exists:
        return {}
    return doc.to_dict() or {}


def save_user_json(username: str, user_data: dict) -> bool:
    """
    Save the given user_data dict to Firestore for the given username.
    Returns True if the data was saved successfully, False otherwise.
    """
    try:
        db.collection(USER_DATA_COLLECTION).document(username).set(user_data)
        return True
    except Exception:
        return False


def get_num_learned_letters(username: str) -> int:
    """
    Reads the user's Firestore document and returns the number of Thai letters marked as learned.
    Returns 0 if the document does not exist or cannot be read.
    """
    user_data = read_user_json(username)
    thai_letters = user_data.get("thai_letters", [])
    if not isinstance(thai_letters, list):
        return 0
    learned_count = sum(1 for letter in thai_letters if letter.get("is_seen") == True)
    return learned_count


def get_num_learned_words(username: str) -> int:
    """
    Reads the user's Firestore document and returns the number of Thai words marked as learned.
    Returns 0 if the document does not exist or cannot be read.
    """
    user_data = read_user_json(username)
    thai_words = user_data.get("thai_words", [])
    if not isinstance(thai_words, list):
        return 0
    learned_count = sum(1 for word in thai_words if word.get("is_seen") == True)
    return learned_count


def add_user_settings(username: str, settings: dict) -> bool:
    """
    Adds or updates the user's settings in their Firestore document.
    Returns True if the settings were saved successfully, False otherwise.
    """
    user_data = read_user_json(username)
    user_data['settings'] = settings
    return save_user_json(username, user_data)


def get_global_learning_statistics(username: str) -> dict:
    """
    Reads the user's Firestore document and returns their learning statistics.
    Returns an empty dict if the document does not exist or cannot be read.
    """
    user_data = read_user_json(username)
    print("Fetching global user statistics for user", username, user_data.get("statistics", {}))
    return user_data.get("statistics", {})


def get_thai_letters_learning_statistics(username: str) -> dict:
    """
    Reads the user's Firestore document and returns their Thai letters learning statistics.
    Returns an empty dict if the document does not exist or cannot be read.
    """
    learning_info = read_user_json(username)
    thai_letters = learning_info.get("thai_letters", [])
    total_letters = len(thai_letters)
    learned_letters = sum(1 for letter in thai_letters if letter.get("is_seen") == True)

    return {
        "total_letters": total_letters,
        "learned_letters": learned_letters
    }


def get_thai_words_learning_statistics(username: str) -> dict:
    """
    Reads the user's Firestore document and returns their Thai words learning statistics.
    Returns an empty dict if the document does not exist or cannot be read.
    """
    learning_info = read_user_json(username)
    thai_words = learning_info.get("thai_words", [])
    total_words = len(thai_words)
    learned_words = sum(1 for word in thai_words if word.get("is_seen") == True)

    return {
        "total_words": total_words,
        "learned_words": learned_words
    }


def add_user_statistics(username: str, statistics: dict) -> bool:
    """
    Adds or updates the user's learning statistics in their Firestore document.
    Returns True if the statistics were saved successfully, False otherwise.
    """
    print("Writing global user statistics for user", username, statistics)
    user_data = read_user_json(username)
    user_data['statistics'] = statistics
    return save_user_json(username, user_data)


def update_user_information_letter(username: str, letter_to_update: str, result: bool) -> bool:
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


def update_user_information_word(username: str, word_to_update: str, result: bool) -> bool:
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


def words_can_learn(username: str) -> list:
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
            final_words.append(word)

    return final_words
