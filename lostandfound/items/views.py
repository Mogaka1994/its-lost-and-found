from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404

from arcutils.ldap import ldapsearch

from .forms import (
    AdminActionForm,
    AdminItemFilterForm,
    CheckInForm,
    ItemArchiveForm,
    ItemFilterForm,
)
from .models import Item, Status


@user_passes_test(lambda u: u.is_staff)
def admin_itemlist(request):
    """Administrative item listing.

    Allows for viewing of items, taking actions on items, and archiving
    items.

    """
    item_filter_form = AdminItemFilterForm(request.GET if 'action' in request.GET else None)
    item_list = item_filter_form.filter()
    item_list = item_list.select_related('category', 'location', 'possible_owner', 'returned_to')
    item_list = item_list.prefetch_related(
        'status_set', 'status_set__action_taken', 'status_set__performed_by')

    if request.method == 'POST':
        item_archive_form = ItemArchiveForm(request.POST, item_list=item_list)
        if item_archive_form.is_valid():
            item_archive_form.save()
            messages.success(request, 'Item successfully changed')
            return HttpResponseRedirect(request.get_full_path())
    else:
        item_archive_form = ItemArchiveForm(item_list=item_list)

    return render(request, 'items/admin-itemlist.html', {
        'items': item_list,
        'item_filter': item_filter_form,
        'archive_form': item_archive_form,
    })


@login_required
def adminaction(request, item_num):
    """Administrative action page.

    Allows user to change status of items.

    """
    chosen_item = get_object_or_404(Item, pk=item_num)
    status_list = Status.objects.filter(item=item_num)

    # Perform action on item
    if request.method == 'POST':
        form = AdminActionForm(request.POST, current_user=request.user)
        if form.is_valid():
            messages.success(request, 'Item successfully changed')
            form.save(item_pk=item_num, current_user=request.user)
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = AdminActionForm(current_user=request.user)

    return render(request, 'items/admin-action.html', {
        'item': chosen_item,
        'form': form,
        'status_list': status_list,
    })


@login_required
def itemlist(request):
    """Non-administrative item listing.

    Can view item list and return items.

    """
    item_filter_form = ItemFilterForm(request.GET if 'action' in request.GET else None)
    item_list = item_filter_form.filter()
    item_list = item_list.select_related('category', 'location', 'possible_owner')
    item_list = item_list.prefetch_related('status_set', 'status_set__action_taken')
    return render(request, 'items/itemlist.html', {
        'items': item_list,
        'item_filter': item_filter_form,
    })


@login_required
def itemstatus(request, item_num):
    """Non-administrative item status page.

    Can view status and information about an item.

    """
    chosen_item = get_object_or_404(Item, pk=item_num)
    status_list = Status.objects.filter(item=item_num)
    return render(request, 'items/itemstatus.html', {
        'item': chosen_item,
        'status_list': status_list,
    })


@login_required
def checkin(request):
    """Item check in form.

    Allows lab attendant to check an item into inventory.

    """
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            new_item = form.save(current_user=request.user)
            return HttpResponseRedirect(reverse('printoff', args=[new_item.pk]))
    else:
        form = CheckInForm()
    return render(request, 'items/checkin.html', {'form': form})


@login_required
def autocomplete(request):
    """Do an LDAP search and return a JSON array."""
    q = request.GET.get('query', '')
    # Require a minimum of three characters before searching LDAP.
    if len(q) < 3:
        return JsonResponse([], safe=False)
    search = '(uid={q}*)'.format(q=q)
    results = ldapsearch(search)
    results.sort(key=lambda r: r['username'][0])
    return JsonResponse(results, safe=False)


@login_required
def printoff(request, item_id):
    """Item check in print off page.

    Page lab attends should print off when they check in an item in.

    """
    if request.method == 'POST' and request.POST['action'] == 'Return to item check-in':
        return HttpResponseRedirect(reverse('checkin'))
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'items/printoff.html', {'item': item})
