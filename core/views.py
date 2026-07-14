from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ConsultaForm
from .models import REGIONES, Consulta, Parcela, Testimonio


def home(request):
    destacadas = Parcela.objects.filter(destacada=True, estado='disponible')[:6]
    testimonios = Testimonio.objects.filter(activo=True)[:4]
    stats = {
        'activas':  Parcela.objects.filter(estado='disponible').count(),
        'regiones': Parcela.objects.values('region').distinct().count(),
        'vendidas': Parcela.objects.filter(estado='vendida').count(),
    }
    return render(request, 'core/home.html', {
        'destacadas': destacadas,
        'testimonios': testimonios,
        'stats': stats,
    })


def catalogo(request):
    region = request.GET.get('region', '').strip()
    qs = Parcela.objects.filter(estado='disponible')
    if region:
        qs = qs.filter(region=region)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    regiones_con_parcelas = (
        Parcela.objects
        .filter(estado='disponible')
        .values_list('region', flat=True)
        .distinct()
        .order_by('region')
    )
    regiones_display = [(r, dict(REGIONES).get(r, r)) for r in regiones_con_parcelas]

    return render(request, 'core/catalogo.html', {
        'page_obj': page_obj,
        'region_activa': region,
        'regiones': regiones_display,
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
    return render(request, 'core/reserva.html', {
        'form': form,
        'tags_contacto': [
            'Parcelas disponibles', 'Precios y financiamiento',
            'Visitas a terreno', 'Proceso de escrituración', 'Asesoría de inversión',
        ],
    })


def _enviar_notificacion(consulta):
    try:
        asunto = f"Nueva consulta — {consulta.nombre}"
        cuerpo = (
            f"Nombre: {consulta.nombre}\n"
            f"Teléfono: {consulta.telefono}\n"
            f"Email: {consulta.email}\n"
            f"Región de interés: {consulta.get_region_interes_display() if consulta.region_interes else '—'}\n"
            f"Presupuesto: {consulta.monto_display}\n"
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
