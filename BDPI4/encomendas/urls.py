from django.urls import path

from . import views

app_name = "encomendas"

urlpatterns = [
    # laboratório
    path("", views.lista, name="lista"),
    path("pedidos/", views.pedidos, name="pedidos"),
    path("nova/", views.nova, name="nova"),
    path("<int:id_encomenda>/", views.detalhe, name="detalhe"),
    path("<int:id_encomenda>/aceitar/", views.aceitar, name="aceitar"),
    path("<int:id_encomenda>/trabalho/<int:id_encomenda_tipo>/estado/", views.alterar_estado, name="alterar_estado"),
    # notas e ficheiros (laboratório e cliente)
    path("<int:id_encomenda>/notas/", views.nova_nota, name="nova_nota"),
    path("<int:id_encomenda>/anexos/", views.novos_anexos, name="novos_anexos"),
    path("anexo/<str:tipo>/<int:id_anexo>/", views.descarregar, name="descarregar"),
    # área do cliente
    path("cliente/", views.inicio_cliente, name="inicio_cliente"),
    path("cliente/encomendas/", views.minhas, name="minhas"),
    path("cliente/encomendas/<int:id_encomenda>/", views.detalhe_cliente, name="detalhe_cliente"),
]
