import pandas as pd
import geopandas as gpd
from src.data_processing_utils import process_gares, process_frequentations, treat_and_merge_communes_population

def generate_plot():
    gares_df = gpd.read_file("../../data/raw/liste-des-gares.geojson")
    frequentations_df = pd.read_csv("../../data/frequentation-gares.csv", sep=";")
    
    communes = pd.read_csv("../../data/raw/20230823-communes-departement-region.csv")
    
    