from django import forms

from inventory.models import Category, InventoryItem


class CurrentInventoryFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="All categories",
    )
    location = forms.ChoiceField(required=False)

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