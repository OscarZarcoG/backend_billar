# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer variables de entorno
# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Asegura que la salida de Python se envíe directamente al terminal sin buffer
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema
# libpq-dev es necesario para psycopg2 (aunque uses binary, a veces es útil)
# gcc y otras herramientas de compilación pueden ser necesarias para algunos paquetes
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt /app/

# Instalar las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto del código del proyecto
COPY . /app/

# Recolectar archivos estáticos (opcional, útil para producción)
# RUN python manage.py collectstatic --noinput

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación (puede ser sobrescrito por docker-compose)
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
