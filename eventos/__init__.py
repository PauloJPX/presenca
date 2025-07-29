from flask import Blueprint

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')
from . import listar_eventos, criar_evento, excluir_evento
