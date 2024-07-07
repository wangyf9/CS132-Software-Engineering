from decimal import Decimal, getcontext
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

# Set the precision to 3 decimal places
getcontext().prec = 3  

class Core:
    # Static variable declaration
    MAX_DAILY_AMOUNT = Decimal('3.0')
    MAX_HOUR_AMOUNT = Decimal('1.0')

    def __init__(self):
        self.__baseline = Decimal('0.01')  # Baseline injection rate [0.01,0.1]
        self.__bolus = Decimal('0.2')  # Bolus injection amount [0.2,0.5]
        self.__dailyAmount = Decimal('0.0')
        self.__hourAmount = Decimal('0.0')
        self.__baselineStatus = 'off'  # Baseline Status: off, on, pause
        self.__minuteRecord = []  # Record the amount injected every minute (Size 60 * 24)
        self.__time = 0
        self.__hourlyRecord = []  # Record the amount injected every hour 
        self.__dailyRecord = []  # Record the amount injected every day 
        self.__timeRecord = []  # Record the time in minutes
        self.figure = plt.Figure(figsize=(10, 5))
        self.line1 = None
        self.line2 = None

    def status(self):
        return {
            'Time': self.__time,
            'Baseline Rate': self.__baseline,
            'Bolus Amount': self.__bolus,
            'Hourly Amount': self.__hourAmount,
            'Daily Amount': self.__dailyAmount,
            'Baseline Status': self.__baselineStatus,
        }
    
    def set_baseline(self, baseline: float) -> str:
        baseline = Decimal(str(baseline))
        if baseline < Decimal('0.01') or baseline > Decimal('0.1'):
            return "Baseline injection rate must be between 0.01 and 0.1 ml."
        self.__baseline =  Decimal(str(baseline))
        return "Success set baseline to " + str(baseline) + " ml."

    def set_bolus(self, bolus: float) -> str:
        bolus = Decimal(str(bolus))
        if bolus < Decimal('0.2') or bolus > Decimal('0.5'):
            return "Bolus injection amount must be between 0.2 and 0.5 ml."
        self.__bolus = Decimal(str(bolus))
        return "Success set bolus to " + str(bolus) + " ml."
    
    def baseline_on(self):
        self.__baselineStatus = 'on'
    
    def baseline_off(self):
        self.__baselineStatus = 'off'
    
    def validate(self, amount: Decimal) -> bool:
        # Check hour limit
        if (Decimal(self.__hourAmount) + amount > Core.MAX_HOUR_AMOUNT):
            return False
        # Check day limit    
        if (Decimal(self.__dailyAmount) + amount > Core.MAX_DAILY_AMOUNT):
            return False
        return True

    def update_by_minute(self):
        # If minuteRecord exceeds 1440, remove the oldest record
        if len(self.__minuteRecord) >= 1440:
            self.__minuteRecord.pop(0)
            self.__hourlyRecord.pop(0)
            self.__dailyRecord.pop(0)
            self.__timeRecord.pop(0)

        if self.__baselineStatus == 'on':
            self.__hourAmount = sum(self.__minuteRecord[-59:])
            if self.validate(self.__baseline):
                self.__minuteRecord.append(Decimal(str(self.__baseline)))

            else:
                self.__minuteRecord.append(Decimal('0.0'))

        else:
            self.__minuteRecord.append(Decimal('0.0'))

        # Calculate the hourly and daily amounts
        self.__time += 1
        self.__hourAmount = sum(self.__minuteRecord[-60:])
        self.__dailyAmount = sum(self.__minuteRecord)

        self.__hourlyRecord.append(self.__hourAmount)
        self.__dailyRecord.append(self.__dailyAmount)
        self.__timeRecord.append(self.__time)
        
    def request_bolus(self) -> bool:
        if self.validate(self.__bolus):
            if len(self.__minuteRecord) == 0:
                return False
            else:
                self.__minuteRecord[-1] += self.__bolus
                # Recalculate hour and daily amounts after bolus request
                self.__hourAmount = sum(self.__minuteRecord[-60:])
                self.__dailyAmount = sum(self.__minuteRecord)
                self.__hourlyRecord[-1] = self.__hourAmount
                self.__dailyRecord[-1] = self.__dailyAmount
            return True
        return False

    def reset(self):
        self.__baseline = Decimal('0.01')
        self.__bolus = Decimal('0.2')
        self.__dailyAmount = Decimal('0.0')
        self.__hourAmount = Decimal('0.0')
        self.__baselineStatus = 'off'
        self.__minuteRecord = []
        self.__hourlyRecord = []
        self.__dailyRecord = []
        self.__timeRecord = []
        self.__time = 0

    def initialize_axes(self, fig):

        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        self.line1, = ax1.plot([], [], color='tab:blue', label='Hourly Amount')
        self.line2, = ax2.plot([], [], color='tab:red', label='Daily Amount')
        self.hourly_limit = ax1.axhline(y=1.0, color='tab:blue', linestyle='--', label='Hourly Limit', linewidth=0.5, alpha=0.5)
        self.daily_limit = ax2.axhline(y=3.0, color='tab:red', linestyle='--', label='Daily Limit', linewidth=0.5, alpha=0.5)
        self.update_axes(ax1, ax2)
        ax1.set_title('Hourly and Daily Amount Over Time') 
        return ax1, ax2
    
    def update_axes(self, ax1, ax2):
        time_data = self.__timeRecord
        hourly_data = self.__hourlyRecord
        daily_data = self.__dailyRecord
        color = 'tab:blue'
        ax1.set_xlabel('Time (minutes)')
        ax1.set_ylabel('Hourly Amount (mL)', color=color)
        ax1.tick_params(axis='y', labelcolor=color, labelsize=8)
        ax1.tick_params(axis='x', labelsize=8)
        ax1.legend(loc='upper left')
        color='tab:red'
        ax2.set_ylabel('Daily Amount (mL)', color=color)
        ax2.tick_params(axis='y', labelcolor=color, labelsize=8)
        ax2.legend(loc='upper right')

        self.line1.set_data(time_data, hourly_data)
        self.line2.set_data(time_data, daily_data)

        if len(time_data) < 1440:
            x_ticks = np.arange(0, 1441, 60)
            x_lim = [0, 1440]
        else:
            max_time = max(time_data)
            extra_ticks = max_time - 1440
            x_ticks = np.arange(extra_ticks, max_time, 60)
            x_lim = [extra_ticks, max_time]

        ax1.set_xticks(x_ticks)
        ax2.set_xticks(x_ticks)
        ax1.set_xlim(x_lim)
        ax2.set_xlim(x_lim)

        ax1.set_ylim([0, 3.5])
        ax2.set_ylim([0, 3.5])
        ax1.set_yticks(np.arange(0, 3.1, 0.1))
        ax2.set_yticks(np.arange(0, 3.1, 0.1))

        ax2.yaxis.set_label_position("right")
        self.figure.canvas.draw_idle()  # Update the figure

if __name__ == "__main__":
    core = Core()
    print(core.set_baseline(0.05))
    print(core.set_bolus(0.3))
    print(core.status())
    core.baseline_on()
    core.update_by_minute()
    print("1",core.status())
    core.update_by_minute()
    print("2",core.status())
    core.update_by_minute()
    core.update_by_minute()
    core.update_by_minute()
    print(core.status())
    core.request_bolus()
    core.update_by_minute()
    core.update_by_minute()
    core.update_by_minute()
    core.update_by_minute()
    core.update_by_minute()
    print(core.status())
