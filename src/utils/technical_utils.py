import unicodedata

def normalize_string(s: str, ipa_map: dict) -> str:
    """
    Normalize a string by:
    - Unicode normalization
    - Replacing IPA sequences with plain-text equivalents
    - Lowercasing
    """
    # Normalize Unicode (important for IPA combining characters)
    s = unicodedata.normalize("NFKD", s)

    # Apply IPA → text mappings (longest first to avoid partial matches)
    for ipa, plain in sorted(ipa_map.items(), key=lambda x: -len(x[0])):
        s = s.replace(ipa, plain)

    return s.lower()


def levenshtein_distance(a: str, b: str) -> int:
    """Classic Levenshtein distance (edit distance)."""
    if len(a) < len(b):
        a, b = b, a

    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current_row = [i]
        for j, cb in enumerate(b, 1):
            insert = previous_row[j] + 1
            delete = current_row[j - 1] + 1
            replace = previous_row[j - 1] + (ca != cb)
            current_row.append(min(insert, delete, replace))
        previous_row = current_row

    return previous_row[-1]


def string_similarity(a: str, b: str) -> float:
    """
    Returns a similarity score between 0 and 1.
    """
    ipa_equivalents = {
        "t͡ɕʰ": "ch",
        "t͡ɕ": "ch",
        "ɕ": "sh",
        "ʃ": "sh",
        "ʰ": "",     # aspiration marker
        "ŋ": "ng",
        "ɲ": "ny",
        "ʔ": "",
        "ː":":"
        # add more as needed
    }

    a_norm = normalize_string(a, ipa_equivalents)
    b_norm = normalize_string(b, ipa_equivalents)

    if a_norm == "chh":
        a_norm = "ch"
    if b_norm == "chh":
        b_norm = "ch"

    print(f"Normalised a = {a_norm}\nNormalised b = {b_norm}")

    if not a_norm and not b_norm:
        return 1.0

    distance = levenshtein_distance(a_norm, b_norm)
    max_len = max(len(a_norm), len(b_norm))

    return 1.0 - (distance / max_len)
