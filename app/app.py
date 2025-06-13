from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '24e23c43d423c434343vfghfgd'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Preencha todos os campos!', 'error')
        elif len(password) < 6:
            flash('Senha deve ter 6+ caracteres!', 'error')
        elif password != "123456":
            flash('Senha incorreta!', 'error')
        # Simular acesso a database
        elif username == "admin" and password == "123456":
            return redirect(url_for('dashboard'))
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
        
        # Validações
        if not all([name, email, password, confirm_password]):
            flash('Preencha todos os campos!', 'error')
        elif len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres!', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem!', 'error')
        else:
            # Aqui você normalmente salvaria no banco de dados
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('registar.html')

@app.route('/recuperar-password')
def recuperar_password():
    return render_template('recuperar-password.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/user/<username>')
def show_user(username):
    return f"Bem-vindo, {username}!"

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

if __name__ == "__main__":
    app.run(debug=True)
    