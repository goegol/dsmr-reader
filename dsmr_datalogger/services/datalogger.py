import logging
from typing import Dict, Iterator, Optional

from django.db.models.expressions import F
from django.utils import timezone
from django.db import connection
import serial

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_parser import telegram_specifications, obis_references
from dsmr_parser.exceptions import InvalidChecksumError, ParseError
from dsmr_parser.parsers import TelegramParser
import dsmr_datalogger.scripts.dsmr_datalogger_api_client
import dsmr_datalogger.signals


logger = logging.getLogger("dsmrreader")


def get_dsmr_connection_parameters() -> Dict:
    """Returns the communication settings required for the DSMR version set."""
    DSMR_VERSION_MAPPING = {
        DataloggerSettings.DSMR_VERSION_2_3: telegram_specifications.V2_2,
        DataloggerSettings.DSMR_VERSION_4_PLUS: telegram_specifications.V5,
        DataloggerSettings.DSMR_BELGIUM_FLUVIUS: telegram_specifications.BELGIUM_FLUVIUS,
        DataloggerSettings.DSMR_LUXEMBOURG_SMARTY: telegram_specifications.LUXEMBOURG_SMARTY,
    }

    datalogger_settings = DataloggerSettings.get_solo()
    is_default_dsmr_protocol = (
        datalogger_settings.dsmr_version != DataloggerSettings.DSMR_VERSION_2_3
    )
    connection_parameters = dict(
        telegram_timeout=20,  # After this threshold, the datalogger will throw an exception to break the infinite loop.
        specifications=DSMR_VERSION_MAPPING[datalogger_settings.dsmr_version],
    )

    extra_connection_parameters = {
        DataloggerSettings.INPUT_METHOD_SERIAL: dict(
            url_or_port=datalogger_settings.serial_port,
            baudrate=115200 if is_default_dsmr_protocol else 9600,
            bytesize=serial.EIGHTBITS if is_default_dsmr_protocol else serial.SEVENBITS,
            parity=(
                serial.PARITY_NONE if is_default_dsmr_protocol else serial.PARITY_EVEN
            ),
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
        ),
        DataloggerSettings.INPUT_METHOD_IPV4: dict(
            url_or_port="socket://{}:{}".format(
                datalogger_settings.network_socket_address,
                datalogger_settings.network_socket_port,
            )
        ),
    }[datalogger_settings.input_method]

    connection_parameters.update(extra_connection_parameters)
    return connection_parameters


def get_telegram_generator() -> Iterator:
    """Returns a generator for reading telegrams."""

    # Partially reuse the remote datalogger.
    connection_parameters = get_dsmr_connection_parameters()
    del connection_parameters["specifications"]

    return dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram(
        **connection_parameters
    )


def telegram_to_reading(data: str) -> DsmrReading:
    """Converts a P1 telegram to a DSMR reading, which will be stored in database."""
    params = get_dsmr_connection_parameters()
    parser = TelegramParser(params["specifications"])
    logger.debug("Received telegram:\n%s", data)

    try:
        parsed_telegram = parser.parse(data)
    except (InvalidChecksumError, ParseError) as error:
        # Hook to keep track of failed readings count.
        MeterStatistics.objects.all().update(
            rejected_telegrams=F("rejected_telegrams") + 1
        )
        logger.warning("Rejected telegram: %s", error)
        raise InvalidTelegramError(error) from error

    return _map_telegram_to_model(parsed_telegram=parsed_telegram, data=data)


