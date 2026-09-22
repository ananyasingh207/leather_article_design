from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:article_id>/', views.design_create_view, name='design_create'),
    path('<int:design_id>/', views.design_detail_view, name='design_detail'),
]
