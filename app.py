import flet as ft
import requests, re
from gps import update_location, get_location_image_backend, get_geolocator
from datatable import table_collumn, show_db
from datetime import datetime

TOKEN = None
session = requests.Session()


def main(page: ft.Page):
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'
    page.window.height = 700
    page.window.width = 400

    snack_bar = ft.SnackBar(ft.Text())
    page.overlay.append(snack_bar)

    gl = get_geolocator()
    page.overlay.append(gl)

    timefield = ft.Ref[ft.Row]()

    nome = ft.TextField(label="Nome")
    email = ft.TextField(label="Email")
    senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

    senha_confirmada = ft.TextField(label="Confirme sua senha", password=True, 
                                    can_reveal_password=True)

    def show_snack_bar(message, color):
        #MOSTRAR BARRA DE AVISO
        snack_bar.content.value = message
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    def check_regex(input):
        emailPattern = r'[\w]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,6}'
        if re.search(emailPattern, input):
            return True
        else:
            return False

    def clean_fields(e):
        #LIMPAR CAMPOS DE TEXTO
        nome.value = ''
        email.value = ''
        senha.value = ''
        senha_confirmada.value = ''

    def toggle_sign_up(e):
        clean_fields(e)
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_signup)
        _stack_main.update()

    def toggle_login(e):
        clean_fields(e)
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_login)
        _stack_main.update()

    def toggle_main(e):
        clean_fields(e)
        listar_pontos()
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_main)
        _stack_main.controls.append(_tableview)
        _tableview.offset=ft.Offset(-5,0)
        _main.offset=ft.Offset(0,0)
        page.bottom_appbar = ft.BottomAppBar(
                            content=ft.Row([
                            ft.IconButton(icon=ft.icons.LIST_ALT, scale=1.5, on_click=toggle_tableview),
                            ft.IconButton(icon=ft.icons.LOCK_CLOCK, scale=1.5, on_click=animate_main)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=100), 
                            height=63)
        page.update()
        _stack_main.update()

    def animate_main(e):
        clean_fields(e)
        _tableview.offset=ft.transform.Offset(-5,0)
        _main.offset=ft.transform.Offset(0,0)
        _stack_main.update()

    def toggle_tableview(e):
        table_collumn.height = 500
        clean_fields(e)
        listar_pontos()
        _tableview.offset=ft.transform.Offset(0,0)
        _main.offset=ft.transform.Offset(2,0)
        _stack_main.update()

    def hide_timefield():
        timefield.current.visible = False
        timefield.current.update()

    def handle_time_change(e):
        timefield.current.visible = True
        timefield.current.controls[0].value = time_picker.value
        page.update()

    def reset_time_picker():
        current_time = datetime.now() 
        time_picker.value = str(current_time.hour) + ':' + str(current_time.minute)
        time_picker.update() 

    def handle_get_current_position(e):
        #OBTER LOCALIZAÇÃO DO USUARIO E ARMAZENAR NA IMAGEM
        try:
            p = gl.get_current_position()
            update_location(p.latitude, p.longitude)
            get_location_image_backend(e)
            _main.update()
        except Exception as error:
            show_snack_bar(error, 'red')

    def login_usuario(e):
        global TOKEN
        if not email.value or not senha.value:
            show_snack_bar("O campo email e senha são obrigatórios.", 'red')
            return
        data = {"email": email.value, "senha": senha.value}
        resposta = requests.post("http://127.0.0.1:5000/api/auth/login", json=data)
        result = resposta.json()
        if resposta.status_code == 200:
            TOKEN = result['token']

            toggle_main(e)
            handle_get_current_position(e)
        else:
            show_snack_bar(result['erro'], 'red')
            return

    def cadastrar_usuario(e):
        # if not check_regex(email.value):
        #     show_snack_bar('Insira um email válido.', 'red')
        #     return
        # if not len(senha.value) >= 8:
        #     show_snack_bar('A senha deve pelo menos conter 8 caracteres.', 'red')
        #     return
        if senha.value != senha_confirmada.value:
            show_snack_bar('As senhas divergem', 'red')
            return
        data = {"nome": nome.value, "email": email.value, "senha": senha.value}
        resposta = requests.post("http://127.0.0.1:5000/api/auth/register", json=data)
        result = resposta.json()
        toggle_login(e)
        if resposta.status_code == 201:
            show_snack_bar(result['mensagem'], 'green')
        else:
            show_snack_bar(result['erro'], 'red')
        page.update()

    def registrar_ponto():
        global TOKEN

        session.headers.update({"Authorization": f"Bearer {TOKEN}"})

        current_date = datetime.now().date()
        datetime_str = f'{current_date} {time_text.value}'
        data = {"ponto": datetime_str}

        resposta = session.post("http://127.0.0.1:5000/api/pontos", json=data)
        result = resposta.json()
        if resposta.status_code == 201:
            show_snack_bar(result['mensagem'], 'green')
        else:
            show_snack_bar(result['erro'], 'red')

    def listar_pontos():
        global TOKEN

        session.headers.update({"Authorization": f"Bearer {TOKEN}"})

        resposta = session.get('http://127.0.0.1:5000/api/users/pontos')
        result = resposta.json()
        if resposta.status_code == 200:
            show_db(result['Pontos'])
        else:
            show_snack_bar(result['erro', 'red'])


    time_picker = ft.TimePicker(
        confirm_text="Confirm",
        error_invalid_text="Time out of range",
        on_change=handle_time_change
    )
    time_text = ft.Text(style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    timefield.current = ft.Row(
        [
            time_text,
            ft.TextButton("Salvar", on_click=lambda e: (registrar_ponto(), hide_timefield())),
        ], alignment=ft.MainAxisAlignment.CENTER
    )

    # container de login
    _login = ft.Container(content=ft.Column(
            [
                ft.Text("Faça Login", weight=50, size=50, text_align=ft.TextAlign.CENTER),
                email,
                senha,
                ft.ElevatedButton("Entrar", width=100, on_click=login_usuario),
                ft.TextButton('Cadastre-se!', on_click=toggle_sign_up)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=10)
    
    # container de cadastro
    _signup = ft.Container(content=ft.Column(
            [
                ft.Text("Faça seu cadastro", weight=30, size=35, text_align=ft.TextAlign.CENTER),
                nome,
                email,
                senha,
                senha_confirmada,
                ft.ElevatedButton('Cadastre-se!', on_click=cadastrar_usuario),
                ft.TextButton('Voltar para o login', on_click=toggle_login)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=10)
    
    _main = ft.Container(
                        height=page.height,
                        expand=True,
                        offset=ft.transform.Offset(0,0),
                        animate_offset=ft.animation.Animation(400,curve='easyIn'),
                        content=ft.Column(
        [   
            ft.IconButton(icon=ft.icons.ARROW_BACK, alignment=ft.alignment.top_left, padding=0, 
                          on_click=toggle_login),
            ft.Text('Bata seu ponto', size=30, weight=10),
            ft.Card(width=page.width,
                    elevation=20,
                    content=ft.Column([
                        ft.Container(ft.Image("assets/imagem_gps.png", scale=0.899), 
                                expand=True, alignment=ft.alignment.center),
                        ft.Row([ft.TextButton("Localização", on_click=handle_get_current_position), 
                                ft.TextButton("Ponto", on_click=lambda e: (reset_time_picker(), 
                                                                           page.open(time_picker)))], 
                                alignment=ft.MainAxisAlignment.END)], 
                                horizontal_alignment='center')
                    ),
            timefield.current
        ]
    ), alignment=ft.alignment.center)

    _tableview = ft.Container(
        top=0,
        offset=ft.transform.Offset(-5,0),
        animate_offset=ft.animation.Animation(400,curve='easyIn'),
        content=ft.Column([
                    ft.IconButton(icon=ft.icons.ARROW_BACK, alignment=ft.alignment.top_left, padding=0, 
                          on_click=toggle_login),
                    table_collumn
                          ])
    )

    timefield.current.visible = False
    _stack_main = ft.Stack(controls=[_login], alignment=ft.alignment.center)

    page.add(_stack_main, time_picker)

ft.app(target=main)
