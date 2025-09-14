from dash import html, callback, Input, Output, State, dcc, no_update
import dash_bootstrap_components as dbc
from src.modules.webbar import webbar_component
from src.utils.user_utils import create_user



def account_create_page():
    layout = dbc.Container(
        [
            html.H2("Create Account Page", className="text-center my-4"),
            dbc.Form(
                [
                    html.Div(
                        [
                            dbc.Label("Username"),
                            dbc.Input(type="text", id="username", placeholder="Enter username", required=True),
                        ],
                        className="mb-3"
                    ),
                    html.Div(
                        [
                            dbc.Label("Password"),
                            dbc.Input(type="password", id="password", placeholder="Enter password", required=True),
                        ],
                        className="mb-3"
                    ),
                    html.Div(
                        [
                            dbc.Label("Repeat Password"),
                            dbc.Input(type="password", id="password-repeat", placeholder="Repeat password", required=True),
                        ],
                        className="mb-3"
                    ),
                    dbc.Button("Create Account", id="create-account-button", color="primary", className="mt-3", n_clicks=0)
                ]
            ),
            html.Div(id="account-creation-message", className="mt-3")
        ],
        className="py-5"
    )
    return layout


@callback(
    Output("url", "pathname"),
    Output("account-creation-message", "children"),
    Input("create-account-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    State("password-repeat", "value")
)
def handle_account_creation(n_clicks, username, password, password_repeat):
    if n_clicks and username and password and password_repeat:
        if password != password_repeat:
            # Passwords do not match; you could handle this with a notification.
            return no_update, html.Div("Passwords do not match", style={"color": "red", "marginTop": "10px"})
        if create_user(username, password):
            # Redirect to login page upon successful account creation.
            return "/login", no_update
        else:
            # Username already exists; you could handle this with a notification.
            return no_update, html.Div("Username already exists", style={"color": "red", "marginTop": "10px"})
    return no_update, html.Div("Please fill in all fields", style={"color": "red", "marginTop": "10px"})
