import time
import matplotlib.dates
import numpy as np

import config
from hardware_state import HardwareState
from sensor_data import SensorLogger
from nicegui import ui
from datetime import datetime
from threading import Thread
from typing import List
import pytz
import os
import csv
from matplotlib.dates import DateFormatter, DayLocator, HourLocator


class WebUI:
    def __init__(self, sensor_logger: SensorLogger, hardware_state: HardwareState):
        self._sensor_logger = sensor_logger
        self._hardware_state = hardware_state
        self.__draw_ui__()
        self._enable_measurements = False

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
                sd1 = self._sensor_logger.get_data(sensor_id="pico_ft")
                if sd1 is not None:
                    last_data1 = sd1[-1]
                    self._label1.set_text("Sensor ID: " + last_data1.sensor_id + " Temperature: " +
                                          str(last_data1.temperature) + " " +
                                          datetime.fromtimestamp(last_data1.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd2 = self._sensor_logger.get_data(sensor_id="pico_fb")
                if sd2 is not None:
                    last_data2 = sd2[-1]
                    self._label2.set_text("Sensor ID: " + last_data2.sensor_id + " Temperature: " +
                                          str(last_data2.temperature) + " " +
                                          datetime.fromtimestamp(last_data2.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd3 = self._sensor_logger.get_data(sensor_id="pico_bt")
                if sd3 is not None:
                    last_data3 = sd3[-1]
                    self._label3.set_text("Sensor ID: " + last_data3.sensor_id + " Temperature: " +
                                          str(last_data3.temperature) + " " +
                                          datetime.fromtimestamp(last_data3.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                sd4 = self._sensor_logger.get_data(sensor_id="pico_bb")
                if sd4 is not None:
                    last_data4 = sd4[-1]
                    self._label4.set_text("Sensor ID: " + last_data4.sensor_id + " Temperature: " +
                                          str(last_data4.temperature) + " " +
                                          datetime.fromtimestamp(last_data4.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

                else:
                    self._label1.set_text("Sensor Pico_ft no data")
                    self._label2.set_text("Sensor Pico_fb no data")
                    self._label3.set_text("Sensor Pico_bt no data")
                    self._label4.set_text("Sensor Pico_bb no data")
            time.sleep(1.0)

    def update_line_plot(self) -> None:
        if not self._sensor_logger.enable_logging:
            return
        timestamps = []
        temperatures = []
        sensor_ids = {"pico_ft", "pico_fb", "pico_bt", "pico_bb"}
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

    def _init_measurement(self):
        with ui.dialog() as dialog, ui.card():
            file_name = ui.input(validation={'Measurement with that name already exists':
                                                    lambda value: not os.path.exists(
                                                        os.path.join(config.data_dir, file_name.value + ".csv"))})
            ui.button('Start Measurement', on_click=lambda: self._on_start_measurement_dialog(dialog, file_name))
        dialog.open()

    def _on_start_measurement_dialog(self, dialog, file_name):
        if not os.path.exists(os.path.join(config.data_dir, file_name.value + ".csv")):
                self._current_log_file = os.path.join(config.data_dir, file_name.value + ".csv")
                dialog.close()
                self._start_measurement()
        else:
            ui.notify("Measurement with that name already exists")
            return

    def _start_measurement(self):
        self._enable_measurements = True
        self._sensor_logger.enable_logging = True
        self.line_updates1 = ui.timer(0.5, self.update_line_plot, active=True)
        ui.notify("Starting Measuring")
        t = Thread(target=self._measuring_cycle)
        t.start()
        log_t = Thread(target=self._write_to_log)
        log_t.start()

    def _write_to_log(self):
        with open(self._current_log_file, "a", newline='')  as log_file:
            fieldnames = ['sensor id', 'temperature', 'timestamp']
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            writer.writeheader()
            last_timestamp = 0
            while self._sensor_logger.enable_logging:
                for sensor_id in config.sensor_ids:
                    try:
                        sd = self._sensor_logger.last_data[sensor_id]
                        if sd.timestamp > last_timestamp:
                            writer.writerow({'sensor id': sensor_id, 'temperature': sd.temperature,
                                             'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sd.timestamp))})
                            last_timestamp = sd.timestamp
                    except KeyError:
                        pass
                time.sleep(1)
            log_file.close()

    def _measuring_cycle(self):
        while True:
            if not self._enable_measurements:
                self._hardware_state.change_state(heater_desired_state="off")
                self._hardware_state.change_state(fan_desired_state="off")
                return
            t_min = 1000
            t_max = 0
            for v in self._sensor_logger.last_data.values():
                if t_max < v.temperature:
                    t_max = v.temperature
                if t_min > v.temperature:
                    t_min = v.temperature  # find t_max and t_min
            if self.slider.value - 3 <= t_min <= self.slider.value + 3 and self.slider.value - 3 <= t_max <= self.slider.value + 3:
                self._hardware_state.change_state(heater_desired_state="off")
                self._hardware_state.change_state(fan_desired_state="off")
            else:
                if t_max > self.slider.value + 3:
                    self._hardware_state.change_state(heater_desired_state="off")
                else:
                    self._hardware_state.change_state(heater_desired_state="on")
                self._hardware_state.change_state(fan_desired_state="on")
            time.sleep(5)

    def _stop_measurement(self):
        self._enable_measurements = False
        self._sensor_logger.reset_data()
        self.line_updates1 = ui.timer(0.1, self.update_line_plot, active=False)
        self._hardware_state.change_state(heater_desired_state="off")
        self._hardware_state.change_state(fan_desired_state="off")
        ui.notify("Stop Measuring")

    def _show_temperature(self):
        self._sensor_logger.enable_logging = True
        self.line_updates1 = ui.timer(0.5, self.update_line_plot, active=True)
        ui.notify("Showing Temperature")

    def _hide_temperature(self):
        self._sensor_logger.enable_logging = False
        self.line_updates1 = ui.timer(0.5, self.update_line_plot, active=False)
        ui.notify("Hiding Temperature")

    def hardware_state_changed(self, hardware_state):
        heater_current_state, heater_desired_state, fan_current_state, fan_desired_state = hardware_state.get_state()

    def __draw_ui__(self):
        self._label1 = ui.label("1")
        self._label2 = ui.label("2")
        self._label3 = ui.label("3")
        self._label4 = ui.label("4")
        self.line_plot = TemperaturePlot()

        ui.label("Auto Mode")
        with ui.row():
            self.slider = ui.slider(min=25, max=75, step=1, value=40)
            ui.linear_progress().bind_value_from(self.slider, 'value')
            ui.button('Auto Mode Start', on_click=lambda: self._init_measurement())
            ui.button('Stop Measurements', on_click=lambda: self._stop_measurement())
            ui.button('Show Temperature', on_click=lambda: self._show_temperature())
            ui.button('Hide Temperature', on_click=lambda: self._hide_temperature())

        ui.label("Manual Mode")
        with ui.row():
            self._switch1 = ui.switch('Heaters', on_change=lambda: self._change_heater_state())
            self._switch2 = ui.switch('Fans', on_change=lambda: self._change_fan_state())

    def _change_heater_state(self):
        if self._switch1.value:
            self._hardware_state.change_state(heater_desired_state="on")
        else:
            self._hardware_state.change_state(heater_desired_state="off")

    def _change_fan_state(self):
        if self._switch2.value:
            self._hardware_state.change_state(fan_desired_state="on")
        else:
            self._hardware_state.change_state(fan_desired_state="off")


class TemperaturePlot:
    def __init__(self):
        self._plot_n = 4
        self.line_plot = ui.line_plot(n=self._plot_n, limit=4200, figsize=(12, 5), update_every=1) \
            .with_legend(['pico_ft', 'pic_fb', 'pico_bt', 'pico_bb'], loc='upper center', ncol=self._plot_n)
        self._last_timestamp = {}

    def push_data(self, timestamp: List[float], temp: List[float]):
        if self._last_timestamp != timestamp[-1]:
            temp_vals = []
            for i in range(0, self._plot_n):
                temp_vals.append([temp[i]])

            self.line_plot.push([matplotlib.dates.date2num(datetime.fromtimestamp(timestamp[0], None))], temp_vals)
            self._last_timestamp = timestamp[-1]

            ax = self.line_plot.fig.get_axes()[0]
            format_str = '%H:%M:%S'
            format_ = matplotlib.dates.DateFormatter(format_str, tz=pytz.timezone("Africa/Accra"))
            ax.xaxis.set_major_formatter(format_)
            self.line_plot.fig.autofmt_xdate()
