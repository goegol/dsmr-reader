# Generated by Django 3.2.16 on 2022-11-23 21:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_backup", "0016_backup_interval_and_filename"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="backupsettings",
            name="backup_interval_hours",
        ),
        migrations.AddField(
            model_name="backupsettings",
            name="backup_interval_in_days",
            field=models.IntegerField(
                default=1,
                help_text="The minimal interval between backups. Defaults to daily.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(7),
                ],
                verbose_name="Backup interval in days",
            ),
        ),
    ]
