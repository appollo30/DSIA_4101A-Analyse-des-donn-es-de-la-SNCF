from get_data.helper import get_data

if __name__ == "__main__":
    url = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/formes-des-lignes-du-rfn/exports/geojson?lang=fr&timezone=Europe%2FParis"
    file_name = "formes-des-lignes-du-rfn.geojson"

    get_data(url, file_name)