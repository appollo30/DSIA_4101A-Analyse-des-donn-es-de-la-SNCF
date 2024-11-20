"""
Module pour télécharger des données depuis une URL et les enregistrer
dans data/raw/
"""
import os
import json
import requests

RAW_DATA_PATH = "../data/raw/" # Chemin du répertoire où enregistrer les données brutes

def download_file(url : str, file_name : str):
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

# Chemin du fichier de configuration des sources pour les urls
SOURCES_PATH = "../config/sources.json"

with open(SOURCES_PATH, encoding="r") as sources_file:
    sources = json.load(sources_file) # Liste des sources à télécharger

for source in sources:
    download_file(source["url"], source["name"])
    print("Le fichier " + source["name"] + " a été téléchargé avec succès.")
