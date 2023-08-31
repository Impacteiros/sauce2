import os
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD']
)

cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY,'
            'nome VARCHAR(255),'
            'celular VARCHAR(255),'
            'senha VARCHAR(255))'
            )

insert_query = 'INSERT INTO usuarios (nome, celular, senha) VALUES (%s, %s, %s)'

# Inserir um usuário de exemplo
exemplo_usuario = ('Exemplo', '5551234567', 'senha123')
cur.execute(insert_query, exemplo_usuario)
conn.commit()

# Consultar e imprimir os dados do usuário inserido
select_query = 'SELECT * FROM usuarios WHERE nome = %s'
cur.execute(select_query, ('Exemplo',))
user_data = cur.fetchone()

if user_data:
    print("Dados do usuário:")
    print("ID:", user_data[0])
    print("Nome:", user_data[1])
    print("Celular:", user_data[2])
    print("Senha:", user_data[3])
else:
    print("Usuário não encontrado.")

# Fechar o cursor e a conexão
cur.close()
conn.close()