def _map_telegram_to_model(parsed_telegram: Dict, data: str):
    """Maps parsed telegram to the fields."""
    READING_FIELDS = [
        x.name
        for x in DsmrReading._meta.get_fields()
        if x.name not in ("id", "processed")
    ]
    STATISTICS_FIELDS = [
        x.name
        for x in MeterStatistics._meta.get_fields()
        if x.name not in ("id", "rejected_telegrams", "latest_telegram")
    ]

    datalogger_settings = DataloggerSettings.get_solo()
    model_fields = {k: None for k in READING_FIELDS + STATISTICS_FIELDS}
    mapping = _get_dsmrreader_mapping(datalogger_settings)

    for obis_ref, obis_data in parsed_telegram.items():
        try:
            # Skip any fields we're not storing in our system.
            target_field = mapping[obis_ref]
        except KeyError:
            continue

        if isinstance(target_field, dict):
            model_fields[target_field["value"]] = obis_data.value
            model_fields[target_field["datetime"]] = obis_data.datetime
        else:
            model_fields[target_field] = obis_data.value

    # Defaults for telegrams with missing data.
    model_fields["timestamp"] = model_fields["timestamp"] or timezone.now()
    model_fields["electricity_delivered_2"] = (
        model_fields["electricity_delivered_2"] or 0
    )  # type:ignore[assignment]
    model_fields["electricity_returned_2"] = (
        model_fields["electricity_returned_2"] or 0
    )  # type:ignore[assignment]

    # Ignore invalid dates on device bus. Reset the delivered value as well. This MUST be checked before override below.
    if model_fields["extra_device_timestamp"] is None:
        model_fields["extra_device_delivered"] = None

    # This optional setting fixes some rare situations where the smart meter's internal clock is incorrect.
    if datalogger_settings.override_telegram_timestamp:
        now = timezone.now()

        logger.debug("WARNING: Overriding telegram timestamps due to configuration")
        model_fields["timestamp"] = now

        if model_fields["extra_device_timestamp"] is not None:
            # WARNING: So None (v2, v3, Fluvius) default to v4 behaviour.
            is_v5 = model_fields["dsmr_version"] is not None and model_fields[
                "dsmr_version"
            ].startswith("5")

            model_fields["extra_device_timestamp"] = (
                calculate_fake_gas_reading_timestamp(now=now, is_dsmr_v5=is_v5)
            )

    # Fix for rare smart meters with a timestamp in the far future. We should disallow that.
    discard_after = timezone.now() + timezone.timedelta(hours=24)

    if model_fields["timestamp"] > discard_after or (
        model_fields["extra_device_timestamp"] is not None
        and model_fields["extra_device_timestamp"] > discard_after
    ):
        error_message = "Discarded telegram with future timestamp(s): {} / {}".format(
            model_fields["timestamp"], model_fields["extra_device_timestamp"]
        )
        logger.error(error_message)
        raise InvalidTelegramError(error_message)

    # Now we need to split reading & statistics. So we split the dict here.
    reading_kwargs = {k: model_fields[k] for k in READING_FIELDS}
    statistics_kwargs = {k: model_fields[k] for k in STATISTICS_FIELDS}

    # Reading will be processed later.
    new_instance = DsmrReading.objects.create(**reading_kwargs)

    # There should already be one in database, created when migrating.
    statistics_kwargs["latest_telegram"] = data  # type:ignore[assignment]
    MeterStatistics.get_solo().update(
        **statistics_kwargs
    )  # Update() is required for signal!

    # Creation should be completed, can now be broadcasted for post processing.
    dsmr_datalogger.signals.raw_telegram.send_robust(None, data=data)
    dsmr_datalogger.signals.dsmr_reading_created.send_robust(
        None, instance=new_instance
    )

    return new_instance


