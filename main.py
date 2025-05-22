from src.charts.emissions import generate_widget as emissions_widget
from src.charts.reseau import generate_widget as reseau_widget
from src.charts.covid import generate_widget as covid_widget

from src.charts.covid import generate_line_plot

import pandas as pd
import geopandas as gpd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

def main():
    # Obtenir les données
    emissions_df = pd.read_csv("data/processed/emissions.csv")
    shapes_speeds_df = gpd.read_file("data/processed/shapes_speeds.geojson")
    gares_communes = gpd.read_file("data/processed/gares_communes.geojson")
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label='Réseau ferroviaire', children=[
                reseau_widget(shapes_speeds_df, gares_communes)
            ]),
            dcc.Tab(label='COVID-19', children=[
                covid_widget(gares_communes)
            ]),
            dcc.Tab(label='Émissions de CO2', children=[
                emissions_widget(emissions_df)
            ]),
        ])
    ])
    
    # Callbacks
    @app.callback(
        Output('covid_line_plot', 'figure'),
        [Input('covid_checklist', 'value')]
    )
    def update_line_plot(selected_regions):
        """
        Pour mettre à jour le graphique selon si l'utilisateur a coché la région Île-de-France ou pas.
        Args:
            selected_regions (list): Liste des régions sélectionnées par l'utilisateur.
        Returns:
            fig (go.Figure): Figure Plotly Express contenant le graphique.
        """
        with_idf = 'Île-de-France' in selected_regions
        fig = generate_line_plot(gares_communes, with_idf)
        return fig
    

    app.run_server(debug=True)
    
if __name__ == '__main__':
    main()
