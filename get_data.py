"""
Script pour télécharger les données brutes depuis les sources
(voir le fichier config/sources.json)
"""
import os
import time
import json
import requests

RAW_DATA_PATH = "./data/raw/" # Chemin du répertoire où enregistrer les données brutes

# Chemin du fichier de configuration des sources pour les urls
SOURCES_PATH = "./config/sources.json"

def clear_data():
    """
    Supprime les fichiers du répertoire ```./data/raw/```
    """
    for file_name in os.listdir(RAW_DATA_PATH):
        file_path = os.path.join(RAW_DATA_PATH, file_name)
        os.remove(file_path)

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

def download_all_files():
    """
    Télécharge tous les fichiers depuis les sources
    """
    with open(SOURCES_PATH, "r", encoding="utf-8") as sources_file:
        sources = json.load(sources_file) # Liste des sources à télécharger

    for source in sources:
        name = source["name"]
        url = source["url"]
        t1 = time.time()
        download_file(url, name)
        t2 = time.time()
        print(f"Le fichier {name} a été téléchargé avec succès ({round(t2-t1,3)}s)")
        time.sleep(1/10)

if __name__ == "__main__":
    clear_data()
    download_all_files()
    