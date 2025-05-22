from src.charts.emissions import generate_line_chart, generate_bar_chart

import pandas as pd
import dash
from dash import dcc
from dash import html

def main():
    # Obtenir les données
    emissions_df = pd.read_csv("data/processed/emissions.csv")
    
    
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        dcc.Graph(
            id='emissions-graph',
            figure=generate_line_chart(emissions_df)
        ),
        dcc.Graph(
            id='emissions-bar-graph',
            figure=generate_bar_chart(emissions_df)
        ),
    ])
    
    app.run_server(debug=True)
    
if __name__ == '__main__':
    main()
