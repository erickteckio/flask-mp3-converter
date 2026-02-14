# Usando a imagem oficial do Python
FROM python:3.9-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos do projeto para dentro do container
COPY . /app

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expondo a porta em que a aplicação vai rodar
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
