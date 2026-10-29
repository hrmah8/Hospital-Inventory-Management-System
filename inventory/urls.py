from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="list"),
    path("<int:pk>/quantity/", views.update_quantity, name="update_quantity"),
    path("add/", views.inventory_add, name="inventory_add"),
    path("edit/<int:pk>/", views.inventory_edit, name="inventory_edit"),
    path("delete/<int:pk>/", views.inventory_delete, name="inventory_delete"),
    path("alerts/", views.stock_alerts, name="stock_alerts")
]