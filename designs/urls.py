from django.urls import path
from . import views

urlpatterns = [
    path('', views.design_list_view, name='design_list'),
    path('my-designs/', views.design_list_view, name='my_designs'),
    path('create/<int:article_id>/', views.design_create_view, name='design_create'),
    path('<int:design_id>/', views.design_detail_view, name='design_detail'),
    path('<int:design_id>/edit/', views.design_edit_view, name='design_edit'),
    path('<int:design_id>/delete/', views.design_delete_view, name='design_delete'),
    path('<int:design_id>/duplicate/', views.design_duplicate_view, name='design_duplicate'),
]
