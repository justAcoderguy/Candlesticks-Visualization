from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_ta as ta
import requests

app = Dash()

app.layout = html.Div([
    dcc.Dropdown(["btcusd", "ethusd", "xrpusd"], id="pair-select", value="btcusd"),
    dcc.Dropdown(["60", "3600", "86400"], id="timeframe-select", value="60"),
    dcc.Dropdown(["20", "50", "100"], id="number_of_bars-select", value="20"),

    dcc.Graph(id="candlesticks"),
    dcc.Graph(id="indicator"),

    dcc.Interval(id="interval", interval=2000)
])


@app.callback(Output("candlesticks", "figure"),
              Output("indicator", "figure"),
              Input("interval", "n_intervals"),
              Input("pair-select", "value"),
              Input("timeframe-select", "value"),
              Input("number_of_bars-select", "value"))
def update_figure(intervals, pair_value, timeframe, number_of_bars):
    url = f"https://www.bitstamp.net/api/v2/ohlc/{pair_value}/"
    params = {
        "step": timeframe,  # timeframe
        "limit": number_of_bars  # number of bars
    }
    data = requests.get(url, params=params).json()["data"]["ohlc"]

    data = pd.DataFrame(data)
    data.timestamp = pd.to_datetime(data.timestamp, unit="s")

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

    data["rsi"] = ta.rsi(data.close.astype(float))
    data = data.iloc[14:]  # so that the rsi is shown from the first candle

    candles.update_layout(xaxis_rangeslider_visible=False, height=400)
    indicator = px.line(x=data.timestamp, y=data.rsi, height=300)

    return candles, indicator


if __name__ == "__main__":
    app.run_server(debug=True)
