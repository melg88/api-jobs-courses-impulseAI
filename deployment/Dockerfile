# Usar imagem base do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0=2.50.3-2 \
    libnss3=2:3.26.2-1.1+deb9u1 \
    libgconf-2-4=3.2.6-4+b1 \
    libfontconfig1=2.11.0-6.7+b1
    wget \
    gnupg \
    curl \
    unzip \
    #libglib2.0-0 \
    #libnss3 \
    #libgconf-2-4 \
    #libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxss1 \
    libxtst6 \
    libdbus-1-3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    fonts-liberation \
    --no-install-recommends \
    && curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar a versão correta do ChromeDriver
# Este comando busca a versão mais recente e compatível do ChromeDriver RUN CHROME_DRIVER_VERSION=$(curl -sS https://storage.googleapis.com/chrome-for-testing-public/...) \
RUN CHROME_DRIVER_VERSION=$(curl -sS https://storage.googleapis.com/chrome-for-testing-public/last-known-good-versions-with-downloads.json | grep -oP '"linux64","url":"https://storage.googleapis.com/chrome-for-testing-public/[^"]*?chromedriver-linux64.zip' | head -n 1 | cut -d '"' -f 4) \
    && wget -q -O /tmp/chromedriver.zip ${CHROME_DRIVER_VERSION} \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 \
    && chmod +x /usr/local/bin/chromedriver

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Comando para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]