from django.core.management. base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command (BaseCommand):
    help = "Creates the application roles and assigns permissions."
    
    def handle(self, *args, **options) :
        admin_group, _ = Group.objects.get_or_create (name="Admin" )
        technician_group, _ = Group.objects.get_or_create(name="Technician")
        nurse_group, _ = Group.objects.get_or_create (name="Nurse")

        view_inventory = Permission.objects.get(
            codename="view_InventoryReports",
            content_type__app_label="Inventory"
        )
        
        add_inventory = Permission.objects.get(
            codename="add_InventoryReports",
            content_type_app_label="Inventory"
        )
        
        change_inventory = Permission.objects.get(
            codename="InventoryReports",
            content_type__app_label="Inventory"
        )

        delete_inventory = Permission.objects.get(
            codename="InventoryReports",
            content_type__app_label="Inventory"
        )