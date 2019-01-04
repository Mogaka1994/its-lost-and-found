from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from lostandfound.items.models import Item, Action


@login_required
def home(request):
    today = now()
    year = now().year
    context_data = {
        'checked_in_today': Item.objects.lost('day').count(),
        'checked_in_this_year': Item.objects.lost('year').count(),
        'checked_in_by_me': Item.objects.lost().performed_by(
            request.user).count(),
        'returned_today': Item.objects.found('day').count(),
        'returned_this_year': Item.objects.found('year').count(),
        'returned_by_me': Item.objects.found().performed_by(
            request.user).count(),
    }
    return render(request, 'home.html', context=context_data)
