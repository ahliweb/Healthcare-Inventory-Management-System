from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Recall

@login_required
def recall_list(request):
    recalls = Recall.objects.select_related('supplier', 'created_by').order_by('-recall_date')
    return render(request, 'recall/recall_list.html', {
        'recalls': recalls,
    })
