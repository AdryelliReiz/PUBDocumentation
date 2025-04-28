# Use a imagem Python 3 oficial
FROM python:3.9-slim

# Instalar dependências para a construção de pacotes e o Avahi
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    autoconf \
    libtool \
    pkg-config \
    libdb-dev \
    libnss-mdns \
    avahi-daemon \
    avahi-utils \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Copiar os arquivos do projeto
WORKDIR /app
COPY . /app

# Configuração do dbus (se necessário)
RUN service dbus start

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta para o servidor
EXPOSE 9494

# Rodar o Avahi daemons e o servidor Python
CMD ["sh", "-c", "avahi-daemon --no-dbus --debug --no-chroot & python main.py"]
