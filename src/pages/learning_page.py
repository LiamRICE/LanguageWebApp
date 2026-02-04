from dash import html, dcc, callback, Input, Output, State
from src.modules.question_modules.pick_one_of_four import create_pick_one_of_four
from src.utils.learning_utils import load_thai_json_as_list, pick_lowest_priority_items, select_random_letters_excluding, make_mc_question
from src.utils.user_utils import add_user_statistics, get_global_learning_statistics, read_user_json, save_user_json


def learning_page(user_info, learned_language: str = "thai", num_questions: int = 20, is_letters:bool=True, is_practice: bool = False):

    user_data = read_user_json(username=user_info.get("username"))
    n = user_data.get("settings", {}).get("letters_per_session", 3)

    priority_key = "letter_priority"
    if is_practice:
        priority_key = "times_learned"

    thai_data = load_thai_json_as_list(user_info.get("username"), is_letters=is_letters)
    question_items = pick_lowest_priority_items(thai_data, n=n, priority_key=priority_key, is_seen=is_practice)
    if is_letters:
        confusion_items = select_random_letters_excluding(question_items, n=10, data=thai_data)
    else:
        pass # select items from words data instead

    next_button = html.Button(
        "Next Question",
        id="next-question-button",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px"},
        disabled=True
    )
    finish_button = html.Button(
        "Finish Quiz",
        id="finish-button",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px", "display": "none"},
    )

    return html.Div([
        html.H2(f"Question 1/{num_questions}", id="current-question-header", className="text-center my-4"),
        html.Div(id="question-container", children=[]),
        next_button,
        finish_button,
        # Stores to keep track of state
        dcc.Store(id="question-items-store", data=question_items),
        dcc.Store(id="confusion-items-store", data=confusion_items),
        dcc.Store(id="current-question-index", data=1),
        dcc.Store(id="num-questions-correct", data=0),
        dcc.Store(id="total-questions", data=num_questions),
        dcc.Store(id="user-learning-info", data=user_data),
        dcc.Store(id="is-practice", data=is_practice),
        dcc.Store(id="username-store", data=user_info.get("username")),
    ])


@callback(
    Output("question-container", "children"),
    Output("current-question-header", "children"),
    Output("current-question-index", "data"),
    Output("next-question-button", "style"),
    Output("finish-button", "style"),
    Input("current-question-header", "children"),
    Input("next-question-button", "n_clicks"),
    State("question-items-store", "data"),
    State("confusion-items-store", "data"),
    State("current-question-index", "data"),
    State("total-questions", "data"),
    State("num-questions-correct", "data")
)
def load_question(header_text, next_clicks, question_items, confusion_items, current_question_index, total_questions, num_correct):
    header_text = f"Question {current_question_index}/{total_questions}"
    visible_style = {"marginTop": "12px", "width": "100%", "padding": "10px 12px", "display": "block"}
    hidden_style = {"display": "none"}

    if current_question_index > total_questions:
        return html.Div(f"Quiz Complete with {num_correct}/{total_questions} correct!"), "Finished!", current_question_index, hidden_style, visible_style
    else:
        print("Updating question values:")
        value, answers, correct_id, instruction = make_mc_question(
            question_items,
            confusion_items,
            num_choices=4
        )

        return create_pick_one_of_four(
            question=value,
            options=answers,
            correct_id=correct_id+1,
            instruction=instruction
        ), header_text, current_question_index+1, visible_style, hidden_style


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("finish-button", "n_clicks"),
    State("num-questions-correct", "data"),
    State("total-questions", "data"),
    State("question-items-store", "data"),
    State("username-store", "data"),
    State("is-practice", "data"),
    prevent_initial_call=True
)
def go_to_learn_thai(n_clicks, num_correct, total_questions, question_items, username, is_practice):
    # read user info from file
    user_learning_info = read_user_json(username=username)
    # letters that are practiced are marked as seen
    question_names = {item.get("letter_char") for item in question_items}
    if is_practice:
        for letter in user_learning_info.get("thai_letters", []):
            if letter.get("letter_char") in question_names:
                if num_correct / total_questions >= 0.95:
                    # letters that are practiced and answered 100% correctly have their priority decreased
                    letter["letter_priority"] = max(0, letter.get("letter_priority", 0) + 1)
    else:
        for letter in user_learning_info.get("thai_letters", []):
            if letter.get("letter_char") in question_names:
                letter["is_seen"] = True
                if num_correct / total_questions >= 0.95:
                    # letters that are practiced and answered 100% correctly have their priority decreased
                    letter["letter_priority"] = max(0, letter.get("letter_priority", 0) + 1)
    
    # write user info back to file
    save_user_json(username=username, user_data=user_learning_info)

    # update user statistics
    user_statistics = get_global_learning_statistics("liam")
    user_statistics["total_sessions"] = user_statistics.get("total_sessions", 0) + 1
    add_user_statistics("liam", user_statistics)

    return "/learn-thai"