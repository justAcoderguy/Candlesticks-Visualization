from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_ta as ta
import requests

app = Dash(external_stylesheets=[dbc.themes.CYBORG])

def create_dropdown(options, id_value):
    return html.Div([
        html.H5(id_value.replace("-", " ").replace("select", "").replace("_", " ").title(),
                style={"padding":"10px 30px 0px 30px", "text-size":"15px"}),
        dcc.Dropdown(options=options, id=id_value, value=options[0])
    ], style={"padding":"0px 20px 0px 20px"})

app.layout = html.Div([
    
    html.Div([
    create_dropdown(["btcusd", "ethusd", "xrpusd"], "pair-select"),
    create_dropdown(["60", "3600", "86400"], "timeframe-select"),
    create_dropdown(["50", "100", "200"], "number_of_bars-select")
    ], style={"display":"flex", "margin":"auto", "width":"800px", 
              "justify-content":"space-around"}),

    html.Div([
        dcc.RangeSlider(0, 20, 1, value=[0, 20], id="range-slider"),
        ], id="range-slider-container",
        style={"width":"800px", "margin":"auto", "padding-top":"30px"}),

    dcc.Graph(id="candlesticks"),
    dcc.Graph(id="indicator"),

    dcc.Interval(id="interval", interval=1000)
])

@app.callback(Output("range-slider-container", "children"),
              Input("number_of_bars-select", "value"))
def update_range_slider(num_bars):
    return dcc.RangeSlider(min=0, max=int(num_bars), step=int(int(num_bars)/20), 
                           value=[0, int(num_bars)], id="range-slider")

@app.callback(Output("candlesticks", "figure"),
              Output("indicator", "figure"),
              Input("interval", "n_intervals"),
              Input("pair-select", "value"),
              Input("timeframe-select", "value"),
              Input("number_of_bars-select", "value"),
              Input("range-slider", "value"))
def update_figure(intervals, pair_value, timeframe, number_of_bars, range_values):
    url = f"https://www.bitstamp.net/api/v2/ohlc/{pair_value}/"
    params = {
        "step": timeframe,  # timeframe
        "limit": number_of_bars  # number of bars
    }
    data = requests.get(url, params=params).json()["data"]["ohlc"]

    data = pd.DataFrame(data)
    data.timestamp = pd.to_datetime(data.timestamp, unit="s")

    

    data["rsi"] = ta.rsi(data.close.astype(float))
    data = data.iloc[14:]  # so that the rsi is shown from the first candle

    data = data.iloc[range_values[0]:range_values[1]] # for the range slider

    candles = go.Figure(
                    data=[
                        go.Candlestick(
                            x=data.timestamp,
                            open=data.open,
                            high=data.high,
                            low=data.low,
                            close=data.close
                        )
                    ])



    candles.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
    candles.update_layout(transition_duration=500) # smoothes the updates

    indicator = px.line(x=data.timestamp, y=data.rsi, height=300, template="plotly_dark")

    return candles, indicator


if __name__ == "__main__":
    app.run_server(debug=True)
