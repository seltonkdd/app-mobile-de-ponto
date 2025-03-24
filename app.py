import flet as ft
import requests, re, os
from gps import update_location, get_location_image_backend, get_geolocator
from datatable import table_column, show_db
from datetime import datetime

# TOKEN INICIALIZADO PARA AUTENTICAÇÃO
token = None
# SESSÃO INICIALIZADA PARA ENVIAR TOKEN AO CABEÇALHO
session = requests.Session()

IMAGE_PATH = 'assets/imagem_gps.png'


def main(page: ft.Page):
   # Configuração inicial da página
    page.window.width, page.window.height = 400, 800
    page.vertical_alignment = page.horizontal_alignment = "center"
    page.expand = True
    page.overlay.append(ft.SnackBar(ft.Text()))

    gl = get_geolocator()
    page.overlay.append(gl)

    timefield = ft.Ref[ft.Row]()

    nome, email, senha, senha_confirmada = [ft.TextField(label=lbl) for lbl in ("Nome", "Email", "Senha", "Confirme sua senha")]
    senha.password = senha_confirmada.password = True
    senha.can_reveal_password = senha_confirmada.can_reveal_password = True

    snack_bar = page.overlay[0]
    
    settings_dlg = lambda e: ft.AlertDialog(
        adaptive=True,
        content=ft.Text('O app precisa de sua permissão de localização. Ative-a nas configurações.'),
        actions=[ft.TextButton(text="Abrir configurações", on_click=e)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    img = ft.Image(IMAGE_PATH, scale=0.899)

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
            page.update()

    def show_snack_bar(message, color):
        snack_bar.content.value, snack_bar.bgcolor, snack_bar.open = message, color, True
        page.update()

    def check_regex(input):
        return re.search(r'\w+@[a-zA-Z0-9]+\.[a-zA-Z]{2,6}', input) is not None

    def clean_fields(e):
        for field in [nome, email, senha, senha_confirmada]:
            field.value = ""

    def toggle_sign_up(e):
        # MOSTRAR TELA DE CADASTRO
        clean_fields(e)
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_signup)
        _stack_main.update()

    def toggle_login(e):
        # MOSTRAR TELA DE LOGIN
        clean_fields(e)
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_login)
        _stack_main.update()
        bottom_appbar.visible = False
        page.update()

    def toggle_main(e):
        # MOSTRAR TELA PRINCIPAL
        clean_fields(e)
        listar_pontos()
        _stack_main.controls.clear()
        _stack_main.update()
        _stack_main.controls.append(_main)
        _stack_main.controls.append(_tableview)
        _tableview.offset=ft.Offset(-5,0)
        _main.offset=ft.Offset(0,0)
        bottom_appbar.visible = True
        page.update()
        _stack_main.update()

    def animate_main(e):
        # ANIMAR NAVEGAÇÃO DA TELA PRINCIPAL
        clean_fields(e)
        _tableview.offset=ft.transform.Offset(-5,0)
        _main.offset=ft.transform.Offset(0,0)
        _stack_main.update()

    def toggle_tableview(e):
        # MOSTRAR TELA DA TABELA
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
            if os.path.exists(IMAGE_PATH):
                os.remove(IMAGE_PATH)

            p = gl.get_current_position()
            update_location(p.latitude, p.longitude)
        except:
            page.open(app_settings_dlg)
            _main.update()
        finally:
            get_location_image_backend() 

    async def handle_open_app_settings(e):
        #ABRIR AS CONFIGURAÇÕES DE LOCALIZAÇÃO
        await gl.open_app_settings_async()
        page.close(app_settings_dlg)

    app_settings_dlg = settings_dlg(handle_open_app_settings)

    def login_usuario(e):
        global token
        if not email.value or not senha.value:
            show_snack_bar("O campo email e senha são obrigatórios.", 'red')
            return
        data = {"email": email.value, "senha": senha.value}
        resposta = requests.post("http://127.0.0.1:5000/api/auth/login", json=data)
        result = resposta.json()
        if resposta.status_code == 200:
            token = result['token']

            toggle_main(e)
            handle_get_current_position(e)
        else:
            show_snack_bar(result['erro'], 'red')
            return

    def cadastrar_usuario(e):
        if not check_regex(email.value):
            show_snack_bar('Insira um email válido.', 'red')
            return
        if not len(senha.value) >= 8:
            show_snack_bar('A senha deve pelo menos conter 8 caracteres.', 'red')
            return
        if senha.value != senha_confirmada.value:
            show_snack_bar('As senhas divergem', 'red')
            return
        data = {"nome": nome.value, "email": email.value, "senha": senha.value}
        resposta = requests.post("http://127.0.0.1:5000/api/auth/register", json=data)
        result = resposta.json()
        if resposta.status_code == 201:
            show_snack_bar(result['mensagem'], 'green')
            toggle_login(e)
        else:
            show_snack_bar(result['erro'], 'red')
            return
        page.update()

    def registrar_ponto():
        global token

        session.headers.update({"Authorization": f"Bearer {token}"})

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
        global token

        session.headers.update({"Authorization": f"Bearer {token}"})

        resposta = session.get('http://127.0.0.1:5000/api/users/pontos')
        result = resposta.json()
        if resposta.status_code == 200:
            show_db(result['Pontos'])
        else:
            show_snack_bar(result['erro'], 'red')


    bottom_appbar = ft.BottomAppBar(
        content=ft.Row([
        ft.IconButton(icon=ft.icons.LIST_ALT, scale=1.5, on_click=toggle_tableview),
        ft.IconButton(icon=ft.icons.LOCK_CLOCK, scale=1.5, on_click=animate_main)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=100), 
        height=63,
    )

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
    _login = ft.Container(
        content=ft.Column(
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
        padding=10
    )
    
    _stack_main = ft.Stack(controls=[_login], alignment=ft.alignment.center)
    
    # container de cadastro
    _signup = ft.Container(
        content=ft.Column(
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
        padding=10
    )
    
    # container principal
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
                ft.Card(
                    width=page.width, 
                    elevation=20, 
                    content=ft.Column(
                        [ 
                            ft.Container(img, expand=True, alignment=ft.alignment.center),
                            ft.Row(
                                [
                                    ft.TextButton("Localização", on_click=handle_get_current_position), 
                                    ft.TextButton("Ponto", on_click=lambda e: (reset_time_picker(), page.open(time_picker)))
                                ], alignment=ft.MainAxisAlignment.END
                                )
                        ], 
                        horizontal_alignment='center'
                    )
                ), 
                timefield.current
            ]
        ), alignment=ft.alignment.center
    )

    # container da tabela
    _tableview = ft.Container(
        height=page.height,
        alignment=ft.alignment.center,
        expand=True,
        offset=ft.transform.Offset(-5,0),
        animate_offset=ft.animation.Animation(400,curve='easyIn'),
        content=ft.Column(
            [
                ft.IconButton(icon=ft.icons.ARROW_BACK, alignment=ft.alignment.top_left, padding=0, on_click=toggle_login),
                ft.Container(content=table_column, alignment=ft.alignment.center, margin=0, height=500)     
            ], 
            expand=True, 
            alignment=ft.alignment.center
        )
    )

    _about = ft.Container(
        height=page.height,
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            [   
                ft.Container(
                    margin=0,
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Text('MasterPoint', size=30, style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
                            ft.Text('Versão 1.0.0', opacity=0.5),
                            ft.Image('leading.png', color='grey', height=90, width=90),
                            ft.Text('© 2025 MasterPoint Inc.', opacity=0.5)
                         ], 
                         alignment=ft.MainAxisAlignment.CENTER, 
                         horizontal_alignment='center'
                    )
                )
            ]
        )
    )

    def route_change(event: ft.RouteChangeEvent):
        routes = {
            '/': ft.View(
                '/',
                [
                    ft.AppBar(
                        title=ft.Text('MasterPoint', size=25),
                        center_title=True,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        actions=[
                            ft.PopupMenuButton(items=[
                                ft.PopupMenuItem(icon=ft.icons.INFO,
                                                text='Sobre',
                                                on_click=lambda _: page.go('/about'))
                                                ])
                        ], automatically_imply_leading=False
                    ), _stack_main, time_picker, bottom_appbar
                ], vertical_alignment='center', horizontal_alignment='center'
            ),
            '/about': ft.View(
                    '/about',
                    [
                        ft.AppBar(
                            title=ft.Text('MasterPoint', size=25),
                            center_title=True,
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            actions=[
                                ft.PopupMenuButton(items=[
                                    ft.PopupMenuItem(icon=ft.icons.INFO,
                                                    text='Sobre',
                                                    on_click=lambda _: page.go('/about'))
                                ])
                            ]
                        ),
                        _about
                    ], vertical_alignment='center', horizontal_alignment='center'
                )
        }
        route = event.route
        if not any(view.route == page.route for view in page.views):
            if page.route in routes:
                page.views.append(routes[route])
        page.update()
    
    timefield.current.visible = False
    page.on_view_pop = view_pop
    page.on_route_change = route_change
    page.go('/')
    bottom_appbar.visible = False
    page.update()

ft.app(target=main)
