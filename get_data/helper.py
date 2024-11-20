import requests
import os

path = "./data/raw/"

def get_data(url, file_name):
    # Créer le répertoire parent s'il n'existe pas
    os.makedirs(path, exist_ok=True)
    relative_path = os.path.join(path, file_name)
    response = requests.get(url)
    with open(relative_path, "wb") as file:
        file.write(response.content)
