from django.urls import path
from . import views

app_name = 'guides'

urlpatterns = [
    path('', views.guide_list_view, name='guide_list'),
    path('official-links/', views.official_links_view, name='official_links'),
    path('<slug:slug>/', views.guide_detail_view, name='guide_detail'),
]
