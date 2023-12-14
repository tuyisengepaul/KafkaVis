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

# Initialize Dash application
EVENTS = []
UDPs = []
TCPs = []
DATA_SIZEs = []
TIMESTAMPS = []

app = dash.Dash(__name__)
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
        return html.Div([
            html.P(f"UDP Count: {udp_count} -- TCP Count: {tcp_count}", style={'color': '#666666'}),
            html.P(f"UDP Data Size: {udp_data_size}  -- TCP Data Size: {tcp_data_size}", style={'color': '#666666'})
        ])

    if msg.error():
        print(f"Error Message: {msg.error()}")
        return html.Div([
            html.P(f"UDP Count: {udp_count} -- TCP Count: {tcp_count}", style={'color': '#666666'}),
            html.P(f"UDP Data Size: {udp_data_size}  -- TCP Data Size: {tcp_data_size}", style={'color': '#666666'})
        ])

    data = json.loads(msg.value())
    print("Data: ", data)
    EVENTS.append(data)
    UDPs.append(udp_count)
    TCPs.append(tcp_count)
    DATA_SIZEs.append(udp_data_size)
    TIMESTAMPS.append(data['timestamp'])

    return html.Div([
        html.P(f"UDP Count: {udp_count} -- TCP Count: {tcp_count}", style={'color': '#666666'}),
        html.P(f"UDP Data Size: {udp_data_size}  -- TCP Data Size: {tcp_data_size}", style={'color': '#666666'})
    ])
    
    

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

