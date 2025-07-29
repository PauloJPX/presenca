import os
from flask import request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from . import convidados_bp
from models import conectar

@convidados_bp.route('/evento/<int:evento_id>/upload_convite', methods=['GET', 'POST'])
def upload_convite(evento_id):
    if request.method == 'POST':
        imagem = request.files.get('imagem')

        if not imagem or imagem.filename == '':
            flash('Nenhum arquivo selecionado.', 'warning')
            return redirect(request.url)

        if not imagem.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            flash('Formato inválido. Envie um .jpg ou .png.', 'danger')
            return redirect(request.url)

        nome_arquivo = 'convite.jpg'  # ou .png conforme extensão
        extensao = os.path.splitext(imagem.filename)[1]
        nome_arquivo = f'convite{extensao}'
        pasta_destino = os.path.join('static', 'convites', f'evento_{evento_id}')
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_absoluto = os.path.join(pasta_destino, nome_arquivo)
        imagem.save(caminho_absoluto)

        # Salvar caminho relativo no banco
        caminho_relativo = os.path.relpath(caminho_absoluto, 'static').replace('\\', '/')

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("UPDATE eventos SET convite_path = %s WHERE id = %s", (caminho_relativo, evento_id))
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Convite Salvo com sucesso!', 'success')
        return redirect(url_for('convidados.painel_evento', evento_id=evento_id))

    return render_template('upload_convite.html', evento_id=evento_id)
