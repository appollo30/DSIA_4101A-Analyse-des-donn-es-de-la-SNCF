import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash import html
import branca.colormap as cm

def generate_line_plot(gares_communes: pd.DataFrame, with_idf = False) -> go.Figure:
    """
    Voir notebooks/6_merge_gares_frequentation.ipynb
    Il s'agit d'un graphique qui montre le nombre total de voyageurs par région pour chaque année entre 2015 et 2023.
    Pour la simplicité, on ne prend pas en compte l'île de France.
    
    Args:
        gares_communes (pd.DataFrame): Dataframe contenant les gares et leur fréquentation.
    Returns:
        fig (go.Figure): Figure Plotly contenant le graphique.
    """
    region_year_travelers = gares_communes.groupby(['Année', 'nom_region'])['Total Voyageurs'].sum().reset_index()
    if not with_idf:
        region_year_travelers = region_year_travelers.query('nom_region != "Île-de-France"').copy()
    region_year_travelers['Année'] = region_year_travelers['Année'].astype(int)

    fig = px.line(
        region_year_travelers.sort_values(['nom_region', 'Année']),
        x='Année',
        y='Total Voyageurs',
        color='nom_region',
        markers=True,
        labels={
            'Année': 'Année',
            'Total Voyageurs': 'Total Voyageurs',
            'nom_region': 'Région'
        },
        title='Nombre total de voyageurs par région (2015-2023)'
    )
    return fig

def generate_bar_chart(gares_communes: pd.DataFrame) -> go.Figure:
    """
    Voir notebooks/6_merge_gares_frequentation.ipynb
    Génère un bar_chart montrant la perte relative de voyageurs par région entre 2019 et 2020 due au Covid.

    Args:
        gares_communes (pd.DataFrame): Dataframe contenant les gares et leur fréquentation.
    Returns:
        fig (go.Figure): Figure Plotly contenant le graphique.
    """
    region_year_travelers = gares_communes.groupby(['Année', 'nom_region'])['Total Voyageurs'].sum().reset_index()
    region_year_travelers_2019_2020 = region_year_travelers.query('Année in [2019, 2020]').reset_index(drop=True)
    region_year_travelers_loss = region_year_travelers_2019_2020.pivot(index='nom_region', columns='Année', values='Total Voyageurs').reset_index()
    region_year_travelers_loss = region_year_travelers_loss.rename(columns={2019.0: "2019", 2020.0: "2020"})
    
    region_year_travelers_loss["relative_loss"] = ((region_year_travelers_loss["2019"] - region_year_travelers_loss["2020"]) / region_year_travelers_loss["2019"] * 100).round(2)
    df_loss = region_year_travelers_loss.copy()
    df_loss = df_loss.sort_values("relative_loss", ascending=False)

    fig = px.bar(
        df_loss,
        x="nom_region",
        y="relative_loss",
        labels={"nom_region": "Région", "relative_loss": "Perte relative (%)"},
        title="Perte relative de voyageurs par région dûe au COVID (entre 2019 et 2020)",
        color="relative_loss",
        color_continuous_scale="Sunsetdark"
    )
    fig.update_layout(xaxis_tickangle=45)
    return fig

def generate_widget(gares_communes: pd.DataFrame) -> dcc.Graph:
    layout = html.Div([
        dcc.Markdown(
            '''
            ## Évolution du nombre de voyageurs dans le temps (2015-2023)
            
            Ce graphique montre l'évolution du nombre total de voyageurs par région pour chaque année entre 2015 et 2023.
            '''
        ),
        html.Label("Inclure l'Île-de-France ?"),
        dcc.Checklist(
            id='covid_checklist',
            options=[
                {'label': 'Île-de-France', 'value': 'Île-de-France'},
            ],
            value=["Île-de-France"],
        ),
        dcc.Graph(
            id='covid_line_plot',
            figure=generate_line_plot(gares_communes)
        ),
        dcc.Markdown(
            '''
            On peut voir que la région Île-de-France est de loin la plus fréquentée, suivie par Auvergne-Rhône-Alpes et les Hauts de France.
            On constate également une baisse significative du nombre de voyageurs en 2020, probablement due à la pandémie de COVID-19.
            
            On peut chercher à voir quelles sont les régions les plus impactées par la pandémie. Ce graphique montre la part des voyageurs
            perdus entre 2019 et 2020 par région en points de pourcentage.
            '''
        ),
        dcc.Graph(
            id='covid_bar_chart',
            figure=generate_bar_chart(gares_communes)
        ),
        dcc.Markdown(
            '''
            On peut voir que la région Île-de-France est de loin la plus impactée par la pandémie, avec plus de 50% de perte de voyageurs.
            Cela témoigne de l'importance qu'a la région Île-de-France dans le réseau ferroviaire français, en tant que hub de transport.
            '''
        )
    ])
    
    return layout