from src.charts.emissions import generate_widget

import pandas as pd
import dash
from dash import dcc
from dash import html

def main():
    # Obtenir les données
    emissions_df = pd.read_csv("data/processed/emissions.csv")
    
    
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        generate_widget(emissions_df),
    ])
    
    app.run_server(debug=True)
    
if __name__ == '__main__':
    main()
