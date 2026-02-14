from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
from src.utils.user_utils import get_num_learned_letters, get_num_learned_words, read_user_json
from src.modules.webbar import webbar_component
from src.modules.navbar import navbar_component
from src.pages.login import login_page
from src.pages.account_create import account_create_page
from src.pages.dashboard import dashboard_page
from src.pages.learning_options import learning_options_page
from src.pages.learning_page import LearningMode, learning_page


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
        return learning_options_page(True, "/learn-thai"), navbar_component()
    elif pathname == "/learn-french":
        return learning_options_page(False, "/learn-french"), navbar_component()
    elif pathname.startswith("/learn-thai") or pathname.startswith("/learn-french"):
        if "/learn-letters" in pathname:
            return learning_page(LearningMode.LETTERS_NEW), navbar_component()
        elif "/learn-words" in pathname:
            return learning_page(LearningMode.WORDS_NEW), navbar_component()
    else:
        return "404 - Page Not Found", navbar_component()