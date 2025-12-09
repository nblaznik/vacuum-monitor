import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time

# Create the Dash app
app = dash.Dash(title='BEC Lab Pressures')

# Define pastel colors
pastel_green = '#FFFFFF' 
pastel_red = '#778da9'
text_color = '#415a77'
mrgn_fac_i = 30
mrgn_fac_f = 10



# PLAN
initial_time_series = [] 
initial_data = []

### INITIAL DATA
# 1. Load all the data I have so far here by opening csv files. 
df = pd.read_csv('pressure_readings.csv')                       # Read data from CSV file
df['Timestamp'] = pd.to_datetime(df['Timestamp'])               # Convert datetime strings into actual datetime
df.sort_values(['Timestamp', 'Channel'], inplace=True)          # Sort based on (1) datetime and (2) channel
last_ch = df['Channel'].iloc[-1]                                # Check the last channel - and ... 
df = df.iloc[:-last_ch]                                         # ... ignore the 'incomplete set' of pressures 
# 2. Mark down the last datestamp
last_datetime = pd.to_datetime(df['Timestamp'].iloc[-1])        # Mark the last datestamp we will plot. 
# 3. Load the data into arrays. 
initial_time_series =  df['Timestamp'].to_list()
initial_channel =  df['Channel'].to_list()
initial_pressure =  df['Pressure'].to_list()


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
                dcc.Store(id='store-data', data={'Timestamp': list(initial_time_series), 
                                                 'Channel': list(initial_channel), 
                                                 'Pressure': list(initial_pressure), 
                                                 'LastDatetime': last_datetime}, 
                                                 ),  # Store cumulative data
                dcc.Store(id='store-reLayout')
            ], style={'width': '90%', 'margin': 'auto', 'fontFamily': 'JetBrains Mono, mono'})


# Callback to update graph
@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('store-data', 'data'),
     Input('store-reLayout', 'data')],
)


def update_graph_live(n_intervals, stored_data, relayout_data):
    # Only load the data after the last_datetime
    df = pd.read_csv('pressure_readings.csv')                       # Read data from CSV file
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])               # Convert datetime strings into actual datetime
    df.sort_values(['Timestamp', 'Channel'], inplace=True)          # Sort based on (1) datetime and (2) channel
    last_ch = df['Channel'].iloc[-1]                                # Check the last channel - and ... 
    if last_ch != 6:
        df = df.iloc[:-last_ch]                                         # ... ignore the 'incomplete set' of pressures 
        new_datetime = pd.to_datetime(df['Timestamp'].iloc[-1])         # Mark the last datestamp we will plot. 
        if pd.to_datetime(new_datetime) >  pd.to_datetime(stored_data['LastDatetime']):    # If new timestamp is larger than old one - append new data
            df = df[df['Timestamp'] >  stored_data['LastDatetime']]                        # Load the data after that datetime
            new_time_series =  df['Timestamp'].to_list()
            new_channel =  df['Channel'].to_list()
            new_pressure =  df['Pressure'].to_list()
            stored_data['Timestamp'] += new_time_series
            stored_data['Channel'] += new_channel
            stored_data['Pressure'] += new_pressure
            stored_data['LastDatetime'] = new_datetime
        

    # Number of channels
    num_channels = 6

    # Create a subplot grid (6 rows, 2 columns)
    fig = make_subplots(rows=num_channels, cols=2, 
                        shared_xaxes=True, 
                        vertical_spacing=0.01, horizontal_spacing=0.01, 
                        column_widths=[0.9, 0.1], 
                        subplot_titles=("",
                                        f"{pd.to_datetime(stored_data['Timestamp'][-1]).date()} <br>at {pd.to_datetime(stored_data['Timestamp'][-1]).time()} <br> ", 
                                        "", "", "", "", "", "", "", "", "", "", ))

    # Add traces for each channel
    for i in range(1, num_channels + 1):
        channel_pressure = stored_data['Pressure'][(i-1)::6]
        channel_timestamp = stored_data['Timestamp'][(i-1)::6]
        channel_channel = stored_data['Channel'][(i-1)::6]
        last_pressure = channel_pressure[-1]  # Get the last pressure value for each channel

        """ This part to correct for that weird switching in ch.5 """
        if i == 5:
            pressure = [p*1e-5 if p > 1e-6 else p for p in channel_pressure]
            fig.add_trace(
                go.Scatter(x=channel_timestamp, 
                           y=pressure,
                           mode='lines', 
                           name=f'Channel {channel_channel}', 
                           line=dict(color="#415a77")), 
                           row=i, col=1 
                           ) 
        else: 
            fig.add_trace(
                go.Scatter(x=channel_timestamp, 
                           y=channel_pressure,
                           mode='lines', 
                           name=f'Channel {channel_channel}', 
                           line=dict(color="#415a77")),
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

    
    # Apply previous relayout data (if any) to preserve zoom/pan/range selector
    if relayout_data:
        print(relayout_data)
        try:
            for key, value in relayout_data.items():
                if 'range[' in key:  # Handles range updates
                    axis = key.split('.')[0]  # Get the axis name (xaxis, yaxis, etc.)
                    if 'xaxis' in axis:
                        fig.update_xaxes(range=[relayout_data.get(f'{axis}.range[0]'), relayout_data.get(f'{axis}.range[1]')])
                    elif 'yaxis' in axis:
                        fig.update_yaxes(range=[relayout_data.get(f'{axis}.range[0]'), relayout_data.get(f'{axis}.range[1]')])
                
                elif 'dragmode' in key:
                    print(key, value)
                    fig.update_layout(dragmode=relayout_data['dragmode'])
 
        except Exception as e:
            print(f"Error updating layout with relayout data: {e}")
    
        for i in range(1, num_channels + 1):
            fig.update_yaxes(range=[0, 1], title_text='',row=i, col=2)
            fig.update_xaxes(range=[0, 1],showticklabels=False, row=i, col=2)
            fig.update_yaxes(showticklabels=False, row=i, col=2)
            fig.update_xaxes(showgrid=False, zeroline=False, row=i, col=2)
            fig.update_yaxes(showgrid=False, zeroline=False, row=i, col=2)        
        
        
        # Update the layout of the figure
        fig.update_layout(
            height=800,  # Reduced plot size
            showlegend=False,
            # xaxis_rangeslider_visible=True,
            transition_duration=500,
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
                )
            ),
            xaxis11=dict(
                    rangeslider=dict(
                        visible=False,  # You can set this to True if you want to display a range slider
                        thickness=0.04
                ), type="date"
            )
        )


    # Update xaxis and yaxis for each subplot
    else: 
        for i in range(1, num_channels + 1):
            if i == num_channels:
                fig.update_xaxes(title_text='Time', row=i, col=1)
            else:
                fig.update_xaxes(title_text='', row=i, col=1)
            fig.update_yaxes(title_text=f"Ch. {i}", tickformat=".1e", row=i, col=1)

        for i in range(1, num_channels + 1):
            fig.update_yaxes(range=[0, 1], title_text='',row=i, col=2)
            fig.update_xaxes(range=[0, 1],showticklabels=False, row=i, col=2)
            fig.update_yaxes(showticklabels=False, row=i, col=2)
            fig.update_xaxes(showgrid=False, zeroline=False, row=i, col=2)
            fig.update_yaxes(showgrid=False, zeroline=False, row=i, col=2)        


        # Update the layout of the figure
        fig.update_layout(
            height=800,  # Reduced plot size
            showlegend=False,
            # xaxis_rangeslider_visible=True,
            transition_duration=500,
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
                )
            ),
            xaxis11=dict(
                    rangeslider=dict(
                        visible=False,  # You can set this to True if you want to display a range slider
                        thickness=0.04
                ), type="date"
            )
        )

    # if relayout_data:
    #     print(relayout_data)
    #     # try:
    #     fig.update_layout(relayout_data)  # Attempt to apply relayout data if it exists
    #     # except Exception as e:
    #     #     print(f"Error updating layout with relayout data: {e}")
    #     #     print(relayout_data)
    
    return fig


