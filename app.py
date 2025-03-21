import os
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
from flask import Flask, session, redirect, url_for
from flask_session import Session  # ✅ Enables server-side session storage

# ✅ Flask Server Setup
server = Flask(__name__)
server.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
server.config["SESSION_TYPE"] = "filesystem"  
server.config["SESSION_PERMANENT"] = False  
Session(server)  # ✅ Initializes session management

VALID_PASSWORD = os.environ.get("PASSWORD", "defaultpassword")

# ✅ Attach Dash to Flask
app = dash.Dash(__name__, server=server)
server = app.server  # ✅ Ensures Gunicorn recognizes the app

# ✅ Leadership Scorecard Data
categories = [
    "CEO Tenure & Impact", "Executive Turnover Rate", "Internal vs. External Hires", "Founder Presence",
    "Headcount Efficiency", "New Role Creation", "Department Growth vs. Market Conditions",
    "Product & R&D Investment", "Acquisitions & Partnerships", "Market Share Growth"
]

companies = ["Databricks", "Snowflake", "Palantir"]

scores = {
    "Databricks": [9, 8, 7, 10, 8, 9, 7, 9, 8, 9],
    "Snowflake": [7, 6, 7, 5, 9, 9, 8, 9, 9, 8],
    "Palantir": [10, 9, 6, 10, 7, 6, 7, 8, 7, 7]
}

weights = {
    "CEO Tenure & Impact": 0.15, "Executive Turnover Rate": 0.10, "Internal vs. External Hires": 0.10,
    "Founder Presence": 0.05, "Headcount Efficiency": 0.15, "New Role Creation": 0.10,
    "Department Growth vs. Market Conditions": 0.10, "Product & R&D Investment": 0.10,
    "Acquisitions & Partnerships": 0.10, "Market Share Growth": 0.05
}

# ✅ Convert Data to DataFrame
data = []
for company, score_list in scores.items():
    for i, category in enumerate(categories):
        data.append({
            "Company": company,
            "Category": category,
            "Score": score_list[i],
            "Weight": weights[category],
            "Weighted Score": round(score_list[i] * weights[category], 2)
        })
df = pd.DataFrame(data)

# ✅ Score Descriptions
score_descriptions = {
    "CEO Tenure & Impact": "Measures how a long-tenured CEO influences stability, strategy, and performance.",
    "Executive Turnover Rate": "Evaluates the frequency of executive changes and its impact on continuity.",
    "Internal vs. External Hires": "Analyzes whether leadership changes come from within or outside the company.",
    "Founder Presence": "Assesses whether founders remain involved and their influence on company direction.",
    "Headcount Efficiency": "Measures revenue per employee to determine efficient scaling.",
    "New Role Creation": "Examines the introduction of new executive roles and strategic priorities.",
    "Department Growth vs. Market Conditions": "Tracks hiring growth compared to market demand.",
    "Product & R&D Investment": "Evaluates investment in innovation and new product development.",
    "Acquisitions & Partnerships": "Analyzes strategic deals for expansion.",
    "Market Share Growth": "Measures leadership impact on competitive positioning."
}

# ✅ Logout Route
@server.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

# ✅ Layout with Login Screen by Default
app.layout = html.Div([
    html.H2("Login Required"),
    dcc.Input(id="password", type="password", placeholder="Enter Password"),
    html.Button("Submit", id="login-button"),
    html.Div(id="login-output"),
    html.Div(id="dashboard-content")  # ✅ Placeholder for dashboard
])

# ✅ Authentication Callback - Loads Dashboard After Login
@app.callback(
    Output("dashboard-content", "children"),
    Input("login-button", "n_clicks"),
    State("password", "value"),
    prevent_initial_call=True
)
def authenticate(n_clicks, password):
    if password == VALID_PASSWORD:
        session["logged_in"] = True
        return html.Div([  # ✅ Show dashboard after login
            html.H1("Leadership Scorecard Dashboard"),
            dcc.Dropdown(
                id='company-dropdown',
                options=[{'label': c, 'value': c} for c in companies],
                value='Databricks',
                clearable=False,
            ),
            dash_table.DataTable(
                id='score-table',
                columns=[
                    {"name": "Category", "id": "Category"},
                    {"name": "Score", "id": "Score"},
                    {"name": "Weight", "id": "Weight"},
                    {"name": "Weighted Score", "id": "Weighted Score"}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'}
            ),
            html.H3("Click a Score for More Details"),
            dcc.Graph(id='score-chart'),
            html.Div(id='score-details')
        ])
    return "Incorrect Password. Try Again."

# ✅ Update Table & Graph Callback
@app.callback(
    [Output('score-table', 'data'),
     Output('score-chart', 'figure')],
    [Input('company-dropdown', 'value')]
)
def update_table(company):
    filtered_df = df[df["Company"] == company]
    fig = px.bar(filtered_df, x='Category', y='Score', title=f'{company} Leadership Scores')
    return filtered_df.to_dict('records'), fig

# ✅ Show Score Details Callback
@app.callback(
    Output('score-details', 'children'),
    [Input('score-table', 'active_cell')]
)
def show_details(active_cell):
    if active_cell:
        row = active_cell['row']
        category = df.iloc[row]['Category']
        score = df.iloc[row]['Score']
        weight = df.iloc[row]['Weight']
        return html.Div([
            html.H4(f"{category}"),
            html.P(f"Definition: {score_descriptions[category]}"),
            html.P(f"Score Assigned: {score}"),
            html.P(f"Weight Applied: {weight * 100}%")
        ])
    return "Click on a score to view details."

# ✅ Run App with Debugging Logs
if __name__ == "__main__":
    print("✅ Starting Dash App...")
    try:
        app.run_server(host="0.0.0.0", port=8080, debug=True)
    except Exception as e:
        print(f"❌ Error starting app: {e}") 
