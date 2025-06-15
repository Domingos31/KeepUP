import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialização da BD
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
app.secret_key = '24e23c43d423c434343vfghfgd'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        if not email or not password:
            flash('Preencha todos os campos!', 'error')
        else:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if row and check_password_hash(row[0], password):
                session['user'] = email
                return redirect(url_for('calendario'))
            else:
                flash('Credenciais inválidas!', 'error')

    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registar', methods=['GET', 'POST'])
def registar():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if not all([name, email, password, confirm_password]):
            flash('Preencha todos os campos!', 'error')
        elif len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres!', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem!', 'error')
        else:
            hashed_password = generate_password_hash(password)
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                               (name, email, hashed_password))
                conn.commit()
                conn.close()
                flash('Conta criada com sucesso! Faça login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Este email já está registado.', 'error')

    return render_template('registar.html')

@app.route('/recuperar-password')
def recuperar_password():
    return render_template('recuperar-password.html')

@app.route('/calendario')
def calendario():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'error')
        return redirect(url_for('login'))
    return render_template('calendario.html')

@app.route('/user/<username>')
def show_user(username):
    return f"Bem-vindo, {username}!"

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

if __name__ == "__main__":
    app.run(debug=True)
