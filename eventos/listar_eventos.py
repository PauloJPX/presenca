from flask import render_template, session, redirect
from . import eventos_bp
from models import conectar


@eventos_bp.route('/')
def listar_eventos():
    if 'usuario_id' not in session:
        return redirect('/login')

    con = conectar()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM EVENTOS WHERE id_usuario = %s", (session['usuario_id'],))
    eventos = cur.fetchall()
    con.close()
    
    return render_template('eventos.html', eventos=eventos, nome=session.get('usuario_nome'),tipo_plano=session.get('tipo_plano', 'free'))
