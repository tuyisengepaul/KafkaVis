import json
import dash
from dash import dcc, html
from init_consumer import init_consumer
from aggegate import aggreate_data
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Initialize Dash application
EVENTS = []
UDPs = []
TCPs = []
DATA_SIZEs = []
TIMESTAMPS = []

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
print("Dash application initialized...")

topic = 'network-events'
consumer = init_consumer(topic)

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'textAlign': 'center', 'margin': '0px'},
                      children=[
                          html.H1(children='Network Traffic Analysis'),
                          html.Div(children=[
                              html.Div(id='live-update-text')]),
                              
                          html.Div(children=[
                            
                            dcc.Graph(id='live-graph'),
                            dcc.Graph(id='graph2', style={'marginLeft': '10px'})
                            ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center', 'marginBottom': '100px'}),
                          html.Div(children=[
                              
                              dcc.Interval(id='interval-comp', interval=3000, n_intervals=5),
                          ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center'}),
                      ])

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-comp', 'n_intervals')])
def update_graph(n):
    global EVENTS, UDPs, TCPs, DATA_SIZEs, TIMESTAMPS
    msg = consumer.poll(1.0)
    udp_count, tcp_count, udp_data_size, tcp_data_size = aggreate_data(EVENTS)
    if msg is None:
        print("No message received")
        count_card = dbc.Card(
            dbc.CardBody(
                [
                    html.H3("Traffic count", className="card-title"),
                    html.P(f"UDP Count: {udp_count}"),
                    html.P(f"TCP Count: {tcp_count}"),
                ]
            ),
            color="primary",
            inverse=True,
        )

        size_card = dbc.Card(
            dbc.CardBody(
                [
                    html.H3("Traffic size", className="card-title"),
                    html.P(f"UDP Data Size: {udp_data_size}"),
                    html.P(f"TCP Data Size: {tcp_data_size}"),
                ]
            ),
            color="success",
            inverse=True,
        )

        return dbc.Row(
            [
                dbc.Col(count_card, width=4),
                dbc.Col(size_card, width=4),
            ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center', 'marginBottom': '40px', 'marginTop': '40px'}
        )

    if msg.error():
        print(f"Error Message: {msg.error()}")
        count_card = dbc.Card(
            dbc.CardBody(
                [
                    html.H3("Traffic count", className="card-title"),
                    html.P(f"UDP Count: {udp_count}"),
                    html.P(f"TCP Count: {tcp_count}"),
                ]
            ),
            color="primary",
            inverse=True,
        )

        size_card = dbc.Card(
            dbc.CardBody(
                [
                    html.H3("Traffic size", className="card-title"),
                    html.P(f"UDP Data Size: {udp_data_size}"),
                    html.P(f"TCP Data Size: {tcp_data_size}"),
                ]
            ),
            color="success",
            inverse=True,
        )

        return dbc.Row(
            [
                dbc.Col(count_card, width=4),
                dbc.Col(size_card, width=4),
            ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center', 'marginBottom': '40px', 'marginTop': '40px'}
        )

    data = json.loads(msg.value())
    print("Data: ", data)
    EVENTS.append(data)
    UDPs.append(udp_count)
    TCPs.append(tcp_count)
    DATA_SIZEs.append(udp_data_size)
    TIMESTAMPS.append(data['timestamp'])

    count_card = dbc.Card(
            dbc.CardBody(
                [
                    html.H3("Traffic count", className="card-title"),
                    html.P(f"UDP Count: {udp_count}"),
                    html.P(f"TCP Count: {tcp_count}"),
                ]
            ),
            color="primary",
            inverse=True,
        )

    size_card = dbc.Card(
        dbc.CardBody(
            [
                html.H3("Traffic size", className="card-title"),
                html.P(f"UDP Data Size: {udp_data_size}"),
                html.P(f"TCP Data Size: {tcp_data_size}"),
            ]
        ),
        color="success",
        inverse=True,
    )

    return dbc.Row(
            [
                dbc.Col(count_card, width=4),
                dbc.Col(size_card, width=4),
            ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center', 'marginBottom': '40px', 'marginTop': '40px'}
        )
    
    

@app.callback(Output('live-graph', 'figure'),
              Output('graph2', 'figure'),
              [Input('interval-comp', 'n_intervals')])
def update_graph(n):
    global UDPs, TCPs, DATA_SIZEs, TIMESTAMPS
    data = {
        'timestamp': TIMESTAMPS,
        'UDPs': UDPs,
        'TCPs': TCPs,
        }
    df = pd.DataFrame(data)
    
    df["date"] = pd.to_datetime(df["timestamp"])
    fig = px.line(df, x='TCPs', y="UDPs")
    
    fig2 = go.Figure(data=[go.Scatter(x=TCPs, y=UDPs)])
    total_count = len(set(TCPs + UDPs))
    figure = {
        'data': [
            {'x': list(range(0, total_count + 1)), 'y': TCPs[-10:], 'type': 'bar', 'name': 'TCPs'},
            {'x': list(range(0, total_count + 1)), 'y': UDPs[-10:], 'type': 'bar', 'name': 'UPDs'},
        ],
        'layout': {
            'title': 'Last Ten TCPs and UDPs'
        }
    }
    
    return fig, figure
    

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

