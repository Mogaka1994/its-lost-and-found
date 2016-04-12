from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Q
from django.forms import ModelForm
from django.template.loader import render_to_string

from arcutils.ldap import escape, ldapsearch

from .models import Item, Location, Category, Status, Action


def check_ldap(username):
    """Check LDAP to ensure a user name exists."""
    q = escape(username)
    search = '(uid={q}*)'.format(q=q)
    results = ldapsearch(search)
    return bool(results)


def create_user(first_name, last_name, email):
    """Create a new user, ensuring their username is unique."""
    user_model = get_user_model()

    i = 0
    username_template = '{first_name}_{last_name}{i}'
    username = username_template.format(**locals())
    while user_model.objects.filter(username=username).exists():
        i += 1
        username = username_template.format(**locals())

    user = user_model.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        is_active=False,
        is_staff=False)

    return user


class AdminActionForm(forms.Form):

    """Form used on the admin-action page."""

    action_choice = forms.ModelChoiceField(
        queryset=Action.objects.all(), required=True, empty_label=None)
    note = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, current_user, **kwargs):
        """Allow only the return option to be selected by lab attendants."""
        self.user = current_user
        super(AdminActionForm, self).__init__(*args, **kwargs)
        if not self.user.is_staff:
            self.fields.pop('action_choice')

    def checkout_email(self, item):
        """Send an email to all the admins when a valuable item is checked out."""
        subject = 'Valuable item checked out'
        to = settings.ITS.CHECKOUT_EMAIL_TO
        from_email = settings.ITS.CHECKOUT_EMAIL_FROM

        ctx = {
            'found_on': str(item.found_on),
            'possible_owner_name': str(item.possible_owner),
            'returned_by': str(item.last_status.performed_by),
            'returned_to': str(item.returned_to),
            'found_in': item.location.name,
            'category': item.category.name,
            'description': item.description
        }

        message = render_to_string('items/checkout_email.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()

    def clean(self):
        """Require note field on action of OTHER."""
        cleaned_data = super().clean()
        if not cleaned_data.get('action_choice'):
            cleaned_data['action_choice'] = Action.objects.get(machine_name=Action.RETURNED)
        note = cleaned_data.get('note')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')

        if cleaned_data['action_choice'].machine_name == Action.RETURNED and not first_name:
            self.add_error('first_name', 'First name is required when returning item.')

        if cleaned_data['action_choice'].machine_name == Action.RETURNED and not last_name:
            self.add_error('last_name', 'Last name is required when returning item.')

        if cleaned_data['action_choice'].machine_name == Action.RETURNED and not email:
            self.add_error('email', 'Email is required when returning item.')

        if cleaned_data['action_choice'].machine_name == Action.OTHER and not note:
            self.add_error('note', 'Note required when choosing action of type Other.')

        return cleaned_data

    def save(self, *args, item_pk, current_user, **kwargs):
        """If an item is being returned, create a new user for the
        person the item is being returned to if they don't already
        exist. Then send an email to the staff mailing list if the item
        is valuable.

        If an item is being set to checked in, set it's returned_to
        field to None.

        """
        item = Item.objects.get(pk=item_pk)
        action_choice = self.cleaned_data['action_choice']
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        Status.objects.create(
            item=item, action_taken=action_choice, note=self.cleaned_data['note'],
            performed_by=current_user)

        # If they chose to change status to checked in we need to make sure to
        # set the returned_to field to None
        if action_choice.machine_name == Action.CHECKED_IN:
            item.returned_to = None
        elif action_choice.machine_name == Action.RETURNED:
            user_model = get_user_model()
            returned_user = user_model.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                email__iexact=email
            ).first()
            if returned_user is None:
                returned_user = create_user(first_name, last_name, email)
            item.returned_to = returned_user
            if item.is_valuable:
                self.checkout_email(item)

        item.save()
        return item


class AdminItemFilterForm(forms.Form):

    """Administrative item filter form for the admin item list page."""

    sort_choices = (
        ('-pk', 'Found most recently'),
        ('pk', 'Found least recently'),
        ('location', 'Location'),
        ('category', 'Category'),
        ('description', 'Description'),
        ('possible_owner', 'Possible owner'),
    )

    admin_item_choices = (
        ('active', 'Active'),
        ('archived', 'Archived only'),
        ('valuable', 'Valuable only'),
    )

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    sort_by = forms.ChoiceField(choices=sort_choices, required=False)
    items = forms.ChoiceField(
        choices=admin_item_choices, required=False, initial=admin_item_choices[0][0])
    keyword_or_last_name = forms.CharField(max_length=50, required=False)

    def filter(self):
        filters = {}
        valid = self.is_valid()

        if valid:
            items = self.cleaned_data.get('items')

            if items == 'active':
                # Show unarchived only and both valuable & not valuable
                filters['is_archived'] = False
            elif items == 'archived':
                # Show archived only and both valuable & not valuable
                filters['is_archived'] = True
            elif items == 'valuable':
                # Show valuable only and both archived & not archived
                filters['is_valuable'] = True

            location = self.cleaned_data.get('location')
            if location:
                filters['location'] = Location.objects.get(name=location).pk

            category = self.cleaned_data.get('category')
            if category:
                filters['category'] = Category.objects.get(name=category).pk

            search_term = self.cleaned_data.get('keyword_or_last_name')
            if search_term:
                keyword_filter = (
                    Q(description__icontains=search_term) |
                    Q(possible_owner__last_name__icontains=search_term)
                )
            else:
                keyword_filter = None
        else:
            filters['is_archived'] = False
            keyword_filter = None

        item_list = Item.objects.filter(**filters)

        if keyword_filter:
            item_list = item_list.filter(keyword_filter)

        if valid:
            order_by = self.cleaned_data.get('sort_by') or '-pk'
        else:
            order_by = '-pk'

        item_list = item_list.order_by(order_by, '-is_archived')

        return item_list


