# Guía de Comandos Docker para Backend Billar

Este documento contiene los comandos esenciales para ejecutar y administrar el proyecto utilizando Docker.

## Requisitos Previos

- Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- Asegurarse de que Docker esté ejecutándose.

## 1. Iniciar el Proyecto

Para construir las imágenes y levantar los contenedores (base de datos y aplicación):

```bash
docker-compose up --build
```

- La aplicación estará disponible en: `http://localhost:8000`
- Para ejecutarlo en segundo plano (detached mode), agrega `-d`: `docker-compose up -d --build`

## 2. Detener el Proyecto

Para detener los contenedores y removerlos (conservando los volúmenes de datos):

```bash
docker-compose down
```

## 3. Ejecutar Migraciones

Cada vez que hagas cambios en los modelos o al iniciar por primera vez:

```bash
docker-compose exec web python manage.py migrate
```

## 4. Crear un Superusuario

Para acceder al panel de administración de Django (`/admin`):

```bash
docker-compose exec web python manage.py createsuperuser
```

## 5. Acceder al Shell del Contenedor

Si necesitas ejecutar comandos directamente dentro del contenedor de la aplicación:

```bash
docker-compose exec web bash
```

O para abrir la shell de Python/Django directamente:

```bash
docker-compose exec web python manage.py shell
```

## 6. Ver Logs

Para ver los logs de la aplicación en tiempo real:

```bash
docker-compose logs -f web
```

## 7. Instalar Nuevas Dependencias

Si agregas un paquete a `requirements.txt`, necesitas reconstruir la imagen:

```bash
docker-compose up --build
```

## Solución de Problemas Comunes

- **Puerto ocupado**: Si obtienes un error de que el puerto 8000 ya está en uso, asegúrate de no tener otra instancia corriendo (como `python manage.py runserver` en tu terminal local).
- **Error de conexión a BD**: Asegúrate de que el contenedor de base de datos (`db`) esté saludable. Docker Compose se encarga de esperar, pero a veces el primer inicio toma unos segundos más.
