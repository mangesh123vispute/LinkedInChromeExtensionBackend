from django.urls import path
from . import views

urlpatterns = [
    path('analyze-profile/', views.analyze_profile, name='analyze-profile'),
    path('save-profile/', views.save_profile, name='save-profile'),
    path('generate-message/', views.generate_message, name='generate-message'),
]

