# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-10 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movieID', models.CharField(blank=True, max_length=255, null=True, verbose_name='movieID')),
            ],
        ),
    ]
