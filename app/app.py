# from flask import Flask
# from flask import Flask, render_template
from Flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
# app.secret_key = 'sua_chave_secreta'  # Necessário para flash messages
app.secret_key = '24e23c43d423c434343vfghfgd'


@app.route('/login', methods=['POST'])
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
        # simular acesso a database
        elif username == "admin" and password == "123456":
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas!', 'error')

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')  # se tiveres uma página principal

@app.route('/registar')
def registar():
    return render_template('registar.html')

@app.route('/recuperar-password')
def recuperar_password():
    return render_template('recuperar-password.html')


@app.route('/dashboard')
def dashboard():
    # return "Página restrita - Dashboard"
    return render_template('index.html')
    

@app.route('/user/<username>')
def show_user(username):
    return f"Bem-vindo, {username}!"


@app.route("/sobre")
def sobre():
    return render_template('sobre.html')


@app.route('/busca', methods=['GET'])
def busca():
    termo = request.args.get('q')
    return f"Você buscou por: {termo}"




if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8000)
    app.run(debug=True)


    