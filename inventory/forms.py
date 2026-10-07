from django import forms

from .models import Category, InventoryItem


class InventoryFilterForm(forms.Form):
    STATUS_CHOICES = [
        ("", "All statuses"),
        ("in", "In Stock"),
        ("low", "Low Stock"),
        ("out", "Out of Stock"),
    ]
    SORT_CHOICES = [
        ("name", "Name (A-Z)"),
        ("-name", "Name (Z-A)"),
        ("quantity", "Quantity (low to high)"),
        ("-quantity", "Quantity (high to low)"),
        ("category__name", "Category"),
        ("location", "Location"),
    ]

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search name, category or location"}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="All categories",
    )
    location = forms.ChoiceField(required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Built at request time so new categories/locations appear automatically
        self.fields["category"].queryset = Category.objects.order_by("name")
        locations = (
            InventoryItem.objects.order_by("location")
            .values_list("location", flat=True)
            .distinct()
        )
        self.fields["location"].choices = [("", "All locations")] + [(l, l) for l in locations]