"""
One-time migration script: pushes existing local data (secure.csv +
data/user_data/user_data/*.json) into Firestore, using the new collection
layout from the updated user_utils.py (credentials / user_data).

Run this ONCE after deploying the new user_utils.py, before removing the old
local data files. Safe to re-run: it uses .set() so re-running just overwrites
with the same data, but it does NOT skip users already migrated, so avoid
running it after new signups have already started hitting Firestore only,
or you could clobber newer data with the old local copy.

Usage:
    python migrate_to_firestore.py
"""

import os
import csv
import json

import firebase_admin
from firebase_admin import credentials, firestore

# Original local paths, matching the pre-migration user_utils.py
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data', 'secure.csv')
USER_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_data', "user_data")

CREDENTIALS_COLLECTION = "credentials"
USER_DATA_COLLECTION = "user_data"


def migrate():
    if not firebase_admin._apps:
        cred = credentials.Certificate("src/data/liamslanguagelearningappdb-firebase.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    migrated_credentials = 0
    migrated_data = 0
    skipped = 0

    # 1. Migrate credentials from secure.csv
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row.get('username')
                password = row.get('password')
                if not username:
                    continue
                db.collection(CREDENTIALS_COLLECTION).document(username).set({"password": password})
                migrated_credentials += 1
    else:
        print(f"No secure.csv found at {DATA_FILE}, skipping credential migration.")

    # 2. Migrate each user's learning-data JSON file
    if os.path.isdir(USER_FOLDER):
        for filename in os.listdir(USER_FOLDER):
            if not filename.endswith('.json'):
                continue
            username = filename[:-len('.json')]
            filepath = os.path.join(USER_FOLDER, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Skipping {filename}: could not read/parse ({e})")
                skipped += 1
                continue
            db.collection(USER_DATA_COLLECTION).document(username).set(data)
            migrated_data += 1
    else:
        print(f"No user_data folder found at {USER_FOLDER}, skipping data migration.")

    print(f"Done. Migrated {migrated_credentials} credentials, {migrated_data} user data documents, skipped {skipped}.")


if __name__ == "__main__":
    migrate()
