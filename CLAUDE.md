# CLAUDE.md — Punto Parcelas (proyecto standalone)

Landing + panel admin para Leonardo Valencia (Punto Parcelas). Ver bitácora
completa del desarrollo original en el CLAUDE.md de GoGoCRM (sesión
14-07-2026). Este archivo es propio del proyecto standalone.

Stack: Django 5 + Bootstrap 5 + Cloudinary (opcional) + Render.
Venv: usar el de GoGoCRM (`../venv/Scripts/python.exe`), no hay uno propio.
Server local: `python manage.py runserver 127.0.0.1:8001`
Admin panel (no es Django admin): `/admin-panel/login/` — leonardo / PuntoParcelas2026!

════════════════════════════════════════════════
## BITÁCORA DE SESIÓN
════════════════════════════════════════════════

---
[15-07-2026] — QA completo (modo tryhard)
Tarea completada: QA de punta a punta del sitio en local (http://127.0.0.1:8001).
  Revisadas las 11 páginas del checklist (home, catálogo, catálogo con filtro región,
  3 fichas de parcela, reserva/contacto, login panel, dashboard, mis parcelas, nueva
  parcela, consultas, testimonios) + checks de DB.

  DB checks (todo OK): 41/41 parcelas con foto principal, 0 FotoParcela con imagen
  vacía, 4 testimonios activos (marcados es_placeholder=True a propósito — feature
  existente para que Leonardo sepa cuáles reemplazar por reales), 0 consultas (normal,
  nadie ha usado el form en local).

  Bugs reales encontrados y corregidos:
  1. Botón flotante de WhatsApp (fixed bottom-right) tapaba el texto "Diseño por
     GoGoDevS" del footer en desktop. Fix: clase `.footer-bottom-row` con
     `padding-right: 5rem` en media (min-width:768px) — core/templates/core/base.html.
  2. Ícono "Inversión Segura" (sección propuesta-bar de /contacto/) usaba
     `bi-handshake`, que NO existe en Bootstrap Icons → se renderizaba vacío.
     Mismo patrón de bug que ya se había corregido antes en el ícono "Confianza"
     de home.html (bi-people-fill, ese ya estaba bien). Fix: reemplazado por
     `bi-shield-lock-fill` — core/templates/core/reserva.html.
  3. `core/static/img/foto-leo.jpeg` tenía el fondo checkerboard de transparencia
     baked-in en los píxeles (herramienta de remove-background exportó a JPEG sin
     aplanar contra un color sólido, y JPEG no soporta alpha). Se veía como un
     patrón de cuadros gris/blanco brillante detrás de Leonardo en /contacto/,
     muy fuera de lugar en el tema oscuro. Fix: script PIL con flood-fill desde
     los bordes de la imagen (detecta píxeles grises del checker, sigue conectividad
     para no invadir la foto real) + blur suave en el borde de la máscara, compositado
     contra #1A1A1A (mismo tono que las cards del sitio). No había backup ni versión
     con alpha real — el archivo era untracked en git, así que no se pudo recuperar
     el original; el resultado del fix quedó limpio y verificado visualmente.

  Falsos positivos investigados y descartados (no se tocó nada):
  - Precios muy bajos en 3 parcelas (Parque Algarrobo $2.800, Vive Puerto Varas
    $3.220, Punta de Toros $11.500) parecían truncados por un bug de regex del
    scraper. Se re-scrapeó cada slug individualmente con
    `manage.py scrape_puntoparcelas --skip-images --slug <slug>` contra el sitio
    real y el valor se repitió exacto → es el precio real listado en la fuente,
    no un bug. Queda como nota para Diego/Leonardo por si vale la pena revisar
    esos 3 listados manualmente (podrían ser precio por m² u otra unidad en el
    sitio original), pero no es un bug de este código.
  - Filtro de región en catálogo probado con `?region=Coquimbo` (capitalizado)
    daba 0 resultados — pero el bug era del tester (los value reales son
    lowercase: 'coquimbo', 'valparaiso', etc., que es lo que usan los pills del
    template vía `{{ val }}`). Con `?region=coquimbo` o clickeando el pill
    real funciona perfecto (1 resultado correcto).
  - Testimonios pantalla "solo 1 de 3 visible" durante scroll rápido programático
    — era timing de la animación scroll-reveal (IntersectionObserver), no bug:
    con scroll a velocidad normal los 3 aparecen bien.
  - Rutas `/reserva/` y `/parcela/<slug>/` (nombradas así en el checklist de QA)
    daban 404 — las rutas reales son `/contacto/` y `/catalogo/<slug>/`
    (core/urls.py). Todos los templates ya usan `{% url %}` con los nombres
    correctos, no hay links rotos en el sitio real.
  - Navbar responsive (isotipo siempre visible, texto desde md, tagline desde lg)
    no se pudo verificar visualmente — la tool de resize_window del browser no
    logró achicar la ventana en este entorno (probablemente por window snapping
    de Windows). Verificado por lectura de código en su lugar: usa clases
    Bootstrap estándar `d-none d-md-flex` / `d-md-none` correctamente aplicadas
    en base.html líneas 430-467. Pendiente de una verificación visual real en
    un dispositivo o DevTools cuando se pueda.

Archivos modificados: core/templates/core/base.html, core/templates/core/reserva.html,
  core/static/img/foto-leo.jpeg (recompuesto, mismo path).
Próxima tarea: verificar navbar mobile en un dispositivo real o Chrome DevTools
  responsive mode (la herramienta de browser automation no pudo simular viewport
  angosto en este entorno). Revisar con Leonardo si los 3 precios bajos detectados
  son intencionales en el sitio original o un error de carga de su parte.
---
