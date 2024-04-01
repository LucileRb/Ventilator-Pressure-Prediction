import time
import pathlib
import os
import pickle
import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash.dependencies import State, Input, Output
import dash_daq as daq

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# This is for gunicorn
server = app.server
app_color = {"graph_bg": "#2b2b2b", "graph_line": "#fec036"}

# Load data
df = pd.read_csv("/Users/lucilerabeau/ventilator-pressure-prediction/data/train.csv")

# load X_test preprocessé
with open("/Users/lucilerabeau/ventilator-pressure-prediction/code/X_test1", "rb") as f:
    X_test1 = pickle.load(f)

# load y_test
with open("/Users/lucilerabeau/ventilator-pressure-prediction/code/y_test1", "rb") as f:
    y_test1 = pickle.load(f)

# load y_pred
with open("/Users/lucilerabeau/ventilator-pressure-prediction/code/y_pred1", "rb") as f:
    y_pred1 = pickle.load(f)
# flatten
y_pred1 = y_pred1.flatten()


## Elements

# time step
# time = html.Div(
#     children=[
#         daq.LEDDisplay(
#             value="16:23", #df['time_step']
#             label="Time",
#             size=40,
#             color="#fec036",
#             backgroundColor="#2b2b2b",
#         )
#     ],
#     n_clicks=0, ## ???
# )

# histogramme lung type
r_values = df['R'].unique()
c_values = df['C'].unique()
rc_values = np.array([[[('R' + str(r) + '_' + 'C' + str(c)), len(df[(df['R'] == r) & (df['C'] == c)])] for r in r_values for c in c_values]])

data = pd.DataFrame(rc_values[0], columns=['type', 'count'])
data['count'] = data['count'].apply(lambda x: int(x))

lung_type = px.histogram(data['type'])

# indicateur inspiration
inspiration = daq.Indicator(
    className="panel-lower-indicator",
    id="control-panel-inspiration",
    label="inspiration",
    labelPosition="bottom",
    value=True,
    color="#fec036",
    style={"color": "#black"},
)

# indicateur expiration
expiration = daq.Indicator(
    className="panel-lower-indicator",
    id="control-panel-expiration",
    label="expiration",
    labelPosition="bottom",
    value=True,
    color="#fec036",
    style={"color": "#black"},
)

# Side panel
# dataset_dropdown = dcc.Dropdown(
#     id="dataset-dropdown-component",
#     options=[
#         {"label": "train", "value": "train"},
#         {"label": "test", "value": "test"},
#     ],
#     clearable=False,
#     value="train",
# )
#
# dataset_dropdown_text = html.P(
#     id="dataset-dropdown-text", children=["dataset", html.Br(), " Dashboard"]
# )
#
# dataset_title = html.H1(id="dataset-name", children="")
#
# dataset_body = html.P(
#     className="dataset-description", id="dataset-description", children=[""]
# )
#
# side_panel_layout = html.Div(
#     id="panel-side",
#     children=[
#         dataset_dropdown_text,
#         html.Div(id="dataset-dropdown", children=dataset_dropdown),
#         html.Div(id="panel-side-text", children=[dataset_title, dataset_body]),
#     ],
# )

# Histogram mae

histogram = html.Div(
    id="histogram-container",
    children=[
        html.Div(
            [
                html.Div(
                    [html.H6("mae", className="graph__title")]
                ),
                dcc.Graph(
                    id="mae",
                    figure=dict(
                        layout=dict(
                            plot_bgcolor=app_color["graph_bg"],
                            paper_bgcolor=app_color["graph_bg"],
                        )
                    ),
                ),
            ],
            className="two-thirds column wind__speed__container",
        ),
        ],
)

# Control panel + map
main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        html.Div(
            [
                html.Div(
                    [html.H6("BREATHING", className="graph__title")]
                ),
                dcc.Graph(
                    id="respirations",
                    figure=dict(
                        layout=dict(
                            plot_bgcolor=app_color["graph_bg"],
                            paper_bgcolor=app_color["graph_bg"],
                        )
                    ),
                ),
                dcc.Interval(
                    id="respirations-update",
                    interval=1000, # regarder si possible de réduire
                    n_intervals=0,
                ),
            ],
            className="two-thirds column wind__speed__container",
        ),
        html.Div(
            id="panel",
            children=[
                histogram,
                html.Div(
                    id="panel-lower",
                    children=[
                        html.Div(
                            id="panel-lower-0",
                            children=[inspiration, expiration, time],
                        ),
                        html.Div(
                            id="panel-lower-1",
                            children=[
                                html.Div(
                                    id="panel-lower-led-displays",
                                    children=[lung_type],
                                ),
                                html.Div(
                                    id="panel-lower-indicators",
                                    children=[
                                        html.Div(
                                            id="panel-lower-indicators-0",
                                            children=[],
                                        ),
                                        html.Div(
                                            id="panel-lower-indicators-1",
                                            children=[],
                                        ),
                                        html.Div(
                                            id="panel-lower-indicators-2",
                                            children=[],
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="panel-lower-graduated-bars",
                                    children=[],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# Data generation


# Root
# root_layout = html.Div(
#     id="root",
#     children=[
#         side_panel_layout,
#         main_panel_layout,
#     ],
# )

# app.layout = root_layout

app.layout = main_panel_layout

# Callback graph respiration
@app.callback(
    Output("respirations", "figure"), [Input("respirations-update", "n_intervals")]
)
def gen_breathing(interval):
    """
    Generate the pressure graph.

    :params interval: update the graph based on an interval
    """

    if interval <= 200:
        ytest = y_test1[0:interval]
        ypred = y_pred1[0:interval]

        trace1 = dict(
            type="scatter",
            y=ytest,
            name="pressure_test",
            line={"color": "#42C4F7"},
            hoverinfo="skip",
            mode="lines",
            )

        trace2 = dict(
            type="scatter",
            y=ypred,
            name="pressure_pred",
            line={"color": "#0000FF"},
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "#fff"},
            height=700,
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
                "gridcolor": app_color["graph_line"],
                "nticks": max(6, round(y_test1.iloc[-1] / 10)),
                },
            )

    else:
        ytest = y_test1[interval-200:interval]
        ypred = y_pred1[interval-200:interval]

        trace1 = dict(
            type="scatter",
            y=ytest,
            name="pressure_test",
            line={"color": "#42C4F7"},
            hoverinfo="skip",
            mode="lines",
            )

        trace2 = dict(
            type="scatter",
            y=ypred,
            name="pressure_pred",
            line={"color": "#0000FF"},
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "#fff"},
            height=700,
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
                "gridcolor": app_color["graph_line"],
                "nticks": max(6, round(y_test1.iloc[-1] / 10)),
                },
            )

    return dict(data=[trace1, trace2], layout=layout)


# Callback graph mae

@app.callback(
    Output("mae", "figure"), [Input("respirations-update", "n_intervals")]
)
def gen_mae(interval):
    """
    Generate the mae evolution graph.

    :params interval: update the graph based on an interval
    """

    if interval <= 200:
        ytest = y_test1[0:interval]
        ypred = y_pred1[0:interval]
        mae = abs(ypred-ytest).to_numpy()

        trace = dict(
            type="scatter",
            y=mae,
            name="mae",
            line={"color": "#42C4F7"},
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "#fff"},
            height=700,
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
                "range": [0, max(mae)],
                "showgrid": True,
                "showline": True,
                "fixedrange": True,
                "zeroline": False,
                "gridcolor": app_color["graph_line"],
                "nticks": max(6, round(mae.iloc[-1] / 10)),
                },
            )

    else:
        ytest = y_test1[interval-200:interval]
        ypred = y_pred1[interval-200:interval]
        mae = abs(ypred-ytest).to_numpy()

        trace = dict(
            type="scatter",
            y=mae,
            name="mae",
            line={"color": "#42C4F7"},
            hoverinfo="skip",
            mode="lines",
            )

        layout = dict(
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "#fff"},
            height=700,
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
                "range": [0, max(mae)],
                "showgrid": True,
                "showline": True,
                "fixedrange": True,
                "zeroline": False,
                "gridcolor": app_color["graph_line"],
                "nticks": max(6, round(mae.iloc[-1] / 10)),
                },
            )

    return dict(data=[trace], layout=layout)

# Callbacks dernier "histogram"

# Update the graph
# @app.callback(
#     [
#         Output("histogram-graph", "figure"),
#         Output("store-data-config", "data"),
#         Output("histogram-title", "children"),
#     ],
#     [
#         Input("interval", "n_intervals"),
#         Input("control-panel-latitude", "n_clicks"),
#         Input("control-panel-longitude", "n_clicks"),
#         Input("control-panel-fuel", "n_clicks"),
#         Input("control-panel-battery", "n_clicks"),
#     ],
# )
# def update_graph(
#     interval,
#     satellite_type,
#     minute_mode,
#     elevation_n_clicks,
#     temperature_n_clicks,
#     speed_n_clicks,
#     latitude_n_clicks,
#     longitude_n_clicks,
#     fuel_n_clicks,
#     battery_n_clicks,
#     data,
#     data_config,
#     old_figure,
#     old_data,
#     old_title,
# ):
#     new_data_config = data_config
#     info_type = data_config["info_type"]
#     ctx = dash.callback_context
#
#     # Check which input fired off the component
#     if not ctx.triggered:
#         trigger_input = ""
#     else:
#         trigger_input = ctx.triggered[0]["prop_id"].split(".")[0]
#
#     # Update store-data-config['satellite_type']
#     if satellite_type == "h45-k1":
#         new_data_config["satellite_type"] = 0
#     elif satellite_type == "l12-5":
#         new_data_config["satellite_type"] = 1
#     else:
#         new_data_config["satellite_type"] = None
#
#     # Decide the range of Y given if minute_mode is on
#     def set_y_range(data_key):
#         if data_key == "elevation":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [0, 1000],
#                     "autorange": False,
#                 }
#
#         elif data_key == "temperature":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [0, 500],
#                     "autorange": False,
#                 }
#
#         elif data_key == "speed":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [0, 40],
#                     "autorange": False,
#                 }
#
#         elif data_key == "latitude":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [-90, 90],
#                     "autorange": False,
#                     "dtick": 30,
#                 }
#
#         elif data_key == "longitude":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [0, 360],
#                     "autorange": False,
#                 }
#
#         elif data_key == "fuel" or data_key == "battery":
#             if minute_mode:
#                 figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
#             else:
#                 figure["layout"]["yaxis"] = {
#                     "rangemode": "normal",
#                     "range": [0, 100],
#                     "autorange": False,
#                 }
#
#     # Function to update values
#     def update_graph_data(data_key):
#         string_buffer = ""
#         if data_config["satellite_type"] == 0:
#             string_buffer = "_0"
#         elif data_config["satellite_type"] == 1:
#             string_buffer = "_1"
#
#         if minute_mode:
#             figure["data"][0]["y"] = list(
#                 reversed(data["minute_data" + string_buffer][data_key])
#             )
#         else:
#             figure["data"][0]["y"] = list(
#                 reversed(data["hour_data" + string_buffer][data_key])
#             )
#
#         # Graph title changes depending on graphed data
#         new_title = data_key.capitalize() + " Histogram"
#         return [data_key, new_title]
#
#     # A default figure option to base off everything else from
#     figure = old_figure
#
#     # First pass checks if a component has been selected
#     if trigger_input == "control-panel-elevation":
#         set_y_range("elevation")
#         info_type, new_title = update_graph_data("elevation")
#
#     elif trigger_input == "control-panel-temperature":
#         set_y_range("temperature")
#         info_type, new_title = update_graph_data("temperature")
#
#     elif trigger_input == "control-panel-speed":
#         set_y_range("speed")
#         info_type, new_title = update_graph_data("speed")
#
#     elif trigger_input == "control-panel-latitude":
#         set_y_range("latitude")
#         info_type, new_title = update_graph_data("latitude")
#
#     elif trigger_input == "control-panel-longitude":
#         set_y_range("longitude")
#         info_type, new_title = update_graph_data("longitude")
#
#     elif trigger_input == "control-panel-fuel":
#         set_y_range("fuel")
#         info_type, new_title = update_graph_data("fuel")
#
#     elif trigger_input == "control-panel-battery":
#         set_y_range("battery")
#         info_type, new_title = update_graph_data("battery")
#
#     # If no component has been selected, check for most recent info_type, to prevent graph from always resetting
#     else:
#         if info_type in [
#             "elevation",
#             "temperature",
#             "speed",
#             "latitude",
#             "longitude",
#             "fuel",
#             "battery",
#         ]:
#             set_y_range(info_type)
#             nil, new_title = update_graph_data(info_type)
#             return [figure, new_data_config, new_title]
#         else:
#             return [old_figure, old_data, old_title]
#     new_data_config["info_type"] = info_type
#     return [figure, new_data_config, new_title]
#
#
# # Callbacks Dropdown
#
#
# @app.callback(
#     Output("dataset-name", "children"),
#     [Input("dataset-dropdown-component", "value")],
# )
# def update_dataset_name(val):
#     if val == "train":
#         return "dataset\train"
#     elif val == "test":
#         return "dataset\test"
#     else:
#         return ""
#
#
# @app.callback(
#     Output("dataset-description", "children"),
#     [Input("dataset-dropdown-component", "value")],
# )
# def update_dataset_description(val):
#     text = "Select a dataset to view using the dropdown above."
#
#     if val == "train":
#         text = (
#             "train set avec valeurs pressures"
#         )
#
#     elif val == "test":
#         text = (
#             "test dataset sans les valeurs de pression"
#         )
#     return text



# Callbacks Components

@app.callback(
    Output("control-panel-inspiration", "value"),
    [Input("interval", "n_intervals"), Input("dataset-dropdown-component", "value")],
)
def update_inspiration_component():
    if df['u_out'] == 0:
        return True
    else:
        return False

@app.callback(
    Output("control-panel-expiration", "value"),
    [Input("interval", "n_intervals"), Input("dataset-dropdown-component", "value")],
)
def update_expiration_component():
    if df['u_out'] == 0:
        return False
    else:
        return True



if __name__ == "__main__":
    app.run_server(debug=True)
