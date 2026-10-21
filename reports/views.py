from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import low_stock_report, stock_summary


@login_required
def low_stock_report_view(request):
    return render(request, "reports/low_stock_report.html", {
        "rows": low_stock_report(),
        "summary": stock_summary(),
    })