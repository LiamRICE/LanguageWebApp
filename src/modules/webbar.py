from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc


def webbar_component():
    navbar = dbc.NavbarSimple(
        brand="Financial Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar