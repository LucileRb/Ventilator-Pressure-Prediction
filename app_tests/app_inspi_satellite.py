import time
import pathlib
import os
import pickle
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Input, Output
import dash_daq as daq

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# This is for Heroku
server = app.server

# Elements

utc = html.Div(
    id="control-panel-utc",
    children=[
        daq.LEDDisplay(
            id="control-panel-utc-component",
            value="16:23",
            label="Time",
            size=40,
            color="#fec036",
            backgroundColor="#2b2b2b",
        )
    ],
    n_clicks=0,
)

# ajouter histogramme lung type

# petit voyant pour dire si inspi
solar_panel_0 = daq.Indicator(
    className="panel-lower-indicator",
    id="control-panel-solar-panel-0",
    label="Solar-Panel-0",
    labelPosition="bottom",
    value=True,
    color="#fec036",
    style={"color": "#black"},
)

# petit voyant pour dire si expi
solar_panel_1 = daq.Indicator(
    className="panel-lower-indicator",
    id="control-panel-solar-panel-1",
    label="Solar-Panel-1",
    labelPosition="bottom",
    value=True,
    color="#fec036",
    style={"color": "#black"},
)


# toggleswitch pour montrer u_in ou non sur graph respi
map_toggle = daq.ToggleSwitch(
    id="control-panel-toggle-map",
    value=True,
    label=["Hide path", "Show path"],
    color="#ffe102",
    style={"color": "#black"},
)

## Side panel

# dropdown du dataset qu'on utilise
satellite_dropdown = dcc.Dropdown(
    id="satellite-dropdown-component",
    options=[
        {"label": "H45-K1", "value": "h45-k1"},
        {"label": "L12-5", "value": "l12-5"},
    ],
    clearable=False,
    value="h45-k1",
)

# dropdown de la description a afficher en fonction du dataset
satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=["Satellite", html.Br(), " Dashboard"]
)

satellite_title = html.H1(id="satellite-name", children="")

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=[""]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        satellite_dropdown_text,
        html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Div(id="panel-side-text", children=[satellite_title, satellite_body]),
    ],
)


## Graph respiration et pression temps réel

map_data = [
    {
        "type": "scattermapbox",
        "lat": [0],
        "lon": [0],
        "hoverinfo": "text+lon+lat",
        "text": "Satellite Path",
        "mode": "lines",
        "line": {"width": 2, "color": "#707070"},
    },
    {
        "type": "scattermapbox",
        "lat": [0],
        "lon": [0],
        "hoverinfo": "text+lon+lat",
        "text": "Current Position",
        "mode": "markers",
        "marker": {"size": 10, "color": "#fec036"},
    },
]

map_layout = {
    "mapbox": {
        "accesstoken": MAPBOX_ACCESS_TOKEN,
        "style": MAPBOX_STYLE,
        "center": {"lat": 45},
    },
    "showlegend": False,
    "autosize": True,
    "paper_bgcolor": "#1e1e1e",
    "plot_bgcolor": "#1e1e1e",
    "margin": {"t": 0, "r": 0, "b": 0, "l": 0},
}

