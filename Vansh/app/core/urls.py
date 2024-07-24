from django.urls import path
from .views import family_tree_view

urlpatterns = [
    path('family-tree/', family_tree_view, name='family-tree'),
]
