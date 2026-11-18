from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("conta/", views.conta, name="conta"),
    path("notificacoes/", views.notificacoes, name="notificacoes"),
    path("notificacoes/lidas/", views.marcar_lida, name="marcar_todas_lidas"),
    path("notificacoes/<int:id_notificacao>/lida/", views.marcar_lida, name="marcar_lida"),
]
