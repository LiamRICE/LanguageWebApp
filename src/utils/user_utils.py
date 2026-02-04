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


def add_user_settings(username:str, settings: dict) -> bool:
    """
    Adds or updates the user's settings in their JSON file.
    Returns True if the settings were saved successfully, False otherwise.
    """
    user_data = read_user_json(username)
    user_data['settings'] = settings
    return save_user_json(username, user_data)
