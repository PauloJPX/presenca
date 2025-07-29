from flask import render_template, request, redirect, session
from . import eventos_bp
from models import conectar


@eventos_bp.route('/criar', methods=['GET', 'POST'])
@eventos_bp.route('/criar', methods=['GET', 'POST'])
def criar_evento():
    if 'usuario_id' not in session:
        return redirect('/login')

    tipo_plano = session.get('tipo_plano', 'free')

    if tipo_plano in ['free', 'plus']:
        # Verifica se o usuário já tem algum evento
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM EVENTOS WHERE id_usuario = %s", (session['usuario_id'],))
        total_eventos = cur.fetchone()[0]
        con.close()

        if total_eventos >= 1:
            # Se já tem 1 evento, e for plano limitado, redireciona com aviso
            return render_template('erro.html', mensagem="Seu plano atual permite apenas 1 evento.")

    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        endereco = request.form['endereco']

        con = conectar()
        cur = con.cursor()
        cur.execute("INSERT INTO EVENTOS (nome_evento, data_evento, id_usuario,endereco) VALUES (%s, %s, %s,%s)",
                    (nome, data, session['usuario_id'], endereco))
        con.commit()
        con.close()
        return redirect('/eventos')

    return render_template('criar_evento.html')