def _get_dsmrreader_mapping(datalogger_settings: DataloggerSettings) -> Dict:
    """Returns the mapping for OBIS to DSMR-reader (model fields)."""
    SPLIT_GAS_FIELD = {
        "value": "extra_device_delivered",
        "datetime": "extra_device_timestamp",
    }

    # Data stored in database for every reading.
    mapping = {
        obis_references.P1_MESSAGE_TIMESTAMP: "timestamp",
        obis_references.ELECTRICITY_USED_TARIFF_1: "electricity_delivered_1",
        obis_references.ELECTRICITY_DELIVERED_TARIFF_1: "electricity_returned_1",
        obis_references.ELECTRICITY_USED_TARIFF_2: "electricity_delivered_2",
        obis_references.ELECTRICITY_DELIVERED_TARIFF_2: "electricity_returned_2",
        obis_references.CURRENT_ELECTRICITY_USAGE: "electricity_currently_delivered",
        obis_references.CURRENT_ELECTRICITY_DELIVERY: "electricity_currently_returned",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: "phase_currently_delivered_l1",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: "phase_currently_delivered_l2",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: "phase_currently_delivered_l3",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: "phase_currently_returned_l1",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: "phase_currently_returned_l2",
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: "phase_currently_returned_l3",
        obis_references.INSTANTANEOUS_VOLTAGE_L1: "phase_voltage_l1",
        obis_references.INSTANTANEOUS_VOLTAGE_L2: "phase_voltage_l2",
        obis_references.INSTANTANEOUS_VOLTAGE_L3: "phase_voltage_l3",
        obis_references.INSTANTANEOUS_CURRENT_L1: "phase_power_current_l1",
        obis_references.INSTANTANEOUS_CURRENT_L2: "phase_power_current_l2",
        obis_references.INSTANTANEOUS_CURRENT_L3: "phase_power_current_l3",
        # For some reason this identifier contains two fields, therefore we split them.
        obis_references.HOURLY_GAS_METER_READING: SPLIT_GAS_FIELD,
        obis_references.GAS_METER_READING: SPLIT_GAS_FIELD,  # Legacy
        # Static data, stored in database but only data of the last reading is preserved.
        obis_references.P1_MESSAGE_HEADER: "dsmr_version",
        obis_references.ELECTRICITY_ACTIVE_TARIFF: "electricity_tariff",
        obis_references.SHORT_POWER_FAILURE_COUNT: "power_failure_count",
        obis_references.LONG_POWER_FAILURE_COUNT: "long_power_failure_count",
        obis_references.VOLTAGE_SAG_L1_COUNT: "voltage_sag_count_l1",
        obis_references.VOLTAGE_SAG_L2_COUNT: "voltage_sag_count_l2",
        obis_references.VOLTAGE_SAG_L3_COUNT: "voltage_sag_count_l3",
        obis_references.VOLTAGE_SWELL_L1_COUNT: "voltage_swell_count_l1",
        obis_references.VOLTAGE_SWELL_L2_COUNT: "voltage_swell_count_l2",
        obis_references.VOLTAGE_SWELL_L3_COUNT: "voltage_swell_count_l3",
    }

    if datalogger_settings.dsmr_version == DataloggerSettings.DSMR_BELGIUM_FLUVIUS:
        # Cheap hack for forcing channel selection.
        try:
            mbus_reference = {
                DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_1: obis_references.BELGIUM_MBUS1_METER_READING2,
                DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_2: obis_references.BELGIUM_MBUS2_METER_READING2,
                DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_3: obis_references.BELGIUM_MBUS3_METER_READING2,
                DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_4: obis_references.BELGIUM_MBUS4_METER_READING2,
            }[datalogger_settings.dsmr_extra_device_channel]
        except KeyError:
            mbus_reference = obis_references.BELGIUM_MBUS_WILDCARD_METER_READING2

        mapping.update(
            {
                mbus_reference: SPLIT_GAS_FIELD,
            }
        )

    if datalogger_settings.dsmr_version == DataloggerSettings.DSMR_LUXEMBOURG_SMARTY:
        mapping.update(
            {
                obis_references.ELECTRICITY_IMPORTED_TOTAL: "electricity_delivered_1",
                obis_references.ELECTRICITY_EXPORTED_TOTAL: "electricity_returned_1",
            }
        )

    return mapping


def postgresql_approximate_reading_count() -> Optional[int]:  # pragma: nocover
    """A live count is too slow on huge datasets. Using reltuples is accurate enough for an approximate."""
    if connection.vendor != "postgresql":
        return None

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT reltuples as approximate_row_count FROM pg_class WHERE relname = %s;",
            [DsmrReading._meta.db_table],
        )
        reading_count = cursor.fetchone()[0]
        return int(reading_count)


def calculate_fake_gas_reading_timestamp(
    now: timezone.datetime, is_dsmr_v5: bool
) -> timezone.datetime:
    """When overriding time, we cannot fake each gas reading to have its own timestamp. Simulate meters instead."""
    now = now.replace(second=0, microsecond=0)

    if not is_dsmr_v5:
        # DSMR v4 should group by hour.
        return now.replace(minute=0)

    # Group by 5 minutes.
    return now.replace(
        minute=now.minute - now.minute % 5,
    )
