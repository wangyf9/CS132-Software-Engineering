import unittest
from decimal import Decimal
from src.core import Core

class TestCore(unittest.TestCase):
    def setUp(self):
        self.core = Core()

    def test_initialize(self):
        status = self.core.status()
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        self.assertEqual(status['Time'], 0)
        self.assertEqual(len(self.core._Core__timeRecord), 0)
        self.assertEqual(len(self.core._Core__minuteRecord), 0)
        self.assertEqual(len(self.core._Core__hourlyRecord), 0)
        self.assertEqual(len(self.core._Core__dailyRecord), 0)
        
    def test_set_baseline_success(self): # 0.01 - 0.1 + correct set status
        response = self.core.set_baseline(0.05)
        self.assertEqual(response, "Success set baseline to 0.05 ml.")
        self.assertEqual(self.core.status()['Baseline Rate'], Decimal('0.05'))

    def test_set_baseline_failure_big(self): # > 0.1
        response = self.core.set_baseline(0.2)
        self.assertEqual(response, "Baseline injection rate must be between 0.01 and 0.1 ml.")
        self.assertEqual(self.core.status()['Baseline Rate'], Decimal('0.01'))

    def test_set_baseline_failure_small(self): # < 0.01
        response = self.core.set_baseline(0.005)
        self.assertEqual(response, "Baseline injection rate must be between 0.01 and 0.1 ml.")
        self.assertEqual(self.core.status()['Baseline Rate'], Decimal('0.01'))

    def test_set_bolus_success(self): # 0.2 - 0.5 + correct set status
        response = self.core.set_bolus(0.3)
        self.assertEqual(response, "Success set bolus to 0.3 ml.")
        self.assertEqual(self.core.status()['Bolus Amount'], Decimal('0.3'))

    def test_set_bolus_failure_big(self): # > 0.5
        response = self.core.set_bolus(0.6)
        self.assertEqual(response, "Bolus injection amount must be between 0.2 and 0.5 ml.")
        self.assertEqual(self.core.status()['Bolus Amount'], Decimal('0.2'))

    def test_set_bolus_failure_small(self): # < 0.2
        response = self.core.set_bolus(0.1)
        self.assertEqual(response, "Bolus injection amount must be between 0.2 and 0.5 ml.")
        self.assertEqual(self.core.status()['Bolus Amount'], Decimal('0.2'))

    def test_baseline_on(self): # correct set status
        self.core.baseline_on()
        self.assertEqual(self.core.status()['Baseline Status'], 'on')

    def test_baseline_off(self): # correct set status
        self.core.baseline_off()
        self.assertEqual(self.core.status()['Baseline Status'], 'off')

    def test_validate_false_1(self):
        response = self.core.validate(Decimal('1.1'))
        self.assertFalse(response)  # False

    def test_validate_false_2(self):
        self.core._Core__hourAmount = 0.0
        self.core._Core__dailyAmount = 3.0
        response = self.core.validate(Decimal('0.1'))

        self.assertFalse(response)  # False

    def test_validate_success(self):
        response = self.core.validate(Decimal('0.1'))
        self.assertTrue(response)  # False

    def test_validate_hour_limit(self): # hour <= 1.0 || > 1.0
        self.core.baseline_on()
        self.core.set_baseline(1/60)
        self.core.update_by_minute()
        # add 60 baselines
        for _ in range(59):
            self.core.update_by_minute()
            # print(self.core.status())
        # hourly amount = 1.00 (max)
        self.assertTrue(self.core.validate(Decimal('0.0')))  # True
        self.assertFalse(self.core.validate(Decimal('0.01')))  # False

    def test_validate_daily_limit(self): # hour <= 1.0 -> daily <= 3.0 || > 3.0
        self.core.baseline_on()
        self.core.set_baseline(0.01)
        for _ in range(300):
            self.core.update_by_minute()
            # print(self.core.status())
        # hourly amount = 0.6 daily = 3.0 at this time
        self.assertTrue(self.core.validate(Decimal('0.0')))  # True
        self.assertFalse(self.core.validate(Decimal('0.01')))  # False

    def test_update_by_minute_more_than_1440(self): # > 1440
        self.core.baseline_on()
        for _ in range(1441):
            self.core.update_by_minute()
        status = self.core.status()
        self.assertEqual(len(self.core._Core__minuteRecord), 1440)
        self.assertEqual(len(self.core._Core__hourlyRecord), 1440)
        self.assertEqual(len(self.core._Core__dailyRecord), 1440)
        self.assertEqual(len(self.core._Core__timeRecord), 1440)
        self.assertEqual(status['Time'], 1441)

    def test_update_by_minute_baseline_on_validate_true(self): # on + validate true
        self.core.baseline_on()
        self.core.set_baseline(0.05)
        for _ in range(5):
            self.core.update_by_minute()
        status = self.core.status()
        self.assertEqual(len(self.core._Core__minuteRecord), 5)
        self.assertEqual(len(self.core._Core__hourlyRecord), 5)
        self.assertEqual(len(self.core._Core__dailyRecord), 5)
        self.assertEqual(len(self.core._Core__timeRecord), 5)
        self.assertEqual(status['Time'], 5)
        for record in self.core._Core__minuteRecord:
            # print(record)
            self.assertEqual(record, Decimal('0.05'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.25'))
        self.assertEqual(status['Daily Amount'], Decimal('0.25'))
        self.assertEqual(self.core._Core__hourlyRecord[-1], status['Hourly Amount'])
        self.assertEqual(self.core._Core__dailyRecord[-1], status['Hourly Amount'])

    def test_update_by_minute_baseline_on_validate_false(self): # on + validate false
        self.core.baseline_on()
        self.core.set_baseline(0.05)
        # 0.05 * 20 = 1 -> 21 - 25  == 0
        for _ in range(25):
            self.core.update_by_minute()
        status = self.core.status()
        self.assertEqual(len(self.core._Core__minuteRecord), 25)
        self.assertEqual(len(self.core._Core__hourlyRecord), 25)
        self.assertEqual(len(self.core._Core__dailyRecord), 25)
        self.assertEqual(len(self.core._Core__timeRecord), 25)
        self.assertEqual(status['Time'], 25)
        for record in self.core._Core__minuteRecord[-5:]:
            # print(record)
            self.assertEqual(record, Decimal('0.0'))
        self.assertTrue(all(amount <= Core.MAX_HOUR_AMOUNT for amount in self.core._Core__hourlyRecord[-5:]))
        self.assertTrue(all(amount <= Core.MAX_DAILY_AMOUNT for amount in self.core._Core__dailyRecord[-5:]))
        self.assertEqual(status['Hourly Amount'], Decimal('1.00'))
        self.assertEqual(status['Daily Amount'], Decimal('1.00'))
        self.assertEqual(self.core._Core__hourlyRecord[-1], status['Hourly Amount'])
        self.assertEqual(self.core._Core__dailyRecord[-1], status['Hourly Amount'])

    def test_update_by_minute_baseline_off(self):
        self.core.baseline_off()
        self.core.set_baseline(0.05)
        for _ in range(5):
            self.core.update_by_minute()
        status = self.core.status()
        self.assertEqual(len(self.core._Core__minuteRecord), 5)
        self.assertEqual(len(self.core._Core__hourlyRecord), 5)
        self.assertEqual(len(self.core._Core__dailyRecord), 5)
        self.assertEqual(len(self.core._Core__timeRecord), 5)
        for record in self.core._Core__minuteRecord:
            self.assertEqual(record, Decimal('0.0'))
        self.assertEqual(status['Time'], 5)
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(self.core._Core__hourlyRecord[-1], status['Hourly Amount'])
        self.assertEqual(self.core._Core__dailyRecord[-1], status['Hourly Amount'])

    
    def test_request_bolus_validate_success_init(self): # validate true + len == 0
        self.core.set_bolus(0.5)
        self.assertFalse(self.core.request_bolus())

        status = self.core.status()
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(len(self.core._Core__minuteRecord), 0)
        self.assertEqual(len(self.core._Core__hourlyRecord), 0)
        self.assertEqual(len(self.core._Core__dailyRecord), 0)

    def test_request_bolus_validate_success_not_init(self): # validate true + len != 0
        self.core.baseline_on()
        self.core.set_baseline(0.05)
        for _ in range(5):
            self.core.update_by_minute()
        self.core.set_bolus(0.35)
        self.assertTrue(self.core.request_bolus())
        status = self.core.status()
        self.assertEqual(status['Hourly Amount'], Decimal('0.60'))
        self.assertEqual(status['Daily Amount'], Decimal('0.60'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.35'))
        self.assertEqual(self.core._Core__hourlyRecord[-1], status['Hourly Amount'])
        self.assertEqual(self.core._Core__dailyRecord[-1], status['Hourly Amount'])

    def test_request_bolus_validate_failure(self): # validate false
        self.core.set_bolus(0.5)
        self.core.baseline_on()
        for _ in range(60):
            self.core.update_by_minute()
        self.assertFalse(self.core.request_bolus())

    def test_reset(self): # correct reset
        self.core.set_baseline(0.05)
        self.core.set_bolus(0.3)
        self.core.baseline_on()
        self.core.update_by_minute()
        self.core.reset()
        status = self.core.status()
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        self.assertEqual(status['Time'], 0)
        self.assertEqual(len(self.core._Core__timeRecord), 0)
        self.assertEqual(len(self.core._Core__minuteRecord), 0)
        self.assertEqual(len(self.core._Core__hourlyRecord), 0)
        self.assertEqual(len(self.core._Core__dailyRecord), 0)

if __name__ == '__main__':
    unittest.main()
