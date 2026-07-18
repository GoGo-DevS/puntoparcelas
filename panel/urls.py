from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('login/',  views.PanelLoginView.as_view(),  name='login'),
    path('logout/', views.PanelLogoutView.as_view(), name='logout'),
    path('',                   views.dashboard,         name='dashboard'),

    # Parcelas
    path('parcelas/',              views.parcelas_lista,    name='parcelas_lista'),
    path('parcelas/nueva/',        views.parcela_create,    name='parcela_create'),
    path('parcelas/<int:pk>/editar/',   views.parcela_edit,      name='parcela_edit'),
    path('parcelas/<int:pk>/eliminar/', views.parcela_delete,    name='parcela_delete'),
    path('parcelas/fotos/<int:pk>/eliminar/',   views.foto_delete,   name='foto_delete'),
    path('parcelas/fotos/<int:pk>/reemplazar/', views.foto_replace,  name='foto_replace'),

    # Consultas
    path('consultas/',             views.consultas_lista,   name='consultas_lista'),
    path('consultas/<int:pk>/',    views.consulta_detail,   name='consulta_detail'),

    # Testimonios
    path('testimonios/',               views.testimonios_lista,   name='testimonios_lista'),
    path('testimonios/nuevo/',         views.testimonio_create,   name='testimonio_create'),
    path('testimonios/<int:pk>/editar/', views.testimonio_edit,   name='testimonio_edit'),
    path('testimonios/<int:pk>/eliminar/', views.testimonio_delete, name='testimonio_delete'),
]
