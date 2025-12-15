"""
URL configuration for busco_repuesto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from busco_repuesto import views as busco_repuesto_views

urlpatterns = [
    path('', busco_repuesto_views.index, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # 👈 Rutas de allauth
    path('comprar/', include('quiero_comprar.urls')),
    path('vender/', include('quiero_vender.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)