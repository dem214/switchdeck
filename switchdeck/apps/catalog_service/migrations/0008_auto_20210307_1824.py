# Generated by Django 3.1.7 on 2021-03-07 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog_service', '0007_auto_20210307_1721'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parseresult',
            options={'get_latest_by': ('time',), 'ordering': ('-time',), 'verbose_name': 'Parse Result', 'verbose_name_plural': 'Parse Results'},
        ),
    ]
