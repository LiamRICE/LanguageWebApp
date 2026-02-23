from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
from src.utils.user_utils import get_num_learned_letters, get_num_learned_words, read_user_json, words_can_learn
from src.modules.webbar import webbar_component
from src.modules.navbar import navbar_component
from src.pages.login import login_page
from src.pages.account_create import account_create_page
from src.pages.dashboard import dashboard_page
from src.pages.learning_options import learning_options_page
from src.pages.learning_page_letters import learning_page as learning_page_letters
from src.pages.learning_page_words import learning_page as learning_page_words


def main_page():

    main_component = html.Div([
        html.Div(id="top-component", children=[webbar_component()]),
        dcc.Store(id='user-info', storage_type='memory', data={"authenticated": False}),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ])
    
    return main_component



@callback(
    Output("page-content", "children"),
    Output("top-component", "children"),
    Input("url", "pathname"),
    Input("user-info", "data")
)
def display_page(pathname, user_info):
    username = user_info.get("username") if user_info else "Guest"
    user_data = read_user_json(username=username)
    
    if pathname == "/login":
        return login_page(), webbar_component()
    elif pathname == "/create-account":
        return account_create_page(), webbar_component()
    elif user_info is None or not user_info.get("authenticated", True):
        return login_page(), webbar_component()
    elif pathname == "/":
        return dashboard_page(username), navbar_component()
    elif pathname == "/learn-thai":
        return learning_options_page(True, username, pathname), navbar_component()
    elif pathname == "/learn-thai/learn-letters":
        return learning_page_letters(user_info=user_info, learned_language="thai", is_letters=True, is_practice=False), navbar_component()
    elif pathname == "/learn-thai/practice-letters":
        # print(f"Checking if enough letters learned to practice, {get_num_learned_letters(username=username)} learned VS {user_data.get('settings', {}).get('letters_per_session', 3)} required")
        if get_num_learned_letters(username=username) < user_data.get("settings", {}).get("letters_per_session", 3):
            # print("Not enough letters learned to practice")
            return html.Div([
                html.H2("You need to learn more letters before you can practice this many!", className="text-center my-4"),
                html.Div([
                    dbc.Button("Back to practice hub", href="/learn-thai", color="primary")
                ], className="text-center")
            ]), navbar_component()
        else:
            # print("Enough letters learned, proceeding to practice")
            return learning_page_letters(user_info=user_info, learned_language="thai", is_letters=True, is_practice=True), navbar_component()
    elif pathname == "/learn-thai/learn-words":
        if len(words_can_learn(username=username)) > user_data.get("settings", {}).get("letters_per_session", 3):
            return learning_page_words(user_info=user_info, learned_language="thai", is_letters=False, is_practice=False), navbar_component()
        else:
            return html.Div([
                html.H2(f"You need to learn more letters before you can learn any words! You can only learn {len(words_can_learn(username=username))} words.", className="text-center my-4"),
                html.Div([
                    dbc.Button("Back to practice hub", href="/learn-thai", color="primary")
                ], className="text-center")
            ]), navbar_component()
    elif pathname == "/learn-thai/practice-words":
        if get_num_learned_words(username) < user_data.get("settings", {}).get("letters_per_session", 3):
            return html.Div([
                html.H2("You need to learn more words before you can practice this many!", className="text-center my-4"),
                html.Div([
                    dbc.Button("Back to practice hub", href="/learn-thai", color="primary")
                ], className="text-center")
            ]), navbar_component()
        else:
            return learning_page_words(user_info=user_info, learned_language="thai", is_letters=False, is_practice=True), navbar_component()
    else:
        return "404 - Page Not Found", navbar_component()