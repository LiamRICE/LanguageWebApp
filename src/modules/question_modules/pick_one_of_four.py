from typing import List, Optional
from dash import html, dcc
from dash import Input, Output, State, callback, callback_context
from dash import html, no_update

def create_pick_one_of_four(question: str, options: List[str], correct_id: int, prefix: str = "learning-page-question") -> html.Div:
    """
    Create a Dash component for a "pick one of four" question.

    - question: question text to display
    - options: list of 4 answer strings
    - correct_id: integer 1..4 indicating which button is correct
    - prefix: id prefix to avoid collisions (buttons will be f"{prefix}-btn-1" .. "-4")
    """
    if not isinstance(options, (list, tuple)) or len(options) != 4:
        raise ValueError("options must be a list of exactly 4 strings")
    if correct_id not in (1, 2, 3, 4):
        raise ValueError("correct_id must be 1, 2, 3, or 4")

    grid_style = {
        "display": "grid",
        "gridTemplateColumns": "repeat(2, 1fr)",
        "gap": "8px",
        "marginTop": "8px"
    }
    btn_style = {
        "width": "100%",
        "padding": "10px 12px",
        "textAlign": "center",
        "cursor": "pointer",
        "fontSize": "48px"
    }

    # Buttons: include a data-index attribute and a className so callbacks can toggle a "selected" class/style.
    buttons = []
    for i, text in enumerate(options, start=1):
        btn_id = f"{prefix}-btn-{i}"
        buttons.append(
            html.Button(
                text,
                id=btn_id,
                n_clicks=0,
                style=btn_style,
                className="learning-page-question-btn",
                **{"data-index": i, "aria-pressed": "false"}
            )
        )

    # Store the correct answer id (1..4) and the user's current selection.
    truth_store = dcc.Store(id=f"{prefix}-truth", data=int(correct_id))
    selected_store = dcc.Store(id=f"{prefix}-selected", data=None)

    # Validate button to trigger checking the answer; result_div can show feedback.
    validate_button = html.Button(
        "Validate",
        id=f"{prefix}-validate",
        n_clicks=0,
        style={"marginTop": "12px", "width": "100%", "padding": "10px 12px"}
    )
    result_div = html.Div("", id=f"{prefix}-result", style={"marginTop": "8px", "fontWeight": "600"})

    container = html.Div(
        [
            html.H1(question, id=f"{prefix}-question", style={"fontWeight": "600", "textAlign": "center"}),
            html.Div(buttons, style=grid_style, id=f"{prefix}-grid"),
            validate_button,
            result_div,
            # stores (hidden)
            truth_store,
            selected_store,
        ],
        id=f"{prefix}-container",
        style={"maxWidth": "600px"}
    )

    return container


# Callback for the default prefix "learning-page-question". Highlights the clicked button and stores the selection.
@callback(
    Output("learning-page-question-btn-1", "style", allow_duplicate=True),
    Output("learning-page-question-btn-2", "style", allow_duplicate=True),
    Output("learning-page-question-btn-3", "style", allow_duplicate=True),
    Output("learning-page-question-btn-4", "style", allow_duplicate=True),
    Output("learning-page-question-validate", "style", allow_duplicate=True),
    Output("learning-page-question-selected", "data", allow_duplicate=True),
    Output("next-question-button", "disabled", allow_duplicate=True),
    Output("num-questions-correct", "data", allow_duplicate=True),
    Input("learning-page-question-btn-1", "n_clicks"),
    Input("learning-page-question-btn-2", "n_clicks"),
    Input("learning-page-question-btn-3", "n_clicks"),
    Input("learning-page-question-btn-4", "n_clicks"),
    Input("learning-page-question-validate", "n_clicks"),
    State("learning-page-question-selected", "data"),
    State("learning-page-question-truth", "data"),
    State("num-questions-correct", "data"),
    prevent_initial_call=True,
)
def _highlight_pick_one(n1, n2, n3, n4, validate_clicks, selected, truth, num_correct):
    default_style = {
        "width": "100%",
        "padding": "10px 12px",
        "textAlign": "center",
        "cursor": "pointer",
        "fontSize": "48px"
    }
    selected_style = {**default_style, "backgroundColor": "#cfe8ff", "border": "2px solid #0074D9"}

    ctx = callback_context

    # If the validate button has been clicked, make buttons non-interactive and don't change the stored selection.
    if not validate_clicks:
        triggered = ctx.triggered[0]["prop_id"].split(".")[0]
        sel = None
        if triggered.endswith("-btn-1"):
            sel = 1
        elif triggered.endswith("-btn-2"):
            sel = 2
        elif triggered.endswith("-btn-3"):
            sel = 3
        elif triggered.endswith("-btn-4"):
            sel = 4

        styles = []
        for i in range(1, 5):
            styles.append(selected_style if sel == i else default_style)

        return styles[0], styles[1], styles[2], styles[3], default_style, sel, True, no_update
    
    else:
        # On validate click, do not change styles or selection.
        unclickable_style = {
            "width": "100%",
            "padding": "10px 12px",
            "textAlign": "center",
            "cursor": "default",
            "backgroundColor": "#f0f0f0",
            "color": "#7a7a7a",
            "border": "1px solid #d0d0d0",
            "opacity": "0.9",
            "pointerEvents": "none",
            "fontSize": "48px"
        }
        correct_style = {**unclickable_style, "backgroundColor": "#d4ffd4", "border": "2px solid #2ecc40"}
        incorrect_style = {**unclickable_style, "backgroundColor": "#ffd4d4", "border": "2px solid #ff4136"}

        # initialize distinct style dicts for each button
        styles = [unclickable_style.copy() for _ in range(4)]

        if selected is None:
            return styles[0], styles[1], styles[2], styles[3], unclickable_style, no_update, False, no_update

        try:
            sel_idx = int(selected)
        except Exception:
            return styles[0], styles[1], styles[2], styles[3], unclickable_style, no_update, False, no_update

        try:
            correct_idx = int(truth) if truth is not None else None
        except Exception:
            correct_idx = None

        # If selection is correct: make that button green
        if correct_idx is not None and sel_idx == correct_idx:
            if 1 <= sel_idx <= 4:
                styles[sel_idx - 1] = correct_style
            num_correct += 1
        else:
            # mark selected red (if valid)
            if 1 <= sel_idx <= 4:
                styles[sel_idx - 1] = incorrect_style
            # mark actual correct answer green (if known)
            if correct_idx is not None and 1 <= correct_idx <= 4:
                styles[correct_idx - 1] = correct_style
        
        return styles[0], styles[1], styles[2], styles[3], unclickable_style, no_update, False, num_correct


    
