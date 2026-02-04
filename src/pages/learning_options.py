import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, State
from src.utils.learning_utils import load_thai_json_as_list
from src.utils.user_utils import add_user_settings, read_user_json
from dash import html


def render_card(item):
    title = f"{item.get('letter_name')} ({item.get('letter_char')})"
    details = [
        html.Div(item.get("letter_sound"), style={'fontSize': '12px', 'color': '#555', 'lineHeight': '1.2'})
    ]

    # stats
    last20 = item.get('last_20_answers', []) or []
    total = len(last20)
    correct = sum(1 for v in last20 if v)
    incorrect = total - correct
    times_practiced = item.get('times_learned', 0)
    accuracy_text = f"{round((correct / total) * 100)}%" if total > 0 else "N/A"

    # small pie figure (uses raw plotly figure dict so no extra imports needed)
    pie_values = [correct, incorrect] if total > 0 else [1, 0]
    pie_figure = {
        "data": [
            {
                "values": pie_values,
                "labels": ["Correct", "Incorrect"],
                "type": "pie",
                "marker": {"colors": ["#28a745", "#dc3545"]},
                "hole": 0.6,
                "textinfo": "none",
                "showlegend": False,
            }
        ],
        "layout": {
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "height": 50,
            "width": 50,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "showlegend": False,
        },
    }

    card_children = []
    if item.get('image'):
        card_children.append(
            dbc.CardImg(src=item.get('image'), top=True, style={'height': '140px', 'objectFit': 'cover'})
        )

    card_children.append(
        dbc.CardBody(
            [
                html.H5(title, className='card-title', style={'marginBottom': '6px'}),
                html.Div(details),
                # Stats row: pie + numbers
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(figure=pie_figure, config={'displayModeBar': False}, style={'height': '50px', 'width':'300px'}),
                            width=4,
                            style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div("Times practiced", style={'fontSize': '12px', 'color': '#666'}),
                                    html.Div(str(times_practiced), style={'fontSize': '20px', 'fontWeight': '700'}),
                                    html.Div("Accuracy (last 20)", style={'fontSize': '12px', 'color': '#666', 'marginTop': '6px'}),
                                    html.Div(accuracy_text, style={'fontSize': '16px', 'fontWeight': '600', 'color': '#333'}),
                                ],
                                style={'textAlign': 'left'}
                            ),
                            width=8,
                            style={'display': 'flex', 'alignItems': 'center'}
                        )
                    ],
                    align='center',
                    className='mt-2'
                )
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

    user_data = read_user_json(username=user_name)
    n = user_data.get("settings", {}).get("letters_per_session", 3)

    if "learn-thai" in url:
        if enable_letters:
            buttons.append(dbc.Button("Learn Letters", color="primary", className="m-1", href="/learn-thai/learn-letters"))
        buttons.append(dbc.Button("Learn Words", color="primary", className="m-1", href="/learn-thai/learn-words"))
        if enable_letters:
            buttons.append(dbc.Button("Practice Letters", color="secondary", className="m-1", href="/learn-thai/practice-letters"))
        buttons.append(dbc.Button("Practice Words", color="secondary", className="m-1", href="/learn-thai/practice-words"))
        buttons.append(dbc.Button("Sentences", color="info", className="m-1", href="/learn-thai/sentences"))
    
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
            html.Div(
                [
                    html.Label("Quantity to learn/practice:", style={'fontWeight': '600', 'marginBottom': '6px'}),
                    dash.dcc.Slider(
                        id='letters-count-slider',
                        min=1,
                        max=10,
                        step=1,
                        value=n,
                        marks={i: str(i) for i in range(1, 11)},
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ],
                className="my-3 px-2"
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
            ),
            dcc.Store(id="user-name-store", data=user_name)
        ],
        fluid=True,
    )
    
    return layout


@callback(
    Input("letters-count-slider", "value"),
    State("user-name-store", "data")
)
def update_letters_count(value, user_name):
    add_user_settings(username=user_name, settings={"letters_per_session": value})