from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list_view, name='article_list'),
    path('<int:article_id>/', views.article_detail_view, name='article_detail'),
    path('<int:article_id>/design/', views.design_article_placeholder_view, name='design_article'),
]
