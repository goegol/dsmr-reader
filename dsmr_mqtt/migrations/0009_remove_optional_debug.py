# Generated by Django 2.2.5 on 2019-09-25 19:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_mqtt", "0008_mqtt_null_payload"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mqttbrokersettings",
            name="debug",
        ),
    ]
