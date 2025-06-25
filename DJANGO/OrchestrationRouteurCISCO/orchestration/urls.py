import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    InterfaceViewSet,
    LogViewSet,
    ModifySubInterface,
    RouterViewSet,
    UserViewSet,
)

# Router pour les API REST
router = DefaultRouter()
router.register(r"routers", RouterViewSet)
router.register(r"logs", LogViewSet)
router.register(r"interfaces", InterfaceViewSet)
router.register(r"users", UserViewSet)


# Inclusion des API REST sous `/api/`
urlpatterns = [
    path("api/", include(router.urls)),
    path("", LoginView.as_view(template_name="login.html"), name="login"),
    path("config/", views.config, name="config"),
    path("dynamic-output/", views.get_dynamic_output, name="get_dynamic_output"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("netconf-action/", views.netconf_action, name="netconf_action"),
    path("send-subinterface/", ModifySubInterface.as_view(), name="send_subinterface"),
    path("sync-router/", views.sync_router, name="sync-router"),
    path(
        "load-subinterface/<str:interface>/<str:ipaddress>/",
        views.load_subinterface,
        name="load_subinterface",
    ),
]


# Ajout du support des fichiers statiques
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
