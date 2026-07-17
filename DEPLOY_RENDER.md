# Deploy Render - Punto Parcelas

## 1. GitHub

Subir este repo a GitHub. La rama actual es `master`.

## 2. Base de datos

Render Free no debe usar SQLite para produccion, porque puede perder datos al reiniciar/redeploy.
Usar una base Postgres externa gratis, por ejemplo Neon, y copiar su URL en `DATABASE_URL`.

Para una demo corta se puede dejar `DATABASE_URL` vacio y usar SQLite. Ojo: los datos pueden perderse si Render reinicia o se redeploya.

## 2.1 Fotos

Para produccion real configurar `CLOUDINARY_URL`, porque Render Free no guarda archivos subidos de forma persistente.

Para una demo corta se puede dejar `CLOUDINARY_URL` vacio. El sitio servira las fotos locales, pero pueden perderse al reiniciar/redeployar.

## 3. Variables en Render

Configurar estas variables:

```text
DEBUG=false
SECRET_KEY=<generada por Render o valor seguro>
DATABASE_URL=<postgres de Neon o Render Postgres>
CLOUDINARY_URL=<cloudinary para media/uploads>
PANEL_USERNAME=leonardo
PANEL_PASSWORD=<clave segura para Leonardo>
PANEL_EMAIL=l.valencia@ctpchile.cl
```

Opcionales:

```text
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

## 4. Build y start

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python manage.py seed_data
```

Start command:

```bash
gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
```

## 5. Acceso cliente

URL panel:

```text
/admin-panel/login/
```

Usuario:

```text
leonardo
```

La clave queda definida por `PANEL_PASSWORD`.
