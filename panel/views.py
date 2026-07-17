from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from core.models import Consulta, FotoParcela, Parcela, Testimonio

from .forms import (
    ConsultaEstadoForm,
    FotoParcelaForm,
    PanelLoginForm,
    ParcelaForm,
    TestimonioForm,
)


class PanelLoginView(LoginView):
    template_name = 'panel/login.html'
    authentication_form = PanelLoginForm
    redirect_authenticated_user = True


class PanelLogoutView(LogoutView):
    next_page = reverse_lazy('panel:login')


@login_required(login_url='panel:login')
def dashboard(request):
    return render(request, 'panel/dashboard.html', {
        'active': 'dashboard',
        'count_activas':   Parcela.objects.filter(estado='disponible').count(),
        'count_reservadas': Parcela.objects.filter(estado='reservada').count(),
        'count_vendidas':  Parcela.objects.filter(estado='vendida').count(),
        'count_consultas': Consulta.objects.filter(estado='nueva').count(),
        'consultas_recientes': Consulta.objects.order_by('-creado')[:5],
        'parcelas_recientes':  Parcela.objects.order_by('-creado')[:5],
    })


# ── PARCELAS ────────────────────────────────────────────────────

@login_required(login_url='panel:login')
def parcelas_lista(request):
    estado = request.GET.get('estado', '')
    qs = Parcela.objects.all()
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, 'panel/parcelas_lista.html', {
        'active': 'parcelas',
        'parcelas': qs,
        'estado_activo': estado,
        'estado_choices': Parcela.ESTADO_CHOICES,
    })


@login_required(login_url='panel:login')
def parcela_create(request):
    if request.method == 'POST':
        form = ParcelaForm(request.POST)
        if form.is_valid():
            parcela = form.save()
            _procesar_fotos(request, parcela)
            messages.success(request, f'Parcela "{parcela.nombre}" creada.')
            return redirect('panel:parcelas_lista')
    else:
        form = ParcelaForm()
    return render(request, 'panel/parcela_form.html', {
        'active': 'parcelas',
        'form': form,
        'titulo': 'Nueva parcela',
        'is_new': True,
    })


@login_required(login_url='panel:login')
def parcela_edit(request, pk):
    parcela = get_object_or_404(Parcela, pk=pk)
    if request.method == 'POST':
        form = ParcelaForm(request.POST, instance=parcela)
        if form.is_valid():
            form.save()
            _procesar_fotos(request, parcela)
            messages.success(request, 'Cambios guardados.')
            return redirect('panel:parcelas_lista')
    else:
        form = ParcelaForm(instance=parcela)
    return render(request, 'panel/parcela_form.html', {
        'active': 'parcelas',
        'form': form,
        'parcela': parcela,
        'titulo': parcela.nombre,
        'is_new': False,
        'fotos': parcela.fotos.all(),
    })


@login_required(login_url='panel:login')
def parcela_delete(request, pk):
    parcela = get_object_or_404(Parcela, pk=pk)
    if request.method == 'POST':
        nombre = parcela.nombre
        parcela.delete()
        messages.success(request, f'Parcela "{nombre}" eliminada.')
        return redirect('panel:parcelas_lista')
    return render(request, 'panel/parcela_confirmar_eliminar.html', {
        'active': 'parcelas',
        'parcela': parcela,
    })


@login_required(login_url='panel:login')
def foto_delete(request, pk):
    foto = get_object_or_404(FotoParcela, pk=pk)
    parcela_pk = foto.parcela_id
    foto.delete()
    messages.success(request, 'Foto eliminada.')
    return redirect('panel:parcela_edit', pk=parcela_pk)


def _procesar_fotos(request, parcela):
    nuevas = []
    for f in request.FILES.getlist('fotos_nuevas'):
        nuevas.append(FotoParcela.objects.create(parcela=parcela, imagen=f))

    principal_id = request.POST.get('foto_principal')
    if principal_id:
        parcela.fotos.update(principal=False)
        parcela.fotos.filter(pk=principal_id).update(principal=True)
    elif nuevas and not parcela.fotos.filter(principal=True).exists():
        nuevas[0].principal = True
        nuevas[0].save(update_fields=['principal'])


# ── CONSULTAS ───────────────────────────────────────────────────

@login_required(login_url='panel:login')
def consultas_lista(request):
    estado = request.GET.get('estado', '')
    qs = Consulta.objects.all()
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, 'panel/consultas_lista.html', {
        'active': 'consultas',
        'consultas': qs,
        'estado_activo': estado,
        'estados': Consulta.ESTADO_CHOICES,
    })


@login_required(login_url='panel:login')
def consulta_detail(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        form = ConsultaEstadoForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta actualizada.')
            return redirect('panel:consultas_lista')
    else:
        form = ConsultaEstadoForm(instance=consulta)
    return render(request, 'panel/consulta_detail.html', {
        'active': 'consultas',
        'consulta': consulta,
        'form': form,
    })


# ── TESTIMONIOS ─────────────────────────────────────────────────

@login_required(login_url='panel:login')
def testimonios_lista(request):
    return render(request, 'panel/testimonios_lista.html', {
        'active': 'testimonios',
        'testimonios': Testimonio.objects.all(),
    })


@login_required(login_url='panel:login')
def testimonio_create(request):
    if request.method == 'POST':
        form = TestimonioForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.es_placeholder = False
            obj.save()
            messages.success(request, 'Testimonio creado.')
            return redirect('panel:testimonios_lista')
    else:
        form = TestimonioForm()
    return render(request, 'panel/testimonio_form.html', {
        'active': 'testimonios', 'form': form, 'titulo': 'Nuevo testimonio', 'is_new': True,
    })


@login_required(login_url='panel:login')
def testimonio_edit(request, pk):
    obj = get_object_or_404(Testimonio, pk=pk)
    if request.method == 'POST':
        form = TestimonioForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.es_placeholder = False
            obj.save()
            messages.success(request, 'Guardado.')
            return redirect('panel:testimonios_lista')
    else:
        form = TestimonioForm(instance=obj)
    return render(request, 'panel/testimonio_form.html', {
        'active': 'testimonios', 'form': form, 'titulo': obj.nombre, 'obj': obj, 'is_new': False,
    })


@login_required(login_url='panel:login')
def testimonio_delete(request, pk):
    obj = get_object_or_404(Testimonio, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Testimonio eliminado.')
        return redirect('panel:testimonios_lista')
    return render(request, 'panel/confirmar_eliminar.html', {
        'active': 'testimonios',
        'titulo': f'Eliminar testimonio de {obj.nombre}',
        'volver_url': reverse_lazy('panel:testimonios_lista'),
    })
