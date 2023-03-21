import time

import matplotlib.dates
import numpy as np

from sensor_data import SensorLogger
from nicegui import ui
from datetime import datetime
from threading import Thread
from typing import List
import pytz
from matplotlib.dates import DateFormatter, DayLocator, HourLocator


class WebUI:
    def __init__(self, sensor_logger: SensorLogger):
        self._sensor_logger = sensor_logger
        self.__draw_ui__()

    def run(self):
        t = Thread(target=self._label_updater)
        t.start()
        ui.run(reload=False)

    def _label_updater(self):
        while True:
            if not self._sensor_logger.enable_logging:
                self._label1.set_text("Sensor: Pico_fb, no active measurements")
                self._label2.set_text("Sensor: Pico_bb, no active measurements")
                self._label3.set_text("Sensor: Pico_bb, no active measurements")
                self._label4.set_text("Sensor: Pico_bb, no active measurements")

            else:
                sd1 = self._sensor_logger.get_data(sensor_id="pico_fb_1")
                if sd1 is not None:
                    last_data1 = sd1[-1]
                    self._label1.set_text("Sensor ID: " + last_data1.sensor_id + " Temperature: " +
                                          str(last_data1.temperature) + " " +
                                          datetime.fromtimestamp(last_data1.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd2 = self._sensor_logger.get_data(sensor_id="pico_bb")
                if sd2 is not None:
                    last_data2 = sd2[-1]
                    self._label2.set_text("Sensor ID: " + last_data2.sensor_id + " Temperature: " +
                                          str(last_data2.temperature) + " " +
                                          datetime.fromtimestamp(last_data2.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd3 = self._sensor_logger.get_data(sensor_id="pico_ft")
                if sd3 is not None:
                    last_data3 = sd3[-1]
                    self._label3.set_text("Sensor ID: " + last_data3.sensor_id + " Temperature: " +
                                          str(last_data3.temperature) + " " +
                                          datetime.fromtimestamp(last_data3.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd4 = self._sensor_logger.get_data(sensor_id="pico_ft")
                if sd4 is not None:
                    last_data4 = sd4[-1]
                    self._label4.set_text("Sensor ID: " + last_data4.sensor_id + " Temperature: " +
                                          str(last_data4.temperature) + " " +
                                          datetime.fromtimestamp(last_data4.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                else:
                    self._label1.set_text("Sensor Pico_fb no data")
                    self._label2.set_text("Sensor Pico_bb no data")
                    self._label3.set_text("Sensor Pico_bb no data")
                    self._label4.set_text("Sensor Pico_bb no data")
            time.sleep(1.0)

    def update_line_plot(self) -> None:
        if not self._sensor_logger.enable_logging:
            return
        timestamps = []
        temperatures = []
        sensor_ids = {"pico_fb_1", "pico_ft", "pico_bb"}
        for sensor_id in sensor_ids:
            sd = self._sensor_logger.get_data(sensor_id=sensor_id)
            if sd is None:
                timestamps.append(time.time())
                temperatures.append(0)
            else:
                last_data = sd[-1]
                timestamps.append(last_data.timestamp)
                temperatures.append(last_data.temperature)

        self.line_plot.push_data(timestamps, temperatures)

    def _start_measurement(self):
        self._sensor_logger.enable_logging = True
        self.line_updates1 = ui.timer(0.5, self.update_line_plot, active=True)
        ui.notify("Starting Measuring")

    def _stop_measurement(self):
        self._sensor_logger.enable_logging = False
        self.line_updates1 = ui.timer(0.1, self.update_line_plot, active=False)
        ui.notify("Stop Measuring")

    def __draw_ui__(self):
        self._label1 = ui.label("1")
        self._label2 = ui.label("2")
        self._label3 = ui.label("3")
        self._label4 = ui.label("4")
        self.line_plot = TemperaturePlot()

        # with ui.row():
        #     with ui.plot(figsize=(5, 3)):
        #         x = np.linspace(0.0, 5.0)
        #         y1 = np.linspace(0.0, 6.1)
        #         y2 = np.linspace(0.0, 5)
        #         y3 = np.linspace(0.0, 54)
        #         y4 = np.linspace(0.0, 12)
        #         plt.plot(x, y1, '-', x, y2, '-', x, y3, '-', x, y4, '-')

        ui.label("Auto Mode")
        with ui.row():
            slider = ui.slider(min=0, max=75, step=1, value=20)
            ui.linear_progress().bind_value_from(slider, 'value')
            ui.button('Auto Mode Start', on_click=lambda: self._start_measurement())
            ui.button('Stop Measurements', on_click=lambda: self._stop_measurement())

        ui.label("Manual Mode")
        with ui.row():
            ui.button('Heaters On', on_click=lambda: ui.notify(f'You clicked me!'))
            ui.button('Ventilators On', on_click=lambda: ui.notify(f'You clicked me!'))
        with ui.row():
            ui.button('Ventilators Off', on_click=lambda: ui.notify(f'You clicked me!'))
            ui.button('Heaters Off', on_click=lambda: ui.notify(f'You clicked me!'))


class TemperaturePlot:
    def __init__(self):
        self._plot_n = 3
        self.line_plot = ui.line_plot(n=self._plot_n, limit=4200, figsize=(12, 5), update_every=1) \
            .with_legend(['pico1', 'pico2', 'pico3'], loc='upper center', ncol=self._plot_n)
        self._last_timestamp = {}

    def push_data(self, timestamp: List[float], temp: List[float]):
        if self._last_timestamp != timestamp[-1]:
            temp_vals = []
            for i in range(0, self._plot_n):
                temp_vals.append([temp[i]])

            print(temp_vals)
            self.line_plot.push([matplotlib.dates.date2num(datetime.fromtimestamp(timestamp[0], None))], temp_vals)
            self._last_timestamp = timestamp[-1]

            ax = self.line_plot.fig.get_axes()[0]
            format_str = '%H:%M:%S'
            format_ = matplotlib.dates.DateFormatter(format_str, tz=pytz.timezone("Europe/Luxembourg"))
            ax.xaxis.set_major_formatter(format_)
            self.line_plot.fig.autofmt_xdate()
