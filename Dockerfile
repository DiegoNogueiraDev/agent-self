# Use uma imagem base oficial e leve do Python
FROM python:3.11-slim

# Defina o diretório de trabalho
WORKDIR /app

# Crie um usuário e grupo não-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copie os arquivos de dependências
COPY requirements.txt .

# Instale as dependências
# Use --no-cache-dir para reduzir o tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o container
COPY src/ /app/src/
COPY config/ /app/config/

# Mude a propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Mude para o usuário não-root
USER appuser

# Comando para rodar a aplicação
CMD ["python3", "-m", "src.main"]
