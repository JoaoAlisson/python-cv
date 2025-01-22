# Usando a imagem oficial do Python
FROM python:3.11-slim

# Instalar as dependências do sistema para OpenCV e outras bibliotecas
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install Flask \
    && pip install opencv-python \
    && pip install pillow

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo requirements.txt para o contêiner
COPY requirements.txt /app/

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação para o contêiner
COPY . /app/

# Expor a porta 5000 para a aplicação Flask
EXPOSE 80

# Comando para rodar a aplicação Flask
CMD ["python", "app.py"]