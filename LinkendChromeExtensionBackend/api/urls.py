from django.urls import path
from . import views

urlpatterns = [
    path('analyze-profile/', views.analyze_profile, name='analyze-profile'),
    path('save-analyzed-data/', views.save_analyzed_data, name='save-analyzed-data'),
    path('generate-message/', views.generate_message, name='generate-message'),
    path('get-raw-data/<str:profile_id>/', views.get_raw_data_by_profile_id, name='get-raw-data'),
    path('get-analyzed-data/<str:profile_id>/', views.get_analyzed_data_by_profile_id, name='get-analyzed-data'),
]

