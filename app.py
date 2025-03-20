import os
import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask, request, Response

# 🚀 Flask Server for Authentication
server = Flask(__name__)

# ✅ Set Username and Password for Basic Authentication
USERNAME = os.getenv("DASH_USERNAME", "admin")  # Default: admin
PASSWORD = os.getenv("DASH_PASSWORD", "password")  # Default: password

# ✅ Authentication Function
def authenticate():
    auth = request.authorization
    if not auth or auth.username != USERNAME or auth.password != PASSWORD:
        return Response(
            "Login Required", 401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'}
        )

@server.before_request
def require_auth():
    if request.path.startswith("/_dash"):  # Protects only Dash routes
        auth_response = authenticate()
        if auth_response:
            return auth_response

# ✅ Initialize Dash App
app = dash.Dash(__name__, server=server)

# ✅ Sample Leadership Score Data
df = pd.DataFrame({
    "Category": [
        "CEO Tenure & Impact", "Executive Turnover Rate", "Internal vs. External Hires",
        "Founder Presence", "Headcount Efficiency", "New Role Creation",
        "Department Growth vs. Market Conditions", "Product & R&D Investment",
        "Acquisitions & Partnerships", "Market Share Growth"
    ],
    "Score": [9, 8, 7, 10, 8, 9, 7, 9, 8, 9],
    "Weight": [0.15, 0.1, 0.1, 0.05, 0.15, 0.1, 0.1, 0.1, 0.1, 0.05]
})

df["Weighted Score"] = df["Score"] * df["Weight"]

# ✅ Define Score Descriptions
score_descriptions = {
    "CEO Tenure & Impact": "Measures the influence of the CEO's tenure on company stability and growth.",
    "Executive Turnover Rate": "Tracks the frequency of executive departures, indicating leadership stability.",
    "Internal vs. External Hires": "Compares internal promotions to external hires, reflecting leadership development.",
    "Founder Presence": "Assesses whether the founder remains actively involved in company leadership.",
    "Headcount Efficiency": "Measures revenue per employee, assessing workforce efficiency.",
    "New Role Creation": "Evaluates the rate of new roles being introduced in the organization.",
    "Department Growth vs. Market Conditions": "Compares department expansion relative to industry growth trends.",
    "Product & R&D Investment": "Analyzes spending on research and development for innovation and competitiveness.",
    "Acquisitions & Partnerships": "Evaluates strategic acquisitions and partnerships contributing to market expansion.",
    "Market Share Growth": "Measures the company’s ability to expand its market presence over time."
}

# ✅ Dash Layout
app.layout = html.Div([
    html.H1("Leadership Scorecard Dashboard"),

    # Dropdown to Select a Company (Future Feature)
    dcc.Dropdown(
        id="company-dropdown",
        options=[{"label": "Databricks", "value": "Databricks"}],
        value="Databricks"
    ),

    # Leadership Score Table
    dash_table.DataTable(
        id="score-table",
        columns=[
            {"name": "Category", "id": "Category"},
            {"name": "Score", "id": "Score"},
            {"name": "Weight", "id": "Weight"},
            {"name": "Weighted Score", "id": "Weighted Score"}
        ],
        data=df.to_dict("records"),
        style_data_conditional=[
            {"if": {"column_id": "Weighted Score", "filter_query": "{Weighted Score} < 1"},
             "backgroundColor": "#FFDDDD", "color": "black"}
        ]
    ),

    html.H3("Click a Score for More Details"),
    html.Div(id="score-details"),

    # Score Bar Chart
    dcc.Graph(id="score-chart"),
])

# ✅ Callback: Show Score Details When Clicked
@app.callback(
    Output("score-details", "children"),
    [Input("score-table", "active_cell")]
)
def show_details(active_cell):
    if active_cell:
        row = active_cell["row"]
        category = df.iloc[row]["Category"]
        score = df.iloc[row]["Score"]
        weight = df.iloc[row]["Weight"]
        description = score_descriptions.get(category, "No description available.")

        return html.Div([
            html.H4(f"{category}"),
            html.P(f"Definition: {description}"),
            html.P(f"Score Assigned: {score}"),
            html.P(f"Weight Applied: {weight * 100}%")
        ])
    return "Click on a score to view details."

# ✅ Callback: Update Chart Based on Selected Company
@app.callback(
    Output("score-chart", "figure"),
    [Input("company-dropdown", "value")]
)
def update_chart(selected_company):
    fig = px.bar(df, x="Category", y="Score", title=f"{selected_company} Leadership Scores")
    return fig

# ✅ Run App
if __name__ == "__main__":
    app.run_server(debug=True)
