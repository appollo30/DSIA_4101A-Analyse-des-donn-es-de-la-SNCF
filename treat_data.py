import pandas as pd
import geopandas as gpd

import src.data_processing_utils as data_utils

def main():
    """
    Fonction pour le traitement et l'enregistrement des données.
    
    """
    # Chargement des données
    # 1_shapes.ipynb et 2_speeds.ipynb
    shapes = gpd.read_file("data/raw/formes-des-lignes-du-rfn.geojson")
    speeds = gpd.read_file("data/raw/vitesse-maximale-nominale-sur-ligne.geojson")
    
    processed_shapes = data_utils.process_shapes(shapes)
    processed_speeds = data_utils.process_speeds(speeds)
    
    processed_shapes.to_csv("data/processed/shapes.csv", index=False)
    processed_speeds.to_csv("data/processed/speeds.csv", index=False)
    # 3_merge_shapes_speeds.ipynb
    shapes_speeds = data_utils.merge_shapes_speeds(processed_shapes, processed_speeds)
    shapes_speeds.to_csv("data/processed/shapes_speeds.csv", index=False)
    
    # 4_frequentation_gares.ipynb
    frequentations = pd.read_csv('data/raw/frequentation-gares.csv', sep=';')
    processed_frequentations = data_utils.process_frequentations(frequentations)
    processed_frequentations.to_csv("data/processed/frequentations.csv", index=False)
    
    # 5_liste_gares.ipynb
    gares = gpd.read_file('data/raw/liste-des-gares.geojson')
    processed_gares = data_utils.process_gares(gares)
    processed_gares.to_csv("data/processed/gares.csv", index=False)
    
    # 6_merge_gares_frequentation.ipynb
    communes = pd.read_csv('data/raw/20230823-communes-departement-region.csv')
    population = pd.read_csv('data/raw/insee-pop-communes.csv', sep=';')
    
    communes_population = data_utils.treat_and_merge_communes_population(communes, population)
    communes_population.to_csv("data/processed/communes_population.csv", index=False)
    
if __name__ == "__main__":
    main()
