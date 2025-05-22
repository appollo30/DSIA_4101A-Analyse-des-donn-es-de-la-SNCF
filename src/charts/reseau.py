import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc
from dash import html
import folium
import branca.colormap as cm

def generate_map(shapes_speeds_df : pd.DataFrame, gares_communes : pd.DataFrame) -> folium.Map:
    
    # On crée une carte Folium
    linear = cm.linear.viridis.scale(0, 300)
    fig = folium.Map(
        location=(46.539758, 2.430331),
        tiles='OpenStreetMap',
        zoom_start=6,
        zoom_control=False, # On désactive le zoom et le déplacement
        scrollWheelZoom=False,
        dragging=False
    )
    # On ajoute les tronçons de lignes
    folium.GeoJson(
        shapes_speeds_df,
        style_function=lambda x: {
            'color': linear(x['properties']['v_max']),
            'weight': 4,
            'opacity': 0.8
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['v_max', "lib_ligne"],
            aliases=['Vitesse (km/h)', 'Ligne'],
            localize=True,
            sticky=False,
            labels=True
        )
    ).add_to(fig)
    
    # On ajoute les gares
    gares_les_plus_frequentees_2023 = gares_communes.query("`Total Voyageurs` > 5000000 and Année == 2023").copy()
    # On ne prend que les gares dont la fréquentation était supérieure à 5 millions de voyageurs en 2023.
    # Pour plus de clareté, on enlève les gares hors de l'île de France
    gares_les_plus_frequentees_2023 = gares_les_plus_frequentees_2023.query('nom_region != "Île-de-France"')
    
    def scale_size(val, min_size=5, max_size=30):
        # On estime la taille du cercle en pixels en fonction de la fréquentation
        min_travelers = gares_les_plus_frequentees_2023["Total Voyageurs"].min()
        max_travelers = gares_les_plus_frequentees_2023["Total Voyageurs"].max()
        if max_travelers == min_travelers:
            return max_size
        return min_size + (max_size - min_size) * (val - min_travelers) / (max_travelers - min_travelers)
    
    for _, row in gares_les_plus_frequentees_2023.iterrows():
        folium.CircleMarker(
            location=[row["geometry"].y, row["geometry"].x],
            radius=scale_size(row["Total Voyageurs"]),
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(f"{row['libelle']}<br>{int(row['Total Voyageurs']):,} voyageurs", max_width=250)
        ).add_to(fig)
    
    return fig

def generate_widget(shapes_speeds_df : pd.DataFrame, gares_frequentations : pd.DataFrame) -> html.Div:
    
    map_fig = generate_map(shapes_speeds_df, gares_frequentations)
    map_html = map_fig.get_root().render()
    
    map_div = html.Div([
        dcc.Markdown('''test'''),
        html.Iframe(
            id='map',
            srcDoc=map_html,
            style={'width': '100%', 'height': '600px'}
        )
    ])
    return map_div