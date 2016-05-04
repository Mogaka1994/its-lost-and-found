from django.db import migrations, models


def set_long_name(apps, schema_editor):
    model = apps.get_model('items', 'location')
    model.objects.filter(name='ML 115').update(long_name='Library First Floor Lab')
    model.objects.filter(name='IDSC').update(long_name='Broadway Housing Computer Lab')
    model.objects.filter(name='ICC').update(long_name='Neuberger Hall Fourth Floor Computer Labs')
    model.objects.filter(name='NH461').update(long_name='Neuberger Hall Fourth Floor Computer Labs')
    model.objects.filter(name='SINQ').update(long_name='University Studies First Floor Computer Labs')
    model.objects.filter(name='FRINQ').update(long_name='University Studies First Floor Computer Labs')
    model.objects.filter(name='CH1').update(long_name='University Studies First Floor Computer Labs')


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0018_auto_20160411_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='long_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),

        migrations.RunPython(set_long_name),
    ]
