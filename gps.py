import flet_geolocator as fg
import requests

def get_geolocator():
    gl = fg.Geolocator(
        location_settings=fg.GeolocatorSettings(
            accuracy=fg.GeolocatorPositionAccuracy.BEST
        ))
    return gl

#### FAZER A REQUISIÇÃO PRO SERVIDOR/LOCALHOST E CONSEGUIR A IMAGEM GPS ARMAZENADA NELE
def get_location_image_backend(latitude, longitude):
    url = f'https://seltonkdd.pythonanywhere.com/api/get_map_image?latitude={latitude}&longitude={longitude}&zoom=15&size=600x400&markers=color:red|label:S|{latitude},{longitude}&maptype=roadmap'
    response = requests.get(url)

    with open('assets/imagem_gps.png', "wb") as file:
        file.write(response.content)

        