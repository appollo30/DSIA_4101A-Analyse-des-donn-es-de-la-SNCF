import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import dcc
from dash import html
import folium
import branca.colormap as cm

def generate_map(shapes_speeds_df : pd.DataFrame, gares_communes : pd.DataFrame) -> folium.Map:
    """
    Voir notebooks/3_merge_shapes_speeds.ipynb et 6_merge_gares_frequentation.ipynb
    Il s'agit d'une carte qui montre les lignes de train et la vitesse maximale sur chaque
    tronçon de ligne. Et également les gares les plus fréquentées (> 5 millions de voyageurs en 2023).
    
    Args:
        shapes_speeds_df (pd.DataFrame): Dataframe contenant les formes des lignes et les vitesses maximales.
        gares_communes (pd.DataFrame): Dataframe contenant les gares et leur fréquentation.
    Returns:    
        fig (folium.Map): Figure Folium contenant la carte.
    """
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

def generate_histogram(shapes_speeds_df : pd.DataFrame) -> go.Figure:
    """
    Voir notebooks/2_speeds.ipynb 
    Il s'agit d'un histogramme qui montre les vitesses maximales sur chaque tronçon de ligne.
    
    Args:
        shapes_speeds_df (pd.DataFrame): Dataframe contenant les formes des lignes et les vitesses maximales.
    Returns:    
        fig (go.Figure): Figure Plotly contenant l'histogramme.
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=shapes_speeds_df['v_max'],
        nbinsx=50,
        hovertemplate='Vitesse: %{x} km/h<br>Nombre de tronçons: %{y}<extra></extra>',
    ))
    fig.update_layout(
        title='Vitesse maximale sur chaque tronçon de ligne',
        xaxis_title='Vitesse (km/h)',
        yaxis_title='Nombre de tronçons',
        xaxis=dict(
            tickmode='linear',
            dtick=10
        )
    )
    
    return fig

def generate_scatterplot(gares_communes: pd.DataFrame) -> go.Figure:
    """
    Génère un scatterplot montrant la fréquentation des gares à fort trafic (> 5M voyageurs)
    en fonction de la population totale de la commune en 2023.

    Args:
        gares_communes (pd.DataFrame): Dataframe contenant les gares et leur fréquentation.

    Returns:
        fig (go.Figure): Figure Plotly Express contenant le scatterplot.
    """
    filtered_df = gares_communes.query('Année == 2023 and `Total Voyageurs` > 5000000')
    fig = px.scatter(
        filtered_df,
        x="PTOT",
        y="Total Voyageurs",
        hover_name="libelle",
        color="nom_region",
        labels={
            "PTOT": "Population totale (PTOT)",
            "Total Voyageurs": "Total Voyageurs",
            "nom_region": "Région"
        },
        title="Gares à fort trafic (> 5M voyageurs) : fréquentation vs population de la commune (2023)"
    )
    return fig

def generate_piechart(gares_communes: pd.DataFrame) -> go.Figure:
    """
    Génère un pie chart montrant la répartition des gares à forte affluence (> 5M voyageurs) par région en 2023.

    Args:
        gares_communes (pd.DataFrame): Dataframe contenant les gares et leur fréquentation.

    Returns:
        fig (go.Figure): Figure Plotly Express contenant le pie chart.
    """
    gares_les_plus_frequentees_2023 = gares_communes.query("`Total Voyageurs` > 5000000 and Année == 2023").copy()
    region_counts = gares_les_plus_frequentees_2023["nom_region"].value_counts().reset_index()
    region_counts.columns = ["Région", "Nombre de gares à fort trafic"]
    fig = px.pie(
        region_counts,
        names="Région",
        values="Nombre de gares à fort trafic",
        title="Répartition des gares à forte affluence (> 5M voyageurs) par région (2023)",
        hole=0.3
    )
    return fig

def generate_widget(shapes_speeds_df : pd.DataFrame, gares_frequentations : pd.DataFrame) -> html.Div:
    
    map_fig = generate_map(shapes_speeds_df, gares_frequentations)
    map_html = map_fig.get_root().render()
    
    histogram = generate_histogram(shapes_speeds_df)
    min_speed = shapes_speeds_df['v_max'].min()
    max_speed = shapes_speeds_df['v_max'].max()
    
    scatterplot = generate_scatterplot(gares_frequentations)
    piechart = generate_piechart(gares_frequentations)

    div = html.Div([
        dcc.Markdown('''
        ## Réseau ferroviaire Français
        
        On peut tout d'abord visualiser la distribution des limitations de vitesse sur tous les tronçons de lignes de train en France via l'histogramme.
        '''
        ),
        html.Div([
            dcc.Graph(
                id='reseau_histogram',
                figure=histogram,
            ),
            dcc.RangeSlider(
                id='reseau_slider',
                min=min_speed,
                max=max_speed,
                value=[min_speed, max_speed],
                step=25
            ),
        ]),
        dcc.Markdown('''
        On constate que la majorité des tronçons de lignes sont à faible vitesse (< 150 km/h).
        Il est important de noter que le nombre de tronçons de lignes à grande vitesse est très faible, mais qu'ils représentent la moitié du réseau ferroviaire français, car ils sont plus longs que les tronçons lents.
        On peut le voir en regardant la carte ci-dessous en jouant avec les boutons radio.
                     
        On peut également visualiser la carte du réseau ferroviaire français, avec les gares les plus fréquentées (> 5 millions de voyageurs en 2023) et la vitesse maximale sur chaque tronçon de ligne.
        Pour des raisons de clareté, on ne montre pas les gares de l'île de France, qui sont de loin les plus fréquentées (voir le scatterplot ci-dessous).
        '''),
        html.Div([
            dcc.RadioItems(
                id="reseau_radio",
                options=["Lignes à faible vitesse (< 100 km/h)", "Lignes à grande vitesse (> 100 km/h)", "Réseau complet"],
                value="Lignes à grande vitesse (> 100 km/h)",
            ),
            html.Iframe(
                id='reseau_map',
                srcDoc=map_html,
                style={'width': '100%', 'height': '600px'}
            ),
        ]),
        dcc.Markdown('''
        On remarque que la zone où le réseau est le plus dense est l'Île-de-France, car Paris est le hub de transport français (il n'existe pas de ligne TGV directe entre Montpellier et Marseille par exemple).
        Les zones où le réseau est le moins exploité par les TGV sont le Massif Central, les Pyrénnées, et le Grand Est.
        
        Le statut de hub de transport de Paris est également visible sur le pie
        chart ci-dessous, qui montre la répartition en nombre de voyageurs des gares à forte affluence (> 5M voyageurs) par région en 2023.
        '''),
        dcc.Graph(
            id='reseau_piechart',
            figure=piechart,
        ),
        dcc.Graph(
            id='reseau_scatterplot',
            figure=scatterplot,
        ),
        dcc.Markdown('''
        On peut directement identifier les 4 plus grandes gares de France, qui sont Paris Gare de Lyon, Paris Montparnasse, Paris Saint-Lazare et Paris Gare du Nord.
        Paris donine donc largement le réseau ferroviaire français, et la plupart des gares à fort trafic sont situées en Île-de-France.
        '''),
    ])
    return div