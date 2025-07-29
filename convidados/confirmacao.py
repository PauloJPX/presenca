from flask import render_template, request, redirect, url_for, flash
from . import convidados_bp
from models import conectar


@convidados_bp.route('/confirmar/<int:evento_id>/<int:convidado_id>', methods=['GET', 'POST'])
def confirmar_presenca_link(evento_id, convidado_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    # Buscar dados do evento e do convidado
    cursor.execute("SELECT nome_evento, convite_path FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()

    cursor.execute("SELECT nome, confirmado FROM convidados WHERE id = %s AND id_evento = %s", (convidado_id, evento_id))
    convidado = cursor.fetchone()

    if not evento or not convidado:
        return "Evento ou convidado não encontrado", 404

    # Se o método for POST, atualizar o status de confirmação
    if request.method == 'POST':
        escolha = request.form.get('confirmacao')  # 'sim' ou 'nao'
        if escolha == 'sim':
            confirmado = 2  # Confirmado pelo convidado
        else:
            confirmado = 3  # Mantém como não confirmado (ou poderia ser outro código, como 3 para recusado)

        cursor.execute("""
            UPDATE convidados
            SET confirmado = %s
            WHERE id = %s AND id_evento = %s
        """, (confirmado, convidado_id, evento_id))
        conexao.commit()

        cursor.close()
        conexao.close()
        return render_template('confirmacao_resultado.html', confirmado=(escolha == 'sim'), nome=convidado['nome'])

    cursor.close()
    conexao.close()

    return render_template('confirmar_presenca.html',
                           evento=evento,
                           convidado=convidado,
                           evento_id=evento_id,
                           convidado_id=convidado_id)


#função para confirmar presença com acompanhantes
@convidados_bp.route('/confirmar_com_acompanhantes/<int:evento_id>/<int:convidado_id>', methods=['GET', 'POST'])
def confirmar_com_acompanhantes(evento_id, convidado_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    # Buscar dados do evento e do convidado "pai"
    cursor.execute("SELECT nome_evento, convite_path FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()

    cursor.execute("SELECT nome, confirmado FROM convidados WHERE id = %s AND id_evento = %s", (convidado_id, evento_id))
    convidado_pai = cursor.fetchone()

    if not evento or not convidado_pai:
        return "Evento ou convidado não encontrado", 404

    if request.method == 'POST':
        escolha = request.form.get('confirmacao')  # 'sim' ou 'nao'

        if escolha == 'sim':
            # Atualiza o convidado pai para confirmado
            cursor.execute("""
                UPDATE convidados SET confirmado = 2 WHERE id = %s AND id_evento = %s
            """, (convidado_id, evento_id))
            conexao.commit()

            # Agora inserir acompanhantes adicionais, que vierem do formulário (exemplo: lista de nomes, telefones, observações)
            acompanhantes = request.form.getlist('acompanhantes[]')  # nomes
            telefones = request.form.getlist('telefones[]')
            obs_list = request.form.getlist('obs[]')

            for i in range(len(acompanhantes)):
                nome_acomp = acompanhantes[i].strip()
                telefone_acomp = telefones[i].strip()
                obs_acomp = obs_list[i].strip()

                if nome_acomp:  # só insere se tiver nome
                    cursor.execute("""
                        INSERT INTO convidados (id_evento, nome, telefone, obs, confirmado, origem)
                        VALUES (%s, %s, %s, %s, 2, %s)
                    """, (evento_id, nome_acomp, telefone_acomp, obs_acomp, convidado_id))
            conexao.commit()

            cursor.close()
            conexao.close()
            return render_template('confirmacao_resultado.html', confirmado=True, nome=convidado_pai['nome'])

        else:
            # Recusou
            cursor.execute("""
                UPDATE convidados SET confirmado = 3 WHERE id = %s AND id_evento = %s
            """, (convidado_id, evento_id))
            conexao.commit()
            cursor.close()
            conexao.close()
            return render_template('confirmacao_resultado.html', confirmado=False, nome=convidado_pai['nome'])

    cursor.close()
    conexao.close()

    return render_template('confirmar_com_acompanhantes.html', evento=evento, convidado=convidado_pai, evento_id=evento_id, convidado_id=convidado_id)
