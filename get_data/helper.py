import requests

path = "../data/raw/"

def get_data(url, file_name):
    response = requests.get(url)
    with open(path + file_name, 'wb') as f:
        f.write(response.content)