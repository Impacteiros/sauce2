from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO
from backup import backup_file
import database
import eventlet

app = Flask(__name__)
app.secret_key = "!yw2gC8!BeM3"
app.config['SECRET_KEY'] = "!yw2gC8!BeM3"

socketio = SocketIO(app)

lanches = database.lista_lanches
bebidas = database.lista_bebidas
adicionais = database.lista_adicionais
cupons = database.lista_cupom
cupom_nome = None
pedidos = database.lista_pedidos

lista_carrinho = {}
pedidos_cozinha = {}


def validar_perm():
    if session:
        if session['usuario'][1] == 'administrador':
            return True
    return False

@socketio.on('atualizacao')
def atualizar_cozinha():
    socketio.emit('atualizacao', {'data': "Dados atualizados"})

@app.route("/selecao/", methods=["GET", "POST"])
def selecao():
    nome = request.form.get("pesquisa")
    session['mesa'] = request.form.get("mesa")
    id_cliente = request.form.get("id_cliente")
    sem_cadastro = request.form.get("sem_cadastro")
    if sem_cadastro:
        session['id_cliente'] = 0
        return redirect(url_for("home"))
    if id_cliente:
        session['id_cliente'] = id_cliente
        return redirect(url_for("home"))
    if nome:
        resultado = database.pesquisa_cliente(nome)
        if resultado:
            return render_template("selecao.html", clientes=resultado)
        return render_template("selecao.html", clientes=False)
    return render_template("selecao.html")

@app.route("/selecao/pesquisa", methods=["GET", "POST"])
def pesquisa_cliente():
    nome = request.form.get("pesquisa")
    resultado = database.pesquisa_cliente(nome)
    if resultado:
        return redirect(url_for("selecao"))
    return "Não encontrou"
    
@app.route("/backup")
def backup():
    if validar_perm():
        response = backup_file()
        return "Backup feito com sucesso"

@app.route("/cadastro/cliente", methods=["POST"])
def cadastro_cliente():
    nome_cliente = request.form.get("nome")
    endereco = request.form.get("endereco")
    celular = request.form.get("celular")
    email = request.form.get("email")
    database.cadastrar_cliente(nome_cliente, endereco, celular, email)
    session['cliente'] = nome_cliente
    flash("Cliente cadastrado com sucesso.", "sucesso")
    return redirect(url_for("home"))

@app.route("/")
def home():
    lanches = database.Produto.get_lanches()
    bebidas = database.Produto.get_bebidas()
    adicionais = database.lista_adicionais

    return render_template("index.html", lanches=lanches, bebidas=bebidas,
                           adicionais=adicionais)

@app.route("/login/", methods=["POST", "GET"])
def login():
    if 'usuario' in session:
        return redirect(url_for('home'))
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario and senha:
        validacao = database.Cliente.validar_login(usuario, senha)
        if validacao:
            session['usuario'] = [validacao[1], validacao[2]]
            return redirect(url_for("home"))
        return render_template("login.html", erro=validacao[1])
    return render_template("login.html")


@app.route("/cadastro/usuario", methods=["POST", "GET"])
def cadastro_usuario():
    nome = request.form.get("nome")
    celular = request.form.get("celular")
    senha = request.form.get("senha")
    if nome and senha and celular:
        cadastrado = database.validar_cadastro(celular)
        if cadastrado:
            return "Usuário em uso"
        database.cadastrar_cliente(nome, celular, senha)
        return "Cadastrado com sucesso"
    else:
        return render_template("cadastro_usuario.html")



@app.route("/cadastro/funcionario/", methods=["POST", "GET"])
def cadastro():
    if validar_perm():
        nome = request.form.get("nome")
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        cargo = request.form.get("cargo")
        if nome and usuario and senha and cargo:
            cadastrado = database.validar_cadastro(usuario)
            if cadastrado:
                return "Usuário em uso"
            database.cadastrar_funcionario(nome, usuario, senha, cargo)
            return "Cadastrado com sucesso"
        else:
            return render_template("cadastro_funcionario.html")
    return "Acesso negado"

@app.route("/cadastro/cupom", methods=["GET", "POST"])
def cadastro_cupom():

    if request.method == "POST":
        cupom = request.form.get("cupom")
        valor = request.form.get("valor")
        database.cadastrar_cupom(cupom, valor)
        return redirect(url_for("gerenciar"))
    return render_template("cadastro_cupom.html")


@app.route("/carrinho/", methods=["POST", "GET"])
def carrinho():
    cargo = session['usuario'][1]
    carrinho_render = []
    cupom = 0
    preco_total = 0
    for id in lista_carrinho:
        produto = database.session.query(database.Produto).get(id)
        preco_total += produto.preco
        carrinho_render.append(produto)

    if request.method == "POST":
        cupom = request.form.get("cupom")
        cupom_info = database.validar_cupom(cupom)
        if cupom_info:
            session['cupom'] = cupom_info.cupom
            cupom = float(cupom_info.valor)

        return render_template("carrinho.html", cargo=cargo, carrinho=carrinho_render, 
                            lanches=lanches, bebidas=bebidas, preco_total=float(preco_total), cupom=cupom)
    
    return render_template("carrinho.html", cargo=cargo, carrinho=carrinho_render, 
                           lanches=lanches, bebidas=bebidas, preco_total=float(preco_total), cupom=cupom)

@app.route("/carrinho/adicionar/<id>", methods=["GET", "POST"])
def adicinar_carrinho(id):
    adicionais = {}

    for nome, qtd in request.form.items():
        adicionais[nome] = int(qtd)

    produto = database.get_produto(id)
    nome = produto.nome
    flash(f"Você adicionou {nome} no carrinho", "adicionado")
    lista_carrinho[id] = adicionais
    return redirect("/")