class ItemFilterForm(AdminItemFilterForm):

    """Item filter form for the regular item list page."""

    item_choices = (
        ('active', 'Active'),
        ('valuable', 'Valuable only'),
    )

    items = forms.ChoiceField(choices=item_choices, required=False, initial=item_choices[0][0])

    def filter(self):
        """Update filter so lab attendants can only see items with CHECKED_IN status."""
        item_list = super(ItemFilterForm, self).filter()
        item_list = item_list.filter(laststatus__machine_name=Action.CHECKED_IN)
        return item_list


class ItemArchiveForm(forms.Form):

    """Item archiving form used on the administrative item listing page."""

    def __init__(self, *args, item_list, **kwargs):
        """Setup a pre-filled checkbox, based on the item's current archived status."""
        super(ItemArchiveForm, self).__init__(*args, **kwargs)

        self.item_list = item_list
        for item in item_list:
            field = forms.BooleanField(
                initial=item.is_archived, required=False,
                widget=forms.CheckboxInput(attrs={'class': 'checkbox_archive'}))
            self.fields['archive-%d' % item.pk] = field

    def __iter__(self):
        """when iterating over this form, add archive-item.pk to each item."""
        for item in self.item_list:
            yield item, self['archive-%d' % item.pk]

    def save(self):
        """If an item is in the list, swap the items archived status."""
        changed = False

        for item in self.item_list:
            is_archived = self.cleaned_data.get("archive-%d" % item.pk)

            if item.is_archived is not is_archived:
                item.is_archived = is_archived
                item.save()
                changed = True

        return changed


class CheckInForm(ModelForm):

    """Form for the checkin view."""

    class Meta:
        model = Item
        fields = ['location', 'category', 'description', 'is_valuable']

    possible_owner_found = forms.BooleanField(required=False)
    username = forms.CharField(
        required=False, label='Odin username',
        help_text='Start typing a username for suggestions')
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def checkin_email(self, item):
        """Send an email to all the admins when a valuable item is checked in."""
        subject = 'Valuable item checked in'
        to = settings.ITS.CHECKIN_EMAIL_TO
        from_email = settings.ITS.CHECKIN_EMAIL_FROM

        ctx = {
            'found_on': str(item.found_on),
            'possible_owner_name': str(item.possible_owner),
            'found_by': str(item.found_by),
            'found_in': item.location.name,
            'category': item.category.name,
            'description': item.description
        }

        message = render_to_string('items/checkin_email.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()

    def user_checkin_email(self, item, possible_owner):
        """Send an email to a possible owner when an item they own is checked in."""

        subject = 'An item belonging to you was found'
        to = [possible_owner.email]
        from_email = settings.ITS.CHECKIN_EMAIL_FROM

        ctx = {
            'possible_owner_name': str(item.possible_owner),
            'found_in': item.location.name,
        }

        if item.category.machine_name == Category.USB:
            message = render_to_string('items/user_checkin_email_usb.txt', ctx)

        elif item.category.machine_name == Category.ID:
            message = render_to_string('items/user_checkin_email_id.txt', ctx)

        else:
            message = render_to_string('items/user_checkin_email_all_other.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()

    def clean(self):
        """If a possible owner has been found, force the person to
        provide a first name, last name, and email."""
        cleaned_data = super(CheckInForm, self).clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        possible_owner_found = cleaned_data.get("possible_owner_found")

        # If possilbe owner found is checked we need to make these
        # optional fields required.
        if possible_owner_found and not first_name:
            self.add_error("first_name", "First name required")

        if possible_owner_found and not last_name:
            self.add_error("last_name", "Last name required")

        if possible_owner_found and not email:
            self.add_error("email", "Email required")

        if possible_owner_found and username and not check_ldap(username):
            self.add_error("username", "Invalid username, enter a valid username or leave blank.")

        return cleaned_data

    def save(self, *args, current_user, **kwargs):
        """If a possible owner has been found send them an email. If an
        item is valuable send the staff mailing list an email."""
        user_first_name = self.cleaned_data['first_name']
        user_last_name = self.cleaned_data['last_name']
        user_email = self.cleaned_data['email']

        # If an owner was found we need to record them as an owner
        # This may require that a new user is created
        if self.cleaned_data.get("possible_owner_found") is True:
            user_model = get_user_model()
            checkin_user = user_model.objects.filter(
                first_name=user_first_name, last_name=user_last_name, email=user_email).first()
            if checkin_user is None:
                checkin_user = create_user(user_first_name, user_last_name, user_email)
            self.instance.possible_owner = checkin_user

        item = super(CheckInForm, self).save(*args, **kwargs)

        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        Status.objects.create(
            item=item, action_taken=new_action, note="Initial check-in", performed_by=current_user)

        if self.cleaned_data['email'] != '':
            self.user_checkin_email(item, checkin_user)

        if self.cleaned_data['is_valuable'] is True:
            self.checkin_email(item)

        return item
