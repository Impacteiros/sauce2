import os
import psycopg2
import hashlib
from datetime import datetime

DATABASE_URL = "dbname=sauce user=foo password=pass host=localhost port=5432"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS funcionario (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(100),'
            'usuario VARCHAR(100),'
            'senha VARCHAR(255),'
            'cargo VARCHAR(20),'
            'ativo BOOLEAN)'
)

cur.execute('CREATE TABLE IF NOT EXISTS usuario (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(100),'
            'celular VARCHAR(11),'
            'senha VARCHAR(255))'
            )

cur.execute('CREATE TABLE IF NOT EXISTS produto (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(100),'
            'preco numeric(10, 2),'
            'descricao VARCHAR(100),'
            'url_imagem VARCHAR(255),'
            'categoria VARCHAR(20),'
            'ativo BOOLEAN,'
            'disponivel BOOLEAN)'
            )

cur.execute('CREATE TABLE IF NOT EXISTS adicional (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(50),'
            'preco numeric(10, 2),'
            'url_imagem VARCHAR(255),'
            'ativo BOOLEAN,'
            'disponivel BOOLEAN)')

cur.execute('CREATE TABLE IF NOT EXISTS pedido ('
            'id SERIAL PRIMARY KEY,'
            'id_cliente INTEGER,'
            'ids_lanches VARCHAR(100),'
            'total NUMERIC(5, 2),'
            'data TIMESTAMP,'
            'atendente VARCHAR(20),'
            'cupom VARCHAR(22),'
            'mesa INTEGER)'
)

cur.execute('CREATE TABLE IF NOT EXISTS cupom (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(50),'
            'valor NUMERIC(5, 2),'
            'ativo BOOLEAN)')


conn.commit()

class Cliente:
    def __init__(self, id, nome, celular, senha):
        self.id = id
        self.nome = nome
        self.celular = celular
        self.__senha = senha

    def limpar_db():
        cur.execute("DELETE FROM usuario;")

    def get_cliente(celular):
        cur.execute('SELECT * FROM usuario WHERE usuario.celular = %s', (celular,))
        result = cur.fetchone()
        if result == None:
            return None
        return Cliente(result[0], result[1], result[2])
    
    def cadastrar_cliente(nome, celular, senha):
        cliente_cadastrado = Cliente.get_cliente(celular)
        if cliente_cadastrado is None:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            insert_query = 'INSERT INTO usuario (nome, celular, senha) VALUES (%s, %s, %s)'
            values = (nome, celular, senha_hash)
            cur.execute(insert_query, values)
            conn.commit()
            return True
        return False

    def validar_login(usuario, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cur.execute('SELECT * FROM usuario WHERE usuario.celular = %s AND usuario.senha = %s', (usuario, senha_hash))
        validation = cur.fetchone()

        if validation == None:
            return False
        return Cliente(validation[0], validation[1], validation[2])

class Funcionario:
    def __init__(self, id, nome, usuario, senha, cargo):
        self.id = id
        self.nome = nome
        self.usuario = usuario
        self.usuario = usuario
        self.__senha = senha
        self.cargo = cargo

    def cadastrar_funcionario(nome, usuario, senha, cargo):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        insert_query = 'INSERT INTO funcionario (nome, usuario, senha, cargo, ativo) VALUES (%s, %s, %s, %s, %s)'
        values = (nome, usuario, senha_hash, cargo, True)
        cur.execute(insert_query, values)
        conn.commit()

    def get_funcionario(usuario):
        cur.execute('SELECT * FROM funcionario WHERE funcionario.usuario = %s', (usuario,))
        result = cur.fetchone()
        if result == None:
            return None
        return result

    def validar_login(usuario, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cur.execute('SELECT * FROM funcionario WHERE funcionario.usuario = %s AND funcionario.senha = %s', (usuario, senha_hash))
        validation = cur.fetchone()

        if validation == None:
            return False
        return validation

class Produto:
    def __init__(self, id, nome, preco, descricao, url_imagem, categoria, ativo, disponivel):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.descricao = descricao
        self.url_imagem = url_imagem
        self.categoria = categoria
        self.ativo = ativo
        self.disponivel = disponivel

    def adicionar_produto(nome, descricao, preco, categoria, url_imagem):
        try:
            insert_query = 'INSERT INTO produto (nome, preco, descricao, categoria, url_imagem, ativo, disponivel) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            values = (nome, preco, descricao, categoria, url_imagem, True, True)
            cur.execute(insert_query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar o produto: {str(e)}")
            return False
        
    def remover_produto(id):
        try:
            cur.execute(f"UPDATE produto SET ativo = False WHERE id = {id};")
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao remover o produto: {str(e)}")
            return False

    def get_lanches():
        lanches = []
        cur.execute("SELECT * FROM produto WHERE produto.categoria = 'hamburguer' AND produto.ativo = True")
        dados = cur.fetchall()
        for produto in dados:
            lanches.append(Produto(produto[0], produto[1], produto[2], produto[3], produto[4], produto[5], produto[6], produto[7]))
        return lanches
        
    def get_lanche(id):
        cur.execute(f"SELECT * FROM produto WHERE produto.categoria = 'hamburguer' AND produto.ativo = True AND produto.id = {id}")
        result = cur.fetchone()
        if result == None:
            return None
        return Produto(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])

    def get_bebidas():
        bebidas = []
        cur.execute("SELECT * FROM produto WHERE produto.categoria = 'bebida' AND produto.ativo = True")
        dados = cur.fetchall()
        for produto in dados:
            bebidas.append(Produto(produto[0], produto[1], produto[2], produto[3], produto[4], produto[5], produto[6], produto[7]))
        return bebidas

    def editar_produto(id, nome, preco, descricao, url_imagem):
        try:
            cur.execute(f"UPDATE produto SET nome = '{nome}', preco = {preco}, descricao = '{descricao}', url_imagem = '{url_imagem}' WHERE id = {id};")
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao editar o produto: {str(e)}")
            return False

class Adicional:
    def __init__(self, id, nome, preco, url_imagem, ativo, disponivel):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.url_imagem = url_imagem
        self.ativo = ativo
        self.disponivel = disponivel

    def get_adicionais():
        cur.execute("SELECT * FROM adicional WHERE adicional.ativo = True")
        return cur.fetchall()

    def adicionar_adicional(nome, preco, url_imagem):
        try:
            insert_query = 'INSERT INTO adicional (nome, preco, url_imagem, ativo, disponivel) VALUES (%s, %s, %s, %s, %s)'
            values = (nome, preco, url_imagem, True, True)
            cur.execute(insert_query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar o adicional: {str(e)}")
            return False
        
    def get_adicional(id):
        cur.execute(f"SELECT * FROM adicional WHERE adicional.ativo = True AND adicional.id = {id}")
        result = cur.fetchone()
        if result == None:
            return None
        return Adicional(result[0], result[1], result[2], result[3], result[4], result[5])