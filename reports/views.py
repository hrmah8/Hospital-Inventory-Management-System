import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .forms import CurrentInventoryFilterForm, LowStockFilterForm
from .services import current_inventory_report, low_stock_report, stock_summary


def _csv_safe(value):
    """Stop spreadsheet programs from running text that starts like a formula."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


# ---------- Report2: Low-Stock Report ----------

def _low_stock_data(request):
    form = LowStockFilterForm(request.GET or None)
    category, location, status = None, "", ""
    if form.is_valid():
        category = form.cleaned_data["category"]
        location = form.cleaned_data["location"]
        status = form.cleaned_data["status"]
    return form, low_stock_report(category, location, status)


@login_required
def low_stock_report_view(request):
    form, rows = _low_stock_data(request)
    return render(request, "reports/low_stock_report.html", {
        "form": form,
        "rows": rows,
        "summary": stock_summary(),
    })


@login_required
def low_stock_export(request):
    _, rows = _low_stock_data(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="low_stock_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Item", "Category", "Quantity", "Threshold", "Shortage", "Location", "Status"])
    for row in rows:
        item = row["item"]
        writer.writerow([
            _csv_safe(item.name),
            _csv_safe(item.category.name),
            item.quantity,
            item.threshold,
            row["shortage"],
            _csv_safe(item.location),
            row["status"],
        ])
    return response


# ---------- Report1: Current Inventory Report ----------

def _current_inventory_data(request):
    form = CurrentInventoryFilterForm(request.GET or None)
    category, location = None, ""
    if form.is_valid():
        category = form.cleaned_data["category"]
        location = form.cleaned_data["location"]
    return form, current_inventory_report(category, location)


@login_required
def current_inventory_report_view(request):
    form, report = _current_inventory_data(request)
    return render(request, "reports/current_inventory_report.html", {
        "form": form,
        "rows": report["rows"],
        "by_category": report["by_category"],
        "summary": report["summary"],
    })


@login_required
def current_inventory_export(request):
    _, report = _current_inventory_data(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="current_inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(["Item", "Category", "Quantity", "Threshold", "Location", "Status"])
    for row in report["rows"]:
        item = row["item"]
        writer.writerow([
            _csv_safe(item.name),
            _csv_safe(item.category.name),
            item.quantity,
            item.threshold,
            _csv_safe(item.location),
            row["status"],
        ])
    return response