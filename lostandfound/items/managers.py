import datetime

from django.db import models
from django.utils.timezone import now, make_aware

#from .models import Status

class ItemQuerySet(models.QuerySet):
    def lost(self, period=None):
        """
        These are items that have been lost at one point,
        but may currently be returned
        """
        qs = self.filter(status__action_taken__machine_name='CHECKED_IN')
        print(qs.count())
        if period == 'year':
            jan1 = make_aware(datetime.datetime(year=now().year, month=1, day=1))
            return qs.filter(status__timestamp__range=(jan1, now())).distinct()
        if period == 'day':
            yesterday = now() - datetime.timedelta(days=1)
            return qs.filter(status__timestamp__gt=yesterday).distinct()
        return qs.distinct()

    def found(self, period=None):
        """
        These are items that are currently returned
        """
        qs = self.filter(laststatus__machine_name='RETURNED')
        if period == 'year':
            jan1 = make_aware(datetime.datetime(year=now().year, month=1, day=1))
            return qs.filter(laststatus__status__timestamp__range=(jan1, now())).distinct()
        if period == 'day':
            yesterday = now() - datetime.timedelta(days=1)
            return qs.filter(laststatus__status__timestamp__gt=yesterday).distinct()
        return qs.distinct()

    def performed_by(self, user):
        return self.filter(status__performed_by=user)
