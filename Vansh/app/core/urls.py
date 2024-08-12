from django.urls import path
# from .views import family_tree_view, user_family_view
from . import views
urlpatterns = [
    path('family_tree/', views.family_tree_view, name='family_tree_view'),
    path('family_tree/<int:generation_depth>/', views.family_tree_view, name='family_tree_with_depth'),
    path('user_family/<int:user_id>/', views.user_family_view, name='user_family_view'),
    path('user_family_list/<int:user_id>/', views.user_family_list_view, name='user_family_list_view'),
]

