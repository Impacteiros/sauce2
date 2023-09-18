from database import Cliente, Produto, cur

# Testes CLIENTE
def test_limpar_db():
    cur.execute("DELETE FROM usuario;")

def test_cadastro():
    cadastro = Cliente.cadastrar_cliente("Iago", "11900000000", "safe_password_123")
    assert cadastro == True

def test_login_correto():
    login = Cliente.validar_login("11900000000", "safe_password_123")
    assert isinstance(login, dict)

def test_cadastro_duplicado():
    cadastro = Cliente.cadastrar_cliente("Iago", "11900000000", "safe_password_123")
    assert cadastro == False

def test_login_incorreto():
    login = Cliente.validar_login("11900000000", "555")
    assert login == False

def test_get_client():
    result = Cliente.get_cliente("11900000001")
    assert result == None

# TESTES PRODUTOS

def test_zerar_db():
    cur.execute("DELETE FROM produto;")
    cur.execute("SELECT setval('produto_id_seq', 1, false);")

def test_cadastro_produto():
    produto_1 = Produto.adicionar_produto("X-Burguer", "180g de CARNE BOVINA", "16.99", "hamburguer", "xburguer.jpg")
    produto_2 = Produto.adicionar_produto("Chicken", "180g Frango", "19.99", "hamburguer", "chicken.jpg")
    produto_3 = Produto.adicionar_produto("X-Salada", "180g de CARNE BOVINA", "21.99", "hamburguer", "salad.jpg")
    produto_4 = Produto.adicionar_produto("Veggie", "180g de CARNE DE SOJA", "23.99", "hamburguer", "veggie.png")
    produto_5 = Produto.adicionar_produto("Coca-Cola", "350ml de COCA-COLA", "3.99", "bebida", "cocacola.jpg")

    assert produto_1 == True
    assert produto_2 == True
    assert produto_3 == True
    assert produto_4 == True
    assert produto_5 == True

def test_get_produtos():
    lanches = Produto.get_lanches()
    assert len(lanches) == 4

    bebidas = Produto.get_bebidas()
    assert len(bebidas) == 1

# def test_remove_produto():
#     Produto.remover_produto(1)
#     lanches = Produto.get_lanches()
#     assert len(lanches) == 3

# def test_editar_produto_get_lanche():
#     Produto.editar_produto(2, "X-Baleia", 19.99, "Grandão", "x-baleia.png")
#     produto = Produto.get_lanche(2)
#     assert produto['nome'] == "X-Baleia"