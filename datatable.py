import flet as ft

table_pontos =ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text('ID')),
        ft.DataColumn(ft.Text('Ponto')),
        ft.DataColumn(ft.Text('Usuário'))
    ],
    rows=[], key='pontos'
)

def populate_table(table, keys, data):
    table.rows.clear()
    for p in data:

        row_cells = [ft.DataCell(ft.Text(str(p[field]))) for field in keys]
        table.rows.append(ft.DataRow(cells=row_cells))

def show_db(pontos):
    keys_pontos = ['id', 'ponto', 'user_email']
    populate_table(table_pontos, keys_pontos, pontos)

table_collumn = ft.Column([ft.Row([table_pontos], scroll='always')], scroll='auto')