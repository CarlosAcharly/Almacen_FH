from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('dashboard/', include('dashboard.urls')),
    path('catalogos/', include('catalogos.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('reportes/', include('reportes.urls')),
    path('dietas/', include('dietas.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


]
