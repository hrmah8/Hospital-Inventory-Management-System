from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="list"),
    path("<int:pk>/quantity/", views.update_quantity, name="update_quantity"),
]