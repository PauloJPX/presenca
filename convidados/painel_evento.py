from flask import session, render_template, redirect, url_for
from . import convidados_bp
from models import conectar


@convidados_bp.route('/evento/<int:evento_id>/painel')
def painel_evento(evento_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()
    cursor.close()
    conexao.close()

    if not evento:
        return "Evento não encontrado", 404

    return render_template('painel_evento.html', evento=evento)
