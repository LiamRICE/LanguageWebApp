from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

NAV_ITEMS = [
    {"name": "Learn Thai", "href": "/learn-thai"},
]

def navbar_component():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(item["name"], href=item["href"])) for item in NAV_ITEMS
        ],
        brand="Liam's Language Learning App",
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar