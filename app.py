from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO
import database
import eventlet

app = Flask(__name__)
app.secret_key = "!yw2gC8!BeM3"
app.config['SECRET_KEY'] = "!yw2gC8!BeM3"

socketio = SocketIO(app)


pedidos_cozinha = {}


def checar_login():
    if 'usuario' not in session:
        return None
    return session['usuario']

@socketio.on('atualizacao')
def atualizar_cozinha():
    socketio.emit('atualizacao', {'data': "Dados atualizados"})

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
    if 'carrinho' not in session:
        session['carrinho'] = []
    cliente = checar_login()
    
    lanches = database.Produto.get_lanches()
    bebidas = database.Produto.get_bebidas()
    adicionais = database.Adicional.get_adicionais()

    return render_template("index.html", lanches=lanches, bebidas=bebidas,
                           adicionais=adicionais, usuario=cliente)


@app.route("/carrinho/", methods=["POST", "GET"])
def carrinho():
    lanches = database.Produto.get_lanches()
    bebidas = database.Produto.get_bebidas()
    adicionais = database.Adicional.get_adicionais()
    cupons = database.Cupom.get_cupons()
    cliente = checar_login()

    carrinho_render = []
    carrinho_enderecos = []

    cupom_valor = 0
    preco_total = 0
    if "carrinho" in session:
        for produto in session['carrinho']:
            produto_carrinho = database.Produto.get_produto(produto['id'])
            produto_carrinho['obs'] = produto['obs']
            produto_carrinho['id_carrinho'] = produto['id_carrinho']
            produto_carrinho['adicionais'] = ', '.join(f'{item[0]}: {item[1]}' for item in produto['adicionais'])
            preco_total += float(produto['preco'])
            carrinho_render.append(produto_carrinho)

    if "usuario" in session:
        enderecos = database.Endereco.get_enderecos_cliente(session['usuario']['id'])
        for endereco in enderecos:
            end = f"Rua: {endereco['rua']}, Nº {endereco['numero']}, Cidade: Campo Grande, Bairro: {endereco['bairro']}, CEP: {endereco['cep']}"
            completo = {"endereco": end, "id": endereco['id']}
            carrinho_enderecos.append(completo)
    if request.method == "POST":
        cupom = request.form.get("cupom")
        cupom_valor = database.Cupom.validar_cupom(cupom)
        if cupom_valor:
            session['cupom'] = cupom_valor

        return render_template("carrinho.html", carrinho=carrinho_render, 
                            lanches=lanches, bebidas=bebidas, preco_total=float(preco_total), cupom=cupom_valor, usuario=cliente, endereco=carrinho_enderecos)
    
    return render_template("carrinho.html", carrinho=carrinho_render, 
                           lanches=lanches, bebidas=bebidas, preco_total=float(preco_total), cupom=cupom_valor, usuario=cliente, enderecos=carrinho_enderecos)

@app.route("/carrinho/adicionar/<id>", methods=["GET", "POST"])
def adicinar_carrinho(id):
    adicionais = []
    produto = database.Produto.get_produto(id)
    obs = ""
    if request.method == "POST":
        obs = request.form.get("obs")
        selecao = request.form.items()
        for add in selecao:
            if add[0] != "obs" and add[1] != "0":
                adicionais.append(add)
        
    id_carrinho = str(len(session['carrinho']) + 1)

    session['carrinho'].append(
        {"id_carrinho": id_carrinho, "id": id, "nome": produto['nome'], "preco": produto['preco'], "adicionais": adicionais, "obs": obs}
    )

    flash(f"Você adicionou {produto['nome']} no carrinho", "adicionado")
    return redirect("/")

@app.route("/carrinho/remover/<id>")
def remover_carrinho(id):

    carrinho = session['carrinho']

    for produto in carrinho:
        if produto['id_carrinho'] == id:
            carrinho.remove(produto)
            break

    session['carrinho'] = carrinho
    
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

@app.route("/endereco/cadastrar", methods=['POST'])
def cadastrar_endereco():
    id_cliente = session['usuario']['id']
    rua = request.form.get("rua")
    numero = request.form.get("numero")
    complemento = request.form.get("complemento")
    bairro = request.form.get("bairro")
    cep = request.form.get("cep")

    database.Endereco.cadastrar_endereco(id_cliente, rua, numero, complemento, bairro, cep)
    return redirect(url_for("carrinho"))

@app.route("/endereco/remover/<id>")
def remover_endereco(id):
    database.Endereco.remover_endereco(id)
    return redirect(url_for("carrinho"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    if 'usuario' in session:
        return redirect(url_for('home'))
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario and senha:
        validacao = database.Cliente.validar_login(usuario, senha)
        erro = "Usuario e/ou senha invalidos."
        if validacao:
            session['usuario'] = {"nome": validacao['nome'], "id": validacao['id'], "celular": validacao['celular']}
            return redirect(url_for("home"))
        return render_template("login.html", erro=erro)
    return render_template("login.html")


@app.route("/cadastro/usuario", methods=["POST", "GET"])
def cadastro_usuario():
    nome = request.form.get("nome")
    celular = request.form.get("celular")
    senha = request.form.get("senha")
    if nome and senha and celular:
        cadastrado = database.Cliente.get_cliente(celular)
        if cadastrado:
            erro = "Usuário já cadastrado."
            return render_template("login.html", erro=erro)
        database.Cliente.cadastrar_cliente(nome, celular, senha)
        flash("Cadastro realizado com sucesso.", "sucesso")
        return redirect(request.referrer)
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
        database.Cupom.adicionar_cupom(cupom, valor)
        return redirect(url_for("gerenciar"))
    return render_template("cadastro_cupom.html")

@app.route("/deslogar/")
def deslogar():
    session.pop("usuario")
    return redirect("/login/")


@app.route("/debug/")
def debug():
    return session['usuario']

@app.route("/gerenciar/")
def gerenciar():
    lanches = database.Produto.get_lanches()
    bebidas = database.Produto.get_bebidas()
    cupons = database.Cupom.get_cupons()
    return render_template("gerenciar.html", lanches=lanches, bebidas=bebidas, cupons=cupons)

@app.route("/gerenciar/cupom/remover/<id>")
def remover_cupom(id):
    database.Cupom.remover_cupom(id)
    return redirect(url_for("gerenciar"))


@app.route("/gerenciar/funcionario")
def gerenciar_funcionarios():
    funcionarios = database.lista_funcionarios
    cargo = session['usuario'][1]
    if validar_perm():
            return render_template("gerenciar_funcionarios.html", cargo=cargo, funcionarios=funcionarios)
    return "Acesso negado", 403

@app.route("/cadastro/produto/", methods=["POST", "GET"])
def adicionar():
    lanches = database.Produto.get_lanches()
    bebidas = database.Produto.get_bebidas()
    tipo = request.form.get("tipo")
    if tipo == "produto":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        preco = request.form.get("preco")
        categoria = request.form.get("categoria")
        url = request.form.get("url")
        if nome and preco and url:
            database.Produto.adicionar_produto(nome, descricao, preco, categoria, url)
            return redirect("/")
    if tipo == "adicional":
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        url_imagem = request.form.get("url_imagem") 
        database.Adicional.adicionar_adicional(nome, preco, url_imagem)
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
        database.Produto.editar_produto(id, nome, descricao, preco, categoria, url_imagem, disponivel)
        return redirect(url_for("gerenciar"))
    produto = database.Produto.get_produto(id)
    return render_template("editar_produto.html", produto=produto)

@app.route("/consulta/<id>")
def consulta(id):
    retorno = database.session.query(database.Produto).get(id)
    if not retorno:
        return "Não encontrado"
    return f"Olá {retorno.nome} seu preço é de {retorno.preco}, foto: <img src=\"{retorno.url_imagem}\" />"

@app.route("/remover/<id>")
def remover(id):
    # if validar_perm():
    database.Produto.remover_produto(id)
    return redirect(request.referrer)
    # return "Acesso negado", 403

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
