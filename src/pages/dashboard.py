from dash import html, dcc, callback, Input, Output, State
from src.utils.user_utils import get_global_learning_statistics, get_thai_letters_learning_statistics, get_thai_words_learning_statistics, read_user_json, save_user_json
import json
import urllib.parse
import base64


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

    thai_words_statistics = get_thai_words_learning_statistics(user_name)
    num_learned_words = thai_words_statistics.get("learned_words", 0)
    total_words = thai_words_statistics.get("total_words", 0)
    words_learned_pct = (num_learned_words / total_words * 100) if total_words > 0 else 0.0

    user_json = read_user_json(user_name)
    json_str = json.dumps(user_json, ensure_ascii=False, indent=2)
    data_uri = "data:application/json;charset=utf-8," + urllib.parse.quote(json_str)

    download_button = html.A(
        "Download your data",
        href=data_uri,
        download=f"{user_name}.json",
        style={
            "display": "inline-block",
            "margin": "5px",
            "padding": "8px 12px",
            "background": "#007BFF",
            "color": "white",
            "borderRadius": "4px",
            "textDecoration": "none",
            "fontSize": "14px",
        },
    )

    upload_button = dcc.Upload(
        id='upload-data',
        children=html.Div([
            "Upload your data"
        ]),
        style={
            "display": "inline-block",
            "margin": "5px",
            "padding": "8px 12px",
            "background": "#28A745",
            "color": "white",
            "borderRadius": "4px",
            "cursor": "pointer",
            "fontSize": "14px",
        },
        multiple=False,
        accept='.json'
    )

    download_component = html.Div(
        [download_button, upload_button],
        style={"textAlign": "center", "width": "100%", "marginBottom": "10px", "display": "flex", "flexWrap": "wrap", "justifyContent": "center"}
    )

    layout = html.Div([
        html.H1(f"Hi {user_name}", style={'textAlign': 'center'}),
        html.Div(
            download_component,
            style={"textAlign": "center"}
        ),
        html.Div(id='upload-status', style={'textAlign': 'center', 'color': 'green', 'marginBottom': '10px'}),
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
                        html.Div(
                            [html.H3("Words Learned", style={"margin": "0"}), html.P(f"{num_learned_words}/{total_words} ({round(words_learned_pct, 1)}%)", style={"fontSize": "18px", "margin": "0"})],
                            style={"textAlign": "center", "padding": "10px", "border": "1px solid #e1e1e1", "borderRadius": "4px", "width": "30%"},
                        ),
                    ],
                    style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px", "flexWrap": "wrap", "gap": "10px"},
                ),
                dcc.Graph(
                    figure={
                        "data": [
                            {"x": ["Accuracy (%)", "Letters Learned (%)", "Words Learned (%)"], "y": [accuracy_pct, letters_learned_pct, words_learned_pct], "type": "bar", "marker": {"color": ["#636EFA", "#00CC96", "#EF553B"]}}
                        ],
                        "layout": {"title": "User statistics", "yaxis": {"range": [0, 100]}},
                    },
                    config={"displayModeBar": False},
                ),
            ]
        )
    ])
    
    return layout


@callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('user-info', 'data'),
    prevent_initial_call=True
)
def handle_upload(contents, filename, user_info):
    user_name = user_info.get("username", "")
    print(f"Received upload: {filename}")
    if contents is None:
        print("No file uploaded.")
        return ""
    try:
        content_string = contents.split(',')[1]
        print(base64.b64decode(content_string)[:100])  # Print the first 100 characters of the content for debugging
        decoded = json.loads(base64.b64decode(content_string))
        save_user_json(user_name, decoded)
        return "✓ Data uploaded successfully!"
    except Exception as e:
        return f"✗ Upload failed: {str(e)}"