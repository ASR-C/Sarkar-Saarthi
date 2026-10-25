from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('set-language/', views.set_language_view, name='set_language'),
    path('about/', views.about_view, name='about'),
]
