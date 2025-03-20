import os
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
from flask import Flask, request, session, redirect, url_for
from flask_session import Session  # ✅ Enables server-side session storage

# ✅ Initialize Flask Server
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecretkey")
server.config["SESSION_TYPE"] = "filesystem"  # ✅ Stores session data on the server
Session(server)  # ✅ Initialize Flask-Session

VALID_PASSWORD = os.environ.get("PASSWORD", "defaultpassword")  # Read password from Render

# ✅ Initialize Dash
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
server = app.server  # ✅ Ensures Gunicorn recognizes the app

# ✅ Debugging Log - Checking Render Environment
print("🟢 App is starting...")
print(f"🛠 SECRET_KEY Loaded: {bool(server.config['SECRET_KEY'])}")
print(f"🛠 Session Config: {server.config['SESSION_TYPE']}")

# ✅ Sample Data
categories = ["CEO Tenure & Impact", "Executive Turnover Rate", "Internal vs. External Hires", "Founder Presence",
              "Headcount Efficiency", "New Role Creation", "Department Growth vs. Market Conditions",
              "Product & R&D Investment", "Acquisitions & Partnerships", "Market Share Growth"]

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

# ✅ Debugging Log - Confirming Data Loaded
print("✅ Leadership Score Data Loaded")

# ✅ Flask Routes for Authentication
@server.route("/")
def home():
    print("🛠 Loading Home Page")  # ✅ Debugging Log
    if not session.get("logged_in"):
        return """
        <html>
        <head><title>Login</title></head>
        <body>
        <h2>Login Required</h2>
        <form action="/login" method="post">
            <input type="password" name="password" placeholder="Enter Password">
            <button type="submit">Submit</button>
        </form>
        </body>
        </html>
        """
    return redirect("/dashboard")

@server.route("/login", methods=["POST"])
def login():
    print("🛠 Processing Login")  # ✅ Debugging Log
    password = request.form.get("password")
    if password == VALID_PASSWORD:
        session["logged_in"] = True
        print("🟢 Login Successful")  # ✅ Debugging Log
        return redirect("/dashboard")
    print("🔴 Incorrect Password")  # ✅ Debugging Log
    return redirect("/")

@server.route("/logout")
def logout():
    session.pop("logged_in", None)
    print("🟢 Logged Out")  # ✅ Debugging Log
    return redirect("/")

@server.route("/dashboard")
def dashboard():
    print("🛠 Loading Dashboard")  # ✅ Debugging Log
    if not session.get("logged_in"):
        return redirect("/")
    return app.index()

# ✅ Dash Layout
def serve_layout():
    return html.Div([  
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

app.layout = serve_layout

# ✅ Debugging Log - Dash Layout Set
print("✅ Dash Layout Loaded")

# ✅ Dash Callbacks
@app.callback(
    [Output('score-table', 'data'),
     Output('score-chart', 'figure')],
    [Input('company-dropdown', 'value')]
)
def update_table(company):
    filtered_df = df[df["Company"] == company]
    fig = px.bar(filtered_df, x='Category', y='Score', title=f'{company} Leadership Scores')
    return filtered_df.to_dict('records'), fig

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

if __name__ == "__main__":
    print("🟢 Starting Dash App...")  # ✅ Debugging Log
    try:
        app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
    except Exception as e:
        print(f"🔴 Error starting app: {e}")  # ✅ Log Errors
