import dash
import dash_bootstrap_components as dbc
from src.utils.learning_utils import load_thai_json_as_list
from dash import html


def render_card(item):
    title = item.get('letter_name') + " (" + item.get('letter_char') + ")"
    details = [
        html.Div(item.get("letter_sound"), style={'fontSize': '12px', 'color': '#555', 'lineHeight': '1.2'})
    ]
    card_children = []
    if item.get('image'):
        card_children.append(
            dbc.CardImg(src=item.get('image'), top=True, style={'height': '140px', 'objectFit': 'cover'})
        )
    card_children.append(
        dbc.CardBody(
            [
                html.H5(title, className='card-title', style={'marginBottom': '6px'}),
                html.Div(details)
            ]
        )
    )
    return dbc.Card(
        card_children,
        className='h-100',
        style={
            'borderRadius': '12px',
            'overflow': 'hidden',
            'boxShadow': '0 6px 18px rgba(24,39,75,0.08)',
            'background': 'linear-gradient(180deg, #ffffff, #fbfbff)',
            'transition': 'transform 0.12s ease, box-shadow 0.12s ease'
        }
    )


def learning_options_page(enable_letters: bool, user_name:str, url:str = ""):
    buttons = []

    if "learn-thai" in url:
        if enable_letters:
            buttons.append(dbc.Button("Learn Letters", color="primary", className="m-1", href="/learn-thai/learn-letters"))
        buttons.append(dbc.Button("Learn Words", color="primary", className="m-1", href="/learn-thai/learn-words"))
        if enable_letters:
            buttons.append(dbc.Button("Practice Letters", color="secondary", className="m-1", href="/learn-thai/practice-letters"))
        buttons.append(dbc.Button("Practice Words", color="secondary", className="m-1", href="/learn-thai/practice-words"))
        buttons.append(dbc.Button("Sentences", color="info", className="m-1", href="/learn-thai/sentences"))
    elif "learn-french" in url:
        if enable_letters:
            buttons.append(dbc.Button("Learn Letters", color="primary", className="m-1", href="/learn-french/learn-letters"))
        buttons.append(dbc.Button("Learn Words", color="primary", className="m-1", href="/learn-french/learn-words"))
        if enable_letters:
            buttons.append(dbc.Button("Practice Letters", color="secondary", className="m-1", href="/learn-french/practice-letters"))
        buttons.append(dbc.Button("Practice Words", color="secondary", className="m-1", href="/learn-french/practice-words"))
        buttons.append(dbc.Button("Sentences", color="info", className="m-1", href="/learn-french/sentences"))

    user_data_letters = load_thai_json_as_list(username=user_name, is_letters=True)
    user_data_words = load_thai_json_as_list(username=user_name, is_letters=False)

    learned_letters = [i for i in user_data_letters if i.get('is_seen')]
    learned_words = [i for i in user_data_words if i.get('is_seen')]

    layout = dbc.Container(
        [
            html.H1("Select Your Learning Method", className="text-center my-4"),
            dbc.Row(
                [dbc.Col(button, width="auto") for button in buttons],
                justify="center",
                className="mb-4"
            ),
            # Learned Letters Section
            html.Div(
                [
                    html.H2("Learned Letters", style={'textAlign': 'center', 'marginTop': '12px'}),
                    dbc.Row(
                        [
                            dbc.Col(render_card(item), xs=12, sm=6, md=4, lg=3)
                            for item in learned_letters
                        ] or [dbc.Col(html.Div("No learned letters yet.", className="text-muted p-3"))],
                        className="g-3"
                    )
                ],
                className="my-3"
            ),
            # Learned Words Section
            html.Div(
                [
                    html.H2("Learned Words", style={'textAlign': 'center', 'marginTop': '18px'}),
                    dbc.Row(
                        [
                            dbc.Col(render_card(item), xs=12, sm=6, md=4, lg=3)
                            for item in learned_words
                        ] or [dbc.Col(html.Div("No learned words yet.", className="text-muted p-3"))],
                        className="g-3"
                    )
                ],
                className="my-3"
            )
        ],
        fluid=True,
    )
    
    return layout
