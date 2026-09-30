from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import render

from .models import Category, InventoryItem


@login_required
def inventory_list(request):
    items = InventoryItem.objects.select_related("category").order_by("name")

    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    status = request.GET.get("status", "")

    if q:
        items = items.filter(Q(name__icontains=q) | Q(location__icontains=q))
    if category_id.isdigit():
        items = items.filter(category_id=category_id)

    if status == "out":
        items = items.filter(quantity=0)
    elif status == "low":
        items = items.filter(quantity__gt=0, quantity__lte=F("threshold"))
    elif status == "in":
        items = items.filter(quantity__gt=F("threshold"))

    page_obj = Paginator(items, 20).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "inventory/inventory_list.html", {
        "page_obj": page_obj,
        "categories": Category.objects.order_by("name"),
        "q": q,
        "selected_category": category_id,
        "selected_status": status,
        "query_string": params.urlencode(),
    })