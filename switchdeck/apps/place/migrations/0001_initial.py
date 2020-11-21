# Generated by Django 3.0.7 on 2020-11-21 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the region or city.', max_length=20, unique=True, verbose_name='Name')),
                ('slug', models.SlugField()),
                ('popularity', models.IntegerField(default=0, help_text='Popularity of place. The higher popularity - the higher this place in place list.', verbose_name='Popularity')),
            ],
            options={
                'verbose_name': 'Place',
                'verbose_name_plural': 'Places',
                'ordering': ['-popularity', 'name'],
            },
        ),
    ]