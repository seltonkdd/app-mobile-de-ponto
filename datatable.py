import flet as ft
import sqlite3

table_pontos =ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text('')),
        ft.DataColumn(ft.Text('ID')),
        ft.DataColumn(ft.Text('Ponto')),
        ft.DataColumn(ft.Text('Usuário'))
    ],
    rows=[], visible=False, key='pontos'
)

table_users = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text('')),
        ft.DataColumn(ft.Text('ID')),
        ft.DataColumn(ft.Text('Usuários')),
        ft.DataColumn(ft.Text('Senhas'))
    ],
    rows = [], visible=False, key='users'
)

def populate_table(table, keys, data):
    table.rows.clear()
    for values in data:
        row_data = dict(zip(keys, values))

        remove_icon = ft.IconButton(ft.icons.DELETE, on_click=lambda e, row=row_data:delete_data(e, row, table))
        row_cells = [ft.DataCell(remove_icon)]

        row_cells.extend(
            [ft.DataCell(ft.Text(str(row_data[field]))) for field in keys]
        )

        table.rows.append(ft.DataRow(cells=row_cells))

def delete_data(e, data, table):
    table_name = table.key
    try:
        id = data['id']
        conn = sqlite3.connect('databases/dbponto.db', check_same_thread=False)
        c = conn.cursor()
        c.execute(f'DELETE from {table_name} WHERE id=?', (id,))
        conn.commit()
        conn.close()
        show_db()
        table.update()
        
    except sqlite3.Error as error:
        print(f'An error ocurred: {error}')

def show_db():
    keys_pontos = ['id', 'ponto', 'user']
    keys_users = ['id', 'users', 'password']
    try:
        conn = sqlite3.connect('databases/dbponto.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT * FROM pontos')
        pontos = c.fetchall()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        conn.close()

        populate_table(table_pontos, keys_pontos, pontos)
        populate_table(table_users, keys_users, users)

    except sqlite3.Error as error:
        print(f'An error ocurred no show_db: {error}')


table_collumn = ft.Column([ft.Row([table_pontos, table_users], scroll='always')], scroll='auto', height=300)