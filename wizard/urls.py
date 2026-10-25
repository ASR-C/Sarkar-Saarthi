from django.urls import path
from . import views

app_name = 'wizard'

urlpatterns = [
    path('', views.wizard_start_view, name='start'),
    path('step/<int:q_id>/', views.wizard_step_view, name='step'),
    path('back/', views.wizard_back_view, name='back'),
    path('result/<slug:guide_slug>/', views.wizard_result_view, name='result'),
]
