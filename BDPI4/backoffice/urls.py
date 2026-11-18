from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("encomendas/", include("encomendas.urls")),
    path("trabalhos/", include("trabalhos.urls")),
    path("gestao/", include("gestao.urls")),
    path("logs/", include("logs.urls")),
]
