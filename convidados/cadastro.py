from flask import render_template, request, redirect, url_for, flash, session
from . import convidados_bp
from models import conectar  # ajuste para seu projeto
from utils import limpar_telefone_br  # ajuste para seu projeto
###
from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

@convidados_bp.route('/<int:evento_id>/listar/pdf')
def gerar_pdf_convidados(evento_id):
    filtro = request.args.get('filtro', 'todos')

    convidados,origem, nome_evento = buscar_convidados(evento_id, filtro)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Lista de Convidados - {nome_evento}")

    # Cabeçalho da tabela
    y = height - 80
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Nome")
    p.drawString(250, y, "Cortesia")
    p.drawString(330, y, "Confirmado")
    p.drawString(430, y, "Assinatura")
    y -= 20

    p.setFont("Helvetica", 11)
    for c in convidados:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Nome")
            p.drawString(250, y, "Cortesia")
            p.drawString(330, y, "Confirmado")
            p.drawString(430, y, "Assinatura")
            y -= 20
            p.setFont("Helvetica", 11)

        p.drawString(50, y, c['nome'])
        p.drawString(250, y, "Sim" if c['cortesia'] == 1 else "Não")

        status = {
            None: "Não Confirmado",
            0: "Não Confirmado",
            1: "Confirmado",
            2: "Confirmado",
            3: "Recusou"
        }
        p.drawString(330, y, status.get(c['confirmado'], "Desconhecido"))

        # Espaço para assinatura (linha)
        p.line(430, y - 5, 530, y - 5)

        y -= 20

    p.save()
    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=convidados_{evento_id}.pdf'
    return response

###

def pode_adicionar_convidado(evento_id):
    # Verifica se o plano do usuário é free
    tipo_plano = session.get('tipo_plano', 'free')
    if tipo_plano != 'free':
        return True  # outros planos podem adicionar à vontade

    # Conta quantos convidados já existem para o evento
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM convidados WHERE id_evento = %s", (evento_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    conexao.close()

    # Free: limite de 5 convidados
    return total < 5

