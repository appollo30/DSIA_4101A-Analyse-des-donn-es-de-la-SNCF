"""
Helper pour télécharger des fichiers depuis une URL
"""
import os
import requests

RAW_DATA_PATH = "./data/raw/" # Chemin du répertoire où enregistrer les données brutes
SOURCES_PATH = "./sources/" # Chemin du répertoire où sont situées les sources

def get_data(url : str, file_name : str):
    """
    Télécharge un fichier depuis une URL et l'enregistre dans 
    le répertoire ```./data/raw/<file_name>```
    
    Args:
        url (str): L'url du fichier à télécharger
        file_name (str): Le nom du fichier à enregistrer
    """
    relative_path = os.path.join(RAW_DATA_PATH, file_name)
    response = requests.get(url, timeout=10) # Timeout de 10 secondes
    with open(relative_path, "wb") as file:
        file.write(response.content)
