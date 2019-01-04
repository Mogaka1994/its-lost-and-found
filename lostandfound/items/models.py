from django.conf import settings
from django.db import models

from lostandfound.items.managers import ItemQuerySet

AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class LastStatus(models.Model):

    class Meta:
        db_table = 'last_status'
        managed = False

    # Because this is only a view in the database we want to do nothing
    # when the parent object is deleted.
    item = models.ForeignKey('items.Item', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('items.Status', on_delete=models.DO_NOTHING)
    machine_name = models.CharField(max_length=50)


class Action(models.Model):

    class Meta:
        db_table = 'action'
        ordering = ['-weight']

    CHECKED_IN = 'CHECKED_IN'
    CPSO = 'CPSO'
    DISPOSED = 'DISPOSED'
    ID_SERVICES = 'ID_SERVICES'
    MISSING = 'MISSING'
    OTHER = 'OTHER'
    RETURNED = 'RETURNED'

    action_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    machine_name = models.CharField(max_length=50, unique=True)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Status(models.Model):

    class Meta:
        db_table = 'status'
        ordering = ['-timestamp']

    status_id = models.AutoField(primary_key=True)
    item = models.ForeignKey('Item')
    action_taken = models.ForeignKey(Action)
    performed_by = models.ForeignKey(AUTH_USER_MODEL, null=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField()

    def __str__(self):
        return str(self.status_id)


class Location(models.Model):

    class Meta:
        db_table = 'location'
        ordering = ['name']

    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)

    def __str__(self):
        return '{self.name} - {self.long_name}'.format(**locals())


class Category(models.Model):

    class Meta:
        db_table = 'category'
        ordering = ['name']

    BOOK = 'BOOK'
    CLOTHING = 'CLOTHING'
    GLASSES = 'GLASSES'
    HEADPHONES = 'HEADPHONES'
    ID = 'ID'
    KEYS = 'KEYS'
    MUSIC = 'MUSIC'
    OTHER = 'OTHER'
    PHONE = 'PHONE'
    USB = 'USB'

    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    machine_name = models.CharField(max_length=50, unique=False, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):

    class Meta:
        db_table = 'item'

    is_valuable_help_text = (
        'Select this box if the item is an ID, key(s), or is valued at $50 or more. Items valued '
        'over $50 are turned into CPSO as soon as possible. Student IDs are turned into the ID '
        'services window in the Neuberger Hall Lobby. Checking this box automatically generates an '
        'email for the item to be picked up from the lab. USB DRIVES ARE NOT VALUABLE.'
    )

    item_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category)
    description = models.TextField()
    is_archived = models.BooleanField(default=False)
    is_valuable = models.BooleanField(default=False, help_text=is_valuable_help_text)
    location = models.ForeignKey(Location)
    possible_owner = models.ForeignKey(AUTH_USER_MODEL, related_name='item_possible_owner', null=True)
    returned_to = models.ForeignKey(AUTH_USER_MODEL, related_name='item_returned_to', null=True)

    objects = ItemQuerySet.as_manager()

    @property
    def status_count(self):
        """Get the number of statuses recorded for this item.

        Returns:
            int: The number of statuses

        """
        return self.status_set.count()

    @property
    def first_status(self):
        status_count = self.status_count
        if status_count > 0:
            return self.status_set.all()[status_count - 1]

    @property
    def last_status(self):
        if self.status_count > 0:
            return self.status_set.all()[0]

    @property
    def found_on(self):
        if self.first_status is not None:
            return self.first_status.timestamp

    @property
    def found_by(self):
        if self.first_status is not None:
            return self.first_status.performed_by

    def __str__(self):
        return self.description
