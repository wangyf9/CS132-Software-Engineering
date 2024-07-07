import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from matplotlib.figure import Figure
from decimal import Decimal


from src.core import Core
from src.doctorAPP import DoctorApp

class TestDoctorApp_function(unittest.TestCase):
    # every test start, run setUp
    def setUp(self):
        self.root = tk.Tk()
        # hide the main window
        self.root.withdraw()
        self.core = Core()
        self.app = DoctorApp(self.root, self.core)
        # self.root.mainloop()

    # every test finish, run tearDown
    def tearDown(self):
        self.root.destroy()

    def test_initialize(self):
        self.assertEqual(self.app.root.title(), "Doctor Interface")
        # print(self.app.root._doctorAPP__simulate_speed)
        self.assertEqual(self.app.simulate_speed, 1000)
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertEqual(self.app.paused, False)
        self.assertEqual(self.app.start, False)
        self.assertEqual(self.app.canvas, None)
        self.assertEqual(self.app.ax1, None)
        self.assertEqual(self.app.ax2, None)
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)

    @patch.object(DoctorApp, 'show_message')
    def test_set_baseline(self, mock_show_message):  # set bolus
        self.app.show_baseline_scale()
        self.app.baseline_scale.set(0.05)
        self.app.set_baseline()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
        mock_show_message.assert_called_with("Success set baseline to " + "0.05" + " ml.")
    
    @patch.object(DoctorApp, 'show_message')
    def test_set_bolus(self, mock_show_message):     # set baseline
        self.app.show_bolus_scale()
        self.app.bolus_scale.set(0.3)
        self.app.set_bolus()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Bolus Amount'], Decimal('0.3'))
        mock_show_message.assert_called_with("Success set bolus to " + "0.3" + " ml.")

    @patch.object(DoctorApp, 'show_message')
    def test_baseline_on(self, mock_show_message): # baseline on
        self.app.baseline_on()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Baseline Status'], 'on')
        mock_show_message.assert_called_with("Baseline injection turned on.") 

    @patch.object(DoctorApp, 'show_message')
    def test_baseline_off(self, mock_show_message): # baseline off
        self.app.baseline_off()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Baseline Status'], 'off')
        mock_show_message.assert_called_with("Baseline injection turned off.")

    @patch.object(DoctorApp, 'show_message')
    def test_start_simulate(self,mock_show_message):
        self.app.start_simulate()
        mock_show_message.assert_called_with("Simulation started.")
        self.assertTrue(self.app.start)
        self.assertTrue(self.app.start_button['state'] == tk.DISABLED)

    @patch.object(DoctorApp, 'show_message')
    def test_pause_resume_off(self, mock_show_message):  # pause + resume off
        self.assertEqual(self.app.showing_graph, 'off')
        self.app.pause()
        self.assertTrue(self.app.paused)
        # self.assertFalse(self.app.start)
        self.app.resume()
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)
        mock_show_message.assert_called_with("Simulation resumed.")

    @patch.object(DoctorApp, 'show_message')
    def test_pause_resume_on(self, mock_show_message):  # pause + resume on + start
        self.app.start_simulate()
        self.app.show_graph()
        self.assertEqual(self.app.showing_graph, 'on')
        self.app.pause()        
        self.assertEqual(self.app.showing_graph, 'pause')
        self.assertTrue(self.app.paused)
        # self.assertFalse(self.app.start)
        self.app.resume()
        self.assertFalse(self.app.paused)
        self.assertEqual(self.app.showing_graph, 'on')
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)
        mock_show_message.assert_called_with("Simulation resumed.")
        self.assertTrue(self.app.start_button['state'] == tk.DISABLED)  

    def test_show_graph(self):
        self.app.show_graph()
        self.assertEqual(self.app.showing_graph, 'on')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.NORMAL)    
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)       

    @patch.object(DoctorApp, 'show_message')
    def test_reset_off(self, mock_show_message):  # show graph off
        self.app.start_simulate()
        mock_show_message.assert_called_with("Simulation started.")
        self.app.reset()
        status = self.core.status()
        mock_show_message.assert_called_with("System reset.")
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertEqual(status['Time'], 0)
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL)    
        self.assertEqual(self.app.simulate_speed, int(1000))

    @patch.object(DoctorApp, 'show_message')
    def test_reset_on(self, mock_show_message):  # show graph on
        self.app.start_simulate()
        mock_show_message.assert_called_with("Simulation started.")
        self.app.show_graph()
        self.assertTrue(self.app.showing_graph == 'on')
        self.app.reset()
        status = self.core.status()
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL)   
        self.assertEqual(status['Time'], 0)
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL) 
        mock_show_message.assert_called_with("System reset.")
        self.assertEqual(self.app.simulate_speed, int(1000))

    @patch.object(DoctorApp, 'show_message')
    def test_set_simulate_speed(self, mock_show_message):
        self.app.show_simulate_speed_scale()
        self.app.speed_scale.set(3)
        self.app.set_simulate_speed()
        self.assertEqual(self.app.simulate_speed, int(1000/3))
        mock_show_message.assert_called_with("Simulation speed set to 3x.")
    
    @patch.object(DoctorApp, 'show_message')
    def test_stop_graph(self, mock_show_message):
        self.assertEqual(self.app.showing_graph, 'off')
        self.app.show_graph()
        self.assertEqual(self.app.showing_graph, 'on')
        self.app.stop_graph()
        mock_show_message.assert_called_with("Graph stopped.")
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL)   

if __name__ == '__main__':
    unittest.main()
