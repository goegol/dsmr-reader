# Generated by Django 3.2.11 on 2022-01-31 21:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_influxdb", "0005_influxdb_v2_support"),
    ]

    operations = [
        migrations.AlterField(
            model_name="influxdbintegrationsettings",
            name="api_token",
            field=models.CharField(
                default="",
                help_text="The API token to use.",
                max_length=128,
                verbose_name="InfluxDB API token",
            ),
        ),
        migrations.AlterField(
            model_name="influxdbintegrationsettings",
            name="bucket",
            field=models.CharField(
                default="dsmrreader_measurements",
                help_text="The name of the bucket used in InfluxDB.",
                max_length=128,
                verbose_name="InfluxDB bucket",
            ),
        ),
        migrations.AlterField(
            model_name="influxdbintegrationsettings",
            name="organization",
            field=models.CharField(
                default="",
                help_text="The organization to use.",
                max_length=128,
                verbose_name="InfluxDB organization",
            ),
        ),
    ]
