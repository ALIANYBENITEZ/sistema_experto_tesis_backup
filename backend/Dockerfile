FROM python:3.11-slim

# psycopg[binary] no requiere paquetes de sistema adicionales (trae libpq).
# Se instalan utilidades mínimas de compilación por si alguna dependencia lo necesita.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Producción: Gunicorn (no el servidor de desarrollo de Flask).
# Render inyecta $PORT; si no existe, usa 5000.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 3 --timeout 120 'app:create_app()'"]
