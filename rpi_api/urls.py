"""
URL configuration for rpi_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rpi_api.views import esp82
from rpi_api.views import dashboard
from django.urls import include
from rpi_api.views import test as test_views
from django.conf import settings
from django.conf.urls.static import static

esp_patterns = [
    path('motion/', esp82.receive_motion),
    path('temperature/', esp82.receive_temperature),
    path('meter/', esp82.receive_power),
    path('initial/', esp82.initial_connection),
    path('ir/', esp82.send_ir_data),
    path('led/', esp82.send_led_signal),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

test_patterns = [
    path('camera/', test_views.test_camera, name = 'test_camera'),
    path('ir/<str:command>', test_views.test_ir, name = 'test_ir'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/esp82/', include(esp_patterns)),
    path('test/', include(test_patterns)),
    path('', dashboard.login, name='login'),
    path('dashboard/', dashboard.dashboard, name='dashboard'),
    path('dashboard/settings/', dashboard.manage_settings, name='settings'),
    path('manage_sensor/<str:sensor_name>/', dashboard.manage_sensor, name='manage_sensor'),
    path('export/temperatures/', dashboard.export_temperatures, name='export_temperatures'),
    path('export/images/', dashboard.export_images, name='export_images'),
    path('export/meter/', dashboard.export_power_meter, name='export_meter'),
    path('export/ir/', dashboard.export_ir, name='export_ir'),
    path('logout/', dashboard.logout, name='logout'),
]


