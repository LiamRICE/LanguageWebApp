import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from src.pages.main import main_page



# Initialize the Dash app.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define the app layout with two side-by-side pie charts.


app.layout = html.Div(children=[
    main_page()
])

if __name__ == '__main__':
    app.run(debug=False)