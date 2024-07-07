import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from matplotlib.figure import Figure
from decimal import Decimal
import time
import matplotlib.pyplot as plt

from src.core import Core
from src.doctorAPP import DoctorApp
from src.patientAPP import PatientApp

class TestDoctorApp_UI(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """Initialize the test environment and set class-level variables"""
        self.root1 = tk.Tk()
        self.root2 = tk.Tk()
        self.core = Core()
        self.app = DoctorApp(self.root1, self.core)
        self.patient = PatientApp(self.root2, self.core)
        self.root1.update_idletasks()
        self.root1.update()
        self.root2.update_idletasks()
        self.root2.update()

    def setUp(self):
        self.app.start = False
        self.paused = False
        self.resume_button = None
        self.pause_label = None
        self.app.start_button.config(state=tk.NORMAL)
        self.app.simulate_speed = 1000
        if self.app.showing_graph == 'on':
            self.app.canvas.figure.clf()
            self.core.figure.clf()
            self.core.figure = plt.Figure(figsize=(10, 5))
            self.app.canvas.get_tk_widget().destroy()
            self.app.canvas = None  
            self.app.ax1 = None
            self.app.ax2 = None
        self.app.showing_graph = 'off'
        self.app.graph_button.config(state=tk.NORMAL)
        self.app.stop_graph_button.config(state=tk.DISABLED)
        self.core.reset()
        self.root1.update_idletasks()
        self.root1.update()
        self.root2.update_idletasks()
        self.root2.update()

    def tearDown(self):
        self.root1.update_idletasks()
        self.root1.update()
        self.root2.update_idletasks()
        self.root2.update()

    @classmethod
    def tearDownClass(self):
        """Cleanup work after all test cases are executed"""
        self.root1.destroy()
        self.root2.destroy()
        self.root1.update_idletasks()
        self.root1.update()
        self.root2.update_idletasks()
        self.root2.update()

    def button_click(self, button): # simulate button click
        button.invoke()

    @patch.object(DoctorApp, 'show_message')
    def test_set_baseline(self, mock_show_message): # set_baseline_button + set_button
        time.sleep(1) 
        self.button_click(self.app.set_baseline_button)
        self.app.baseline_scale.set(0.03)
        self.button_click(self.app.set_button)
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.03'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        mock_show_message.assert_called_with("Success set baseline to " + "0.03" + " ml.")
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_set_bolus(self, mock_show_message): # set_bolus_button + set_button
        time.sleep(1) 
        self.button_click(self.app.set_bolus_button)
        time.sleep(1) 
        self.app.bolus_scale.set(0.32)
        self.button_click(self.app.set_button)
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.32'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        mock_show_message.assert_called_with("Success set bolus to " + "0.32" + " ml.")
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_baseline_on(self, mock_show_message): # baseline_on_button
        time.sleep(1) 
        self.button_click(self.app.baseline_on_button)
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'on')
        mock_show_message.assert_called_with("Baseline injection turned on.") 
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_baseline_off(self, mock_show_message): # baseline_off_button
        time.sleep(1) 
        self.button_click(self.app.baseline_off_button)
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        mock_show_message.assert_called_with("Baseline injection turned off.") 
        time.sleep(1) 

    def test_graph(self): # graph_button
        time.sleep(1) 
        self.button_click(self.app.graph_button)
        self.assertEqual(self.app.showing_graph, 'on')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.NORMAL)    
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)   
        self.button_click(self.app.stop_graph_button)  
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_stop_graph(self, mock_show_message): # graph_button + stop_graph_button
        time.sleep(1) 
        self.button_click(self.app.graph_button)
        self.button_click(self.app.stop_graph_button)
        mock_show_message.assert_called_with("Graph stopped.")
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL)        
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_start(self, mock_show_message): # start_button
        time.sleep(1) 
        self.button_click(self.app.start_button)
        status = self.core.status()
        self.assertTrue(self.app.start_button['state'] == tk.DISABLED)
        self.assertTrue(self.app.start)
        mock_show_message.assert_called_with("Simulation started.")
        ## start will update once
        self.assertEqual(status['Time'], Decimal('1'))
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_simulate_speed(self, mock_show_message): # set_simulate_speed_button + set button
        time.sleep(1)         
        self.button_click(self.app.set_simulate_speed_button)
        self.app.speed_scale.set(3)
        self.button_click(self.app.set_button)
        self.assertEqual(self.app.simulate_speed, int(1000/3))
        mock_show_message.assert_called_with("Simulation speed set to 3x.")
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        time.sleep(1) 

    def test_pause_not_show(self): # pause_button
        time.sleep(1) 
        self.button_click(self.app.pause_button)
        expected_text = "Simulation is paused. Press the \"Resume\" button to restart the system."
        self.assertEqual(self.app.pause_label.cget("text"), expected_text)
        self.assertEqual(self.app.showing_graph, 'off')
        self.button_click(self.app.resume_button)
        time.sleep(1) 


    def test_pause_show(self): # pause_button + graph_button
        time.sleep(1) 
        self.button_click(self.app.graph_button)
        self.button_click(self.app.pause_button)
        expected_text = "Simulation is paused. Press the \"Resume\" button to restart the system."
        self.assertEqual(self.app.pause_label.cget("text"), expected_text)
        self.assertEqual(self.app.showing_graph, 'pause')
        self.button_click(self.app.resume_button)
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_reset_not_show(self, mock_show_message) : # reset_button
        time.sleep(1) 
        self.button_click(self.app.reset_button)

        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL) 
        mock_show_message.assert_called_with("System reset.")
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_reset_show(self, mock_show_message) : # reset_button + graph_button
        time.sleep(1) 
        self.button_click(self.app.graph_button)
        self.button_click(self.app.reset_button)

        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL) 
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL)  
        mock_show_message.assert_called_with("System reset.")
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_resume_pause_show(self, mock_show_message): # graph_button + pause_button + resume_button
        time.sleep(1) 
        self.button_click(self.app.graph_button)
        self.button_click(self.app.pause_button)
        self.button_click(self.app.resume_button)
        self.assertFalse(self.app.paused)
        mock_show_message.assert_called_with("Simulation resumed.")
        self.assertTrue(self.app.showing_graph == 'on')
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)    
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_resume_pause_not_show(self, mock_show_message): # start_button + pause_button + resume_button
        time.sleep(1) 
        self.button_click(self.app.start_button)
        self.button_click(self.app.pause_button)
        self.button_click(self.app.resume_button)
        self.assertFalse(self.app.paused)
        mock_show_message.assert_called_with("Simulation resumed.")
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.start_button['state'] == tk.DISABLED)   
        time.sleep(1) 

    def test_combine_1(self): # simulate the all day condition 1 start can go truely: start + baseline off
        time.sleep(1) 
        self.button_click(self.app.start_button)
        for _ in range(599):
            self.core.update_by_minute()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('600'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        time.sleep(1) 

    def test_combine_2(self): # simulate the all day condition 2 start can go correctly with set baseline: start + set baseline + baseline on
        time.sleep(1) 
        self.button_click(self.app.set_baseline_button)
        self.app.baseline_scale.set(0.05)
        self.button_click(self.app.set_button)
        self.button_click(self.app.baseline_on_button)
        self.button_click(self.app.start_button)
        for _ in range(69):
            self.core.update_by_minute()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('70'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('1.0'))
        self.assertEqual(status['Daily Amount'], Decimal('1.5'))
        self.assertEqual(status['Baseline Status'], 'on')
        time.sleep(1) 

    def test_combine_3(self): # simulate the all day condition 2 start can go correctly with set bolus: start + set bolus + baseline off
        time.sleep(1)         
        self.button_click(self.app.set_bolus_button)
        self.app.bolus_scale.set(0.35)
        self.button_click(self.app.set_button)
        self.button_click(self.app.start_button)
        for _ in range(69):
            self.core.update_by_minute()
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('70'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.35'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        time.sleep(1) 

    @patch.object(DoctorApp, 'show_message')
    def test_combine_4(self, mock_show_message): # simulate the all day condition 2 start can go correctly with set bolus + baseline: start + set bolus + set baseline + baseline on + request bolus + set simulate speed + pasuse + resume + reset + show graph + stop graph + set baseline off
        time.sleep(1)         
        self.button_click(self.app.set_baseline_button)
        self.app.baseline_scale.set(0.05)
        self.button_click(self.app.set_button)
        self.button_click(self.app.set_bolus_button)
        self.app.bolus_scale.set(0.30)
        self.button_click(self.app.set_button)
        self.button_click(self.app.baseline_on_button)
        self.button_click(self.app.graph_button)
        self.assertEqual(self.app.showing_graph, 'on')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.NORMAL)    
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)    
        status = self.core.status()
        # print(status['Time'])
        self.button_click(self.app.start_button)
        for i in range(1, 60):
            self.core.update_by_minute()
            status = self.core.status()
            # print(status['Time'])
            if i == 4: # 5 min
                self.button_click(self.patient.request_bolus_button)
                self.assertEqual(status['Time'], Decimal('5'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('0.25'))
                self.assertEqual(status['Daily Amount'], Decimal('0.25'))
                self.assertEqual(status['Baseline Status'], 'on')
            if i == 5: # 6 min
                self.assertEqual(status['Time'], Decimal('6'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('0.60'))
                self.assertEqual(status['Daily Amount'], Decimal('0.60'))
                self.assertEqual(status['Baseline Status'], 'on')
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('60'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
        self.assertEqual(status['Hourly Amount'], Decimal('1.00'))
        self.assertEqual(status['Daily Amount'], Decimal('1.00'))
        self.assertEqual(status['Baseline Status'], 'on')
        
        self.button_click(self.app.set_simulate_speed_button)
        self.app.speed_scale.set(2)
        self.button_click(self.app.set_button)
        self.assertEqual(self.app.simulate_speed, int(1000/2)) 
        self.button_click(self.app.pause_button)
        expected_text = "Simulation is paused. Press the \"Resume\" button to restart the system."
        self.assertEqual(self.app.pause_label.cget("text"), expected_text)
        self.assertEqual(self.app.showing_graph, 'pause')
        self.button_click(self.app.resume_button)
        self.assertFalse(self.app.paused)
        mock_show_message.assert_called_with("Simulation resumed.")
        self.assertTrue(self.app.showing_graph == 'on')
        self.assertTrue(self.app.graph_button['state'] == tk.DISABLED)    
        self.button_click(self.app.stop_graph_button)
        mock_show_message.assert_called_with("Graph stopped.")
        self.assertEqual(self.app.showing_graph, 'off')
        self.assertTrue(self.app.stop_graph_button['state'] == tk.DISABLED)    
        self.assertTrue(self.app.graph_button['state'] == tk.NORMAL)       

        for i in range(1, 61): # 60 start
            self.core.update_by_minute()
            status = self.core.status()
            # print(status['Time'])
            if i == 5: # 66
                self.assertEqual(status['Time'], Decimal('66'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('0.70'))
                self.assertEqual(status['Daily Amount'], Decimal('1.3'))
                self.assertEqual(status['Baseline Status'], 'on')
            if i == 15: # 76
                self.assertEqual(status['Time'], Decimal('76'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('0.80'))
                self.assertEqual(status['Daily Amount'], Decimal('1.80'))
                self.assertEqual(status['Baseline Status'], 'on')

        for i in range(1, 60): # 120 start
            self.core.update_by_minute()
            status = self.core.status()
            # print(status['Time'])
            if i == 5: # 126
                self.button_click(self.app.baseline_off_button)
                status = self.core.status()
                self.assertEqual(status['Time'], Decimal('126'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('1.00'))
                self.assertEqual(status['Daily Amount'], Decimal('2.30'))
                self.assertEqual(status['Baseline Status'], 'off')
            if i == 6: # 127
                self.assertEqual(status['Time'], Decimal('127'))
                self.assertEqual(status['Baseline Rate'], Decimal('0.05'))
                self.assertEqual(status['Bolus Amount'], Decimal('0.30'))
                self.assertEqual(status['Hourly Amount'], Decimal('0.95'))
                self.assertEqual(status['Daily Amount'], Decimal('2.30'))
                self.assertEqual(status['Baseline Status'], 'off')

        self.button_click(self.app.reset_button)
        mock_show_message.assert_called_with("System reset.")
        status = self.core.status()
        # print(status)
        self.assertEqual(status['Time'], Decimal('0'))
        self.assertEqual(status['Baseline Rate'], Decimal('0.01'))
        self.assertEqual(status['Bolus Amount'], Decimal('0.2'))
        self.assertEqual(status['Hourly Amount'], Decimal('0.0'))
        self.assertEqual(status['Daily Amount'], Decimal('0.0'))
        self.assertEqual(status['Baseline Status'], 'off')
        self.assertFalse(self.app.start)
        self.assertFalse(self.app.paused)
        self.assertTrue(self.app.showing_graph == 'off')
        self.assertTrue(self.app.start_button['state'] == tk.NORMAL) 
        time.sleep(1) 

    def test_combine_5(self): # set_simulate_speed + start + reset + start 
        time.sleep(1) 
        self.button_click(self.app.set_simulate_speed_button)
        self.app.speed_scale.set(3)
        self.button_click(self.app.set_button)
        self.assertEqual(self.app.simulate_speed, int(1000/3)) 
        self.button_click(self.app.start_button)
        self.button_click(self.app.reset_button)
        self.button_click(self.app.start_button)
        self.assertEqual(self.app.simulate_speed, int(1000)) 
        time.sleep(1) 
    # def test_combine_6(self):
    #     pass
if __name__ == "__main__":
    unittest.main()
