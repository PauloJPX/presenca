from flask import redirect, session, flash, url_for
from . import eventos_bp
from models import conectar

@eventos_bp.route('/<int:evento_id>/excluir', methods=['POST'])
def excluir_evento(evento_id):
    if 'usuario_id' not in session:
        return redirect('/login')

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute(
            "DELETE FROM eventos WHERE id = %s AND id_usuario = %s",
            (evento_id, session['usuario_id'])
        )
        con.commit()
        flash('Evento excluído com sucesso.', 'success')
    except Exception as e:
        con.rollback()
        flash('Não foi possível excluir o evento. Verifique se há convidados vinculados.', 'danger')

    con.close()
    return redirect('/eventos')
