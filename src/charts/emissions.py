import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
from dash import dcc
from dash import html

color_palette = ["#af2bbf","#8770bf","#6c91bf","#5fb0b7","#5bc8af"] # Palette de couleurs pour les barres
    
colors_moyens_de_transport = {
    "Train":color_palette[0],
    "Autocar":color_palette[1],
    "Avion":color_palette[2],
    "Voiture thermique":color_palette[3],
    "Voiture électrique":color_palette[4]
} # Une couleur par moyen de transport

def generate_line_chart(emissions_df : pd.DataFrame, log_scale : bool =False) -> go.Figure:
    """
    Voir notebooks/7_emissions-co2.ipynb
    
    Génère le line chart des émissions de CO2 d'un trajet en fonction de la distance parcourue et du moyen de transport.
    On peut voir les émissions on hover.
    
    Args:
        emissions_df (pd.DataFrame): Dataframe contenant les émissions de CO2 pour chaque moyen de transport.
        log_scale (bool): Si True, on affiche l'échelle logarithmique.
    Returns:
        fig (go.Figure): Figure Plotly contenant le line chart.
    """
    
    fig = go.Figure()
    # On ajoute les courbes pour chaque moyen de transport
    emissions_df = emissions_df.sort_values(by='Distance')
    moyens_transport = ["Autocar", "Voiture électrique", "Voiture thermique", "Avion"]
    
    # Solutionn inspirée de https://github.com/plotly/plotly.py/issues/4278 pour afficher l'origine et la destination des trajets dans le hover
    # On ajoute une courbe invisible pour chaque moyen de transport, et on change son hovertext pour afficher l'origine et la destination
    fig.add_trace(go.Scatter(
        x=emissions_df['Distance'], 
        y=emissions_df['Train'], 
        opacity=0, 
        showlegend=False,
        hovertext=emissions_df['Origine'] + ' - ' + emissions_df['Destination'],
        hovertemplate='<b>%{hovertext}</b><extra></extra>'
        ))

    # On ajoute les courbes pour les trains, en montrant le transporteur dans le hover
    fig.add_trace(go.Scatter(
        x=emissions_df['Distance'],
        y=emissions_df['Train'],
        mode='lines+markers',
        name='Train',
        connectgaps=True,
        hovertext=emissions_df['Transporteur'],
        hovertemplate='<b>%{hovertext}</b> : %{y:.2f} kgCO2e <extra></extra>',
        marker=dict(color=colors_moyens_de_transport['Train'])
    ))
    for column in moyens_transport:
        fig.add_trace(go.Scatter(
            x=emissions_df['Distance'],
            y=emissions_df[column],
            mode='lines+markers',
            name=column,
            connectgaps=True,
            hovertemplate='%{y:.2f} kgCO2e',
            marker=dict(color=colors_moyens_de_transport[column])
        ))
    
    fig.update_layout(
        title='Émissions de CO2 par moyen de transport en fonction de la distance',
        xaxis_title='Distance entre les gares (km)',
        yaxis_title='CO2 émis en fonction de la distance',
        legend_title='Moyen de transport',
        hovermode='x unified'
    )
    
    if log_scale:
        fig.update_layout(title='Émissions de CO2 par moyen de transport en fonction de la distance (échelle logarithmique)')
        fig.update_yaxes(
            title='CO2 émis en fonction de la distance (échelle logarithmique)', 
            type="log"
    )
    
    return fig
    