@app.route("/carrinho/remover/<id>")
def remover_carrinho(id):
    lista_carrinho.pop(id)
    return redirect("/carrinho")

@app.route("/carrinho/enviar/", methods=["POST", "GET"])
def enviar_cozinha():
    mesa_numero = session['mesa']
    produtos_enviar = []
    atualizar_cozinha()

    if "cupom" in session:
        cupom = session["cupom"]
    else:
        cupom = "Nenhum"

    for id in lista_carrinho:
        query_result = database.session.query(database.Produto).get(id)
        produtos_enviar.append({"nome": query_result.nome, "id": id, "preco": query_result.preco, "id_cliente": session['id_cliente'], "adicionais": lista_carrinho[id], "cupom": cupom})
    
    pedidos_cozinha[mesa_numero] = produtos_enviar

    lista_carrinho.clear()
    session.pop('mesa')
    session.pop('id_cliente')
    if "cupom" in session:
        session.pop("cupom")
    flash("Pedido enviado para produção.", "sucesso")
    return redirect(url_for("selecao"))

@app.route("/deslogar/")
def deslogar():
    session.clear()
    return redirect("/login/")


@app.route("/debug/")
def debug():
    return pedidos_cozinha

@app.route("/gerenciar/")
def gerenciar():
    cupons = database.lista_cupom
    cargo = session['usuario'][1]
    if validar_perm():
            return render_template("gerenciar.html", cargo=cargo, lanches=lanches, bebidas=bebidas, cupons=cupons)
    return "Acesso negado", 403

@app.route("/gerenciar/cupom/remover/<id>")
def remover_cupom(id):
    database.deletar_cupom(id)
    return redirect(url_for("gerenciar"))


@app.route("/gerenciar/funcionario")
def gerenciar_funcionarios():
    funcionarios = database.lista_funcionarios
    cargo = session['usuario'][1]
    if validar_perm():
            return render_template("gerenciar_funcionarios.html", cargo=cargo, funcionarios=funcionarios)
    return "Acesso negado", 403

@app.route("/adicionar/", methods=["POST", "GET"])
def adicionar():
    tipo = request.form.get("tipo")
    if tipo == "produto":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        preco = request.form.get("preco")
        categoria = request.form.get("categoria")
        url = request.form.get("url")
        if nome and preco and url:
            database.adicionar_produto(nome, descricao, preco, categoria, url)
            return redirect("/")
    if tipo == "adicional":
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        url_imagem = request.form.get("url_imagem") 
        database.adicionar_adicional(nome, preco, url_imagem)
        return redirect("/")

    return render_template("adicionar.html", lanches=lanches, bebidas=bebidas)

@app.route("/editar/<id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        preco = request.form.get("preco")
        categoria = request.form.get("categoria")
        disponivel = request.form.get("disponivel")
        if disponivel == "True":
            disponivel = True
        else:
            disponivel = False

        url_imagem = request.form.get("url")
        database.editar_produto(id, nome, descricao, preco, categoria, url_imagem, disponivel)
        return redirect(url_for("gerenciar"))
    produto = database.get_produto(id)
    return render_template("editar_produto.html", produto=produto)

@app.route("/consulta/<id>")
def consulta(id):
    retorno = database.session.query(database.Produto).get(id)
    if not retorno:
        return "Não encontrado"
    return f"Olá {retorno.nome} seu preço é de {retorno.preco}, foto: <img src=\"{retorno.url_imagem}\" />"

@app.route("/remover/<id>")
def remover(id):
    if validar_perm():
        database.remover_produto(id)
        return redirect(request.referrer)
    return "Acesso negado", 403

@app.route("/funcionario/remover/<id>")
def remover_funcionario(id):
    if validar_perm():
        database.remover_funcionario(id)
        return redirect(request.referrer)
    return "Acesso negado", 403

@app.route("/pedidosfinalizados/")
def pedidos_finalizados():
    return render_template("listar_pedidos.html", pedidos=pedidos, lanches=lanches)


@app.route("/cozinha/")
def cozinha():
    if not validar_perm():
        return "Acesso negado"
    query_resp = database.session.query(database.Pedido).order_by(database.Pedido.id.desc()).limit(5).all()
    ultimos_pedidos = {}
    lista_pedidos = []

    for pedido in query_resp:
        nome_lanches = []
        ultimos_pedidos = {}
        lanches = pedido.ids_lanches.split(",")
        for id_lanche in lanches:
            lanche = database.get_produto(id_lanche)
            nome_lanches.append(lanche.nome)
        
        ultimos_pedidos["mesa"] = pedido.mesa
        ultimos_pedidos["atendente"] = pedido.atendente
        ultimos_pedidos["lanches"] = nome_lanches
        lista_pedidos.append(ultimos_pedidos)

    return render_template("cozinha.html", pedidos=pedidos_cozinha, atendente=session['usuario'][0], finalizados=lista_pedidos)

@socketio.on('pedido')
@app.route("/cozinha/finalizar/<id>", methods=["POST", "GET"])
def finalizar_pedido(id):

    socketio.emit('pedido', id)
    id_cliente = pedidos_cozinha[id][0]['id_cliente']
    cupom = pedidos_cozinha[id][0]['cupom']
    id_lanches = []
    for produto in pedidos_cozinha[id]:
        id_lanches.append(str(produto['id']))

    preco_total = 0
    for produto in pedidos_cozinha[id]:
        preco_total += produto['preco']
    pedidos_cozinha.pop(id)
    ids = ",".join(id_lanches)
    database.salvar_pedido(ids, id_cliente, session['usuario'][0], preco_total, id, cupom)
    return redirect(url_for("cozinha"))

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0')