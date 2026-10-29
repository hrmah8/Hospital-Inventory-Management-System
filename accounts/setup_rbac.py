from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Creates the application roles and assigns permissions."
    
    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Admin" )
        technician_group, _ = Group.objects.get_or_create(name="Technician")
        nurse_group, _ = Group.objects.get_or_create(name="Nurse")
        
        content_type - ContentType.objects.get_for_model(InventoryItem)
        
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                "view_inventoryitem",
                "add_inventoryitem",
                "change_inventoryitem",
                "delete_inventoryitem"
            ],
        )
        
        permission_map = {
            permission.codename: permission
            for permission in permissions
        }
        
        required = [
            "view_inventoryitem",
            "add_inventoryitem",
            "change_inventoyritem",
            "delete_inventoryitem",
        ]
        
        missing = [code for code in required if code not in permission_map]
        if missing: 
            self.stderr.write(
                self.style.ERROR(
                    "Missing permissions: "
                    + ", ".join(missing)
                    +". Run 'python manage.py migrate' first."
                )
            )
            return
        
        view_inventory = permission_map["view_inventoryitem"]
        add_inventory = permission_map["add_inventoryitem"]
        change_inventory = permission_map["change_inventoryitem"]
        delete_inventory = permission_map["delete_inventoryitem"]
        
        admin_group.permissions.set([
            view_inventory,
            add_inventory,
            change_inventory,
            delete_inventory,
        ])
        
        technician_group.permissions.set([
            view_inventory,
            change_inventory
        ])
        
        nurse_group.permissions.set([
            view_inventory,
        ])
        
        self.stdout.write(
            self.style.SUCCESS(
                "Admin, Technician, and Nurse roles configured successfully."
            )
        )