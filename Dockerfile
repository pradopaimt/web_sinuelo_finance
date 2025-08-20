ROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copia tudo (backend + index.html + assets)
COPY . /app

# DB em /data (será um volume no fly)
ENV SINUELO_DB_NAME=/data/sinuelo.db
ENV PORT=8080

# segurança e timezone mínimos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]