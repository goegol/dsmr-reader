from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestDatalogger(InterceptStdoutMixin, TestCase):
    """ Test Landis+Gyr 350 DSMR v4.2. """

    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB231126481\n",
            "\n",
            "1-3:0.2.8(42)\n",
            "0-0:1.0.0(160317221058W)\n",
            "0-0:96.1.1(xxxxxxxxxxxxxx)\n",
            "1-0:1.8.1(001255.252*kWh)\n",
            "1-0:2.8.1(000000.000*kWh)\n",
            "1-0:1.8.2(001284.838*kWh)\n",
            "1-0:2.8.2(000000.000*kWh)\n",
            "0-0:96.14.0(0002)\n",
            "1-0:1.7.0(00.187*kW)\n",
            "1-0:2.7.0(00.000*kW)\n",
            "0-0:96.7.21(00008)\n",
            "0-0:96.7.9(00000)\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\n",
            "1-0:32.32.0(00000)\n",
            "1-0:32.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(001*A)\n",
            "1-0:21.7.0(00.187*kW)\n",
            "1-0:22.7.0(00.000*kW)\n",
            "0-2:24.1.0(003)\n",
            "0-2:96.1.0(xxxxxxx)\n",
            "0-2:24.2.1(160317220000W)(01438.997*m3)\n",
            "!D625\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self.assertFalse(DsmrReading.objects.exists())
        self._intercept_command_stdout('dsmr_datalogger')
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading for Landis+Gyr 350 DSMR v4.2. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """ Test whether dsmr_datalogger reads the correct values. """
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp,
            datetime(2016, 3, 17, 21, 10, 58, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('1255.252'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('1284.838'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.187'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2016, 3, 17, 21, 0, 0, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('1438.997'))

        # Different data source.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 8)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 0)
        self.assertIsNone(meter_statistics.voltage_sag_count_l2)
        self.assertIsNone(meter_statistics.voltage_sag_count_l3)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertIsNone(meter_statistics.voltage_swell_count_l2)
        self.assertIsNone(meter_statistics.voltage_swell_count_l3)
