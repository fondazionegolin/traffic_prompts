from django.urls import path
from . import views

app_name = 'traffic_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('save_data/', views.save_data, name='save_data'),
    path('wait/<str:user_code>/', views.wait, name='wait'),
    path('prompts/', views.get_prompts, name='get_prompts')
]
