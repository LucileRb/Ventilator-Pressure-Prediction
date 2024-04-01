import os
import numpy as np
import pandas as pd
import datetime as dt
import dash
import time
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from dash import html
from dash import dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# dcc = dash core components

# load dataset
df = pd.read_csv("train.csv")

# nombre total de respirations
#breath_number = df["breath_id"].nunique()
# nombre total de valeurs dans le dataset
#df.shape[0]

# min/max values
pressure_max = round(max(df["pressure"]), 2)
pressure_min = round(min(df["pressure"]), 2)
uin_max = max(df["u_in"])
uin_min = min(df["u_in"])
R_max = max(df["R"])
R_min = min(df["R"])
C_max = max(df["C"])
C_min = min(df["C"])
uout_max = max(df["u_out"])
uout_min = max(df["u_out"])

# définition de l'app
app = dash.Dash(__name__,   # because we use Flask in the background
                external_stylesheets=[dbc.themes.DARKLY]) # va loader le theme "Darkly" de dbc

app.layout = dbc.Container([
    dbc.Row([dbc.Col([html.H1("Breath Streaming", className="text-center text-primary mb-4"),
                    html.P("This app continually displays live features of respirations with expected and predicted values.")], width=12) #pour centrer le texte et le colorer en bleu et avoir un petit padding avec le reste

    ]),

    dbc.Row([dbc.Col([html.P("dropdown dataset train test")], width={"size":3, "offset":0}),
                dbc.Col([html.P("endroit où mettre si inspiration ou expiration")], width={"size":3, "offset":0})
            ], className="g-0", justify='around'),

    dbc.Row([dbc.Col([html.H3("Respirations"),
                    dcc.Graph(id="respirations",figure=dict(layout=dict(plot_bgcolor="#082255", paper_bgcolor="#082255"))),
                    dcc.Interval(id="respirations-update", interval=1000, n_intervals=0)], width={"size":11, "offset":0})
            ], className="g-0 mb-4", justify='around'),

    dbc.Row([dbc.Col([html.H4("Pressure"),
                        html.P("definition de la pression"),
                        html.P(id="pressure-live", children=[]),
                        html.P(f"max: {pressure_max}"),
                        html.P(f"min: {pressure_min}"),
                        html.P("cmH2O")], width={"size":2, "offset":0}),
            dbc.Col([html.H4("U_in"),
                    html.P("definition de u_in"),
                    html.P(id="uin-live", children=[]),
                    html.P(f"max: {uin_max}"),
                    html.P(f"min: {uin_min}"),
                    html.P("cmH2O")], width={"size":2, "offset":0}),
            dbc.Col([html.H4("R"),
                    html.P("definition de R"),
                    html.P(id="R-live", children=[]),
                    html.P(f"max: {R_max}"),
                    html.P(f"min: {R_min}"),
                    html.P("cmH2O/L/S")], width={"size":2, "offset":0}),
            dbc.Col([html.H4("C"),
                    html.P("definition de C"),
                    html.P(id="C-live", children=[]),
                    html.P(f"max: {C_max}"),
                    html.P(f"min: {C_min}"),
                    html.P("mL/cmH2O")],width={"size":2, "offset":0})
            ], className="g-0", justify='around')

    ], fluid=True)


# update le graph avec les respirations
@app.callback(Output("respirations", "figure"), [Input("respirations-update", "n_intervals")])

def gen_respirations(interval):
    """
    Generate the respirations graph.
    :params interval: update the graph based on an interval
    """
    if interval <= 200:
        data = df[0:interval]

        trace1 = dict(
            type="scatter",
            y=data["pressure"],
            name="pressure",
            hoverinfo="skip",
            mode="lines",
            )

        trace2 = dict(
            type="scatter",
            y=data["u_in"],
            name="u_in",
            hoverinfo="skip",
            mode="lines",
            )

        trace3 = dict(
            type="scatter",
            y=data["u_out"],
            name="u_out",
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor="#082255",
            paper_bgcolor="#082255",
            font={"color": "#fff"},
            xaxis={
                "range": [0, 200],
                "showline": True,
                "zeroline": False,
                "fixedrange": True,
                "tickvals": [0, 50, 100, 150, 200],
                "ticktext": ["0", "50", "100", "150", "200"],
                "title": "Time Elapsed (sec)",
                },
            yaxis={
                "range": [0, pressure_max],
                "showgrid": True,
                "showline": True,
                "fixedrange": True,
                "zeroline": False,
                "nticks": max(6, round(df["pressure"].iloc[-1] / 10)),
                },
            )


    else:
        data = df[interval-200:interval]

        trace1 = dict(
            type="scatter",
            y=data["pressure"],
            name="pressure",
            hoverinfo="skip",
            mode="lines",
            )

        trace2 = dict(
            type="scatter",
            y=data["u_in"],
            name="u_in",
            hoverinfo="skip",
            mode="lines",
            )

        trace3 = dict(
            type="scatter",
            y=data["u_out"],
            name="u_out",
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor="#082255",
            paper_bgcolor="#082255",
            font={"color": "#fff"},
            xaxis={
                "range": [0, 200],
                "showline": True,
                "zeroline": False,
                "fixedrange": True,
                "tickvals": [0, 50, 100, 150, 200],
                "ticktext": ["0", "50", "100", "150", "200"],
                "title": "Time Elapsed (sec)",
                },
            yaxis={
                "range": [0, pressure_max],
                "showgrid": True,
                "showline": True,
                "fixedrange": True,
                "zeroline": False,
                "nticks": max(6, round(df["pressure"].iloc[-1] / 10)),
                },
            )


    return dict(data=[trace1, trace2, trace3], layout=layout)


# Update the live pression value Tag
@app.callback(Output("pressure-live", "children"), [Input("respirations-update", "n_intervals")])
def update_pressure(interval):
    pressure_live = round(df.iloc[interval]["pressure"], 2)
    return pressure_live

# Update the live u_in value Tag
@app.callback(Output("uin-live", "children"), [Input("respirations-update", "n_intervals")])
def update_uin(interval):
    u_in_live = round(df.iloc[interval]["u_in"], 2)
    return u_in_live
#
# # Update the live u_out value Tag
# @app.callback(Output("u-out-live", "children"), [Input("respirations-update", "n_intervals")])
# def update_uout(interval):
#     u_out_live = df.iloc[interval]["u_out"]
#     return u_out_live
#
# Update the live R value Tag
@app.callback(Output("R-live", "children"), [Input("respirations-update", "n_intervals")])
def update_R(interval):
    R_live = df.iloc[interval]["R"]
    return R_live

# Update the live C value Tag
@app.callback(Output("C-live", "children"), [Input("respirations-update", "n_intervals")])
def update_C(interval):
    C_live = df.iloc[interval]["C"]
    return C_live


# # Update the live time step value Tag
# @app.callback(Output("timestep-live", "children"), [Input("respirations-update", "n_intervals")])
# def update_timestep(interval):
#     timestep_live = df.iloc[interval]["time_step"]
#     return timestep_live


# Update the live mae value Tag
#@app.callback(Output("mae-live", "children"), [Input("respirations-update", "n_intervals")])
#def update_mae(interval):
#    mae_live = df.iloc[interval]["mae"]
#    return mae_live


if __name__ == "__main__":
    app.run_server(debug=True)
