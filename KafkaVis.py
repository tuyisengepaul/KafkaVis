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
UDP_DATA_SIZEs = []
TCP_DATA_SIZEs = []
COUNTER = []


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'KafkaVis'

print("Dash application initialized...")

topic = 'network-events'
consumer = init_consumer(topic)

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'textAlign': 'center', 'margin': '0px', 'padding': '20px'},
                      children=[
                          html.P(),
                          html.H1(children='Network Traffic Analysis', style={'marginBottom': '50px'}),
                          html.Div(children=[
                              html.Div(id='live-update-text')]),
                              
                          html.Div(children=[
                            
                            dcc.Graph(id='live-graph_bar'),
                            dcc.Graph(id='live-graph_line', style={'marginLeft': '10px'})
                            ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center', 'marginBottom': '150px'}),
                          
                          html.Div(children=[
                              dcc.Interval(id='interval-comp', interval=3000, n_intervals=0),
                              dcc.Interval(id='interval-graph', interval=10000, n_intervals=0),
                          ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center'}),
                      ])

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-comp', 'n_intervals')])
def update_graph(n):
    global EVENTS, UDPs, TCPs, DATA_SIZEs, TIMESTAMPS, UDP_DATA_SIZEs, TCP_DATA_SIZEs, COUNTER
    msg = consumer.poll(1.0)
    udp_count, tcp_count, udp_data_size, tcp_data_size, counter = aggreate_data(EVENTS)
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
    DATA_SIZEs.append(udp_data_size + tcp_data_size)
    TIMESTAMPS.append(data['timestamp'])
    UDP_DATA_SIZEs.append(udp_data_size)
    TCP_DATA_SIZEs.append(tcp_data_size)
    COUNTER.append(counter * 3)

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
    

@app.callback(Output('live-graph_bar', 'figure'),
              Output('live-graph_line', 'figure'),
              [Input('interval-graph', 'n_intervals')])
def update_graph(n):
    global UDPs, TCPs, DATA_SIZEs, TIMESTAMPS, UDP_DATA_SIZEs, TCP_DATA_SIZEs, COUNTER
    data = {
        'Count (Seconds)': COUNTER,
        'timestamp': TIMESTAMPS,
        'UDPs': UDPs,
        'TCPs': TCPs,
        'DataSize': DATA_SIZEs,
        'UDPDataSize': UDP_DATA_SIZEs,
        'TCPDataSize': TCP_DATA_SIZEs
        }
    df = pd.DataFrame(data)
    df["DateTime"] = pd.to_datetime(df["timestamp"])
    df_last_20 = df.tail(20)

    # Create a line chart for the last 20 data points
    fig1 = px.line(df_last_20, x="Count (Seconds)", y=["UDPDataSize", "TCPDataSize"], 
                labels={'value': 'Data Size (KB)', 'variable': 'Metric'})
    fig1.update_layout(title_text='Data Size for UDPs and TCPs', title_x=0.5)

    total_count = len(set(TCPs + UDPs))
    fig2 = {
        'data': [
            {'x':  list(range(1, total_count)) , 'y': TCPs[-10:], 'type': 'bar', 'name': 'TCPs'},
            {'x':  list(range(1, total_count)) , 'y': UDPs[-10:], 'type': 'bar', 'name': 'UPDs'},
        ],
        'layout': {
            'title': {'text': 'TCPs Counts vs UDPs Counts', 'x': 0.5},
            'xaxis': {'title': 'Index'},
            'yaxis': {'title': 'No. of IPs'}
        }
    }
    
    return fig1, fig2
    

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