def generate_bar_chart(emissions_df: pd.DataFrame) -> go.Figure:
    
    emissions_df_reduced = emissions_df[["Transporteur","Distance","Train","Autocar","Avion","Voiture électrique","Voiture thermique"]].copy()
    # On divise les émissions par la distance pour obtenir l'empreinte carbone par km
    emissions_df_reduced["Train"] = emissions_df_reduced["Train"] / emissions_df_reduced["Distance"]
    emissions_df_reduced["Autocar"] = emissions_df_reduced["Autocar"] / emissions_df_reduced["Distance"]
    emissions_df_reduced["Avion"] = emissions_df_reduced["Avion"] / emissions_df_reduced["Distance"]
    emissions_df_reduced["Voiture électrique"] = emissions_df_reduced["Voiture électrique"] / emissions_df_reduced["Distance"]
    emissions_df_reduced["Voiture thermique"] = emissions_df_reduced["Voiture thermique"] / emissions_df_reduced["Distance"]
    emissions_df_reduced = emissions_df_reduced.drop(columns=["Distance"])
    
    # On fait un melt pour avoir une colonne pour chaque moyen de transport. On a donc une dataframe longue avec une colonne 
    # pour le moyen de transport et une colonne pour l'empreinte carbone
    emissions_df_reduced = emissions_df_reduced.melt(id_vars=["Transporteur"], var_name="Moyen_de_transport", value_name="Empreinte carbone")
    
    emissions_df_reduced_train = emissions_df_reduced.query("Moyen_de_transport == 'Train'")
    emissions_df_reduced_train = emissions_df_reduced_train[["Transporteur","Empreinte carbone"]].groupby(["Transporteur"]).mean().reset_index()
    emissions_df_reduced_train = emissions_df_reduced_train.rename(columns={"Transporteur":"Moyen_de_transport"})
    
    emissions_df_reduced_other = emissions_df_reduced.query("Moyen_de_transport != 'Train'")
    emissions_df_reduced_other = emissions_df_reduced_other[["Moyen_de_transport","Empreinte carbone"]].groupby(["Moyen_de_transport"]).mean().reset_index()
    
    # On doit faire des subplots afin de pouvoir avoir des largeurs de colonnes différentes selon si c'est un train ou un autre moyen de transport
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Train", "Autres moyens de transport"], shared_yaxes=True, column_widths=[1, 4], horizontal_spacing=0)
    fig.add_trace(go.Bar(
        x=emissions_df_reduced_train["Moyen_de_transport"],
        y=emissions_df_reduced_train["Empreinte carbone"],
        name='Train',
        marker_color=colors_moyens_de_transport['Train']
    ), row=1, col=1)
    
    for index, row in emissions_df_reduced_other.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Moyen_de_transport"]],
            y=[row["Empreinte carbone"]],
            name=row["Moyen_de_transport"],
            marker_color=colors_moyens_de_transport[row["Moyen_de_transport"]]
        ), row=1, col=2)
        
    fig.update_layout(
        barcornerradius=15,
        yaxis_title='Empreinte carbone moyenne (kgCO2e/km)',
        legend_title='Moyen de transport',
        title='Empreinte carbone moyenne par km pour chaque moyen de transport',
    )
    
    return fig

def generate_widget(emissions_df: pd.DataFrame) -> dcc.Graph:
    layout = html.Div([
        dcc.Markdown('''
        ## Émissions de CO2 par moyen de transport
        
        On cherche à comparer les émissions de CO2 pour chaque moyen de transport en fonction 
        de la distance parcourue. On peut voir le détail des émissions selon le trajet et le moyen de transport.
        '''),
        dcc.Graph(
            id='emissions-graph',
            figure=generate_line_chart(emissions_df)
        ),
        dcc.Markdown('''
        On constate que le train est le moyen de transport le plus écologique, et que la distance n'est pas le seul
        facteur à prendre en compre pour l'avion notamment. En effet la relation entre la distance et les émissions de CO2
        pour l'avion n'est pas linéaire.
        
        On peut aussi essayer de comparer les émissions moyennes par km pour chaque moyen de transport.
        '''),
        dcc.Graph(
            id='emissions-bar-graph',
            figure=generate_bar_chart(emissions_df)
        ),
        dcc.Markdown('''
        Ici, le train est de loin le moyen de transport le plus écologique, suivi par l'autocar et la voiture électrique.
        La voiture thermique et l'avion sont les moyens de transport les plus polluants.
        On peut également voir que selon le type de train que l'on prend, les émissions de CO2 peuvent varier.
        Le TGV est entièrement électrique, et donc beaucoup moins polluant que le TER ou l'intercité, qui sont moins propres à 
        cause des locomotives diesels sur les lignes non électrifiées ainsi que des bus qui font partie de l’offre TER.
        ''')
    ])
    
    return layout