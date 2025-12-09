import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import datetime

# Create the Dash app
app = dash.Dash(__name__)

# Define pastel colors
pastel_green = '#FFFFFF' 
pastel_red = '#778da9'
text_color = '#415a77'
mrgn_fac_i = 30
mrgn_fac_f = 10


# Define the external stylesheet for JetBrains Mono font
external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap" 
]

# Create the Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Layout of the app
app.layout = html.Div([
                html.Div([
                    html.Button('Live Pressure BEC Lab', id='toggle-button', n_clicks=0, style={
                                    'backgroundColor': pastel_green,  # Set initial background color
                                    'border': 'none',  # Remove border
                                    'color': text_color, 
                                    'padding': '10px 20px', 
                                    'textAlign': 'right', 
                                    'textDecoration': 'none',
                                    'display': 'inline-block',
                                    'fontSize': '30px',
                                    'margin-top': '40px',
                                    'margin-bottom': '2px',
                                    'margin-right': f'{mrgn_fac_i}px',
                                    'cursor': 'pointer',
                                    'borderRadius': '12px',
                                    'fontFamily': 'JetBrains Mono, mono',
                                    'transition': 'background-color 1s ease, color 1s ease, margin-right 1s ease',  # CSS transition for smooth animation
                                }),
                    ]),
                dcc.Graph(id='live-update-graph'),
                dcc.Interval(
                    id='interval-component',
                    interval=5*1000,  # in milliseconds
                    n_intervals=0,
                    disabled=False
                ),
            ], style={'width': '90%', 'margin': 'auto', 'fontFamily': 'JetBrains Mono, mono'})

# Callback to update graph
@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
)

# def update_graph_live(n_intervals, stored_range, relayout_data):
def update_graph_live(n_intervals):
    # Read data from CSV file
    df = pd.read_csv('pressure_readings.csv', names=["Timestamp", "Channel", "Pressure"], skiprows=1)
    # df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Channel"] = pd.to_numeric(df["Channel"], errors="coerce").astype("Int64")
    df["Pressure"] = pd.to_numeric(df["Pressure"], errors="coerce")
    df = df.dropna(subset=["Timestamp", "Channel", "Pressure"])

    df.sort_values('Timestamp', inplace=True)

    # Number of channels
    num_channels = 6
        
    last_time = df['Timestamp'].max()

    # Create a subplot grid (6 rows, 2 columns)
    fig = make_subplots(rows=num_channels, cols=2, 
                        shared_xaxes=True, 
                        vertical_spacing=0.01, horizontal_spacing=0.01, 
                        column_widths=[0.9, 0.1], 
                        subplot_titles = [f"Channel {i}" for i in range(1, num_channels + 1)])

    # Add traces for each channel
    for i in range(1, num_channels + 1):
        channel_data = df[df['Channel'] == i]
        last_pressure = channel_data['Pressure'].iloc[-1]  # Get the last pressure value
        
        """ This part to correct for that weird switching in ch.5 """
        if i == 5:
            pressure = [p*1e-5 if p > 1e-6 else p for p in channel_data['Pressure']]
            fig.add_trace(
                go.Scatter(x=channel_data['Timestamp'], y=pressure,
                       mode='lines', name=f'Channel {i}', line=dict(color="#415a77")), row=i, col=1 ) 
        else: 
            fig.add_trace(
                go.Scatter(x=channel_data['Timestamp'], y=channel_data['Pressure'],
                        mode='lines', name=f'Channel {i}', line=dict(color="#415a77")),
                row=i, col=1
            )
            
        fig.add_annotation(
            text=f'{last_pressure:.2E}',  # Replace this with the number you want to display
            xref=f"x{i*2}", 
            yref=f"y{i*2}",   
            x=0.5, 
            y=0.5,  
            showarrow=False,
            # font=dict(family='DigitFont', size=15, color='#7f7f7f'),
            font=dict(family='Courier New, monospace', size=20, color='#415a77'),
            align="center",
            xanchor='center',  # Horizontal alignment
            yanchor='middle'   # Vertical alignment
        )

    # Update the layout of the figure
    fig.update_layout(
        height=800,  # Reduced plot size
        showlegend=False,
        # xaxis_rangeslider_visible=True,
        transition_duration=500,
        # Add range slider
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1 min",
                        step="minute",
                        stepmode="backward"),  # Past 1 minute
                    dict(count=1,
                        label="1 h",
                        step="hour",
                        stepmode="backward"),  # Past 1 hour
                    dict(count=1,
                        label="Today",
                        step="day",
                        stepmode="todate"),  # Past day since the start of the day
                    dict(count=24,
                        label="24 h",
                        step="hour",
                        stepmode="backward"),  # Past 24 hours
                    dict(count=7,
                        label="1 week",
                        step="day",
                        stepmode="backward"),  # Past 7 days (week)
                    dict(count=31,
                        label="1 month",
                        step="day",
                        stepmode="backward"),  # Past 7 days (week)
                    dict(step="all")  # All data
                ])
            ),
            rangeslider=dict(
                visible=False  # You can set this to True if you want to display a range slider
            ),
            type="date"
        )

    )
    # fig['layout']['uirevision'] = True


    # Update xaxis and yaxis for each subplot
    for i in range(1, num_channels + 1):
        if i == num_channels:
            fig.update_xaxes(title_text='Time', row=i, col=1)
        else:
            fig.update_xaxes(title_text='', row=i, col=1)
        fig.update_yaxes(title_text=f"Ch. {i}", tickformat=".1e", row=i, col=1)

    for i in range(1, num_channels + 1):
        #fig.update_xaxes([])
        fig.update_yaxes(title_text='',row=i, col=2)
        fig.update_xaxes(showticklabels=False, row=i, col=2)
        fig.update_yaxes(showticklabels=False, row=i, col=2)
        fig.update_xaxes(showgrid=False, zeroline=False, row=i, col=2)
        fig.update_yaxes(showgrid=False, zeroline=False, row=i, col=2)        

    return fig

