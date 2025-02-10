import flet as ft
import re
from db_table import create_table, save_data, validate_user, insert_user
from datetime import datetime
from datatable import table_pontos, table_users, show_db, table_collumn
from gps import update_location, get_location_image_backend, get_geolocator

#INICIALIZANDO CONEXÃO DO BANCO DE DADOS

def main(page: ft.Page):
    page.title = "App de Ponto"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

#### CRIANDO TABELA DO BANCO DE DADOS
    create_table()
    show_db()

#### INICIALIZANDO GEOLOCALIZADOR E SNACKBAR
    gl = get_geolocator()
    snack_bar = ft.SnackBar(ft.Text())
    page.overlay.append(gl)
    page.overlay.append(snack_bar)

#### INSTANCIANDO CAMPOS PARA INSERÇÃO DE DADOS
    email_input = ft.TextField(width=300, label="Insira seu email")
    password_input = ft.TextField(
        width=300, can_reveal_password=True, password=True, label="Insira sua senha")
    
    sign_up_email_input = ft.TextField(width=300, label="Insira seu email")
    sign_up_password_input = ft.TextField(
        width=300, can_reveal_password=True, password=True, label="Insira sua senha")
    sign_up_confirm_password_input = ft.TextField(
        width=300, can_reveal_password=True, password=True, label="Confirme sua senha")
    
    timefield = ft.Ref[ft.Row]()

    def check_regex(input):
        emailPattern = r'[\w]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,6}'
        if re.search(emailPattern, input):
            return True
        else:
            return False


    def show_snack_bar(message, color):
        #MOSTRAR BARRA DE AVISO
        snack_bar.content.value = message
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()


    def clean_fields(e):
        #LIMPAR CAMPOS DE TEXTO
        email_input.value = ''
        password_input.value = ''
        sign_up_email_input.value = ''
        sign_up_password_input.value = ''
        sign_up_confirm_password_input.value = ''

    
    settings_dlg = lambda e: ft.AlertDialog(
        adaptive=True,
        content=ft.Text('O app precisa de sua permissão de localização. Ative-a nas configurações.'),
        actions=[ft.TextButton(text="Abrir configurações", on_click=e)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    
    def handle_get_current_position(e):
        #OBTER LOCALIZAÇÃO DO USUARIO E ARMAZENAR NA IMAGEM
        try:
            p = gl.get_current_position()
            update_location(p.latitude, p.longitude)
            page.update()
        except:
            page.open(app_settings_dlg)
        try:
            get_location_image_backend(e)
        except Exception as error:
            show_snack_bar(error, 'red')    


    async def handle_open_app_settings(e):
        #ABRIR AS CONFIGURAÇÕES DE LOCALIZAÇÃO
        await gl.open_app_settings_async()
        page.close(app_settings_dlg)

    app_settings_dlg = settings_dlg(handle_open_app_settings)


    def login_usuario(e):
        #VALIDAR LOGIN DO USUARIO
        if not email_input.value or not password_input.value:
            show_snack_bar("O campo email e senha são obrigatórios.", 'red')
            return
        if validate_user(email_input.value, password_input.value):
            show_clockin(e)
            handle_get_current_position(e)
            page.update()
        else:
            show_snack_bar('Email ou senha inválidos', 'red')
            return


    def create_usuario(e):
        #CADASTRAR NOVO USUARIO NO BANCO DE DADOS
        if not sign_up_email_input.value or not sign_up_password_input.value:
            show_snack_bar("O campo email e senha são obrigatórios.", 'red')
            return
        if sign_up_password_input.value != sign_up_confirm_password_input.value:
            show_snack_bar('As senhas divergem.', 'red')
            return
        if not check_regex(sign_up_email_input.value):
            show_snack_bar('Insira um email válido.', 'red')
            return
        if not len(sign_up_password_input.value) >= 8:
            show_snack_bar('A senha deve pelo menos conter 8 caracteres.', 'red')
            return
        insert_user(sign_up_email_input.value, sign_up_password_input.value)
        show_snack_bar('Cadastro concluído.', 'green')
        clean_fields(e)
        sign_up_con.visible = False
        log_con.visible = True
        page.update()

#### ATUALIZAR VISUALIZAÇÃO DOS CONTROLES NA TELA###
    def hide_clockin(e):
        clean_fields(e)
        toggle_visibility(e, clockin=False)


    def show_clockin(e):
        toggle_visibility(e, clockin=True)


    def show_sign_up(e):
        log_con.visible = False
        sign_up_con.visible = True
        clean_fields(e)
        page.update()


    def hide_timefield(e):
        timefield.current.visible = False
        table_pontos.rows.clear()
        save_data(str(time_picker.value), email_input.value)
        page.update()


    def hide_table(e):
        table_pontos.visible = not table_pontos.visible
        table_users.visible = not table_users.visible
        page.update()


    def toggle_visibility(e, clockin):
        log_con.visible = not clockin
        sign_up_con.visible = False
        header.controls[0].visible = clockin
        header.controls[1].visible = clockin
        table_pontos.visible = clockin
        table_users.visible = False
        clockin_con.visible = clockin
        page.update()


    def handle_time_change(e):
        timefield.current.visible = True
        timefield.current.controls[0].value = time_picker.value
        page.update()
        

    def reset_time_picker():
        current_time = datetime.now() 
        time_picker.value = str(current_time.hour) + ':' + str(current_time.minute)
        time_picker.update() 


    #CONTROL DO PONTO
    timefield.current = ft.Row(
        [
            ft.TextField(
                "", width=100, text_align="center", bgcolor="#bfbfbf", color="black"
            ),
            ft.TextButton("Salvar", on_click=hide_timefield),
        ]
    )

    #CONTROL DA TELA DE LOGIN
    log_con = ft.Container(
        content=ft.Column(
            [
                ft.Text("Faça Login", weight=50, size=50, text_align=ft.TextAlign.CENTER),
                email_input,
                password_input,
                ft.ElevatedButton("Entrar", width=100, on_click=login_usuario),
                ft.TextButton('Cadastre-se!', on_click=show_sign_up)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=10
    )

    #CONTROL DA TELA DE CADASTRO
    sign_up_con = ft.Container(
        content=ft.Column(
            [
                ft.Text("Crie sua conta", weight=50, size=50, text_align=ft.TextAlign.CENTER),
                sign_up_email_input,
                sign_up_password_input,
                sign_up_confirm_password_input,
                ft.ElevatedButton("Cadastrar", width=150, on_click=create_usuario),
                ft.TextButton("Voltar para o login", on_click=lambda e: toggle_visibility(e, clockin=False))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=400,
        padding=20,
    )

    #CONTROL DAS HORAS
    time_picker = ft.TimePicker(
        confirm_text="Confirm",
        error_invalid_text="Time out of range",
        on_change=handle_time_change,
    )

    #CABEÇALHO
    header = ft.Row([ft.IconButton(icon=ft.icons.ARROW_BACK, visible=False, on_click=hide_clockin), 
                     ft.OutlinedButton('Trocar tabela', on_click=hide_table, visible=False)])

    #CONTROL DA TELA DE PONTO E TABELA DO BD
    clockin_con = ft.Card(
        elevation=20,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text('Bata seu ponto', size=30, weight=10),
                    ft.Container(
                        ft.Image(
                            "assets/imagem_gps.png",

                            fit=ft.ImageFit.CONTAIN,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Row(
                        [
                            ft.TextButton("Localização", on_click=handle_get_current_position),
                            ft.TextButton("Ponto", on_click=lambda e: (reset_time_picker(), page.open(time_picker))),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    timefield.current,
                    ft.Container(content=table_collumn, alignment=ft.alignment.center)
                ]
            ),
            padding=10,
        )
    )

    sign_up_con.visible = False
    clockin_con.visible = False
    timefield.current.visible = False

    page.add(
        ft.Row([header], alignment=ft.MainAxisAlignment.START),
        log_con,
        sign_up_con,
        clockin_con,
        time_picker
        )

ft.app(main)