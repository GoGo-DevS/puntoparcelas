from django.conf import settings
from django.contrib import messages
from django.contrib.sitemaps import Sitemap
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ConsultaForm
from .models import REGIONES, Consulta, Parcela, Testimonio


def home(request):
    destacadas = Parcela.objects.filter(destacada=True, estado='disponible')[:6]
    testimonios = Testimonio.objects.filter(activo=True)[:3]
    return render(request, 'core/home.html', {
        'destacadas': destacadas,
        'testimonios': testimonios,
    })


def catalogo(request):
    region = request.GET.get('region', '').strip()
    qs = Parcela.objects.filter(estado='disponible')
    if region:
        qs = qs.filter(region=region)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/catalogo.html', {
        'page_obj': page_obj,
        'region_activa': region,
        'regiones': REGIONES,
        'total': qs.count(),
    })


def parcela_detail(request, slug):
    parcela = get_object_or_404(Parcela, slug=slug)
    form = ConsultaForm(initial={'parcela': parcela.pk})
    relacionadas = (
        Parcela.objects
        .filter(region=parcela.region, estado='disponible')
        .exclude(pk=parcela.pk)[:3]
    )
    return render(request, 'core/parcela_detail.html', {
        'parcela': parcela,
        'form': form,
        'relacionadas': relacionadas,
    })


def reserva(request):
    form = ConsultaForm()
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            _enviar_notificacion(consulta)
            messages.success(request, '¡Mensaje enviado! Leonardo te contactará pronto.')
            return redirect('core:reserva')
    return render(request, 'core/reserva.html', {'form': form})


def _enviar_notificacion(consulta):
    try:
        asunto = f"Nueva consulta — {consulta.nombre}"
        cuerpo = (
            f"Nombre: {consulta.nombre}\n"
            f"Teléfono: {consulta.telefono}\n"
            f"Email: {consulta.email}\n"
            f"Región de interés: {consulta.get_region_interes_display() if consulta.region_interes else '—'}\n"
            f"Monto a invertir: {consulta.monto_display}\n"
            f"¿Cómo nos conoció?: {consulta.get_como_nos_conociste_display() if consulta.como_nos_conociste else '—'}\n"
            f"Parcela consultada: {consulta.parcela or '—'}\n\n"
            f"Mensaje:\n{consulta.mensaje}"
        )
        send_mail(
            asunto, cuerpo,
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_DESTINO],
            fail_silently=True,
        )
    except Exception:
        pass


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nDisallow: /admin-panel/\nDisallow: /django-admin/\n\nSitemap: https://puntoparcelas.cl/sitemap.xml\n"
    return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
    parcelas = Parcela.objects.filter(estado='disponible').values_list('slug', flat=True)
    base = "https://puntoparcelas.cl"
    urls = [
        f"  <url><loc>{base}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{base}/catalogo/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base}/reserva/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
    ]
    for slug in parcelas:
        urls.append(f"  <url><loc>{base}/parcela/{slug}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(urls)
    xml += '\n</urlset>'
    return HttpResponse(xml, content_type='application/xml')
