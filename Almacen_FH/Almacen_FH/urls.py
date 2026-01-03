from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalogos/', include('catalogos.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('reportes/', include('reportes.urls')),
    path('dietas/', include('dietas.urls')),

]
