from django.urls import path
from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("posts/novo/", views.post_create, name="post_create"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/editar/", views.post_update, name="post_update"),
    path("posts/<int:pk>/remover/", views.post_delete, name="post_delete"),
]
