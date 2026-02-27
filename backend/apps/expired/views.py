from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expired

@login_required
def expired_list(request):
    items = Expired.objects.select_related('created_by').order_by('-report_date')
    return render(request, 'expired/expired_list.html', {
        'expired_items': items,
    })
