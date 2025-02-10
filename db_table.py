import sqlite3
import os
import hashlib
from datatable import show_db

db_directory = 'databases'
if not os.path.exists(db_directory):
    os.makedirs(db_directory)

def create_table():
    try:
        conn = sqlite3.connect(os.path.join(db_directory, 'dbponto.db'), check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT NOT NULL,
                  password TEXT NOT NULL,
                  CONSTRAINT unique_email UNIQUE (email)
                  )''')
        c.execute('''CREATE TABLE IF NOT EXISTS pontos (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ponto TIME NOT NULL,
                  email_ID CHAR,
                  CONSTRAINT fk_ponto_name_idx FOREIGN KEY (email_ID) REFERENCES users(email)
                  )''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f'An error ocurred: {e}')

def save_data(ponto, email):
    try:
        conn = sqlite3.connect(os.path.join(db_directory, 'dbponto.db'), check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT INTO pontos (ponto, email_ID) VALUES (?, ?)', (ponto, email))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f'An error ocurred no save_data: {e}')
    show_db()


def insert_user(email, senha):
    try:
        conn = sqlite3.connect(os.path.join(db_directory, 'dbponto.db'), check_same_thread=False)
        c = conn.cursor()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, senha_hash))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f'erro no insert_user: {e}')
    show_db()

def validate_user(email, senha):
    try:
        conn = sqlite3.connect(os.path.join(db_directory, 'dbponto.db'), check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE email = ?', (email,))
        result = c.fetchone()
        conn.close()
    except sqlite3.Error as e:
        print(f'erro no validate_user: {e}')
    if result:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        if senha_hash == result[0]:
            return True
    return False
    

   
        
    
    