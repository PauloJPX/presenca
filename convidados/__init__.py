from flask import Blueprint
convidados_bp = Blueprint('convidados', __name__, url_prefix='/convidados')
from . import painel_evento
from . import cadastro
from . import convite
from . import confirmacao



