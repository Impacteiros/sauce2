import psycopg2
import hashlib

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
            'senha VARCHAR(255),'
            'endereco VARCHAR(3))'
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
            'ativo BOOLEAN)'
            )

cur.execute('CREATE TABLE IF NOT EXISTS endereco (id SERIAL PRIMARY KEY,'
            'id_cliente VARCHAR(10),'
            'rua VARCHAR(255),'
            'numero INT,'
            'complemento VARCHAR(255),'
            'bairro VARCHAR(255),'
            'cidade VARCHAR(255) DEFAULT\'Campo Grande\','
            'cep VARCHAR(10))'
            )

conn.commit()

class Cliente:
    def __init__(self, id, nome, celular, senha):
        self.id = id
        self.nome = nome
        self.celular = celular
        self.__senha = senha

    def get_cliente(celular):
        cur.execute(f"SELECT * FROM usuario WHERE usuario.celular = '{celular}';")
        result = cur.fetchone()
        if result is None:
            return None
        res = {"id": result[0], "nome": result[1], "celular": result[2]}
        return res
    
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

        if validation is None:
            return False
        res = {"id": validation[0], "nome": validation[1], "celular": validation[2]}
        return res

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
        if result is None:
            return None
        return result

    def validar_login(usuario, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cur.execute('SELECT * FROM funcionario WHERE funcionario.usuario = %s AND funcionario.senha = %s', (usuario, senha_hash))
        validation = cur.fetchone()

        if validation is None:
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
            lanche = {"id": produto[0], "nome": produto[1], "preco": produto[2], "descricao": produto[3], "url_imagem": produto[4], "categoria": produto[5], "ativo": produto[6], "disponivel": produto[7]}
            lanches.append(lanche)
        return lanches
        
    def get_produto(id):
        cur.execute(f"SELECT * FROM produto WHERE produto.ativo = True AND produto.id = {id}")
        result = cur.fetchone()
        if result is None:
            return None
        res = {"id": result[0], "nome": result[1], "preco": result[2], "descricao": result[3], "url_imagem": result[4], "categoria": result[5], "ativo": result[6], "disponivel": result[7]}
        return res

    def get_bebidas():
        bebidas = []
        cur.execute("SELECT * FROM produto WHERE produto.categoria = 'bebida' AND produto.ativo = True")
        dados = cur.fetchall()
        for produto in dados:
            bebida = {"id": produto[0], "nome": produto[1], "preco": produto[2], "descricao": produto[3], "url_imagem": produto[4], "categoria": produto[5], "ativo": produto[6], "disponivel": produto[7]}
            bebidas.append(bebida)
        return bebidas

    def editar_produto(id, nome, descricao, preco, categoria, url_imagem, disponivel):
        try:
            cur.execute(f"UPDATE produto SET nome = '{nome}', preco = {preco}, descricao = '{descricao}', url_imagem = '{url_imagem}', categoria = '{categoria}', disponivel = '{disponivel}' WHERE id = {id};")
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
        adicionais = []
        cur.execute("SELECT * FROM adicional WHERE adicional.ativo = True")
        dados = cur.fetchall()
        for adicional in dados:
            res = {"id": adicional[0], "nome": adicional[1], "preco": adicional[2], "url_imagem": adicional[3], "ativo": adicional[4], "disponivel": adicional[5]}
            adicionais.append(res)
        return adicionais

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
        if result is None:
            return None
        return Adicional(result[0], result[1], result[2], result[3], result[4], result[5])
    
class Cupom:
    def __init__(self, id, nome, valor):
        self.id = id
        self.nome = nome
        self.valor = valor
        self.ativo = True

    def adicionar_cupom(nome, valor):
        insert_query = 'INSERT INTO cupom (nome, valor, ativo) VALUES (%s, %s, %s)'
        values = (nome, valor, True)
        cur.execute(insert_query, values)
        conn.commit()

    def remover_cupom(id):
        cur.execute(f"UPDATE cupom set ativo = FALSE WHERE id = {id}")
        conn.commit()

    def get_cupom(id):
        cur.execute(f"SELECT * FROM cupom WHERE cupom.ativo = True and cupom.id = {id}")
        result = cur.fetchone()
        if result is None:
            return None
        return {"id": result[0], "nome": result[1], "valor": result[2]}
    
    def get_cupons():
        cupons = []
        cur.execute("SELECT * FROM cupom WHERE cupom.ativo = True")
        dados = cur.fetchall()
        for cupom in dados:
            res = {"id": cupom[0], "nome": cupom[1], "valor": cupom[2]}
            cupons.append(res)
        return cupons
    
    def validar_cupom(nome):
        valor = 0
        cur.execute(f"SELECT * FROM cupom WHERE cupom.ativo = True AND cupom.nome = '{nome}'")
        dados = cur.fetchone()
        if dados:
            valor = float(dados[2])
        return valor

class Endereco:
    def __init__(self, id, rua, numero, complemento, bairro, cep):
        self.id = id
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cep = cep

    def cadastrar_endereco(id_cliente, rua, numero, complemento, bairro, cep):
        insert_query = 'INSERT INTO endereco (id_cliente, rua, numero, complemento, bairro, cep) VALUES (%s, %s, %s, %s, %s, %s)'
        values = (id_cliente, rua, numero, complemento, bairro, cep)
        cur.execute(insert_query, values)
        conn.commit()

    def get_endereco(id):
        cur.execute(f"SELECT * FROM endereco WHERE endereco.id = {id}")
        result = cur.fetchone()
        if result is None:
            return None
        return {"id_cliente": result[0], "rua": result[1], "numero": result[2], "complemento": result[3], "bairro": result[4], "cep": result[5]}
    
    def get_enderecos_cliente(id_cliente):
        enderecos = []
        cur.execute(f"SELECT * FROM endereco WHERE endereco.id_cliente = '{id_cliente}'")
        result = cur.fetchall()
        if result is None:
            return None
        for endereco in result:
            res = {"id": endereco[0], "id_cliente": endereco[1], "rua": endereco[2], "numero": endereco[3], "complemento": endereco[4], "bairro": endereco[5], "cidade": endereco[6], "cep": endereco[7]}
            enderecos.append(res)
        return enderecos

    def get_enderecos():
        cur.execute("SELECT * FROM endereco")
        dados = cur.fetchall()
        enderecos = []
        for endereco in dados:
            res = {"id": endereco[0], "rua": endereco[1], "numero": endereco[2], "complemento": endereco[3], "bairro": endereco[4], "cep": endereco[5]}
            enderecos.append(res)
        return enderecos
    
    def remover_endereco(id):
        cur.execute(f"DELETE FROM endereco WHERE endereco.id = {id}")
        conn.commit()