import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from confluent_kafka import Consumer, KafkaError

# Initialize Dash application
EVENTS = []
app = dash.Dash(__name__)

# Initialize Kafka consumer
bootstrap_servers = 'localhost:9092'
topic = 'network-events'
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'network-events-id',
    'auto.offset.reset': 'earliest',
    'session.timeout.ms': 6000,  # Adjust as needed
    'heartbeat.interval.ms': 2000  # Adjust as needed
}
consumer = Consumer(consumer_config)
consumer.subscribe([topic])

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'textAlign': 'center', 'margin': '0px'},
                      children=[
                          html.H1(children='IP Address Analysis'),

                          html.Div(children=[
                              html.Div(id='live-update-text'),
                              dcc.Interval(id='interval-comp', interval=3000, n_intervals=5),
                          ], style={'display': 'flex', 'margin': 'auto', 'justifyContent': 'center'}),
                      ])

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-comp', 'n_intervals')])
def update_graph(n):
    global EVENTS

    try:
        msg = consumer.poll(1.0)
        if msg is None:
            print("No message received")
            return html.Div([
                html.P(f"{EVENTS}", style={'color': '#666666'})
            ])

        if msg.error():
            print(f"Error Message: {msg.error()}")
            return html.Div([
                html.P(f"{EVENTS}", style={'color': '#666666'})
            ])

        data = json.loads(msg.value())
        print("Data: ", data)
        EVENTS.append(data)

        return html.Div([
            html.P(f"{EVENTS}", style={'color': '#666666'})
        ])

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
