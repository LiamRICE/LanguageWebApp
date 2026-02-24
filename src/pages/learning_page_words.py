from dash import html, dcc, callback, Input, Output, State
from src.modules.question_modules.pick_one_of_four_words import create_pick_one_of_four
from src.modules.question_modules.type_the_result_words import create_type_the_result
from src.utils.learning_utils import pick_lowest_priority_items, select_random_words_excluding, pick_one_of_four_question_data_words, random_question_from_pool, get_type_the_result_question_data, last_20_percentage
from src.utils.user_utils import words_can_learn, add_user_statistics, get_global_learning_statistics, read_user_json, save_user_json


def learning_page(user_info, learned_language: str = "thai", num_questions: int = 20, is_letters:bool=False, is_practice: bool = False):

    user_data = read_user_json(username=user_info.get("username"))
    n = user_data.get("settings", {}).get("letters_per_session", 3)

    priority_key = "priority"
    if is_practice:
        priority_key = "times_learned"

    thai_data = words_can_learn(user_info.get("username"))
    question_items = pick_lowest_priority_items(thai_data, n=n, priority_key=priority_key, is_seen=is_practice)
    confusion_items = select_random_words_excluding(question_items, n=10, data=thai_data)

    next_button = html.Button(
        "Next Question",
        id="next-question-button-words",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px"},
        disabled=True
    )
    finish_button = html.Button(
        "Finish Quiz",
        id="finish-button-words",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px", "display": "none"},
    )

    # TODO - 21/20 correct? Does not count this, the first, loaded question.
    question_container, question_header, _, _, _ = load_question_word("", None, question_items, confusion_items, 1, num_questions, 0)

    return html.Div([
        html.H2(question_header, id="current-question-header-words", className="text-center my-4"),
        html.Div(id="question-container-words", children=question_container),
        next_button,
        finish_button,
        # Stores to keep track of state
        dcc.Store(id="question-items-store-words", data=question_items),
        dcc.Store(id="confusion-items-store-words", data=confusion_items),
        dcc.Store(id="current-question-index-words", data=1),
        dcc.Store(id="num-questions-correct-words", data=0),
        dcc.Store(id="total-questions", data=num_questions),
        dcc.Store(id="user-learning-info", data=user_data),
        dcc.Store(id="is-practice", data=is_practice),
        dcc.Store(id="username-store", data=user_info.get("username")),
    ])


@callback(
    Output("question-container-words", "children", allow_duplicate=True),
    Output("current-question-header-words", "children", allow_duplicate=True),
    Output("current-question-index-words", "data", allow_duplicate=True),
    Output("next-question-button-words", "style", allow_duplicate=True),
    Output("finish-button-words", "style", allow_duplicate=True),
    Input("current-question-header-words", "children"),
    Input("next-question-button-words", "n_clicks"),
    State("question-items-store-words", "data"),
    State("confusion-items-store-words", "data"),
    State("current-question-index-words", "data"),
    State("total-questions", "data"),
    State("num-questions-correct-words", "data"),
    prevent_initial_call=True
)
def load_question_word(header_text, next_clicks, question_items, confusion_items, current_question_index, total_questions, num_correct):
    header_text = f"Question {current_question_index}/{total_questions}"
    visible_style = {"marginTop": "12px", "width": "100%", "padding": "10px 12px", "display": "block"}
    hidden_style = {"display": "none"}

    min_learned = -1
    for word in question_items:
        if min_learned == -1 or word.get("times_learned", -1) < min_learned:
            min_learned = word.get("times_learned", -1)

    if current_question_index > total_questions:
        return html.Div(f"Quiz Complete with {num_correct}/{total_questions} correct!"), "Finished!", current_question_index, hidden_style, visible_style
    else:
        if min_learned >= 20:
            question_type = random_question_from_pool(is_letters=False)
        else:
            question_type = "pick_one_of_four"
        # question_type = "type_the_result" # temporary, for testing
        # question_type = "pick_one_of_four" # temporary, for testing

        if question_type == "pick_one_of_four":
            value, answers, correct_id, instruction, small_buttons = pick_one_of_four_question_data_words(question_items, confusion_items, num_choices=4)

            return create_pick_one_of_four(
                question=value,
                options=answers,
                correct_id=correct_id+1,
                instruction=instruction,
                small_buttons=small_buttons,
                is_letters=False
            ), header_text, current_question_index+1, visible_style, hidden_style
        
        elif question_type == "type_the_result":
            question, correct_answer, instruction = get_type_the_result_question_data(question_items)
            
            return create_type_the_result(
                question=question,
                correct_answer=correct_answer,
                instruction=instruction,
                is_letters=False
            ), header_text, current_question_index+1, visible_style, hidden_style


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("finish-button-words", "n_clicks"),
    State("num-questions-correct-words", "data"),
    State("total-questions", "data"),
    State("question-items-store-words", "data"),
    State("username-store", "data"),
    State("is-practice", "data"),
    prevent_initial_call=True
)
def go_to_learn_thai_word(n_clicks, num_correct, total_questions, question_items, username, is_practice):
    # read user info from file
    user_learning_info = read_user_json(username=username)
    # words that are practiced are marked as seen
    question_names = {item.get("word") for item in question_items}
    if is_practice:
        for word in user_learning_info.get("thai_words", []):
            if word.get("word") in question_names:
                if last_20_percentage(word) >= 0.95:
                    # words that are practiced and answered 100% correctly have their priority decreased
                    word["priority"] = max(0, word.get("priority", 0) + 1)
    else:
        for word in user_learning_info.get("thai_words", []):
            if word.get("word") in question_names:
                word["is_seen"] = True
                if last_20_percentage(word) >= 0.95:
                    # words that are practiced and answered 100% correctly have their priority decreased
                    word["priority"] = max(0, word.get("priority", 0) + 1)
    
    # write user info back to file
    save_user_json(username=username, user_data=user_learning_info)

    # update user statistics
    user_statistics = get_global_learning_statistics("liam")
    user_statistics["total_sessions"] = user_statistics.get("total_sessions", 0) + 1
    add_user_statistics("liam", user_statistics)

    return "/learn-thai"