# imports
import pickle, os
import dash
from dash import dcc
from dash import html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#load external CSS stylesheet
#app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# load data
# load y_test
# load dataset
with open("/Users/lucilerabeau/ventilator-pressure-prediction/app/X_test", "rb") as f:
    X_test = pickle.load(f)

# load X_test preprocessé
# with open("/Users/lucilerabeau/ventilator-pressure-prediction/app/X_test_lookback", "rb") as f:
#     X_test_lookback = pickle.load(f)

# load y_test
# with open("/Users/lucilerabeau/ventilator-pressure-prediction/app/y_test", "rb") as f:
#     y_test = pickle.load(f)

# load y_pred
# with open("/Users/lucilerabeau/ventilator-pressure-prediction/app/y_pred1", "rb") as f:
#     y_pred1 = pickle.load(f)
# # flatten
# y_pred1 = y_pred1.flatten()

#load model entrainé
# with open("/Users/lucilerabeau/ventilator-pressure-prediction/app/model", "rb") as f:
#     model = pickle.load(f)

print(X_test[0][3])
#print(type(y_pred))
#app layout
# app.layout = html.Div(
#     [
#      html.H1("test", style={'text-align': 'center'}),
#      dcc.Graph(figure=fig),
#     ]
# )
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)
