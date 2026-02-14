import dash
from dash import html, dcc, Input, Output, State, callback, callback_context, no_update




def multiple_select_exercise_letter(input_letter, options, learning_mode):
    mapping = {
        "name to char": ("letter_name", "letter_char"),
        "name to sound": ("letter_name", "letter_sound"),
        "char to name": ("letter_char", "letter_name"),
        "char to sound": ("letter_char", "letter_sound"),
        "sound to char": ("letter_sound", "letter_char"),
        "sound to name": ("letter_sound", "letter_name"),
    }
    if learning_mode not in mapping:
        raise ValueError("Unsupported learning mode")
    question_field, answer_field = mapping[learning_mode]

    layout = html.Div([
        # Display the input letter based on learning mode
        html.H3(input_letter.get(question_field, "")),
        # Hidden store to save the selected option index
        dcc.Store(id="selected-option", data=None),
        # Option buttons showing the appropriate field
        html.Div([
            html.Button(
                option.get(answer_field, ""),
                id=f"option-{i}",
                n_clicks=0,
                style={"margin": "5px", "padding": "10px"}
            ) for i, option in enumerate(options)
        ]),
        # Button to check the answer
        html.Br(),
        html.Button("Check", id="check-button", n_clicks=0, style={"margin": "10px", "padding": "10px"}),
        html.Div(id="result", style={"marginTop": "10px", "fontWeight": "bold"})
    ])
    return layout


def multiple_select_exercise_word(input_word, options, learning_mode):
    mapping = {
        "word to meaning": ("word", "word_meaning"),
        "meaning to word": ("word_meaning", "word"),
        "word to letters": ("word", "word_letters"),
        "letters to word": ("word_letters", "word"),
    }
    if learning_mode not in mapping:
        raise ValueError("Unsupported learning mode")
    question_field, answer_field = mapping[learning_mode]

    def format_field(value):
        return " ".join(value) if isinstance(value, list) else value

    question_text = format_field(input_word.get(question_field, ""))

    layout = html.Div([
        html.H3(question_text),
        dcc.Store(id="selected-option", data=None),
        html.Div([
            html.Button(
                format_field(option.get(answer_field, "")),
                id=f"option-{i}",
                n_clicks=0,
                style={"margin": "5px", "padding": "10px"}
            )
            for i, option in enumerate(options)
        ]),
        html.Br(),
        html.Button("Check", id="check-button", n_clicks=0, style={"margin": "10px", "padding": "10px"}),
        html.Div(id="result", style={"marginTop": "10px", "fontWeight": "bold"})
    ])
    return layout


# Callback to update the selected option in the Store when an option button is clicked
callback(
    Output("selected-option", "data"),
    Input("option-0", "n_clicks"),
    Input("option-1", "n_clicks"),
    Input("option-2", "n_clicks"),
    Input("option-3", "n_clicks"),
    State("selected-option", "data")
)
def update_selection(n0, n1, n2, n3, stored):
    ctx = callback_context
    if not ctx.triggered:
        return stored
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        selected_index = int(button_id.split("-")[1])
        return selected_index
    except Exception:
        return stored

# Callback to check answer and update button styles and display result
callback(
    Output("option-0", "style"),
    Output("option-1", "style"),
    Output("option-2", "style"),
    Output("option-3", "style"),
    Output("result", "children"),
    Input("check-button", "n_clicks"),
    State("selected-option", "data")
)
def check_answer(n_clicks, selected_index):
    if n_clicks == 0 or selected_index is None:
        return (no_update, no_update, no_update, no_update, "")
    correct_index = next((i for i, option in enumerate(options) if option.get("is_correct")), None)
    
    base_style = {"margin": "5px", "padding": "10px", "pointerEvents": "none", "backgroundColor": "lightgrey"}
    styles = [base_style.copy() for _ in range(4)]
    result_msg = ""

    if selected_index == correct_index:
        styles[correct_index]["backgroundColor"] = "lightgreen"
        result_msg = "Correct!"
    else:
        styles[selected_index]["backgroundColor"] = "salmon"
        if correct_index is not None:
            styles[correct_index]["backgroundColor"] = "lightgreen"
        result_msg = "Incorrect!"

    return (*styles, result_msg)
