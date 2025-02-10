import flet as ft
import requests

latitude, longitude = None, None

def get_geolocator():
    gl = ft.Geolocator(
        location_settings=ft.GeolocatorSettings(
            accuracy=ft.GeolocatorPositionAccuracy.BEST
        ))
    return gl

def update_location(lat, lon):
    global latitude, longitude
    latitude, longitude = lat, lon
    
#### FAZER A REQUISIÇÃO PRO SERVIDOR/LOCALHOST E CONSEGUIR A IMAGEM GPS ARMAZENADA NELE
def get_location_image_backend(e):
    url = f'http://SEU.IP.SEU.IP/get_map_image?latitude={latitude}&longitude={longitude}&zoom=15&size=600x400&markers=color:red|label:S|{latitude},{longitude}&maptype=roadmap'
    response = requests.get(url)

    with open("assets/imagem_gps.png", "wb") as file:
        file.write(response.content)

        