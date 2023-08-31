import boto3
import os
import datetime

s3 = boto3.client('s3')
def backup_file():
    file_path = os.path.join(os.getcwd(), 'database.db')
    hora = datetime.datetime.now()
    nome = f"backup_{hora.strftime('%Y-%m-%d_%H-%M-%S')}.db"
    # Faz o upload do arquivo para o bucket da AWS
    s3.upload_file(file_path, 'iago-teste-12345678123', nome)

    return 'Backup concluído com sucesso!'
