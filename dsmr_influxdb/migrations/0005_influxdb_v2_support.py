# Generated by Django 3.2.8 on 2021-11-17 20:50

from django.db import migrations, models


def disable_influxdb_integration(apps, schema_editor):
    """Ensure the user manually reconfigures the integration first."""
    InfluxdbIntegrationSettings = apps.get_model(
        "dsmr_influxdb", "InfluxdbIntegrationSettings"
    )

    instance, _ = InfluxdbIntegrationSettings.objects.get_or_create()
    instance.update(enabled=False)


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_influxdb", "0004_client_settings_update"),
    ]

    operations = [
        migrations.RenameField(
            model_name="influxdbintegrationsettings",
            old_name="database",
            new_name="bucket",
        ),
        migrations.AlterField(
            model_name="influxdbintegrationsettings",
            name="bucket",
            field=models.CharField(
                default="dsmrreader_measurements",
                help_text="The name of the bucket used in InfluxDB.",
                max_length=64,
                verbose_name="InfluxDB bucket",
            ),
        ),
        migrations.AddField(
            model_name="influxdbintegrationsettings",
            name="api_token",
            field=models.CharField(
                default="",
                help_text="The API token to use.",
                max_length=64,
                verbose_name="InfluxDB API token",
            ),
        ),
        migrations.AddField(
            model_name="influxdbintegrationsettings",
            name="organization",
            field=models.CharField(
                default="",
                help_text="The organization to use.",
                max_length=64,
                verbose_name="InfluxDB organization",
            ),
        ),
        migrations.RemoveField(
            model_name="influxdbintegrationsettings",
            name="username",
        ),
        migrations.RemoveField(
            model_name="influxdbintegrationsettings",
            name="password",
        ),
        # The same disable applies both ways.
        migrations.RunPython(
            disable_influxdb_integration, disable_influxdb_integration
        ),
    ]
