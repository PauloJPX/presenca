from flask import Flask,redirect
from auth import auth_bp
from eventos import eventos_bp
from convidados import convidados_bp

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

app.register_blueprint(auth_bp)
app.register_blueprint(eventos_bp)
app.register_blueprint(convidados_bp)


@app.route('/')
def index():
    return redirect('/login')


if __name__ == '__main__':
#    app.run(debug=True)
     app.run(host='0.0.0.0', port=5000, debug=True)


