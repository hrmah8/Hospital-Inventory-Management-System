from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("low-stock/", views.low_stock_report_view, name="low_stock"),
]