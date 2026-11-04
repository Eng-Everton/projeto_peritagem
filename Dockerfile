FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UPLOAD_FOLDER=/app/uploads \
    LAUDO_FOLDER=/app/laudos \
    FOTOS_SERVIDOR_DIR=/mnt/fotos-servidor

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY app.py .

RUN mkdir -p /app/uploads /app/laudos

EXPOSE 5000

# Executa como root no container para possuir CAP_DAC_OVERRIDE sobre diretórios CIFS
# mapeados como dr-xr-xr-x (0555) pelo Windows Server.
# Usa worker gthread para lidar melhor com conexões móveis (keep-alive/preconnect).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "gthread", "--workers", "2", "--threads", "4", "--timeout", "120", "app:create_app()"]