@convidados_bp.route('/<int:evento_id>/cadastrar', methods=['GET', 'POST'])
def cadastrar_convidado(evento_id):
    if request.method == 'POST':
        if not pode_adicionar_convidado(evento_id):
            return render_template('erro.html', mensagem="Seu plano atual permite no máximo 5 convidados.")

        nome = request.form['nome']
        telefone = request.form['telefone']
        telefone = limpar_telefone_br(telefone)  # Limpa o telefone
        if telefone is None:
            flash('Telefone inválido. Use o formato (XX) XXXXX-XXXX.', 'danger')
            return redirect(url_for('convidados.cadastrar_convidado', evento_id=evento_id))
        
        obs = request.form['obs']

        # 👇 Novo campo: checkbox cortesia
        #cortesia = request.form.get('cortesia') == 'on'  # True se marcado, False se não
        cortesia = 1 if request.form.get('cortesia') == 'on' else 0
 
        if not nome or not telefone:
            flash('Nome e telefone são obrigatórios.', 'danger')
            return redirect(url_for('convidados.cadastrar_convidado', evento_id=evento_id))

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO convidados (id_evento, nome, telefone, obs, cortesia)
            VALUES (%s, %s, %s, %s, %s)
        """, (evento_id, nome, telefone, obs, cortesia))
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Convidado cadastrado com sucesso!', 'success')
        return redirect(url_for('convidados.cadastrar_convidado', evento_id=evento_id))

    return render_template('cadastrar_convidado.html', evento_id=evento_id)



def contar_convidados(evento_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM convidados WHERE id_evento = %s", (evento_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return total


@convidados_bp.route('/<int:evento_id>/importar', methods=['POST'])
def importar_convidados(evento_id):
    tipo_plano = session.get('tipo_plano', 'free')
    limite = 5 if tipo_plano == 'free' else None

    arquivo = request.files.get('arquivo')

    if not arquivo:
        flash('Nenhum arquivo selecionado.', 'warning')
        return redirect(url_for('convidados.cadastrar_convidado', evento_id=evento_id))

    total_existente = contar_convidados(evento_id)
    if limite and total_existente >= limite:
        return render_template('erro.html', mensagem="Seu plano atual permite no máximo 5 convidados.")

    inseridos = 0
    ignorados = 0

    conexao = conectar()
    cursor = conexao.cursor()

    for linha in arquivo.stream.read().decode('utf-8').splitlines():
        if limite and (total_existente + inseridos) >= limite:
            break  # já atingiu o limite permitido

        try:
            nome, telefone = map(str.strip, linha.split(','))
            telefone = limpar_telefone_br(telefone)
            if telefone is None:
                ignorados += 1
                continue

            cursor.execute("""
                INSERT INTO convidados (id_evento, nome, telefone)
                VALUES (%s, %s, %s)
            """, (evento_id, nome, telefone))
            conexao.commit()
            inseridos += 1
        except Exception:
            conexao.rollback()
            ignorados += 1

    cursor.close()
    conexao.close()

    mensagem = f'{inseridos} convidados importados com sucesso. {ignorados} ignorados.'
    if limite and (total_existente + inseridos) >= limite:
        mensagem += ' Limite de convidados do plano atingido.'

    return render_template('importacao_resultado.html', mensagem=mensagem, evento_id=evento_id)


#sera usado para buscar convidados com base no filtro e sera usado no rendere_template e na impressão
def buscar_convidados(evento_id, filtro='todos'):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    query = """
        SELECT id, nome, telefone, obs, confirmado, origem, cortesia
        FROM convidados
        WHERE id_evento = %s
    """
    params = [evento_id]

    if filtro == 'confirmados':
        query += " AND confirmado IN (1, 2)"
    elif filtro == 'nao_confirmados':
        query += " AND (confirmado IS NULL OR confirmado = 0)"
    elif filtro == 'recusados':
        query += " AND confirmado = 3"
    elif filtro == 'cortesia':
        query += " AND cortesia = 1"

    query += " ORDER BY nome"
    cursor.execute(query, params)
    convidados = cursor.fetchall()

    origem_por_id = {c['id']: c['nome'] for c in convidados}

    # Agora busca o nome do evento aqui dentro
    cursor.execute("SELECT nome_evento FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()
    nome_evento = evento['nome_evento'] if evento else 'Evento desconhecido'

    cursor.close()
    conexao.close()

    return convidados, origem_por_id, nome_evento

@convidados_bp.route('/<int:evento_id>/listar')
def listar_convidados(evento_id):
    filtro = request.args.get('filtro', 'todos')
    convidados, origem_por_id, nome_evento = buscar_convidados(evento_id, filtro)

    return render_template('listar_convidados.html',
                           convidados=convidados,
                           evento_id=evento_id,
                           nome_evento=nome_evento,
                           origem_por_id=origem_por_id,
                           filtro=filtro)




@convidados_bp.route('/<int:evento_id>/editar/<int:convidado_id>', methods=['GET', 'POST'])
def editar_convidado(evento_id, convidado_id):
    conexao = conectar()
    #cursor = conexao.cursor()
    cursor = conexao.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        obs = request.form['obs']
        cortesia = 1 if request.form.get('cortesia') == 'on' else 0
        cursor.execute("""
            UPDATE convidados
            SET nome = %s, telefone = %s, obs = %s, cortesia = %s
            WHERE id = %s AND id_evento = %s
        """, (nome, telefone, obs,cortesia, convidado_id, evento_id))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash('Convidado atualizado com sucesso!', 'success')
        return redirect(url_for('convidados.listar_convidados', evento_id=evento_id))

    cursor.execute("""
        SELECT nome, telefone, obs, cortesia
        FROM convidados
        WHERE id = %s AND id_evento = %s 
    """, (convidado_id, evento_id))
    convidado = cursor.fetchone()
    cursor.close()
    conexao.close()
    if not convidado:
        flash('Convidado não encontrado.', 'danger')
        return redirect(url_for('convidados.listar_convidados', evento_id=evento_id))
    return render_template('editar_convidado.html', convidado=convidado, evento_id=evento_id, convidado_id=convidado_id)


@convidados_bp.route('/<int:evento_id>/excluir/<int:convidado_id>', methods=['POST'])
def excluir_convidado(evento_id, convidado_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        DELETE FROM convidados
        WHERE id = %s AND id_evento = %s
    """, (convidado_id, evento_id))
    conexao.commit()
    cursor.close()
    conexao.close()
    flash('Convidado excluído com sucesso.', 'info')
    return redirect(url_for('convidados.listar_convidados', evento_id=evento_id))

@convidados_bp.route('/<int:evento_id>/confirmar/<int:convidado_id>', methods=['POST'])
def confirmar_convidado(evento_id, convidado_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE convidados
        SET confirmado = 1
        WHERE id = %s AND id_evento = %s
    """, (convidado_id, evento_id))
    conexao.commit()
    cursor.close()
    conexao.close()
    flash('Presença confirmada pelo dono do evento.', 'success')
    return redirect(url_for('convidados.listar_convidados', evento_id=evento_id))
