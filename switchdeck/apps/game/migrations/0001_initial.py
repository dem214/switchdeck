# Generated by Django 3.0.7 on 2020-11-22 22:03

from django.db import migrations, models
import switchdeck.apps.game.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of the game in english (may look from the shop page).', max_length=50, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(max_length=30, verbose_name='Slug')),
                ('cover', models.ImageField(blank=True, help_text='Cover of the game box or any related image.', null=True, upload_to=switchdeck.apps.game.models.games_images_path, verbose_name='Cover')),
                ('description', models.TextField(blank=True, help_text='Description of the game. Related from shop page.', verbose_name='Description')),
                ('eshop_url', models.URLField(blank=True, help_text='Link to page there can locate additional information (nintendo eshop).', null=True, verbose_name='Link to eshop')),
            ],
            options={
                'verbose_name': 'Game',
                'verbose_name_plural': 'Games',
            },
        ),
    ]
