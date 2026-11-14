# Daniel García · EA1RFI

Web personal en **Wagtail 7.4 / Django 5.2**, con portada, Sobre mí, Radioafición e Historia y patrimonio. Diseño adaptable a móvil, sin dependencias de CDN ni tipografías remotas.

Los artículos se escriben en un único editor de texto enriquecido: títulos, listas, enlaces, imágenes, documentos y vídeos incrustados. Incluyen entradilla, portada, pie/crédito, fecha, etiquetas, lugar y bibliografía. Historia permite filtrar por Galicia, Aldearrubia u otros lugares. Buscador global con paginación y exclusión de borradores/páginas privadas.

## Desarrollo local

Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_site
python manage.py createsuperuser
python manage.py runserver
```

Web: http://localhost:8000/ · Administración: http://localhost:8000/admin/

`seed_site` crea las secciones y una presentación inicial editable. Es idempotente y no sustituye textos ya editados. No importa el blog anterior ni publica investigaciones ficticias. No se incluyen credenciales de administrador.

## Publicar contenido

1. En **Páginas → Inicio**, edita la presentación y la imagen de portada opcional.
2. En **Sobre mí**, añade tu biografía y retrato.
3. Dentro de **Radioafición** o **Historia y patrimonio**, elige **Añadir página → Article page**.
4. Escribe el artículo, añade sus imágenes/documentos con el editor y selecciona la zona cuando corresponda.
5. Guarda un borrador, previsualiza y pulsa **Publicar**. El artículo aparecerá automáticamente en la sección y en la portada.

Las fotos insertadas conservan su proporción; la portada de las tarjetas usa un recorte editorial. Los pies/créditos de portada tienen un campo propio. Los documentos se sirven mediante Wagtail para respetar los permisos de sus colecciones. Las imágenes subidas se consideran públicas: no uses la biblioteca de imágenes para material confidencial.

## Docker en un VPS detrás de Nginx con HTTPS

Incluye PostgreSQL, Gunicorn y un Nginx interno que sirve estáticos y medios. El único puerto publicado se limita a `127.0.0.1:8085`, pensado para un proxy HTTPS en el host. No cambia ningún otro proyecto/compose.

```bash
cp .env.example .env
# Edita .env: claves aleatorias independientes, dominio, SITE_URL y origen HTTPS.
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose run --rm web python manage.py seed_site
docker compose run --rm web python manage.py createsuperuser
docker compose up -d
```

Genera cada secreto con `python -c 'import secrets; print(secrets.token_urlsafe(48))'`. No subas `.env` a Git.

En el Nginx **del host**, dentro de tu servidor HTTPS con certificado válido:

```nginx
location / {
    proxy_pass http://127.0.0.1:8085;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    client_max_body_size 20m;
}
```

Configura `DJANGO_ALLOWED_HOSTS` con tus dominios separados por comas y `CSRF_TRUSTED_ORIGINS` con sus orígenes `https://`. El proxy externo debe sobrescribir `X-Forwarded-Proto`; no expongas el Nginx interno directamente a Internet. Si tu proxy existente vive en Docker, utiliza una red compartida y adapta el upstream: `127.0.0.1` dentro de otro contenedor no es el host.

En Wagtail, **Configuración → Sitios**, cambia `localhost` por tu dominio, puerto `443` y conserva Inicio como raíz. Esto es necesario para enlaces absolutos, además de configurar `SITE_URL`.

El perfil de producción exige HTTPS y cookies seguras. Para desarrollo HTTP usa `runserver` con los ajustes locales, no desactives la seguridad del despliegue. Para recuperar contraseñas/configurar notificaciones, define `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` y `DEFAULT_FROM_EMAIL` en `.env`.

### Actualizaciones

Haz una copia de seguridad antes de migrar. En una ventana de mantenimiento:

```bash
git pull
docker compose build
docker compose stop web nginx
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

Conserva copias de PostgreSQL (`pg_dump`) y del volumen `media_data`; el repositorio no contiene artículos, usuarios ni archivos subidos. No ejecutes `docker compose down -v` salvo que quieras borrar los datos. Los estáticos se pueden regenerar.

## Comprobaciones

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Las pruebas cubren rutas públicas y editor, búsqueda, filtros, exclusión de contenido privado/borradores y conservación de contenido al reinicializar. GitHub Actions ejecuta las comprobaciones en cada push/PR.

## Estructura

- `home/models.py`: tipos de página y consultas.
- `home/templates/home/`: presentación, secciones y artículos.
- `config/static/css/site.css`: diseño sin compilación frontend.
- `search/`: búsqueda pública.
- `config/settings/`: configuración local y producción.
- `deploy/nginx.conf`, `compose.yaml`: despliegue independiente.

Pendiente de completar por el propietario: biografía definitiva, fotografías, artículos originales y dominio/servidor. El código no despliega automáticamente en ningún servidor.
