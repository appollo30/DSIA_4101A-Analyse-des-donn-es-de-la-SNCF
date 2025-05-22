from src.charts.emissions import generate_widget as emissions_widget
from src.charts.reseau import generate_widget as reseau_widget

import pandas as pd
import geopandas as gpd
import dash
from dash import dcc
from dash import html

def main():
    # Obtenir les données
    emissions_df = pd.read_csv("data/processed/emissions.csv")
    shapes_speeds_df = gpd.read_file("data/processed/shapes_speeds.geojson")
    gares_communes = gpd.read_file("data/processed/gares_communes.geojson")
    
    
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        reseau_widget(shapes_speeds_df, gares_communes),
    ])
    
    app.run_server(debug=True)
    
if __name__ == '__main__':
    main()
