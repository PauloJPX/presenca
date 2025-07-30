# 📋 Sistema de Confirmação de Presença

Este é um sistema web para **gestão de eventos e confirmação de presença**, desenvolvido com **Flask**. Ele permite o cadastro de eventos, convidados e envio de convites personalizados com link de confirmação.

---

## 🚀 Tecnologias Utilizadas

- Python
- Flask
- MySQL
- Jinja2
- HTML/CSS (via templates)

---

## 📦 Instalação e Execução

Siga os passos abaixo para rodar o sistema localmente:

### 1. Clone o repositório

```bash
git clone https://github.com/PauloJPX/presenca.git
cd presenca
python -m venv venv
venv\Scripts\activate  # No Windows
pip install -r requirements.txt
presenca/
├── app.py
├── requirements.txt
├── .gitignore
├── static/
├── templates/
├── auth/           # Módulo de autenticação
├── eventos/        # Módulo de eventos
├── convidados/     # Módulo de convidados
└── ...
