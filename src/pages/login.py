from dash import html, callback, Input, Output, State, dcc, no_update
import dash_bootstrap_components as dbc
from src.modules.webbar import webbar_component
from src.utils.user_utils import check_user

username_login_component = dbc.Input(type="text", id="username", placeholder="Enter username")
password_login_component = dbc.Input(type="password", id="password", placeholder="Enter password")


def login_page():
    print("Rendering login page")
    layout = dbc.Container(
        [
            html.H2("Login Page", className="text-center my-4"),
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Label("Username"),
                                username_login_component
                            ],
                            className="mb-3",
                            id="username-div"
                        ),
                        html.Div(
                            [
                                dbc.Label("Password"),
                                password_login_component
                            ],
                            className="mb-3",
                            id="password-div"
                        ),
                        dbc.Button("Login", id="login-button", color="primary"),
                        html.Div(id="password-div", className="mt-3")
                    ],
                    width=6,
                    lg={"size": 6, "offset": 3}
                )
            ),
            html.Div([
                html.P(["Don't have an account? ", dcc.Link("Create Account", href="/create-account")]),
            ], className="text-center mt-3"),
        ],
        className="py-5"
    )
    return layout


@callback(
    Output("user-info", "data"),
    Output("url", "pathname", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def check_login(n_clicks, username, password):
    if n_clicks and username and password:
        if check_user(username, password):
            print(f"User {username} authenticated successfully.")
            return {"username": username, "authenticated": True}, "/"
    return {"authenticated": False}, "/login"
