# Use uma imagem Python leve
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e bufferize stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para o PyMuPDF e outros
# (Geralmente o slim já tem o basico, mas as vezes precisa de build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Cria a pasta de saída para garantir permissões
RUN mkdir -p convertidos && chmod 777 convertidos

# Expõe a porta que o Gunicorn vai usar
EXPOSE 5000

# Comando para rodar a aplicação com Gunicorn
# -w 4: 4 workers (ajuste conforme a CPU)
# -b 0.0.0.0:5000: bind em todos os IPs na porta 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_web:app"]
