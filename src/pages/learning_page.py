from enum import Enum
from src.pages.exercises.multiple_select_exercise import multiple_select_exercise_letter, multiple_select_exercise_word
import random

class LearningMode(Enum):
    LETTERS_NEW = 0
    WORDS_NEW = 1
    LETTERS_PRACTICE = 2
    WORDS_PRACTICE = 3
    SENTENCES_PRACTICE = 4


def learning_page(mode: LearningMode):
    exercises_letter = [multiple_select_exercise_letter]
    exercises_word = [multiple_select_exercise_word]
    
    if mode in [LearningMode.LETTERS_NEW, LearningMode.LETTERS_PRACTICE]:
        selected_exercise = random.choice(exercises_letter)
    elif mode in [LearningMode.WORDS_NEW, LearningMode.WORDS_PRACTICE]:
        selected_exercise = random.choice(exercises_word)
    elif mode == LearningMode.SENTENCES_PRACTICE:
        selected_exercise = lambda: "Sentence exercise is not implemented yet."  # Fallback for sentences
    else:
        selected_exercise = lambda: "Invalid learning mode."

    # Render the selected exercise on the screen
    # Assuming the exercise function returns HTML or appropriate content.
    return selected_exercise()
