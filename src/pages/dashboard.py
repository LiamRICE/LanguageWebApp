from dash import html, dcc
from src.utils.user_utils import get_global_learning_statistics, get_thai_letters_learning_statistics, read_user_json
import json
import urllib.parse


def dashboard_page(user_name):

    statistics = get_global_learning_statistics(user_name)
    total_sessions = statistics.get("total_sessions", 0)
    total_questions = statistics.get("total_questions", 0)
    total_correct = statistics.get("total_correct", 0)

    total_accuracy = (total_correct / total_questions) if total_questions > 0 else 0.0
    accuracy_pct = round(total_accuracy * 100, 1)

    thai_letters_statistics = get_thai_letters_learning_statistics(user_name)
    num_learned_letters = thai_letters_statistics.get("learned_letters", 0)
    total_letters = thai_letters_statistics.get("total_letters", 0)
    letters_learned_pct = (num_learned_letters / total_letters * 100) if total_letters > 0 else 0.0

    user_json = read_user_json(user_name)
    json_str = json.dumps(user_json, ensure_ascii=False, indent=2)
    data_uri = "data:application/json;charset=utf-8," + urllib.parse.quote(json_str)

    download_button = html.A(
        "Download your data",
        href=data_uri,
        download=f"{user_name}_data.json",
        style={
            "display": "inline-block",
            "margin": "10px 0",
            "padding": "8px 12px",
            "background": "#007BFF",
            "color": "white",
            "borderRadius": "4px",
            "textDecoration": "none",
        },
    )

    download_component = html.Div(download_button, style={"textAlign": "center", "width": "100%", "marginBottom": "10px"})
    layout = html.Div([
        html.H1(f"Hi {user_name}", style={'textAlign': 'center'}),
        html.Div(
            download_component,
            style={"textAlign": "center"}
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [html.H3("Total Sessions", style={"margin": "0"}), html.P(f"{total_sessions}", style={"fontSize": "24px", "margin": "0"})],
                            style={"textAlign": "center", "padding": "10px", "border": "1px solid #e1e1e1", "borderRadius": "4px", "width": "30%"},
                        ),
                        html.Div(
                            [html.H3("Overall Accuracy", style={"margin": "0"}), html.P(f"{accuracy_pct}%", style={"fontSize": "24px", "margin": "0"})],
                            style={"textAlign": "center", "padding": "10px", "border": "1px solid #e1e1e1", "borderRadius": "4px", "width": "30%"},
                        ),
                        html.Div(
                            [html.H3("Letters Learned", style={"margin": "0"}), html.P(f"{num_learned_letters}/{total_letters} ({round(letters_learned_pct, 1)}%)", style={"fontSize": "18px", "margin": "0"})],
                            style={"textAlign": "center", "padding": "10px", "border": "1px solid #e1e1e1", "borderRadius": "4px", "width": "30%"},
                        ),
                    ],
                    style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"},
                ),
                dcc.Graph(
                    figure={
                        "data": [
                            {"x": ["Total Sessions", "Accuracy (%)", "Letters Learned (%)"], "y": [total_sessions, accuracy_pct, letters_learned_pct], "type": "bar", "marker": {"color": ["#636EFA", "#00CC96", "#EF553B"]}}
                        ],
                        "layout": {"title": "User statistics", "yaxis": {"range": [0, 100]}},
                    },
                    config={"displayModeBar": False},
                ),
            ]
        )
    ])
    
    return layout