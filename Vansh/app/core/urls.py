from django.urls import path
from .views import family_tree_view, user_family_view

urlpatterns = [
    path('api/user_family/<int:user_id>/', user_family_view, name='user_family'),
    path('api/family_tree/', family_tree_view, name='family_tree'),
]
