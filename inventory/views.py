
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import InventoryItem
from django.db import models


@login_required
def dashboard(request):
    search_query = request.GET.get("q", "").strip()

    items = InventoryItem.objects.select_related("category").all()

    if search_query:
        items = items.filter(
            Q(name__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    low_stock_items = items.filter(
        quantity__lte=models.F("low_stock_threshold")
    )

    context = {
        "items": items,
        "search_query": search_query,
        "low_stock_count": low_stock_items.count(),
        "total_items": items.count(),
    }

    return render(request, "inventory/dashboard.html", context)

