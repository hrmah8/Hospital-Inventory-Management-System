from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import InventoryItem
from .forms import InventoryItemForm

# Create your views here.
def inventory_list(request):
    items = InventoryItem.objects.all().order_by('name')
    return render(request, 'inventory/inventory_list.html', {'items': items})

def inventory_add(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory item added successfully.")
            return redirect("inventory_list")
    else:
        form = InventoryItemForm()

    return render(request, "inventory/inventory_form.html", {
        "form": form,
        "title": "Add Inventory Item"
    })

def inventory_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory item updated successfully.")
            return redirect("inventory_list")
    else:
        form = InventoryItemForm(instance=item)

    return render(request, "inventory/inventory_form.html", {
        "form": form,
        "title": "Edit Inventory Item"
    })

def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Inventory item removed successfully.")
        return redirect("inventory_list")

    return render(request, "inventory/inventory_confirm_delete.html", {
        "item": item
    })