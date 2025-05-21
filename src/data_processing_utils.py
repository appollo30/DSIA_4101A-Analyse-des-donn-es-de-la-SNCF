import pandas as pd
import numpy as np
import geopandas as gpd

def process_shapes(shapes_df : pd.DataFrame) -> pd.DataFrame:
    """
    Voir notebooks/1_shapes.ipynb
    Traitement des données de formes-des-lignes-du-rfn.geojson
    On ne se concentre que sur les lignes exploitées par la SNCF, car il s'agit du libellé
    le plus courant.

    Args:
        shapes_df (pd.DataFrame): DataFrame contenant les données de formes-des-lignes-du-rfn.geojson

    Returns:
        pd.DataFrame: Dataframe traitée.
    """
    relevant_columns = ["code_ligne", "libelle", "geometry","pk_debut_r","pk_fin_r"] # On garde les colonnes qui peuvent servir comme clé primaire
    shapes_df_processed = shapes_df[relevant_columns].copy() # On garde une copie pour éviter de modifier l'original
    shapes_df_processed = shapes_df_processed.query("libelle == 'Exploitée'")  # Equivalent à shapes_df_processed[shapes_df_processed["libelle"] == "Exploitée"]
    shapes_df_processed = shapes_df_processed.reset_index(drop=True)
    return shapes_df_processed

def process_speeds(speeds_df : pd.DataFrame, ignore_na=True) -> pd.DataFrame:
    """
    Voir notebooks/2_speeds.ipynb
    Traitement des données de vitesse-maximale-nominale-sur-la-ligne.geojson
    
    Args:
        speeds_df (pd.DataFrame): DataFrame contenant les données de vitesse-maximale-nominale-sur-la-ligne.geojson
        ignore_na (bool): Si True, ignore les NaN dans la colonne v_max. Sinon, remplace les NaN par la vitesse max de la colonne.
        
    Returns:
        pd.DataFrame: Dataframe traitée.
    """
    relevant_columns = ["code_ligne", "lib_ligne", "v_max","geometry","pkd","pkf"] # On garde les colonnes qui peuvent être des clés primaires (voir 1_shapes.ipynb)
    speeds_df_processed = speeds_df[relevant_columns].copy() # On garde une copie pour éviter de modifier l'original
    speeds_df_processed["v_max"] = speeds_df_processed["v_max"].astype("Int64") # v_max est par défaut un object, on le convertit en int64
    # On convertit la vitesse max en entier nullable (la méthode .astype(int) ne fonctionne que pour les entiers non-nullables, 
    # voir https://stackoverflow.com/questions/21287624/convert-pandas-column-containing-nans-to-dtype-int)
    if ignore_na:
        speeds_df_processed = speeds_df_processed[~speeds_df_processed["v_max"].isna()]
        # Si on ignore les NaN, on supprime les lignes qui en contiennent
    else:
        max_speed = speeds_df_processed["v_max"].max()
        speeds_df_processed["v_max"] = speeds_df_processed["v_max"].fillna(max_speed)
        # Si on ne les ignore pas, on remplace les NaN par la vitesse max de la colonne
    speeds_df_processed = speeds_df_processed.reset_index(drop=True)
    # On renomme les colonnes pkd et pkf en pk_debut_r et pk_fin_r pour être cohérent avec le fichier shapes
    speeds_df_processed = speeds_df_processed.rename(columns={"pkd":"pk_debut_r","pkf":"pk_fin_r"})
    return speeds_df_processed

def merge_shapes_speeds(shapes_df, speeds_df):
    """
    Voir notebooks/3_merge_shapes_speeds.ipynb
    Fusion des données traitées de formes-des-lignes-du-rfn.geojson et vitesse-maximale-nominale-sur-la-ligne.geojson
    On utilise la méthode sjoin_nearest de geopandas pour faire une jointure spatiale entre les deux dataframes.
    On utilise la distance entre les géométries pour faire la jointure, et on ne garde que les lignes qui sont à moins de 1e-10 de distance.
        
    Args:
        shapes_df (pd.DataFrame): DataFrame contenant les données de formes-des-lignes-du-rfn.geojson
        speeds_df (pd.DataFrame): DataFrame contenant les données de vitesse-maximale-nominale-sur-la-ligne.geojson
    Returns:
        pd.DataFrame: Dataframe fusionnée."""
    merged_df = gpd.sjoin_nearest(
        shapes_df,
        speeds_df,
        how="inner",
        max_distance=1e-10,
        distance_col="distance",
        lsuffix="shapes",
        rsuffix="speeds"
    )
    
    merged_df = merged_df.drop_duplicates(subset=["geometry"])
    
    relevant_columns = [
        "code_ligne_shapes",
        "geometry",
        "v_max",
        "lib_ligne"
    ]
    merged_df = merged_df[relevant_columns].copy()
    merged_df = merged_df.rename(columns={"code_ligne_shapes": "code_ligne"})
    
    return merged_df