map_graph = html.Div(
    id="world-map-wrapper",
    children=[
        map_toggle,
        dcc.Graph(
            id="world-map",
            figure={"data": map_data, "layout": map_layout},
            config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)

# courbe mae

histogram = html.Div(
    id="histogram-container",
    children=[
        html.Div(
            id="histogram-header",
            children=[
                html.H1(
                    id="histogram-title", children=["Select A Property To Display"]
                ),
                minute_toggle,
            ],
        ),
        dcc.Graph(
            id="histogram-graph",
            figure={
                "data": [
                    {
                        "x": [i for i in range(60)],
                        "y": [i for i in range(60)],
                        "type": "scatter",
                        "marker": {"color": "#fec036"},
                    }
                ],
                "layout": {
                    "margin": {"t": 30, "r": 35, "b": 40, "l": 50},
                    "xaxis": {"dtick": 5, "gridcolor": "#636363", "showline": False},
                    "yaxis": {"showgrid": False},
                    "plot_bgcolor": "#2b2b2b",
                    "paper_bgcolor": "#2b2b2b",
                    "font": {"color": "gray"},
                },
            },
            config={"displayModeBar": False},
        ),
    ],
)

## Architecture des figures
main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        dcc.Interval(id="interval", interval=1 * 2000, n_intervals=0),
        map_graph,
        html.Div(
            id="panel",
            children=[
                histogram,
                html.Div(
                    id="panel-lower",
                    children=[
                        html.Div(
                            id="panel-lower-0",
                            children=[elevation, temperature, speed, utc],
                        ),
                        html.Div(
                            id="panel-lower-1",
                            children=[
                                html.Div(
                                    id="panel-lower-led-displays",
                                    children=[latitude, longitude],
                                ),
                                html.Div(
                                    id="panel-lower-indicators",
                                    children=[
                                        html.Div(
                                            id="panel-lower-indicators-0",
                                            children=[solar_panel_0, thrusters],
                                        ),
                                        html.Div(
                                            id="panel-lower-indicators-1",
                                            children=[solar_panel_1, motor],
                                        ),
                                        html.Div(
                                            id="panel-lower-indicators-2",
                                            children=[camera, communication_signal],
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="panel-lower-graduated-bars",
                                    children=[fuel_indicator, battery_indicator],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

## Data generation
df = pd.read_csv("/Users/lucilerabeau/ventilator-pressure-prediction/train.csv")

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


## Architecture totale
root_layout = html.Div(
    id="root",
    children=[
        dcc.Store(id="store-placeholder"),
        dcc.Store(
            id="store-data",
            data={
                "hour_data_0": {
                    "elevation": [df_non_gps_h_0["elevation"][i] for i in range(60)],
                    "temperature": [
                        df_non_gps_h_0["temperature"][i] for i in range(60)
                    ],
                    "speed": [df_non_gps_h_0["speed"][i] for i in range(60)],
                    "latitude": [
                        "{0:09.4f}".format(df_gps_h_0["lat"][i]) for i in range(60)
                    ],
                    "longitude": [
                        "{0:09.4f}".format(df_gps_h_0["lon"][i]) for i in range(60)
                    ],
                    "fuel": [df_non_gps_h_0["fuel"][i] for i in range(60)],
                    "battery": [df_non_gps_h_0["battery"][i] for i in range(60)],
                },
                "minute_data_0": {
                    "elevation": [df_non_gps_m_0["elevation"][i] for i in range(60)],
                    "temperature": [
                        df_non_gps_m_0["temperature"][i] for i in range(60)
                    ],
                    "speed": [df_non_gps_m_0["speed"][i] for i in range(60)],
                    "latitude": [
                        "{0:09.4f}".format(df_gps_m_0["lat"][i]) for i in range(60)
                    ],
                    "longitude": [
                        "{0:09.4f}".format(df_gps_m_0["lon"][i]) for i in range(60)
                    ],
                    "fuel": [df_non_gps_m_0["fuel"][i] for i in range(60)],
                    "battery": [df_non_gps_m_0["battery"][i] for i in range(60)],
                },
                "hour_data_1": {
                    "elevation": [df_non_gps_h_1["elevation"][i] for i in range(60)],
                    "temperature": [
                        df_non_gps_h_1["temperature"][i] for i in range(60)
                    ],
                    "speed": [df_non_gps_h_1["speed"][i] for i in range(60)],
                    "latitude": [
                        "{0:09.4f}".format(df_gps_h_1["lat"][i]) for i in range(60)
                    ],
                    "longitude": [
                        "{0:09.4f}".format(df_gps_h_1["lon"][i]) for i in range(60)
                    ],
                    "fuel": [df_non_gps_h_1["fuel"][i] for i in range(60)],
                    "battery": [df_non_gps_h_1["battery"][i] for i in range(60)],
                },
                "minute_data_1": {
                    "elevation": [df_non_gps_m_1["elevation"][i] for i in range(60)],
                    "temperature": [
                        df_non_gps_m_1["temperature"][i] for i in range(60)
                    ],
                    "speed": [df_non_gps_m_1["speed"][i] for i in range(60)],
                    "latitude": [
                        "{0:09.4f}".format(df_gps_m_1["lat"][i]) for i in range(60)
                    ],
                    "longitude": [
                        "{0:09.4f}".format(df_gps_m_1["lon"][i]) for i in range(60)
                    ],
                    "fuel": [df_non_gps_m_1["fuel"][i] for i in range(60)],
                    "battery": [df_non_gps_m_1["battery"][i] for i in range(60)],
                },
            },
        ),
        # For the case no components were clicked, we need to know what type of graph to preserve
        dcc.Store(id="store-data-config", data={"info_type": "", "satellite_type": 0}),
        side_panel_layout,
        main_panel_layout,
    ],
)

app.layout = root_layout


# Callbacks Data

# Add new data every second/minute
@app.callback(
    Output("store-data", "data"), [Input("interval", "n_intervals")])

def update_data(interval):
    # data en fonction de l'interval
    if interval <= 200:
        ytest = y_test1[0:interval]
        ypred = y_pred1[0:interval]
    else:
        ytest = y_test1[interval-200:interval]
        ypred = y_pred1[interval-200:interval]

    return ytest, ypred


# Callbacks Histogram

# Update the graph
@app.callback(
    Output("respirations", "figure"), [Input("respirations-update", "n_intervals")]
)
def gen_breathing(interval):
    """
    Generate the wind speed graph.

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

    # Check which input fired off the component
    if not ctx.triggered:
        trigger_input = ""
    else:
        trigger_input = ctx.triggered[0]["prop_id"].split(".")[0]

    # Update store-data-config['satellite_type']
    if satellite_type == "h45-k1":
        new_data_config["satellite_type"] = 0
    elif satellite_type == "l12-5":
        new_data_config["satellite_type"] = 1
    else:
        new_data_config["satellite_type"] = None

    # Decide the range of Y given if minute_mode is on
    def set_y_range(data_key):
        if data_key == "elevation":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [0, 1000],
                    "autorange": False,
                }

        elif data_key == "temperature":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [0, 500],
                    "autorange": False,
                }

        elif data_key == "speed":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [0, 40],
                    "autorange": False,
                }

        elif data_key == "latitude":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [-90, 90],
                    "autorange": False,
                    "dtick": 30,
                }

        elif data_key == "longitude":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [0, 360],
                    "autorange": False,
                }

        elif data_key == "fuel" or data_key == "battery":
            if minute_mode:
                figure["layout"]["yaxis"] = {"rangemode": "normal", "autorange": True}
            else:
                figure["layout"]["yaxis"] = {
                    "rangemode": "normal",
                    "range": [0, 100],
                    "autorange": False,
                }

    # Function to update values
    def update_graph_data(data_key):
        string_buffer = ""
        if data_config["satellite_type"] == 0:
            string_buffer = "_0"
        elif data_config["satellite_type"] == 1:
            string_buffer = "_1"

        if minute_mode:
            figure["data"][0]["y"] = list(
                reversed(data["minute_data" + string_buffer][data_key])
            )
        else:
            figure["data"][0]["y"] = list(
                reversed(data["hour_data" + string_buffer][data_key])
            )

        # Graph title changes depending on graphed data
        new_title = data_key.capitalize() + " Histogram"
        return [data_key, new_title]

    # A default figure option to base off everything else from
    figure = old_figure

    # First pass checks if a component has been selected
    if trigger_input == "control-panel-elevation":
        set_y_range("elevation")
        info_type, new_title = update_graph_data("elevation")

    elif trigger_input == "control-panel-temperature":
        set_y_range("temperature")
        info_type, new_title = update_graph_data("temperature")

    elif trigger_input == "control-panel-speed":
        set_y_range("speed")
        info_type, new_title = update_graph_data("speed")

    elif trigger_input == "control-panel-latitude":
        set_y_range("latitude")
        info_type, new_title = update_graph_data("latitude")

    elif trigger_input == "control-panel-longitude":
        set_y_range("longitude")
        info_type, new_title = update_graph_data("longitude")

    elif trigger_input == "control-panel-fuel":
        set_y_range("fuel")
        info_type, new_title = update_graph_data("fuel")

    elif trigger_input == "control-panel-battery":
        set_y_range("battery")
        info_type, new_title = update_graph_data("battery")

    # If no component has been selected, check for most recent info_type, to prevent graph from always resetting
    else:
        if info_type in [
            "elevation",
            "temperature",
            "speed",
            "latitude",
            "longitude",
            "fuel",
            "battery",
        ]:
            set_y_range(info_type)
            nil, new_title = update_graph_data(info_type)
            return [figure, new_data_config, new_title]
        else:
            return [old_figure, old_data, old_title]
    new_data_config["info_type"] = info_type
    return [figure, new_data_config, new_title]


# Callbacks Dropdown


@app.callback(
    Output("satellite-name", "children"),
    [Input("satellite-dropdown-component", "value")],
)
def update_satellite_name(val):
    if val == "h45-k1":
        return "Satellite\nH45-K1"
    elif val == "l12-5":
        return "Satellite\nL12-5"
    else:
        return ""


@app.callback(
    Output("satellite-description", "children"),
    [Input("satellite-dropdown-component", "value")],
)
def update_satellite_description(val):
    text = "Select a satellite to view using the dropdown above."

    if val == "h45-k1":
        text = (
            "H45-K1, also known as GPS IIR-9 and GPS SVN-45, is an American navigation satellite which forms part "
            "of the Global Positioning System. It was the ninth Block IIR GPS satellite to be launched, out of "
            "thirteen in the original configuration, and twenty one overall. It was built by Lockheed Martin, using "
            "the AS-4000 satellite bus. -168 was launched at 22:09:01 UTC on 31 March 2003, atop a Delta II carrier "
            "rocket, flight number D297, flying in the 7925-9.5 configuration. The launch took place from Space "
            "Launch Complex 17A at the Cape Canaveral Air Force Station, and placed H45-K1 into a transfer orbit. "
            "The satellite raised itself into medium Earth orbit using a Star-37FM apogee motor."
        )

    elif val == "l12-5":
        text = (
            "L12-5, also known as NRO Launch 22 or NROL-22, is an American signals intelligence satellite, "
            "operated by the National Reconnaissance Office. Launched in 2006, it has been identified as the first "
            "in a new series of satellites which are replacing the earlier Trumpet spacecraft. L12-5 was launched "
            "by Boeing, using a Delta IV carrier rocket flying in the Medium+(4,2) configuration. The rocket was the "
            "first Delta IV to launch from Vandenberg Air Force Base, flying from Space Launch Complex 6, a launch "
            "pad originally constructed as part of abandoned plans for manned launches from Vandenberg, originally "
            "using Titan rockets, and later Space Shuttles. The launch also marked the first launch of an Evolved "
            "Expendable Launch Vehicle from Vandenberg, and the first launch of an NRO payload on an EELV."
        )
    return text


# Callbacks Map


@app.callback(
    Output("world-map", "figure"),
    [
        Input("interval", "n_intervals"),
        Input("control-panel-toggle-map", "value"),
        Input("satellite-dropdown-component", "value"),
    ],
    [
        State("world-map", "figure"),
        State("store-data", "data"),
        State("store-data-config", "data"),
    ],
)
def update_word_map(clicks, toggle, satellite_type, old_figure, data, data_config):
    figure = old_figure
    string_buffer = ""

    # Set string buffer as well as drawing the satellite path
    if data_config["satellite_type"] == 0:
        string_buffer = "_0"
        figure["data"][0]["lat"] = [df_gps_m_0["lat"][i] for i in range(3600)]
        figure["data"][0]["lon"] = [df_gps_m_0["lon"][i] for i in range(3600)]

    elif data_config["satellite_type"] == 1:
        string_buffer = "_1"
        figure["data"][0]["lat"] = [df_gps_m_1["lat"][i] for i in range(3600)]
        figure["data"][0]["lon"] = [df_gps_m_1["lon"][i] for i in range(3600)]
    else:
        figure["data"][0]["lat"] = [df_gps_m["lat"][i] for i in range(3600)]
        figure["data"][0]["lon"] = [df_gps_m["lon"][i] for i in range(3600)]

    if not string_buffer:
        figure["data"][1]["lat"] = [1.0]
        figure["data"][1]["lon"] = [1.0]

    elif clicks % 2 == 0:
        figure["data"][1]["lat"] = [
            float(data["minute_data" + string_buffer]["latitude"][-1])
        ]
        figure["data"][1]["lon"] = [
            float(data["minute_data" + string_buffer]["longitude"][-1])
        ]

    # If toggle is off, hide path
    if not toggle:
        figure["data"][0]["lat"] = []
        figure["data"][0]["lon"] = []
    return figure


# Callbacks Components


@app.callback(
    Output("control-panel-utc-component", "value"), [Input("interval", "n_intervals")]
)
def update_time(interval):
    hour = time.localtime(time.time())[3]
    hour = str(hour).zfill(2)

    minute = time.localtime(time.time())[4]
    minute = str(minute).zfill(2)
    return hour + ":" + minute


@app.callback(
    [
        Output("control-panel-elevation-component", "value"),
        Output("control-panel-temperature-component", "value"),
        Output("control-panel-speed-component", "value"),
        Output("control-panel-fuel-component", "value"),
        Output("control-panel-battery-component", "value"),
    ],
    [Input("interval", "n_intervals"), Input("satellite-dropdown-component", "value")],
    [State("store-data-config", "data"), State("store-data", "data")],
)
def update_non_gps_component(clicks, satellite_type, data_config, data):
    string_buffer = ""
    if data_config["satellite_type"] == 0:
        string_buffer = "_0"
    if data_config["satellite_type"] == 1:
        string_buffer = "_1"

    new_data = []
    components_list = ["elevation", "temperature", "speed", "fuel", "battery"]
    # Update each graph value
    for component in components_list:
        new_data.append(data["minute_data" + string_buffer][component][-1])

    return new_data


@app.callback(
    [
        Output("control-panel-latitude-component", "value"),
        Output("control-panel-longitude-component", "value"),
    ],
    [Input("interval", "n_intervals"), Input("satellite-dropdown-component", "value")],
    [State("store-data-config", "data"), State("store-data", "data")],
)
def update_gps_component(clicks, satellite_type, data_config, data):
    string_buffer = ""
    if data_config["satellite_type"] == 0:
        string_buffer = "_0"
    if data_config["satellite_type"] == 1:
        string_buffer = "_1"

    new_data = []
    for component in ["latitude", "longitude"]:
        val = list(data["minute_data" + string_buffer][component][-1])
        if val[0] == "-":
            new_data.append("0" + "".join(val[1::]))
        else:
            new_data.append("".join(val))
    return new_data


@app.callback(
    [
        Output("control-panel-latitude-component", "color"),
        Output("control-panel-longitude-component", "color"),
    ],
    [Input("interval", "n_intervals"), Input("satellite-dropdown-component", "value")],
    [State("store-data-config", "data"), State("store-data", "data")],
)
def update_gps_color(clicks, satellite_type, data_config, data):
    string_buffer = ""
    if data_config["satellite_type"] == 0:
        string_buffer = "_0"
    if data_config["satellite_type"] == 1:
        string_buffer = "_1"

    new_data = []

    for component in ["latitude", "longitude"]:
        value = float(data["minute_data" + string_buffer][component][-1])
        if value < 0:
            new_data.append("#ff8e77")
        else:
            new_data.append("#fec036")

    return new_data


@app.callback(
    Output("control-panel-communication-signal", "value"),
    [Input("interval", "n_intervals"), Input("satellite-dropdown-component", "value")],
)
def update_communication_component(clicks, satellite_type):
    if clicks % 2 == 0:
        return False
    else:
        return True


if __name__ == "__main__":
    app.run_server(debug=True)
