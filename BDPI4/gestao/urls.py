from django.urls import path

from . import views

app_name = "gestao"

urlpatterns = [
    path("clientes/", views.clientes, name="clientes"),
    path("clientes/novo/", views.cliente_form, name="cliente_novo"),
    path("clientes/<int:id_cliente>/", views.cliente_form, name="cliente_editar"),
    path("clientes/<int:id_cliente>/ativar/", views.ativar_cliente, name="ativar_cliente"),
    path("colaboradores/", views.colaboradores, name="colaboradores"),
    path("colaboradores/novo/", views.colaborador_novo, name="colaborador_novo"),
    path("colaboradores/<int:id_colaborador>/ativar/", views.ativar_colaborador, name="ativar_colaborador"),
    path("utilizadores/", views.utilizadores, name="utilizadores"),
    path("utilizadores/<int:id_utilizador>/ativar/", views.ativar_utilizador, name="ativar_utilizador"),
    path("utilizadores/<int:id_utilizador>/password/", views.repor_password, name="repor_password"),
    path("tipos/", views.tipos, name="tipos"),
    path("tipos/novo/", views.tipo_novo, name="tipo_novo"),
    path("tipos/<int:id_tipo_trabalho>/", views.tipo, name="tipo"),
    path("tipos/<int:id_tipo_trabalho>/guardar/", views.tipo_guardar, name="tipo_guardar"),
    path("tipos/<int:id_tipo_trabalho>/etapas/nova/", views.etapa_nova, name="etapa_nova"),
    path("tipos/<int:id_tipo_trabalho>/etapas/<int:id_etapa>/", views.etapa_guardar, name="etapa_guardar"),
    path("permissoes/", views.permissoes, name="permissoes"),
    path("permissoes/<int:id_perfil>/<int:id_funcionalidade>/", views.alternar_permissao, name="alternar_permissao"),
]
