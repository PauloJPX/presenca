from flask import Blueprint, render_template, session, redirect
from models import conectar

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')



@eventos_bp.route('/')
def eventos():
    if 'usuario_id' not in session:
        return redirect('/login')

    con = conectar()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM EVENTOS WHERE id_usuario = %s", (session['usuario_id'],))
    eventos = cur.fetchall()
    con.close()

    return render_template('eventos.html', eventos=eventos, nome=session.get('usuario_nome'))






