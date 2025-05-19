import pandas as pd

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

def process_frequentations(frequentations_df : pd.DataFrame) -> pd.DataFrame:
    """
    Voir notebooks/4_frequentation_gares.ipynb
    Traitement des données de fréquentation des gares.
    
    La transformation consiste à passer d'un format large, où chaque année est une colonne distincte, 
    à un format long, où chaque année est une ligne distincte. Cela facilite les comparaisons et l'analyse 
    des données sur plusieurs années.
    """
    years = [str(year) for year in range(2015, 2024)]
    frequentations_df_processed = pd.DataFrame()
    for year in years:
        year_df = frequentations_df[["Nom de la gare", "Code UIC", "Code postal", "Segmentation DRG", f"Total Voyageurs {year}", f"Total Voyageurs + Non voyageurs {year}"]]
        year_df = year_df.assign(Année=year) # On peut faire year_df["Année"] = year mais c'est moins propre, on a le warning SettingWithCopyWarning.
        year_df = year_df.rename(columns={f"Total Voyageurs {year}":"Total Voyageurs", f"Total Voyageurs + Non voyageurs {year}":"Total Voyageurs + Non Voyageurs"})
        frequentations_df_processed = pd.concat([frequentations_df_processed, year_df])
    frequentations_df_processed = frequentations_df_processed.sort_values(by=["Nom de la gare", "Année"]) # On trie par nom de gare et année pour avoir un affichage plus lisible
    frequentations_df_processed = frequentations_df_processed.drop(columns=["Code UIC", "Code postal"])
    frequentations_df_processed = frequentations_df_processed.drop(columns=["Nom de la gare"])
    frequentations_df_processed = frequentations_df_processed.reset_index(drop=True)
    return frequentations_df_processed

def process_gares(gares_df):
    """
    Voir notebooks/5_liste_gares.ipynb
    Traitement des données de la liste des gares françaises.
    On ne garde que les gares qui sont ouvertes aux voyageurs et qui sont exploitées par la SNCF.
    """
    gares_processed_df = gares_df.query("voyageurs == 'O'")
    gares_processed_df = gares_processed_df.drop(columns=["voyageurs"])
    gares_processed_df = gares_processed_df.reset_index(drop=True)
    gares_processed_df["fret"] = gares_processed_df["fret"].apply(lambda x: x == "O") # Par défaut, la colonne fret est un object, on la convertit en booléen
    # fret contient des valeurs "O" et "N", on les remplace par True et False

    # On ne garde que les colonnes qui nous intéressent
    relevant_columns = ["code_uic", "libelle", "fret", "code_ligne", "geometry"]
    gares_processed_df = gares_processed_df[relevant_columns].copy() # On garde une copie pour éviter de modifier l'original
    
    return gares_processed_df