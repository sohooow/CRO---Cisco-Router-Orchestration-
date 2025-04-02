from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from .views import ConfigAPIView, RouterViewSet, InterfaceViewSet, LogViewSet, UserViewSet
from . import views
from rest_framework.routers import DefaultRouter

#Router pour les API REST
router = DefaultRouter()
router.register(r'routers', RouterViewSet)
router.register(r'logs',LogViewSet)
router.register(r'interfaces', InterfaceViewSet)
router.register(r'users', UserViewSet)


# Inclusion des API REST sous `/api/`
urlpatterns = [
    path("api/", include(router.urls)),
    path("login/", LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("auth/", views.auth, name="auth"),
    path("config/", views.config, name="config"),
    path("dynamic-output/", views.get_dynamic_output, name="get_dynamic_output"),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('manage-interface/', views.manage_interface, name='manage_interface'),
    path('json/', ConfigAPIView.as_view(), name='config'),  

] 

# Ajout du support des fichiers statiques
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 



