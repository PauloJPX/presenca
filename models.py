# aqui tem funçoes genericas que todo mundo pode usar

from mysql.connector import connect

#função que conecta ao banco de dados
#não é necessário importar o mysql.connector, pois já está importado aqui
def conectar():
    return connect(
        host='localhost',
        user='root',
        password='@J2ptpaulo@',
        database='presenca'
    )