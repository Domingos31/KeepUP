from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '24e23c43d423c434343vfghfgd'  # Em produção, usa uma chave mais segura

# ====================
# ROTA: LOGIN
# ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validações básicas (em produção, usar base de dados)
        if not username or not password:
            flash('Preencha todos os campos!', 'error')
        elif len(password) < 6:
            flash('A password deve ter pelo menos 6 caracteres.', 'error')
        elif username == "admin" and password == "123456":
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')

    return render_template('login.html')


# ====================
# ROTA: REGISTAR
# ====================
@app.route('/registar', methods=['GET', 'POST'])
def registar():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirmPassword')
        terms = request.form.get('terms')

        # Validações simples
        if not all([name, email, password, confirm]):
            flash('Todos os campos são obrigatórios!', 'error')
        elif password != confirm:
            flash('As passwords não coincidem.', 'error')
        elif len(password) < 8:
            flash('A password deve ter pelo menos 8 caracteres.', 'error')
        elif not terms:
            flash('Deve aceitar os termos e condições.', 'error')
        else:
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('login'))

    return render_template('registar.html')


# ====================
# OUTRAS ROTAS
# ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Deves criar este ficheiro HTML

@app.route('/recuperar-password')
def recuperar_password():
    return render_template('recuperar-password.html')

@app.route('/user/<username>')
def show_user(username):
    return f"Bem-vindo, {username}!"

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# ====================
# MAIN
# ====================
if __name__ == "__main__":
    app.run(debug=True)
