from typing import List
from dash import html, dcc
from dash import Input, Output, State, callback, callback_context
from dash import html, no_update
from src.utils.user_utils import read_user_json, save_user_json, get_global_learning_statistics, add_user_statistics
from src.utils.learning_utils import check_text_answer_is_valid


def create_type_the_result(question: str, correct_answer: str, instruction:str, prefix: str = "learning-page-question") -> html.Div:
    """
    Create a Dash component for a "type the result" question.

    - question: question text to display
    - correct_answer: the expected answer string (case-insensitive)
    - instruction: additional instructions to display below the question
    - prefix: id prefix to avoid collisions (input will be f"{prefix}-input", validate button will be f"{prefix}-validate")
    """
    input_style = {
        "width": "100%",
        "padding": "10px 12px",
        "fontSize": "24px",
        "textAlign": "center"
    }

    # Input field for user's answer
    answer_input = dcc.Input(
        id=f"{prefix}-input",
        type="text",
        placeholder="Type your answer here",
        value="",
        style=input_style,
        debounce=True  # Trigger change on blur or enter, not every keystroke
    )

    # Store the correct answer and user's current input
    truth_store = dcc.Store(id=f"{prefix}-truth", data=correct_answer.lower())
    user_input_store = dcc.Store(id=f"{prefix}-user-input", data="")
    question_store = dcc.Store(id="letter-in-question", data=question)
    # username_store = dcc.Store(id="username-store")

    # Validate button to trigger checking the answer; result_div can show feedback.
    validate_button = html.Button(
        "Validate",
        id=f"{prefix}-complete-let-validate",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px"}
    )
    result_div = html.Div(id=f"{prefix}-result", style={"marginTop": "8px", "minHeight": "24px"})

    return html.Div([
        html.Div(question, style={"fontSize": "24px", "fontWeight": "bold"}),
        html.Div(instruction, style={"fontSize": "14px", "color": "#555", "marginBottom": "8px"}),
        answer_input,
        validate_button,
        result_div,
        truth_store,
        user_input_store,
        question_store,
    ])


@callback(
    Output("learning-page-question-complete-let-validate", "style", allow_duplicate=True),
    Output("next-question-button", "disabled", allow_duplicate=True),
    Output("num-questions-correct", "data", allow_duplicate=True),
    Output("learning-page-question-complete-let-validate", "style"),
    Output("learning-page-question-result", "children"),
    Input("learning-page-question-complete-let-validate", "n_clicks"),
    State("learning-page-question-input", "value"),
    State("learning-page-question-truth", "data"),
    State("num-questions-correct", "data"),
    State("letter-in-question", "data"),
    State("username-store", "data"),
    prevent_initial_call=True
)
def _check_result(n_clicks, user_input, ground_truth, num_questions_correct, question_letter, username):
    print("Complete text callback active")
    ctx = callback_context
    print(ctx.triggered[0])

    unclickable_style = {
        "width": "100%",
        "padding": "10px 12px",
        "textAlign": "center",
        "cursor": "default",
        "backgroundColor": "#f0f0f0",
        "color": "#7a7a7a",
        "border": "1px solid #d0d0d0",
        "opacity": "0.9",
        "pointerEvents": "none"
    }

    correct_style = {
        "width": "100%",
        "padding": "10px 12px",
        "fontSize": "24px",
        "textAlign": "center",
        "pointerEvents": "none",
        "backgroundColor": "#08b608",
        "color": "#09ff00",
    }

    false_style = {
        "width": "100%",
        "padding": "10px 12px",
        "fontSize": "24px",
        "textAlign": "center",
        "pointerEvents": "none",
        "backgroundColor": "#c71919",
        "color": "#ff0000",
    }

    if "learning-page-question-complete-let-validate" in ctx.triggered[0]["prop_id"].split(".")[0] and n_clicks > 0:
        print("Validate button clicked")
        # check answer is valid
        print("User input :", user_input)
        result = check_text_answer_is_valid(user_input, ground_truth)
        print(f"Provided answer is {result}")

        style = false_style
        text = html.P("")

        if result == True:
            text = html.P(children=f"Yes! The answer is {ground_truth} !")
            style = correct_style
            num_questions_correct = num_questions_correct + 1

        else:
            text = html.P(children=f"Sorry, the correct answer is {ground_truth}")
        
        # update stats
        user_data = read_user_json(username)
        letters = user_data.get("thai_letters", [])

        question_letter = None
        for letter in letters:
            if letter.get("letter_char") == question_letter or letter.get("letter_name") == question_letter or letter.get("letter_sound") == question_letter:
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
        
        user_data["thai_letters"] = letters
        saved = save_user_json(username, user_data)

        # update global user statistics
        user_statistics = get_global_learning_statistics(username)
        user_statistics["total_questions"] = user_statistics.get("total_questions", 0) + 1
        user_statistics["total_correct"] = user_statistics.get("total_correct", 0) + (1 if result else 0)
        add_user_statistics(username, user_statistics)

        return unclickable_style, False, num_questions_correct, style, text

    else:
        print("No update")
        return no_update, no_update, no_update, no_update, no_update

