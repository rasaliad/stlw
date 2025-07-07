FROM python:3.12-slim

WORKDIR /app

# Instalar las mismas dependencias que el backend STL
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    firebird-dev \
    libfbclient2 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configurar zona horaria
ENV TZ=America/Santo_Domingo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY main.py .

# Configurar variables de entorno para Firebird (igual que backend STL)
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Comando para ejecutar el bot
CMD ["python", "main.py"]