# Callback to toggle the enabling of the Interval component and change button properties
@app.callback(
    [
        Output('interval-component', 'disabled'),
        Output('toggle-button', 'children'),
        Output('toggle-button', 'style'),
     ],
    Input('toggle-button', 'n_clicks'),
    State('interval-component', 'disabled'),
)

def toggle_interval_updates(n_clicks, is_disabled):
    if n_clicks > 0:
        new_state = not is_disabled
        btn_bg_color = pastel_red if new_state else pastel_green  # Change entire background color
        btn_txt_color = pastel_green if new_state else text_color  # Change text color
        mrgn_fc = mrgn_fac_i if new_state else mrgn_fac_f  # Change the position

        return new_state, 'Live Pressure BEC Lab     ||' if new_state else 'Live Pressure BEC Lab', {
            'backgroundColor': btn_bg_color,  # Change background color
            'border': 'none',  # No border
            'color': btn_txt_color,
            'padding': '10px 20px',
            'textAlign': 'center',
            'textDecoration': 'none',
            'display': 'inline-block',
            'fontSize': '30px',
            'margin-top': '40px',
            'margin-bottom': '2px',
            'margin-right': f'{mrgn_fc}px',
            'cursor': 'pointer',
            'borderRadius': '12px',
            'fontFamily': 'JetBrains Mono, mono',
            'transition': 'background-color 1s ease, color 1s ease, margin-right 1s ease',  # CSS transition for smooth animation
        }
        
    return is_disabled, 'Live Pressure BEC Lab' if not is_disabled else 'Live Pressure BEC Lab     ||', {
        'backgroundColor': pastel_green,
        'border': 'none',
        'color': text_color,
        'padding': '10px 20px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inline-block',
        'fontSize': '30px',
        'margin-top': '40px',
        'margin-bottom': '2px',
        'margin-right': f'{mrgn_fac_f}px',
        'cursor': 'pointer',
        'borderRadius': '12px',
        'fontFamily': 'JetBrains Mono, mono',
        'transition': 'background-color 1s ease, color 1s ease, margin-right 1s ease'  # CSS transition for smooth animation
    }




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8080)
