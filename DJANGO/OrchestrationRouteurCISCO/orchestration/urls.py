from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    InterfaceViewSet,
    LogViewSet,
    ModifySubInterface,
    MyLoginView,
    RouterViewSet,
    UserViewSet,
    logout_view,
)

# Router for the API REST
router = DefaultRouter()
router.register(r"routers", RouterViewSet)
router.register(r"logs", LogViewSet)
router.register(r"interfaces", InterfaceViewSet)
router.register(r"users", UserViewSet)


# Inclusion of API REST under `/api/`
urlpatterns = [
    path("api/", include(router.urls)),
    path("", MyLoginView.as_view(), name="login"),
    path("config/", views.config, name="config"),
    path("dynamic-output/", views.get_dynamic_output, name="get_dynamic_output"),
    path("logout/", logout_view, name="logout"),
    path("send-subinterface/", ModifySubInterface.as_view(), name="send_subinterface"),
    path("sync-router/", views.sync_router, name="sync-router"),
    path(
        "add-subinterface/<str:interface>/<str:ipaddress>/",
        views.add_subinterface,
        name="add_subinterface",
    ),
    path(
        "update-subinterface/<str:interface>/<str:ipaddress>/",
        views.update_subinterface,
        name="update_subinterface",
    ),
    path(
        "delete-subinterface/<str:interface>/<str:ipaddress>/",
        views.delete_subinterface,
        name="delete_subinterface",
    ),
]
