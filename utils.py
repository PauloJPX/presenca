import re

def limpar_telefone_br(telefone_raw):
    """
    Limpa e padroniza o número de telefone brasileiro.
    Ex: (21) 99999-8888 → 5521999998888
    """
    # Remove tudo que não é número
    numeros = re.sub(r'\D', '', telefone_raw)

    # Se já começa com 55, deixa assim
    if numeros.startswith("55"):
        return numeros

    # Se tem 11 dígitos (DDD + número), adiciona 55
    elif len(numeros) == 11:
        return "55" + numeros

    # Se tiver 9 dígitos ou menos, está incompleto
    else:
        return None  # ou lançar erro, dependendo do seu caso
