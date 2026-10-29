from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import InventoryFilterForm, QuantityUpdateForm
from .models import InventoryItem
from .services import apply_quantity_change
from .alerts import get_stock_alerts
from .models import Category, InventoryItem


@login_required
def stock_alerts(request):
    alerts = get_stock_alerts()
    
    return render(
        request,
        "inventory/stock_alerts.html",
        {"alerts": alerts},
    )
    
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

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "inventory/inventory_list.html", {
        "form": form,
        "page_obj": page_obj,
        "query_string": params.urlencode(),
    })


@login_required
@require_POST
def update_quantity(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = QuantityUpdateForm(request.POST)

    if form.is_valid():
        try:
            updated = apply_quantity_change(
                item_id=item.pk,
                user=request.user,
                change=form.signed_change(),
                action_type=form.cleaned_data["action_type"],
            )
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            messages.success(
                request, f"{updated.name}: quantity is now {updated.quantity}."
            )
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)

    # Return to the same filtered/paginated list, but only to our own site
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse("inventory:list")
    return redirect(next_url)
