import os
import psycopg2
import hashlib
from datetime import datetime

DATABASE_URL = "dbname=sauce user=foo password=pass host=localhost port=5432"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

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
conn.commit()

def cadastrar_cliente(nome, celular, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    insert_query = 'INSERT INTO usuario (nome, celular, senha) VALUES (%s, %s, %s)'
    values = (nome, celular, senha_hash)
    cur.execute(insert_query, values)
    conn.commit()

def cadastrar_funcionario(nome, usuario, senha, cargo):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    insert_query = 'INSERT INTO funcionario (nome, usuario, senha, cargo, ativo) VALUES (%s, %s, %s, %s, %s)'
    values = (nome, usuario, senha_hash, cargo, True)
    cur.execute(insert_query, values)
    conn.commit()

def cadastrar_produto(nome, descricao, preco, categoria, url_imagem):
    insert_query = 'INSERT INTO produto (nome, preco, descricao, categoria, url_imagem, ativo) VALUES (%s, %s, %s, %s, %s, %s)'
    values = (nome, preco, descricao, categoria, url_imagem, True)
    cur.execute(insert_query, values)
    conn.commit()

lista_lanches = cur.execute("SELECT * FROM produto WHERE produto.categoria = 'hamburguer' AND produto.ativo = True")
