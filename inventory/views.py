from .alerts import get stock_alerts

def stock_alerts(request):
    alerts = get_stock_alerts()
    
    return render(
        request,
        "inventory/stock_alerts.html",
        {"alerts": alerts},
    )