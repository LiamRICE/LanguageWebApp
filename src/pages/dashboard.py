from dash import html, dcc

def dashboard_page(user_name):

    layout = html.Div([
        html.H1(f"Hi {user_name}", style={'textAlign': 'center'}),
    ])
    
    return layout