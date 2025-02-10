# App mobile de ponto
Aplicativo mobile de bater ponto, desenvolvido inteiramente em Python, utilizando Framework Flet para interface interativa com integração de API do Google Maps, CRUD usando SQlite3 e lidando com requisições via servidor usando Flask.

# Versão 0.9.5

# Pré-requisitos



Python 3.9+

> ## Bibliotecas

[Flet](https://flet.dev/docs/guides/python/getting-started/)

[SQLite3](https://www.sqlite.org/docs.html)

[Requests](https://pypi.org/project/requests/)

[Flask](https://flask.palletsprojects.com/en/stable/)

#### Faça a instalação do ambiente virtual via terminal
    python -m venv env
    .\env\Scripts\activate

#### Instale as bibliotecas
    pip install flet db-sqlite3 flask

# Funcionalidades

- Cadastro e Login de usuários, com email e senha, utilizando criptografia hash e validação de login
- Registro de pontos armazenado em banco de dados
- Tela de visualização da localização atual do usuário, integrado na API do Google Maps
- Requisição cliente-servidor usando Flask
- CRUD, criar, editar, ler e deletar registros e usuários


> ## Implementação

A interface gráfica foi criada usando o framework Flet, onde foi implementado funções em botões e ações chamadas pelo usuário. O banco de dados foi desenvolvido em SQLite3, com as tabelas `users` e `pontos`.
Também foi implementado a API do Google Maps para visualização da localização atual do usuário, obtido atráves do pacote `flet_geolocator`.
Para ocorrer a requisição na API do Google Maps, de modo que sua própria chave API não seja acessada pelo usuário, foi desenvolvido um backend de servidor intermediário para realiza-la sem ser diretamente pelo código do aplicativo.


# Como usar

> ## Passo a passo

#### Caso tenha uma API do Google Maps, adicione-a em `teste_server.py` (opcional):
    API_KEY = ''

#### Adicione seu servidor em `gps.py` (opcional):
    url = f'http://SEU.IP.SEU.IP/get_map_image?latitude={latitude}&longitude={longitude}&zoom=15&size=600x400&markers=color:red|label:S|{latitude},{longitude}&maptype=roadmap'

#### Rode seu servidor do Flask em `teste_server.py`, execute no terminal (opcional):
    python ./teste_server.py

#### Em outro terminal, execute:
    python ./main.py

#### Feito isso, a aplicação estará rodando

# Buildar para APK
#### Qualquer alteração posterior no código, será necessário buildar o apk novamente usando o Flet


>> ## Pré-requisitos

- [Flutter](https://docs.flutter.dev/get-started/install)
- [Android Studio](https://developer.android.com/studio?)
- Android SDK (Instalar dentro do Android Studio)
- [Git](https://git-scm.com/downloads)

> Passo a Passo

Mude o `teste_server.py` para um diretório de sua preferencia fora do diretório raiz, pois o Flet não aceita Frameworks externos como dependências no APK, veja mais na [documentação](https://flet.dev/docs/publish). 

No terminal, execute `flet build apk --include-packages flet_geolocator -vv` para começar o processo de contrução do APK.

Na nova pasta `./build/apk` será armazenado o APK criado.



### Espero que tenha entendido com a documentação, sinta-se livre para melhoras!