@app.callback(
    Output('store-reLayout', 'data'),
    [Input('live-update-graph', 'relayoutData')],
    [State('store-reLayout', 'data')]
)
def preserve_layout(relayout_data, stored_layout):
    if relayout_data:
        return relayout_data
    return stored_layout


# Callback to toggle the enabling of the Interval component and change button properties
@app.callback(
    [
        Output('interval-component', 'disabled'),
        Output('toggle-button', 'children'),
        Output('toggle-button', 'style'),
     ],
    [
        Input('toggle-button', 'n_clicks'),
    ],
    [
        State('interval-component', 'disabled'),
    ]
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

@app.callback(
    Output('store-data', 'data'),
    [Input('interval-component', 'n_intervals')],
    [State('store-data', 'data')]
)

def update_data(n_intervals, stored_data):
    # Only load the data after the last_datetime
    df = pd.read_csv('pressure_readings.csv')                       # Read data from CSV file
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])               # Convert datetime strings into actual datetime
    df.sort_values(['Timestamp', 'Channel'], inplace=True)          # Sort based on (1) datetime and (2) channel
    last_ch = df['Channel'].iloc[-1]                                # Check the last channel - and ... 
    if last_ch != 6:
        df = df.iloc[:-last_ch]                                         # ... ignore the 'incomplete set' of pressures 
        new_datetime = df['Timestamp'].iloc[-1]                         # Mark the last datestamp we will plot. 
        if pd.to_datetime(new_datetime) >  pd.to_datetime(stored_data['LastDatetime']):     # If new timestamp is larger than old one - append new data
            print("-"*65)
            print("|" + f"{'NEW DATA at ' + f'{pd.to_datetime(new_datetime)}': ^63}" + "|")
            df = df[df['Timestamp'] >  stored_data['LastDatetime']]                         # Load the data after that datetime
            new_time_series =  df['Timestamp'].to_list()
            new_channel =  df['Channel'].to_list()
            new_pressure =  df['Pressure'].to_list()
            stored_data['Timestamp'] += new_time_series
            stored_data['Channel'] += new_channel
            stored_data['Pressure'] += new_pressure
            stored_data['LastDatetime'] = new_datetime
            print(f"| Ch. 1: {new_pressure[0]: >10.2e}  |  Ch. 2: {new_pressure[1]: >10.2e}  |  Ch. 3: {new_pressure[2]: >10.2e} |")
            print(f"| Ch. 4: {new_pressure[3]: >10.2e}  |  Ch. 5: {new_pressure[4]: >10.2e}  |  Ch. 6: {new_pressure[5]: >10.2e} |")
            print("-"*65)

    return stored_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8081)
