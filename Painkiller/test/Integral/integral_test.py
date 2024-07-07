import unittest
from unittest.mock import patch
import tkinter as tk
from decimal import Decimal
from time import sleep
from src.core import Core
from src.doctorAPP import DoctorApp
from src.patientAPP import PatientApp

class TestDoctorAppIntegration(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.core = Core()
        self.app = DoctorApp(self.root, self.core)
        self.patient_app = PatientApp(self.root, self.core)

    def tearDown(self):
        self.root.destroy()

    @patch.object(DoctorApp, 'show_message')
    def test_doctor_patient_integration(self, mock_doctor_show_message):
        # init
        self.assertEqual(self.app.simulate_speed, 1000)
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertEqual(self.app.paused, False)
        self.assertEqual(self.app.start, False)

        # Doc set baseline
        self.app.show_baseline_scale()
        self.app.baseline_scale.set(0.02)
        self.app.set_baseline()
        status = self.core.status()
        self.assertEqual(status['Baseline Rate'], Decimal('0.02'))
        mock_doctor_show_message.assert_called_with("Success set baseline to " + "0.02" + " ml.")
        
        # Doc set bolus
        self.app.show_bolus_scale()
        self.app.bolus_scale.set(0.34)
        self.app.set_bolus()
        status = self.core.status()
        self.assertEqual(status['Bolus Amount'], Decimal('0.34'))
        mock_doctor_show_message.assert_called_with("Success set bolus to " + "0.34" + " ml.")
        
        # Patient requests bolus + Doc start
        self.core.baseline_on()
        self.app.start_simulate()
        mock_doctor_show_message.assert_called_with("Simulation started.")
        self.assertTrue(self.app.start)

        # Doc graph
        self.app.show_graph()
        self.assertEqual(self.app.showing_graph, 'on')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.NORMAL)    
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED) 

        # simulate process
        self.assertTrue(self.patient_app.request_bolus())
        for _ in range(5):
            self.core.update_by_minute()

        status = self.core.status()
        self.assertEqual(status['Time'], 6)
        self.assertEqual(status['Hourly Amount'], Decimal('0.46'))
        self.assertEqual(status['Daily Amount'], Decimal('0.46'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.34'))
        self.assertEqual(self.core._Core__hourlyRecord[-1], status['Hourly Amount'])
        self.assertEqual(self.core._Core__dailyRecord[-1], status['Hourly Amount'])

        # Doc set simulate speed
        self.app.show_simulate_speed_scale()
        self.app.speed_scale.set(2)
        self.app.set_simulate_speed()
        self.assertEqual(self.app.simulate_speed, int(1000/2))
        mock_doctor_show_message.assert_called_with("Simulation speed set to 2x.")

        # Patient requests bolus
        self.core.set_bolus(0.3)
        self.assertTrue(self.patient_app.request_bolus())
        self.core.update_by_minute()
        status = self.core.status()
        self.assertEqual(status['Time'], 7)
        self.assertEqual(status['Hourly Amount'], Decimal('0.78'))
        self.assertEqual(status['Daily Amount'], Decimal('0.78'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.3'))

        # Doc pauses + resume
        self.app.pause()
        self.assertTrue(self.app.paused)
        self.app.resume()
        self.assertFalse(self.app.paused)
        mock_doctor_show_message.assert_called_with("Simulation resumed.")

        # Doc stop graph
        self.app.stop_graph()
        mock_doctor_show_message.assert_called_with("Graph stopped.")
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL) 

        # Doc off
        self.core.baseline_on()
        
        # Doc resets system
        self.app.reset()
        status = self.core.status()
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertEqual(status['Time'], 0)
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL)    
        self.assertEqual(self.app.simulate_speed, int(1000))
        mock_doctor_show_message.assert_called_with("System reset.")
    
if __name__ == '__main__':
    unittest.main()
