# Plan de implementación de GitHub Actions (backend_billar)

## Objetivo
- Validar automáticamente Pull Requests hacia `main` con una base de datos PostgreSQL real.
- Ejecutar verificaciones rápidas en ramas `feature/**` y `fix/**` tras cada `push`.
- Preparar la base para despliegue automático a EC2 cuando se haga `push` a `main` (habilitable cuando se creen los Secrets necesarios).

## Resumen del proyecto
- Framework: Django 4.2 con DRF, dj-rest-auth y allauth.
- Entrypoint: `manage.py` con `DJANGO_SETTINGS_MODULE=backend.settings` (`manage.py:9`).
- Configuración: uso de `python-decouple` y `dj_database_url` para variables de entorno (`backend/settings.py:1-5`).
- Base de datos: preferencia por `DATABASE_URL`; si no existe, fallback local PostgreSQL (`backend/settings.py:77-91`).
- Dependencias: definidas en `requirements.txt` (`requirements.txt:1-11`).
- Script de build: `build.sh` con `collectstatic`, `migrate` (`build.sh:7-13`).

## Workflows a crear

### 1) `CI` (Pull Request hacia `main`)
- Propósito: asegurar que el proyecto instala dependencias, migra y ejecuta tests contra PostgreSQL.
- Disparador: `pull_request` a `main`.
- Pasos principales: checkout, setup de Python 3.11, cache de `pip`, servicio Postgres 14, instalación de requisitos, `migrate`, `check`, `test`.

```yaml
name: Django CI

on:
  pull_request:
    branches: ['main']

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - '5432:5432'
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run migrations
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: dummy-ci-secret
          DEBUG: 'true'
        run: python manage.py migrate --noinput

      - name: Django system check
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: dummy-ci-secret
          DEBUG: 'true'
        run: python manage.py check

      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: dummy-ci-secret
          DEBUG: 'true'
        run: python manage.py test
```

Notas de compatibilidad:
- `backend/settings.py` respeta `DATABASE_URL` cuando está definido (`backend/settings.py:77-81`).
- Con `DEBUG=true` y `SECRET_KEY` de prueba se satisfacen las lecturas de `decouple.config` (`backend/settings.py:9-11`).

### 2) `Feature Checks` (push a `feature/**` y `fix/**`)
- Propósito: validar rápido que Django carga sin errores de configuración.
- Disparador: `push` a ramas `feature/**` y `fix/**`.
- Pasos principales: checkout, setup de Python 3.11, instalación de requisitos, `manage.py check`.

```yaml
name: Feature checks

on:
  push:
    branches:
      - 'feature/**'
      - 'fix/**'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Django check
        env:
          SECRET_KEY: dev-feature
          DEBUG: 'true'
        run: python manage.py check
```

### 3) `Deploy a EC2` (push a `main`) [preparado]
- Propósito: copiar el proyecto a EC2 y reiniciar Gunicorn/Nginx.
- Gating: el job sólo corre si existen los Secrets mínimos (`EC2_HOST`, `EC2_USER`, `EC2_KEY`).
- Disparador: `push` a `main`.

```yaml
name: Deploy Django to EC2

on:
  push:
    branches: ['main']

jobs:
  deploy:
    if: ${{ secrets.EC2_HOST != '' && secrets.EC2_USER != '' && secrets.EC2_KEY != '' }}
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Upload project to EC2
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_KEY }}
          source: '.'
          target: '/var/www/backend'

      - name: Restart services
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_KEY }}
          script: |
            cd /var/www/backend
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate --noinput
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
            sudo systemctl restart nginx
```

## Secrets y variables de entorno
- CI/Feature:
  - `SECRET_KEY`: cadena de prueba (no sensible).
  - `DEBUG`: `'true'`.
  - `DATABASE_URL` (sólo CI): `postgres://postgres:postgres@localhost:5432/test_db`.
- Deploy (crear en GitHub > Settings > Secrets and variables > Actions):
  - `EC2_HOST`: IP o hostname de la instancia.
  - `EC2_USER`: usuario SSH (p.ej., `ubuntu`).
  - `EC2_KEY`: contenido de la llave privada SSH.
  - `DJANGO_SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` (usados por la app en EC2; gestionarlos en `.env` del servidor o en el unit de `gunicorn`).

## Estructura de archivos nueva
- `.github/workflows/ci.yml`
- `.github/workflows/feature.yml`
- `.github/workflows/deploy.yml`

## Consideraciones específicas del repo
- `DJANGO_SETTINGS_MODULE` apunta a `backend.settings` (`manage.py:9`).
- La conexión DB respeta `DATABASE_URL` cuando existe (`backend/settings.py:77-81`).
- Fallback local usa credenciales por defecto (`backend/settings.py:83-91`); en CI evitamos este camino definiendo `DATABASE_URL` explícito.
- Dependencias compatibles con Python 3.11 (`requirements.txt:1-11`).
- El flujo de despliegue propuesto replica `build.sh` (`build.sh:7-13`).

## Validación
- CI: el job debe completar `migrate`, `check` y `test` sin errores.
- Feature: `python manage.py check` debe pasar.
- Deploy: se ejecuta sólo con Secrets presentes y debe dejar el servicio operativo tras `migrate` y `collectstatic`.

## Supuestos
- Se usará Python `3.11` en los runners.
- No se añadirá linting adicional hasta que el proyecto lo requiera explícitamente (evita dependencias innecesarias).
- El entorno en EC2 gestionará sus variables de entorno fuera del pipeline (systemd o `.env`).

## Referencias oficiales
- GitHub Actions (workflows, jobs, services): https://docs.github.com/actions
- Django `manage.py` commands: https://docs.djangoproject.com/en/4.2/ref/django-admin/
- PostgreSQL container image: https://hub.docker.com/_/postgres
