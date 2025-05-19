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