from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from .views import ConfigAPIView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("auth/", views.auth, name="auth"),
    path("config/", views.config, name="config"),
    path("dynamic-output/", views.get_dynamic_output, name="get_dynamic_output"),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('manage-interface/', views.manage_interface, name='manage_interface'),
    path('json/', ConfigAPIView.as_view(), name='config-api'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
