import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from matplotlib.figure import Figure
from decimal import Decimal


from src.core import Core
from src.patientAPP import PatientApp

class TestDoctorApp(unittest.TestCase):
    # every test start, run setUp
    def setUp(self):
        self.root = tk.Tk()
        # hide the main window
        self.root.withdraw()
        self.core = Core()
        self.app = PatientApp(self.root, self.core)

    # every test finish, run tearDown
    def tearDown(self):
        self.root.destroy()

    def test_request_bolus_validate_success_init(self): # validate true + len == 0
        self.core.set_bolus(0.5)
        self.assertFalse(self.app.request_bolus())
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
        self.assertTrue(self.app.request_bolus())
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
        self.assertFalse(self.app.request_bolus())

if __name__ == '__main__':
    unittest.main()
