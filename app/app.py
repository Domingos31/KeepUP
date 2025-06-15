import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '24e23c43d423c434343vfghfgd'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            allday INTEGER NOT NULL,
            creator_id INTEGER NOT NULL,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            permission TEXT NOT NULL,
            UNIQUE(event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# Helpers

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def add_event(title, category, start, end, allday, creator_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (title, category, start, end, allday, creator_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, category, start, end, int(allday), creator_id))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id

def share_event(event_id, user_id, permission):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO event_shares (event_id, user_id, permission)
            VALUES (?, ?, ?)
        ''', (event_id, user_id, permission))
    except sqlite3.IntegrityError:
        cursor.execute('''
            UPDATE event_shares SET permission = ?
            WHERE event_id = ? AND user_id = ?
        ''', (permission, event_id, user_id))
    conn.commit()
    conn.close()

def get_user_events(user_id):
    conn = get_db_connection()

    own_events = conn.execute('''
        SELECT * FROM events WHERE creator_id = ?
    ''', (user_id,)).fetchall()

    shared_events = conn.execute('''
        SELECT e.* FROM events e
        JOIN event_shares es ON e.id = es.event_id
        WHERE es.user_id = ?
    ''', (user_id,)).fetchall()

    conn.close()
    return own_events, shared_events

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        if not email or not password:
            flash('Preencha todos os campos!', 'error')
        else:
            user = get_user_by_email(email)
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user'] = user['email']
                return redirect(url_for('calendario'))
            else:
                flash('Credenciais inválidas!', 'error')

    return render_template('login.html')


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
                conn = get_db_connection()
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                             (name, email, hashed_password))
                conn.commit()
                conn.close()
                flash('Conta criada com sucesso! Faça login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Este email já está registado.', 'error')

    return render_template('registar.html')


@app.route('/calendario')
def calendario():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    own_events, shared_events = get_user_events(user_id)

    def event_to_dict(e):
        return {
            'id': e['id'],
            'title': e['title'],
            'category': e['category'],
            'start': e['start'],
            'end': e['end'],
            'allDay': bool(e['allday'])
        }

    events = [event_to_dict(e) for e in own_events + shared_events]

    return render_template('calendario.html', events=events)


@app.route('/criar_evento', methods=['POST'])
def criar_evento():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    title = request.form.get('title')
    category = request.form.get('category')
    start = request.form.get('start')
    end = request.form.get('end')
    allday = request.form.get('allDay') == 'true'

    if not title or not category or not start or not end:
        flash('Preencha todos os campos do evento.', 'error')
        return redirect(url_for('calendario'))

    add_event(title, category, start, end, allday, user_id)
    flash('Evento criado com sucesso!', 'success')
    return redirect(url_for('calendario'))


@app.route('/partilhar_evento', methods=['POST'])
def partilhar_evento():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    event_id = request.form.get('event_id')
    target_user_email = request.form.get('user_email')
    permission = request.form.get('permission')  # 'view' ou 'edit'

    if not event_id or not target_user_email or not permission:
        flash('Preencha todos os campos da partilha.', 'error')
        return redirect(url_for('calendario'))

    event_id = int(event_id)

    # Verifica se o utilizador atual é o criador do evento
    own_events, _ = get_user_events(user_id)
    if event_id not in [e['id'] for e in own_events]:
        flash('Sem permissão para partilhar este evento.', 'error')
        return redirect(url_for('calendario'))

    target_user = get_user_by_email(target_user_email)
    if not target_user:
        flash('Utilizador para partilha não encontrado.', 'error')
        return redirect(url_for('calendario'))

    share_event(event_id, target_user['id'], permission)
    flash('Evento partilhado com sucesso!', 'success')
    return redirect(url_for('calendario'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão terminada.', 'success')
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recuperar-password')
def recuperar_password():
    return render_template('recuperar-password.html')


@app.route('/user/<username>')
def show_user(username):
    return f"Bem-vindo, {username}!"


@app.route("/sobre")
def sobre():
    return render_template('sobre.html')


if __name__ == "__main__":
    app.run(debug=True)
