from flask import render_template, request, redirect, session
from . import auth_bp


from models import conectar

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        con = conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM USUARIOS WHERE email = %s AND senha_hash = %s", (email, senha))
        usuario = cur.fetchone()
        con.close()

        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['tipo_plano'] = usuario.get('tipo_plano', 'free')  # carrega o plano na sessão
            return redirect('/eventos')
        else:
            msg = 'Credenciais inválidas.'

    return render_template('login.html', msg=msg)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    msg = ''
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not nome or not email or not senha:
            msg = 'Preencha todos os campos.'
        else:
            con = conectar()
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM USUARIOS WHERE email = %s", (email,))
            if cur.fetchone():
                msg = 'Email já cadastrado.'
            else:
                cur.execute("INSERT INTO USUARIOS (nome, email, senha_hash) VALUES (%s, %s, %s)",
                            (nome, email, senha))
                con.commit()
                con.close()
                return redirect('/login')
    return render_template('registrar.html', msg=msg)
