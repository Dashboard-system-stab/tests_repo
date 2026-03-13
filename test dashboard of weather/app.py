import dash
from dash.dependencies import Output, Input
from dash import dcc, html
import plotly
import pandas as pd
import plotly.graph_objs as go
from collections import deque
import numpy as np

df = pd.read_csv('weather_data.csv')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')


X = deque(maxlen=len(df))  # дата
Y = deque(maxlen=len(df))  # температура (средняя за сутки)

# Начальные данные (5 дней)
for i in range(5):
    X.append(df['date'].iloc[i])
    Y.append(df['temperature'].iloc[i])

current_index = 5

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        
        html.Div(id='data-panel', style={
            'backgroundColor': '#ffffff',
            'padding': '15px',
            'marginTop': '20px',
            'borderRadius': '4px',
            'border': '1px solid #dddddd',
            'fontFamily': 'Arial',
            'color': "#000000"
        }),
        
        html.Div(id='debug-info', style={'marginTop': 20, 'fontSize': 16}),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
    ]
)

@app.callback(
    [Output('live-graph', 'figure'),
     Output('data-panel', 'children'),
     Output('debug-info', 'children')],
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    global current_index, X, Y, df
    
    if current_index < len(df):
        X.append(df['date'].iloc[current_index])
        Y.append(df['temperature'].iloc[current_index])
        current_index += 1

    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Температура',
        mode='lines+markers',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    )

    layout = go.Layout(
        title='Прогноз погоды',
        xaxis=dict(
            title='Дата',
            range=[min(X), max(X)] if X else [0, 1]
        ),
        yaxis=dict(
            title='Температура (°C)',
            range=[min(Y)-2, max(Y)+2] if Y else [-10, 10]
        ),
        showlegend=True
    )

    panel = create_minimal_panel(X, Y)
    
    debug_info = ""

    return {'data': [data], 'layout': layout}, panel, debug_info


def create_minimal_panel(dates, temps):
    
    dates_list = list(dates)
    temps_list = list(temps)
    
    # Заголовки столбцов
    header = html.Div([
        html.Span('Дата', style={
            'width': '120px',
            'display': 'inline-block',
            'fontWeight': 'bold',
            'marginBottom': '5px'
        }),
        html.Span('Температура', style={
            'width': '100px',
            'display': 'inline-block',
            'fontWeight': 'bold',
            'marginBottom': '5px'
        })
    ], style={'marginBottom': '10px'})
    

    rows = [header]
    
    for i in range(len(dates_list)):
        date = dates_list[i]
        temp = temps_list[i]
        
        row = html.Div([
            html.Span(date.strftime('%d.%m.%Y'), style={
                'width': '120px',
                'display': 'inline-block'
            }),
            html.Span(f"{temp:.1f}°C", style={
                'width': '100px',
                'display': 'inline-block'
            })
        ], style={
            'padding': '3px 0',
            'fontFamily': 'Arial',
            'fontSize': '14px'
        })
        
        rows.append(row)
    

    return html.Div(rows, style={
        'maxHeight': '300px',        
        'overflowY': 'auto',         
        'overflowX': 'hidden',        
        'border': '1px solid #dddddd',
        'padding': '10px'
    })

if __name__ == '__main__':
    app.run(debug=True)