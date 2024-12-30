# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_backup", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dropboxsettings",
            name="access_token",
            field=models.CharField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                verbose_name="Dropbox access token",
            ),
        ),
    ]
