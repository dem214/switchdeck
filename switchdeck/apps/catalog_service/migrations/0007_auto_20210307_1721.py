# Generated by Django 3.1.7 on 2021-03-07 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog_service', '0006_parseresult_successful'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parseresult',
            options={'ordering': ('-time',), 'verbose_name': 'Parse Result', 'verbose_name_plural': 'Parse Results'},
        ),
    ]