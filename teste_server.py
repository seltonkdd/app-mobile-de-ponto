import requests
from flask import Flask, request

app = Flask(__name__)

API_KEY = '' ## CHAVE API DO MAPS STATIC

@app.route('/get_map_image', methods=['GET'])
def get_map_image():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    zoom = request.args.get('zoom', 15)
    size = request.args.get('size', '600x400')
    markers = request.args.get('markers', f'color:red|label:S|{latitude},{longitude}')
    map_type = request.args.get('maptype', 'roadmap')
    
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom}&size={size}&markers={markers}&maptype={map_type}&key={API_KEY}"
    
    # FAZER A REQUISIÇÃO DA API DO MAPS
    response = requests.get(url)
    
    # RETORNA A IMAGEM NO SERVER
    return response.content, 200, {'Content-Type': 'image/png'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)