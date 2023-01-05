# Generated by Django 3.2.16 on 2023-01-05 21:46

from django.db import migrations


def regenerate_data(apps, schema_editor):
    """Try to find any historic data for day statistics meter positions."""
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")

    import dsmr_datalogger.services.readings

    # No DB index, but should be fine.
    days = DayStatistics.objects.filter(electricity_reading_timestamp=None)
    day_count = days.count()
    x = 0

    for current in days:
        x += 1
        print(
            "Data migration: Retroactively adding reading meter position timestamps and updating meter positions for day statistics: {} ({}/{})".format(
                current.day, x, day_count
            )
        )

        try:
            # @TODO: day_consumption() is still unreliable at this time due to #1770, rework later before marking OK again.
            meter_positions = (
                dsmr_datalogger.services.readings.first_meter_positions_of_day(
                    day=current.day
                )
            )
        except LookupError:
            print(" - No data found for {}, skipping...".format(current.day))
            continue

        current.electricity_reading_timestamp = meter_positions.electricity_timestamp
        current.electricity1_reading = meter_positions.electricity_delivered_1
        current.electricity2_reading = meter_positions.electricity_delivered_2
        current.electricity1_returned_reading = meter_positions.electricity_returned_1
        current.electricity2_returned_reading = meter_positions.electricity_returned_2

        # Do not override old values, when they happen to be gone by now (e.g. a user lost readings in the past year).
        if (
            meter_positions.extra_device_delivered is not None
            or current.gas_reading is None
        ):
            current.gas_reading_timestamp = meter_positions.extra_device_timestamp
            current.gas_reading = meter_positions.extra_device_delivered

        current.save()


def revert_regenerated_data(apps, schema_editor):
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")
    DayStatistics.objects.all().update(
        electricity_reading_timestamp=None,
        gas_reading_timestamp=None,
    )


class Migration(migrations.Migration):

    operations = [migrations.RunPython(regenerate_data, revert_regenerated_data)]

    dependencies = [
        ("dsmr_stats", "0018_day_statistics_meter_position_timestamps"),
    ]