def process_frequentations(frequentations_df : pd.DataFrame) -> pd.DataFrame:
    """
    Voir notebooks/4_frequentation_gares.ipynb
    Traitement des données de frequentation-gares.csv
    
    La transformation consiste à passer d'un format large, où chaque année est une colonne distincte, 
    à un format long, où chaque année est une ligne distincte. Cela facilite les comparaisons et l'analyse 
    des données sur plusieurs années.
    
    Args:
        frequentations_df (pd.DataFrame): DataFrame contenant les données de frequentation-gares.csv
    Returns:
        pd.DataFrame: Dataframe traitée.
    """
    years = [str(year) for year in range(2015, 2024)]
    frequentations_df_processed = pd.DataFrame()
    for year in years:
        year_df = frequentations_df[["Nom de la gare", "Code UIC", "Code postal", "Segmentation DRG", f"Total Voyageurs {year}", f"Total Voyageurs + Non voyageurs {year}"]]
        year_df = year_df.assign(Année=year) # On peut faire year_df["Année"] = year mais c'est moins propre, on a le warning SettingWithCopyWarning.
        year_df = year_df.rename(columns={f"Total Voyageurs {year}":"Total Voyageurs", f"Total Voyageurs + Non voyageurs {year}":"Total Voyageurs + Non Voyageurs"})
        frequentations_df_processed = pd.concat([frequentations_df_processed, year_df])
    frequentations_df_processed = frequentations_df_processed.sort_values(by=["Nom de la gare", "Année"]) # On trie par nom de gare et année pour avoir un affichage plus lisible
    frequentations_df_processed = frequentations_df_processed.drop(columns=["Nom de la gare"])
    frequentations_df_processed = frequentations_df_processed.reset_index(drop=True)
    return frequentations_df_processed

def process_gares(gares_df : pd.DataFrame) -> pd.DataFrame:
    """
    Voir notebooks/5_liste_gares.ipynb
    Traitement des données de liste-des-gares.geojson
    On ne garde que les gares qui sont ouvertes aux voyageurs et qui sont exploitées par la SNCF.
    
    Args:
        gares_df (pd.DataFrame): DataFrame contenant les données de liste-des-gares.geojson
    Returns:
        pd.DataFrame: Dataframe traitée.
    """
    gares_processed_df = gares_df.query("voyageurs == 'O'")
    gares_processed_df = gares_processed_df.drop(columns=["voyageurs"])
    gares_processed_df = gares_processed_df.reset_index(drop=True)
    gares_processed_df["fret"] = gares_processed_df["fret"].apply(lambda x: x == "O") # Par défaut, la colonne fret est un object, on la convertit en booléen
    # fret contient des valeurs "O" et "N", on les remplace par True et False

    # On ne garde que les colonnes qui nous intéressent
    relevant_columns = ["code_uic", "libelle", "fret", "code_ligne", "geometry"]
    gares_processed_df = gares_processed_df[relevant_columns].copy() # On garde une copie pour éviter de modifier l'original
    gares_processed_df = gares_processed_df.drop_duplicates(subset=["code_uic"]) # On supprime les doublons sur le code UIC, car il y a parfois plusieurs lignes pour une même gare
    
    return gares_processed_df

def merge_gares_frequentations(gares_df : pd.DataFrame, frequentations_df : pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Voir notebooks/6_merge_gares_frequentation.ipynb
    Fusion des données de gares et de fréquentation.
    On utilise la colonne code_uic pour faire la jointure entre les deux dataframes.
    
    Args:
        gares_df (pd.DataFrame): DataFrame contenant les données de gares
        frequentations_df (pd.DataFrame): DataFrame contenant les données de fréquentation
    Returns:
        gpd.GeoDataFrame: Dataframe fusionnée.
    """
    merged_df = gares_df.merge(frequentations_df, on="code_uic", how="left") 
    merged_df = merged_df.rename(columns={"Code postal":"code_postal"})
    merged_df["code_postal"] = merged_df["code_postal"].astype("Int64") # On convertit le code postal en entier pour éviter les problèmes de type
    merged_df = gpd.GeoDataFrame(merged_df, geometry=merged_df.geometry) # On convertit le DataFrame en GeoDataFrame
    return merged_df

def treat_and_merge_communes_population(communes_df,population_df):
    """
    Voir notebooks/6_merge_gares_frequentation.ipynb
    Traitement des données de communes-france.csv et insee-pop-communes.csv
    
    La transformation consiste à ne garder que les communes qui sont dans l'année 2024 et à ne garder que les colonnes qui nous
    intéressent. On renomme les colonnes pour qu'elles soient cohérentes pour le merging.
    
    Args:
        communes_df (pd.DataFrame): DataFrame contenant les données de communes-france.csv
        population_df (pd.DataFrame): DataFrame contenant les données de insee-pop-communes.csv
    Returns:
        pd.DataFrame: Dataframe traitée.
    """
    communes_df = communes_df.copy()
    population_df = population_df.copy()
    
    population_df = population_df.rename(columns={"DEPCOM" : "code_commune_INSEE"})
    
    communes_df["code_commune_INSEE"] = communes_df["code_commune_INSEE"].astype(str).str.zfill(5) # On s'assure que le code commune est bien au format 5 chiffres
    
    communes_population_df = communes_df.merge(population_df, how="left", on="code_commune_INSEE")
    
    relevant_columns = ["code_commune_INSEE", "nom_commune", "code_postal", "code_departement", "nom_departement", "nom_region", "PTOT"]
    
    communes_population_df = communes_population_df[relevant_columns].copy() # On garde une copie pour éviter de modifier l'original
    
    return communes_population_df

def merge_gares_communes(gares_frequentations_df: gpd.GeoDataFrame, communes_population_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Voir notebooks/6_merge_gares_frequentation.ipynb
    Fusion des données de gares et de communes.
    On utilise la colonne code_postal pour faire la jointure entre les deux dataframes.
    
    Args:
        gares_frequentations_df (gpd.GeoDataFrame): DataFrame contenant les données de gares et de fréquentation
        communes_population_df (pd.DataFrame): DataFrame contenant les données de communes et de population
    Returns:
        gpd.GeoDataFrame: Dataframe fusionnée.
    """
    merged_df = gares_frequentations_df.merge(communes_population_df, on="code_postal", how="left")
    merged_df = merged_df.drop_duplicates(subset=["code_uic", "Année"])
    return merged_df