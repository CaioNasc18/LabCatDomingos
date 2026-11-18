from django.urls import path

from . import views

app_name = "trabalhos"

urlpatterns = [
    path("", views.meus, name="meus"),
    path("disponiveis/", views.disponiveis, name="disponiveis"),
    path("realizados/", views.realizados, name="realizados"),
    path("<int:id_encomenda_tipo>/", views.detalhe, name="detalhe"),
    path("<int:id_encomenda_tipo>/assumir/", views.assumir, name="assumir"),
    path("<int:id_encomenda_tipo>/estado/", views.estado, name="estado"),
    path("execucao/<int:id_execucao>/concluir/", views.concluir, name="concluir"),
]
