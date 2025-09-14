import dash
import dash_bootstrap_components as dbc
from dash import html

def learning_options_page(enable_letters: bool):
    buttons = []
    
    if enable_letters:
        buttons.append(dbc.Button("Learn Letters", color="primary", className="m-1", href="#/learn-letters"))
    buttons.append(dbc.Button("Learn Words", color="primary", className="m-1", href="#/learn-words"))
    if enable_letters:
        buttons.append(dbc.Button("Practice Letters", color="secondary", className="m-1", href="#/practice-letters"))
    buttons.append(dbc.Button("Practice Words", color="secondary", className="m-1", href="#/practice-words"))
    buttons.append(dbc.Button("Sentences", color="info", className="m-1", href="#/sentences"))
    
    layout = dbc.Container(
        [
            html.H1("Select Your Learning Method", className="text-center my-4"),
            dbc.Row(
                [dbc.Col(button, width="auto") for button in buttons],
                justify="center",
                className="mb-4"
            )
        ],
        fluid=True,
    )
    
    return layout
