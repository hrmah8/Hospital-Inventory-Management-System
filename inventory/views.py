from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import render

from .forms import InventoryFilterForm
from .models import InventoryItem


@login_required
def inventory_list(request):
    form = InventoryFilterForm(request.GET or None)
    items = InventoryItem.objects.select_related("category")
    sort = "name"

    if form.is_valid():
        data = form.cleaned_data

        q = data["q"].strip()
        if q:
            items = items.filter(
                Q(name__icontains=q)
                | Q(category__name__icontains=q)
                | Q(location__icontains=q)
            )

        if data["category"]:
            items = items.filter(category=data["category"])

        if data["location"]:
            items = items.filter(location=data["location"])

        status = data["status"]
        if status == "out":
            items = items.filter(quantity=0)
        elif status == "low":
            items = items.filter(quantity__gt=0, quantity__lte=F("threshold"))
        elif status == "in":
            items = items.filter(quantity__gt=F("threshold"))

        sort = data["sort"] or "name"

    items = items.order_by(sort, "pk")

    page_obj = Paginator(items, 20).get_page(request.GET.get("page"))

    # keep the active filters in the pagination links
    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "inventory/inventory_list.html", {
        "form": form,
        "page_obj": page_obj,
        "query_string": params.urlencode(),
    })