from dash import dcc, html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc

NAV_ITEMS = [
    {"name": "Learn Thai", "href": "/learn-thai"},
]

def navbar_component():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(item["name"], href=item["href"])) for item in NAV_ITEMS
        ] + [
            dbc.NavItem(
                dbc.Button(
                    "Disconnect",
                    id="logout-button",
                    color="light",
                    outline=True,
                    size="sm",
                    className="ms-2",
                    n_clicks=0,
                )
            )
        ],
        brand="Liam's Language Learning App",
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar


@callback(
    Output("user-info", "data", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def logout_user(n_clicks):
    """
    Resets the session 'user-info' store to an unauthenticated state.
    main.py's display_page callback already treats a missing/False
    'authenticated' flag as "show the login page", regardless of the
    current pathname, so no URL change is needed here.

    Because navbar_component() (and its logout-button) is re-created
    fresh on every navigation, Dash fires this callback once with
    n_clicks=0 the moment the button is (re)mounted, even with
    prevent_initial_call=True. The guard below ignores that phantom
    call and only logs out on an actual click (n_clicks >= 1).
    """
    if not n_clicks:
        return no_update
    return {"authenticated": False}